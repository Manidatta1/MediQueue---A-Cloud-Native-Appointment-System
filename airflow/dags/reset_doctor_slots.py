from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging

def reset_slots():
    url = "http://app-service:8000/doctor/slots/reset"
    try:
        response = requests.post(url)
        logging.info(f"Reset response: {response.status_code} | {response.text}")
    except Exception as e:
        logging.error(f"❌ Failed to reset doctor slots: {e}")

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_doctor_slot_reset',
    default_args=default_args,
    start_date=datetime(2025, 11, 1),
    schedule_interval='0 14 * * *',  # Every day at 2 PM
    catchup=False,
    tags=['healthcare', 'automation'],
) as dag:
    reset_task = PythonOperator(
        task_id='reset_doctor_slots',
        python_callable=reset_slots
    )
