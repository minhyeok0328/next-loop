from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'spark_cluster_test',
    default_args=default_args,
    description='Test Spark Cluster Connection',
    schedule_interval=None,
    catchup=False
)

spark_test = SparkSubmitOperator(
    task_id='spark_test_task',
    conn_id='spark_default',
    application='/opt/airflow/dags/scripts/spark_test.py',
    conf={
        'spark.driver.memory': '1g',
        'spark.executor.memory': '2g',
        'spark.executor.cores': '1',
        'spark.executor.instances': '2',
        'spark.dynamicAllocation.enabled': 'false',
        'spark.local.hostname': '10.178.0.20',
        'spark.driver.extraJavaOptions': '-Djava.net.preferIPv4Stack=true',
        'spark.hadoop.google.cloud.auth.service.account.enable': 'true',
        'spark.hadoop.google.cloud.auth.service.account.json.keyfile': '/opt/airflow/config/gcp-credentials.json',
        'spark.hadoop.fs.gs.impl': 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem',
        'spark.hadoop.fs.AbstractFileSystem.gs.impl': 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS'
    },
    verbose=True,
    dag=dag
)
