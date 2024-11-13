from pyspark.sql import SparkSession
from airflow.models import Variable
import logging
import tempfile
import json
import os

def create_spark_session(app_name="GCS_Spark_App"):
    """
    Creates and configures a Spark session for GCS connectivity using Airflow Variables
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
            #.master('local[*]')   주석처리하고 클러스터 모드 사용
            .config('spark.jars', '/opt/airflow/jars/gcs-connector-hadoop3-latest.jar')
            .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true')
            .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', temp_credentials_path)
            .config('spark.hadoop.fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')
            .config('spark.hadoop.fs.AbstractFileSystem.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS')
            # 메모리 설정
            .config('spark.driver.memory', '1g')
            .config('spark.executor.memory', '1g')
            .config('spark.executor.cores', '1')
            .config('spark.executor.instances', '2')
            .config('spark.dynamicAllocation.enabled', 'false')  # 명시적으로 동적 할당 비활성화
            .getOrCreate())
        
        return spark, temp_credentials_path
        
    except Exception as e:
        logging.error(f"Error creating Spark session: {str(e)}")
        raise

def stop_spark_session(spark, temp_credentials_path=None):
    """
    Safely stops the Spark session and cleans up temporary files
    """
    try:
        if spark is not None:
            spark.stop()
        
        # 임시 credentials 파일 삭제
        if temp_credentials_path and os.path.exists(temp_credentials_path):
            os.unlink(temp_credentials_path)
            logging.info(f"Cleaned up temporary credentials file: {temp_credentials_path}")
            
    except Exception as e:
        logging.error(f"Error in cleanup: {str(e)}")
