import logging

from airflow.decorators import task, dag
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.bash import BashOperator
from airflow.models import Variable

logger = logging.getLogger(__name__)

GCS_BUCKET_NAME = 'dowhat-de1-datalake'
PROCESSED_BUCKET_NAME = 'dowhat-de1-datawarehouse'
CSV_PATH = 'v1/csv/'
GCP_API_KEY = Variable.get('GCP_API_KEY')

@dag(
    start_date=days_ago(1),
    schedule="@daily",
    catchup=False
)
def process_hotel_csv_data():
    
    @task
    def list_csv_files():
        gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
        files = gcs_hook.list(GCS_BUCKET_NAME, prefix=CSV_PATH)
        gcs_file_paths = []

        for file in files:
            if file.endswith('.csv'):
                gcs_path = f'gs://{GCS_BUCKET_NAME}/{file}'
                gcs_file_paths.append(gcs_path)

        logger.info(f'GCS file paths: {gcs_file_paths}')
        return gcs_file_paths

    @task
    def prepare_gcs_key():
        import os
        
        # 디렉토리 생성
        os.makedirs('/tmp/airflow', exist_ok=True)

        # 지정된 경로에 키 파일 생성
        key_path = '/tmp/airflow/key.json'
        gcs_key_content = Variable.get('GCP_API_KEY')

        with open(key_path, 'w') as f:
            f.write(gcs_key_content)
        
        return key_path

    gcs_key_path = prepare_gcs_key()

    @task
    def prepare_csv_files_string(csv_files):
        if not csv_files:
            logger.warning('No CSV files found. Returning an empty string.')
            return ''
        return ','.join(csv_files)

    csv_files = list_csv_files()
    csv_files_str = prepare_csv_files_string(csv_files)

    # BashOperator를 사용한 spark-submit 명령어 구성
    spark_job = BashOperator(
        task_id='process_csv_with_spark',
        bash_command="""
            spark-submit \
            --master local[*] \
            --deploy-mode client \
            --conf spark.executor.instances=2 \
            --conf spark.executor.memory=4g \
            --conf spark.executor.cores=2 \
            --conf spark.driver.cores=1 \
            --conf spark.hadoop.fs.gs.impl=com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem \
            --conf spark.hadoop.fs.gs.auth.service.account.enable=true \
            --conf spark.hadoop.google.cloud.auth.service.account.json.keyfile=/tmp/airflow/key.json \
            --conf spark.driver.bindAddress=0.0.0.0 \
            --files {{ task_instance.xcom_pull(task_ids='prepare_gcs_key') }} \
            --jars https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar \
            /opt/airflow/scripts/process_hotel_csv_data.py \
            {{ task_instance.xcom_pull(task_ids='prepare_csv_files_string') }}
        """
    )
    gcs_key_path >> csv_files_str >> spark_job

process_hotel_csv_data()