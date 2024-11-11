# dags/gcs_spark_feast_pipeline.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os

def create_spark_session(app_name):
    """Spark 세션 생성 함수"""
    return SparkSession.builder \
        .appName(app_name) \
        .master(os.getenv('SPARK_MASTER_URL')) \
        .config('spark.jars', '/opt/airflow/jars/gcs-connector-hadoop3-latest.jar') \
        .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true') \
        .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', 
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS')) \
        .getOrCreate()

def extract_from_gcs(**context):
    """GCS에서 데이터 추출"""
    spark = create_spark_session("Extract_GCS")
    try:
        # GCS 버킷 정보 가져오기
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        
        # GCS에서 데이터 읽기
        df = spark.read.parquet(f"gs://{bucket_name}/raw-data/")
        
        # 중간 결과 저장
        output_path = f"gs://{bucket_name}/staging/extracted/"
        df.write.mode("overwrite").parquet(output_path)
        
        context['task_instance'].xcom_push(
            key='data_location', 
            value=output_path
        )
    finally:
        spark.stop()

def transform_data(**context):
    """Spark로 데이터 변환"""
    spark = create_spark_session("Transform_Data")
    try:
        # 이전 단계 데이터 위치 가져오기
        data_location = context['task_instance'].xcom_pull(
            key='data_location'
        )
        
        # 데이터 읽기
        df = spark.read.parquet(data_location)
        
        # 데이터 변환 작업 수행
        transformed_df = df.withColumn(
            "processed_timestamp", 
            F.current_timestamp()
        )
        
        # 추가적인 변환 로직은 여기에 구현
        # ...
        
        # 변환된 데이터 저장
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        output_path = f"gs://{bucket_name}/staging/transformed/"
        transformed_df.write.mode("overwrite").parquet(output_path)
        
        context['task_instance'].xcom_push(
            key='transformed_data_location', 
            value=output_path
        )
    finally:
        spark.stop()

def load_to_feast(**context):
    """Feast로 데이터 로드"""
    from feast import FeatureStore
    
    # Feast store 초기화
    store = FeatureStore(repo_path="/opt/airflow/feast")
    
    # 변환된 데이터 위치
    data_location = context['task_instance'].xcom_pull(
        key='transformed_data_location'
    )
    
    try:
        # Feast에 데이터 로드
        store.materialize_incremental(
            end_date=datetime.now(),
            feature_views=store.list_feature_views()
        )
    except Exception as e:
        print(f"Error loading data to Feast: {str(e)}")
        raise

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

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
