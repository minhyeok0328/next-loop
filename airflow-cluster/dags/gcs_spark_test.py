from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from config.spark_conf import create_spark_session, stop_spark_session
from airflow.models import Variable
import logging

def test_gcs_spark_connection():
    """
    GCS와 Spark 연결 테스트를 위한 함수
    """
    spark = None
    temp_credentials_path = None
    
    try:
        # Spark 세션 생성
        spark, temp_credentials_path = create_spark_session("GCS_Spark_Test")
        
        # 테스트용 간단한 DataFrame 생성
        test_data = [
            ("1", "test_1", "2024-01-01"),
            ("2", "test_2", "2024-01-02"),
            ("3", "test_3", "2024-01-03")
        ]
        df = spark.createDataFrame(test_data, ["id", "value", "date"])
        
        # GCS에 쓰기 테스트
        bucket_name = Variable.get("gcp_bucket_name")
        output_path = f"gs://{bucket_name}/test-connection/"
        
        logging.info(f"Attempting to write to GCS bucket: {bucket_name}")
        
        # Parquet 형식으로 저장 (파티셔닝 적용)
        df.write \
          .mode("overwrite") \
          .partitionBy("date") \
          .parquet(output_path)
        
        logging.info("Successfully wrote data to GCS")
        
        # GCS에서 읽기 테스트
        read_df = spark.read.parquet(output_path)
        logging.info("Successfully read data from GCS:")
        read_df.show()
        
        return "연결 테스트 성공!"
    
    except Exception as e:
        logging.error(f"Error in GCS Spark test: {str(e)}")
        raise
    
    finally:
        stop_spark_session(spark, temp_credentials_path)

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
