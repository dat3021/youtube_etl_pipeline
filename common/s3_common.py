import boto3
import logging 

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self, default_bucket_name="project-test-zone"):
        """
        Initialize the S3 client.
        :param default_bucket_name: Optional default bucket to use.
        """
        self.s3_client = boto3.client('s3')
        self.default_bucket_name = default_bucket_name

    def upload_file(self, file_name, object_name, bucket_name=None):
        """
        Uploads a file to S3.
        """
        target_bucket = bucket_name if bucket_name else self.default_bucket_name
        
        if not target_bucket:
            logger.error("No bucket name provided for upload.")
            return False

        try:
            self.s3_client.upload_file(file_name, target_bucket, object_name)
            logger.info(f"Successfully uploaded {file_name} to {target_bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Error uploading {file_name} to {target_bucket}/{object_name}: {e}")
            return False

    def download_file(self, object_name, file_name, bucket_name=None):
        """
        Downloads a file from S3.
        :param object_name: The S3 key of the object to download.
        :param file_name: The local file path where the object should be saved.
        :param bucket_name: Optional override for the target bucket.
        :return: True if successful, False otherwise.
        """
        target_bucket = bucket_name if bucket_name else self.default_bucket_name
        
        if not target_bucket:
            logger.error("No bucket name provided for download.")
            return False

        try:
            self.s3_client.download_file(target_bucket, object_name, file_name)
            logger.info(f"Successfully downloaded {target_bucket}/{object_name} to {file_name}")
            return True
        except Exception as e:
            logger.error(f"Error downloading {target_bucket}/{object_name} to {file_name}: {e}")
            return False