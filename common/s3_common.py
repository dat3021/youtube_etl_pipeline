import boto3 
import logging 

logger = logging.getLogger(__name__)

class s3_service:
    def __init__(self, default_bucket="project-test-zone"):
        self.s3_client = boto3.client('s3')
        self.default_bucket = default_bucket
        
    def upload_file(self, file_name, object_name, bucket_name=None):
        
        target_bucket = bucket_name if bucket_name else self.default_bucket

        try:
            self.s3_client.upload_file(file_name, target_bucket, object_name)
            logger.info(f"uploaded {file_name} to {target_bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Error uploading: {e}")
            return False
        
    def download_file(self, file_name, object_name, bucket_name=None):
            
        target_bucket = bucket_name if bucket_name else self.default_bucket

        try:
            self.s3_client.download_file(target_bucket, object_name, file_name)
            logger.info(f"downloaded {file_name} in {target_bucket}/{bucket_name} ")
            return True
        except Exception as e:
            logger.error(f"Error downloading {file_name} in {target_bucket}/{object_name}")
            return False