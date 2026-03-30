import os
import logging
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError

logger = logging.getLogger(__name__)

def get_glue_catalog(s3_path: str, region: str = None):
    region = region or os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'ap-southeast-2'
    os.environ['AWS_DEFAULT_REGION'] = region

    return load_catalog(
        "default",
        **{
            "type": "glue",
            "s3.region": region,
            "s3_path": s3_path
        }
    )

def write_to_iceberg(arrow_table, namespace: str, table_name: str, s3_path: str):

    catalog = get_glue_catalog(s3_path)
    identifier = f"{namespace}.{table_name}"
    
    try:
        catalog.create_namespace(namespace)
        logger.info(f"Created namespace: {namespace}")
    except Exception:
        # Namespace already exists
        pass

    # Append or Create Table
    try:
        table = catalog.load_table(identifier)
        logger.info(f"Table {identifier} found. Appending {arrow_table.num_rows} rows...")
        table.append(arrow_table)
    except NoSuchTableError:
        location = f"{s3_path}{namespace}/{table_name}"
        logger.info(f"Table {identifier} not found. Creating Iceberg table at {location}...")
        table = catalog.create_table(
            identifier,
            schema=arrow_table.schema,
            location=location
        )
        table.append(arrow_table)

    logger.info(f"Successfully committed changes to Iceberg table: {identifier}")
    return table