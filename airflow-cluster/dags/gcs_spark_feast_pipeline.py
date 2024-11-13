from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import tempfile
import logging
import json

def create_spark_session(app_name):
    """
    Spark 세션 생성 함수
    Airflow Variables의 credentials 사용
    """
    try:
        # Airflow Variables에서 GCP credentials 가져오기
        gcp_credentials = Variable.get("gcp_credentials")
        
        # 임시 credentials 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(gcp_credentials)
            temp_credentials_path = f.name
            
        logging.info(f"Created temporary credentials file at: {temp_credentials_path}")
        
        # Spark 세션 생성
        spark = (SparkSession.builder
            .appName(app_name)
            .master('local[*]')
            .config('spark.jars', '/opt/airflow/jars/gcs-connector-hadoop3-latest.jar')
            .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true')
            .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', temp_credentials_path)
            .config('spark.hadoop.fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')
            .config('spark.hadoop.fs.AbstractFileSystem.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS')
            .config('spark.driver.memory', '2g')
            .config('spark.executor.memory', '2g')
            .getOrCreate())
            
        return spark, temp_credentials_path
        
    except Exception as e:
        logging.error(f"Error creating Spark session: {str(e)}")
        raise

def stop_spark_session(spark, temp_credentials_path=None):
    """Spark 세션 종료 및 임시 파일 정리"""
    try:
        if spark is not None:
            spark.stop()
        if temp_credentials_path:
            import os
            if os.path.exists(temp_credentials_path):
                os.unlink(temp_credentials_path)
                logging.info(f"Cleaned up temporary credentials file: {temp_credentials_path}")
    except Exception as e:
        logging.error(f"Error in cleanup: {str(e)}")

def extract_from_gcs(**context):
    """GCS에서 데이터 추출"""
    spark = None
    temp_credentials_path = None
    
    try:
        spark, temp_credentials_path = create_spark_session("Extract_GCS")
        
        # GCS 버킷 정보 가져오기
        bucket_name = Variable.get("gcp_bucket_name")
        logging.info(f"Extracting data from bucket: {bucket_name}")
        
        # GCS에서 데이터 읽기
        input_path = f"gs://{bucket_name}/raw-data/test_data"
        df = spark.read.parquet(input_path)
        logging.info(f"Successfully read data from: {input_path}")
        
        # 중간 결과 저장
        output_path = f"gs://{bucket_name}/staging/extracted/"
        df.write.mode("overwrite").parquet(output_path)
        logging.info(f"Successfully wrote extracted data to: {output_path}")
        
        context['task_instance'].xcom_push(key='data_location', value=output_path)
        return output_path
        
    except Exception as e:
        logging.error(f"Error in extract_from_gcs: {str(e)}")
        raise
        
    finally:
        stop_spark_session(spark, temp_credentials_path)

def transform_data(**context):
    """Spark로 데이터 변환"""
    spark = None
    temp_credentials_path = None
    
    try:
        spark, temp_credentials_path = create_spark_session("Transform_Data")
        
        # 이전 단계 데이터 위치 가져오기
        data_location = context['task_instance'].xcom_pull(key='data_location')
        logging.info(f"Reading data from: {data_location}")
        
        # 데이터 읽기
        df = spark.read.parquet(data_location)
        
        # 데이터 변환 작업 수행
        transformed_df = df.withColumn(
            "processed_timestamp",
            F.current_timestamp()
        )
        # 추가적인 변환 로직
        # transformed_df = transformed_df.withColumn(...) 
        
        # 변환된 데이터 저장
        bucket_name = Variable.get("gcp_bucket_name")
        output_path = f"gs://{bucket_name}/staging/transformed/"
        transformed_df.write.mode("overwrite").parquet(output_path)
        logging.info(f"Successfully wrote transformed data to: {output_path}")
        
        context['task_instance'].xcom_push(key='transformed_data_location', value=output_path)
        return output_path
        
    except Exception as e:
        logging.error(f"Error in transform_data: {str(e)}")
        raise
        
    finally:
        stop_spark_session(spark, temp_credentials_path)

def load_to_feast(**context):
    """Feast로 데이터 로드"""
    try:
        from feast import FeatureStore

        # Feast store 초기화
        store = FeatureStore(repo_path="/opt/airflow/feast")
        logging.info("Initialized Feast Feature Store")

        # 변환된 데이터 위치
        data_location = context['task_instance'].xcom_pull(key='transformed_data_location')
        logging.info(f"Loading data from: {data_location}")

        # Feast feature view 가져오기
        feature_views = store.list_feature_views()
        logging.info(f"Found feature views: {[fv.name for fv in feature_views]}")

        # Feast에 데이터 materialize
        store.materialize_incremental(end_date=datetime.now())
        logging.info("Successfully materialized features to online store")

    except Exception as e:
        logging.error(f"Error loading data to Feast: {str(e)}")

# DAG 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
dag = DAG(
    'gcs_spark_feast_pipeline',
    default_args=default_args,
    description='Pipeline from GCS through Spark to Feast',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Task 정의
extract_task = PythonOperator(
    task_id='extract_from_gcs',
    python_callable=extract_from_gcs,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_feast',
    python_callable=load_to_feast,
    provide_context=True,
    dag=dag,
)

# Task 순서 정의
extract_task >> transform_task >> load_task
