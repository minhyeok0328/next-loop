import logging
import os
from datetime import datetime
from airflow.decorators import task, dag
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.models import Variable
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
logger = logging.getLogger(__name__)
GCS_BUCKET_NAME = 'dowhat-de1-datalake'
PROCESSED_BUCKET_NAME = 'dowhat-de1-datawarehouse'
CSV_PATH = 'v1/csv/'
PARQUET_PATH = '/v1/hotel_order/'
LOCAL_PATH = '/tmp/hotel_order.parquet'
# JSON 필드(contents)의 스키마 정의
contents_schema = StructType([
    StructField("orderType", StringType(), True),
    StructField("itemSeq", IntegerType(), True),
    StructField("count", IntegerType(), True),
    StructField("itemName", StringType(), True),
    StructField("departmentSeq", IntegerType(), True),
    StructField("person", IntegerType(), True),
    StructField("price", IntegerType(), True),
    StructField("wantStart", StringType(), True),
    StructField("wantEnd", StringType(), True)
])
@dag(
    start_date=days_ago(1),
    schedule="@daily",
    catchup=False
)
def process_hotel_csv_data():
    
    @task
    def list_csv_files():
        # Google Cloud Storage에서 CSV 파일 목록 가져오기
        gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
        files = gcs_hook.list(GCS_BUCKET_NAME, prefix=CSV_PATH)
        gcs_file_paths = []
        # 각 파일의 GCS 경로 생성
        for file in files:
            if file.endswith('.csv'):
                gcs_path = f'gs://{GCS_BUCKET_NAME}/{file}'
                gcs_file_paths.append(gcs_path)
        logger.info(f'GCS file paths: {gcs_file_paths}')
        return gcs_file_paths
    @task
    def prepare_csv_files_string(csv_files):
        return ','.join(csv_files)
    csv_files = list_csv_files()    
    csv_files_str = prepare_csv_files_string(csv_files)
    # Spark 작업을 클러스터에 제출하는 작업 생성
    spark_job = SparkSubmitOperator(
        task_id='process_csv_with_spark',
        application='/opt/airflow/scripts/process_hotel_csv_data.py',  # Spark 스크립트 경로
        name='hotel_csv_processing',
        conn_id='spark_default',
        application_args=[csv_files_str, 'gs://dowhat-datawarehouse/data.parquet'],
        conf={
            'spark.executor.memory': '2g',
            'spark.driver.memory': '1g'
        }
    )
    spark_job
process_hotel_csv_data()