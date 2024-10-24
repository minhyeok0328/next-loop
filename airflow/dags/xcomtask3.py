from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


# DAG 기본 설정

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# DAG 정의

dag = DAG(
    'jinja_xcom_example',
    default_args=default_args,
    description='Example DAG for Jinja template with XCom',
    schedule_interval=timedelta(days=1),
)

def pull_value_from_jinja(**context):
    """XCom에서 jinja key로 저장된 값을 가져오는 함수"""
    res = context['task_instance'].xcom_pull(key='jinja')
    print(res)


# Jinja 템플릿을 사용하는 BashOperator

jinja_template = BashOperator(
    task_id='jinja_template',
    bash_command='echo {{ task_instance.xcom_push(key="jinja", value="airflow") }}',
    dag=dag,
)


# XCom 값을 가져오는 PythonOperator

pulled_value_jinja = PythonOperator(
    task_id='pulled_value_jinja',  # task_id 중복을 피하기 위해 변경
    python_callable=pull_value_from_jinja,
    dag=dag,
)


# Task 의존성 설정

jinja_template >> pulled_value_jinja