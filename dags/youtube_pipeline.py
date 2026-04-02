from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os 

# Ensure project root is in sys.path for local imports
project_home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from extract.ytb_playlist_extract import run_extraction_playlist
from extract.ytb_playlistitems_extract import run_extraction_playlist_item
from transform.transform_playlist import transform_playlist_to_iceberg
from transform.transform_playlist_items import transform_playlist_items_to_iceberg

default_args = {
    'owner': 'datpham',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1), 
    'email_on_failure': False,
    'retries': 1,                      
    'retry_delay': timedelta(minutes=5), 
}

S3_BUCKET = 'project-zone'

with DAG(
    'youtube_pipeline',
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
    tags=['youtube','s3','aws']
) as dag:

    extract_playlists = PythonOperator(
        task_id='extract_playlist',
        python_callable=run_extraction_playlist,
        op_kwargs={'bucket_name': S3_BUCKET}
    )

    extract_playlist_items = PythonOperator(
        task_id="extract_playlist_items",
        python_callable=run_extraction_playlist_item,
        op_kwargs={'bucket_name': S3_BUCKET}
    )

    transform_playlists = PythonOperator(
        task_id='transform_playlists',
        python_callable=transform_playlist_to_iceberg,
        op_kwargs={
            'bucket_name': S3_BUCKET
        }
    )

    transform_playlist_items = PythonOperator(
        task_id='transform_playlist_items',
        python_callable=transform_playlist_items_to_iceberg,
        op_kwargs={
            'bucket_name': S3_BUCKET
        }
    )

    extract_playlists >> extract_playlist_items
    extract_playlist_items >> [transform_playlists, transform_playlist_items]
