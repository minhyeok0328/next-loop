# PythonOperator return 값을 이용한 Xcom

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# DAG의 기본 인자 설정

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
    'xcom_example_dag',
    default_args=default_args,
    description='Example DAG for XCom usage',
    schedule_interval=timedelta(days=1),
)

def pythonOperator_return_xcom():
    return "python은 return 값이 xcom으로 바로 반환됨"

def get_pythonOperator_xcom(**context):
    ti = context['task_instance']
    res = ti.xcom_pull(task_ids='pythonOperator_return_xcom')
    print(res)

# Task 정의

task1 = PythonOperator(
    task_id='pythonOperator_return_xcom',
    python_callable=pythonOperator_return_xcom,
    dag=dag,
)

task2 = PythonOperator(
    task_id='get_pythonOperator_xcom',
    python_callable=get_pythonOperator_xcom,
    dag=dag,
)

# Task 순서 설정

task1 >> task2