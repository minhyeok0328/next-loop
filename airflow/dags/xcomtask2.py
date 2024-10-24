from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


# DAG 기본 설정

default_args = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2024, 1, 1),
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5),
}


# DAG 정의

dag = DAG(
    'xcom_push_pull_example',
    default_args=default_args,
    description='XCom push and pull example DAG',
    schedule_interval=timedelta(days=1),
)

def push_value(**context):
    """XCom에 값을 push하는 함수"""
    task_instane = context['task_instance']
    task_instane.xcom_push(key='pushedValue', value="값이 들어갔지")

def pull_value(**context):
    """XCom에서 값을 pull하는 함수"""
    res = context['task_instance'].xcom_pull(key='pushedValue')
    print(res)


# Task 정의

pushed_value = PythonOperator(
    task_id='pushed_value',
    python_callable=push_value,
    dag=dag,
)

pulled_value = PythonOperator(
    task_id='pulled_value',
    python_callable=pull_value,
    dag=dag,
)


# Task 의존성 설정

pushed_value >> pulled_value