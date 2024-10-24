import logging

from airflow.decorators import task, dag
from airflow.utils.dates import days_ago

XCOM_KEY: str = 'test_xcom_key'
logger = logging.getLogger(__name__)

@dag(
    start_date=days_ago(1),
    schedule="@daily",
    catchup=False
)
def dag_decorator_example():
    
    @task
    def task_1(**context):
        test_data: dict = []
        
        for i in range(100):
            test_data.append({
                'key': f'test{i}',
                'value': i
            })
        
        context['task_instance'].xcom_push(key=XCOM_KEY, value=test_data)


    @task
    def task_2(**context):
        data = context['task_instance'].xcom_pull(key=XCOM_KEY, task_ids='task_1')
        
        total_value: int = 0
        for x in data:
            total_value += x['value']

        logger.info(f'total value is: {total_value}')
    
    task_1_instance = task_1()
    task_2_instance = task_2()

    task_1_instance >> task_2_instance

dag_decorator_example()
