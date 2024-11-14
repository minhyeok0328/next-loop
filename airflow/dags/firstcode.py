import datetime

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@daily")
def generate_dag():
    @task()
    def xcom1_dag1(**context):
        print("hello world")
        context['task_instance'].xcom_push(key="testkey", value="1234")
        EmptyOperator(task_id="task")

    @task()
    def xcom1_dag2(**context):
        print("hello world")
        context['task_instance'].xcom_pull(task_ids='generate_dag', key="testkey")
        EmptyOperator(task_id="task22")

generate_dag()