from airflow.decorators import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.models import Variable
from airflow.utils.dates import days_ago
from datetime import timedelta
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

XCOM_KEY = 'file_path'

@dag(
    default_args=default_args,
    description='GCS에서 CSV 파일 가져오기',
    start_date=days_ago(1),
    schedule="@daily",
    catchup=False,
    tags=['gcs', 'csv'],
)
def process_csv_to_parquet():

    @task()
    def get_csv_from_gcs(**context):
        # GCS 연결 생성
        gcs_hook = GCSHook(
            gcp_conn_id='google_cloud_default',
            keyfile_dict=Variable.get('GCP_API_KEY')
        )
        
        bucket_name = 'dowhat-de1-datalake'
        object_name = 'v1/csv_테이크.csv' # 이걸로 테스트
        local_file_path = f'/tmp/{object_name}'

        # GCS에서 파일 다운로드
        file_content = gcs_hook.download(bucket_name=bucket_name, object_name=object_name)
        
        # 대충 tmp에 저장 
        with open(local_file_path, 'wb') as file:
            file.write(file_content)
        
        print(f"csv download: {local_file_path}")

        context['task_instance'].xcom_push(key=XCOM_KEY, value=local_file_path)

    @task()
    def process_file(**context):
        file_path: str = context['task_instance'].xcom_pull(key=XCOM_KEY, task_ids='task_1')
        print(f"success: {file_path}")

    csv_file_path = get_csv_from_gcs()
    process_result = process_file()
    
    csv_file_path >> process_result

gcs_csv_import_dag = process_csv_to_parquet()