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
    name='arrow-spark',
    verbose=True,
    conf={
        # Resource Configuration
        'spark.driver.memory': '1g',
        'spark.executor.memory': '1g',
        'spark.executor.cores': '2',
        'spark.task.cpus': '1',
        'spark.executor.instances': '2',
        'spark.dynamicAllocation.enabled': 'true',
        'spark.dynamicAllocation.minExecutors': '1',
        'spark.dynamicAllocation.maxExecutors': '2',
        'spark.shuffle.service.enabled': 'true',
        
        # Network Configuration
        'spark.master': 'spark://spark-master:7077',
        'spark.driver.host': '10.0.1.3',
        'spark.driver.bindAddress': '0.0.0.0',
        'spark.driver.port': '4041',
        
        # Timeout Settings
        'spark.network.timeout': '1200s',
        'spark.rpc.askTimeout': '180s',
        'spark.rpc.lookupTimeout': '180s',
        'spark.executor.heartbeatInterval': '30s',
        
        # Python Worker Settings
        'spark.python.worker.reuse': 'true',
        'spark.python.worker.memory': '512m',
        'spark.driver.maxResultSize': '512m',
        
        # Memory Management
        'spark.memory.fraction': '0.6',
        'spark.memory.storageFraction': '0.5',
        
        # GC Options
        'spark.executor.extraJavaOptions': '-XX:+UseG1GC -XX:+PrintGCDetails -XX:+PrintGCTimeStamps',
        
        # Python Configuration
        'spark.pyspark.driver.python': '/usr/local/bin/python3',
        'spark.pyspark.python': '/usr/local/bin/python3',
        'spark.executorEnv.PYSPARK_PYTHON': '/usr/local/bin/python3',
        'spark.executor.extraClassPath': '/usr/local/lib/python3.x/site-packages',
        
        # Scheduler Settings
        'spark.scheduler.mode': 'FAIR',
        'spark.scheduler.allocation.mode': 'FAIR',
        'spark.locality.wait': '3s',
        
        # GCP Configuration
        'spark.hadoop.google.cloud.auth.service.account.enable': 'true',
        'spark.hadoop.google.cloud.auth.service.account.json.keyfile': '/opt/airflow/config/gcp-credentials.json',
        
        # Deploy Configuration
        'spark.submit.deployMode': 'client'
    },
    dag=dag
)
