import duckdb
import os
import logging
import yaml
from common.pyiceberg_common import write_to_iceberg
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def transform_playlist_items_to_iceberg(bucket_name, **kwargs):

    config = load_config()
    
    # Load parameters from YAML
    p_config = config['youtube_playlist_items']
    run_date = datetime.now().strftime('%Y%m%d')

    source_path = p_config['source_path'].format(date_str=run_date)
    source_s3_path = f"s3://{bucket_name}/{source_path}"
    s3_path = f"s3://{bucket_name}/{p_config['object_path']}"
    namespace = p_config['target_namespace']
    table_name = p_config['target_table']

    # Initialize DuckDB and AWS
    region = os.environ.get('MY_AWS_REGION', 'ap-southeast-2')
    setup_query = p_config['duckdb_setup'].format(region=region) 
    con = duckdb.connect()
    con.execute(setup_query)

    query = p_config['sql_transform'].format(source_s3_path=source_s3_path)
    logger.info(f"Scanning source path: {source_s3_path}")
    arrow_table = con.execute(query).arrow().read_all()

    # Write to Iceberg using common library
    if arrow_table.num_rows > 0:
        write_to_iceberg(
            arrow_table=arrow_table,
            namespace=namespace,
            table_name=table_name,
            s3_path=s3_path
        )
    else:
        logger.warning("No data found to process.")

if __name__ == "__main__":
    bucket = os.environ.get('S3_BUCKET_NAME', 'project-zone')
    transform_playlist_items_to_iceberg(bucket)
