from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# DAG의 기본 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 28),
    'email': ['your-email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
dag = DAG(
    'example_dag',
    default_args=default_args,
    description='첫 번째 DAG 예제',
    schedule_interval=timedelta(days=1),
)

# 작업 1: 날짜 출력
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

# 작업 2: Python 함수 실행
def print_hello():
    print('Hello from Airflow!')

t2 = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# 작업 순서 설정
t1 >> t2
