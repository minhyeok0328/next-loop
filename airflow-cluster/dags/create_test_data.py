from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.models import Variable
import logging
import tempfile
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

def create_and_upload_test_data(**context):
    """테스트 데이터 생성 및 GCS 업로드"""
    spark = None
    temp_credentials_path = None
    
    try:
        # GCP credentials 가져오기
        gcp_credentials = Variable.get("gcp_credentials")
        
        # 임시 credentials 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(gcp_credentials)
            temp_credentials_path = f.name
        
        logging.info(f"Created temporary credentials file at: {temp_credentials_path}")
        
        # Spark 세션 생성
        spark = (SparkSession.builder
            .appName("Create_Test_Data")
            .master('local[*]')
            .config('spark.jars', '/opt/airflow/jars/gcs-connector-hadoop3-latest.jar')
            .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true')
            .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', temp_credentials_path)
            .config('spark.hadoop.fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')
            .config('spark.hadoop.fs.AbstractFileSystem.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS')
            .getOrCreate())
        
        # 스키마 정의
        schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("item_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("amount", IntegerType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        
        # 테스트 데이터 생성
        data = [
            ("user1", "item1", "electronics", 100, datetime.now()),
            ("user2", "item2", "books", 50, datetime.now()),
            ("user3", "item3", "clothing", 75, datetime.now()),
            ("user4", "item4", "electronics", 200, datetime.now()),
            ("user5", "item5", "books", 30, datetime.now())
        ]
        
        # DataFrame 생성
        df = spark.createDataFrame(data, schema)
        
        # GCS에 저장
        bucket_name = Variable.get("gcp_bucket_name")
        output_path = f"gs://{bucket_name}/raw-data/test_data"
        
        df.write \
          .mode("overwrite") \
          .partitionBy("category") \
          .parquet(output_path)
        
        logging.info(f"Successfully created and uploaded test data to: {output_path}")
        
    except Exception as e:
        logging.error(f"Error creating test data: {str(e)}")
        raise
        
    finally:
        if spark:
            spark.stop()
        if temp_credentials_path:
            import os
            if os.path.exists(temp_credentials_path):
                os.unlink(temp_credentials_path)
                logging.info(f"Cleaned up temporary credentials file: {temp_credentials_path}")

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
    'create_test_data',
    default_args=default_args,
    description='Create and upload test data to GCS',
    schedule_interval=None,
    catchup=False
)

create_data_task = PythonOperator(
    task_id='create_and_upload_test_data',
    python_callable=create_and_upload_test_data,
    provide_context=True,
    dag=dag,
)
