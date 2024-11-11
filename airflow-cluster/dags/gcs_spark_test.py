# dags/gcs_spark_test.py
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
import os

def test_gcs_spark_connection():
    """GCS와 Spark 연결 테스트"""
    # Spark 세션 생성
    spark = SparkSession.builder \
        .appName("GCS_Spark_Test") \
        .master(os.getenv('SPARK_MASTER_URL')) \
        .config('spark.jars', '/opt/airflow/jars/gcs-connector-hadoop3-latest.jar') \
        .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true') \
        .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', 
                os.getenv('GOOGLE_APPLICATION_CREDENTIALS')) \
        .getOrCreate()

    try:
        # 테스트용 간단한 DataFrame 생성
        test_data = [("1", "test")]
        df = spark.createDataFrame(test_data, ["id", "value"])
        
        # GCS에 쓰기 테스트
        bucket_name = os.getenv('GCP_BUCKET_NAME')
        df.write.mode("overwrite").parquet(f"gs://{bucket_name}/test-connection/")
        
        # GCS에서 읽기 테스트
        read_df = spark.read.parquet(f"gs://{bucket_name}/test-connection/")
        print("데이터 읽기 성공:")
        read_df.show()
        
        return "연결 테스트 성공!"
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        spark.stop()

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
    'gcs_spark_test',
    default_args=default_args,
    description='Test GCS and Spark Connection',
    schedule=None,
    catchup=False
)

test_task = PythonOperator(
    task_id='test_gcs_spark_connection',
    python_callable=test_gcs_spark_connection,
    dag=dag,
)
