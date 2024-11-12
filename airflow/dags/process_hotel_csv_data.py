import logging
import os

from airflow.decorators import task, dag
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.models import Variable

logger = logging.getLogger(__name__)

GCS_BUCKET_NAME = 'dowhat-de1-datalake'
PROCESSED_BUCKET_NAME = 'dowhat-de1-datawarehouse'
CSV_PATH = 'v1/csv/'
PARQUET_PATH = '/v1/hotel_order/'
LOCAL_PATH = '/tmp/hotel_order.parquet'
GCP_API_KEY = Variable.get('GCP_API_KEY')

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
        csv_files = [file for file in files if file.endswith('.csv')]
        logger.info(f'Found CSV files: {csv_files}')
        return csv_files

    @task
    def process_csv_with_spark(files):
        # SparkSubmitOperator를 사용하여 스파크 작업 실행
        spark_job = SparkSubmitOperator(
            task_id='spark_process_csv',
            application='/opt/airflow/scripts/process_hotel_csv_data.py',  # Spark 어플리케이션 경로 지정
            conf={
                'spark.hadoop.fs.gs.impl': 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem'
            },
            application_args=files + [LOCAL_PATH],
            verbose=True,
            env_vars={
                'GOOGLE_APPLICATION_CREDENTIALS': GCP_API_KEY
            }
        )
        return spark_job.execute({})

    @task
    def upload_parquet_to_gcs():
        # 로컬에 저장된 Parquet 파일을 GCS로 업로드
        upload_task = LocalFilesystemToGCSOperator(
            task_id='upload_parquet_to_gcs',
            src=LOCAL_PATH,
            dst=PARQUET_PATH + 'processed_orders.parquet',
            bucket=PROCESSED_BUCKET_NAME,
            google_cloud_storage_conn_id="google_cloud_default"
        )
        upload_task.execute({})

    csv_files = list_csv_files()
    process_csv_with_spark(csv_files)
    upload_parquet_to_gcs()

process_hotel_csv_data()
