from common.youtube_common import YtbService, YouTubeExtractor
from common.s3_common import s3_service
import json
import logging
import os 
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_playlist_ids(bucket, prefix) -> list:
    try:
        s3 = s3_service()    
        resp = s3.list_object(bucket_name=bucket, prefix=prefix)

        files = []
        for obj in resp['Contents']:
            if not obj['Key'].endswith('/'):
                files.append(obj)

        latest = max(files, key=lambda x: x['LastModified'])['Key']
        file_name = os.path.basename(latest)
        s3.download_file(file_name=file_name, object_name=latest, bucket_name=bucket)

        with open(file_name, 'r') as f:
            data = json.load(f)

        playlist_ids = []
        for item in data:
            playlist_ids.append(item['id'])

        return playlist_ids
    except Exception as e:
        logger.error(f"error getting playlist ids: {e}")
        return []
    finally:
        if 'file_name' in locals() and file_name and os.path.exists(file_name):
            os.remove(file_name)

def run_extraction_playlist_item(bucket_name, local_file='temp.json', **kwargs):
    try:
        extractor = YouTubeExtractor(YtbService().service)
        s3 = s3_service()
        date_str = datetime.now().strftime('%Y%m%d')

        playlist_ids = get_playlist_ids("project-zone", f"raw/youtube/playlist/{date_str}")

        for i, pid in enumerate(playlist_ids, 1):
            object_name = f'raw/youtube/playlist_items/{date_str}/playlist_{pid}.json'

            items_data = extractor.extract_playlist_items(playlist_id=pid)

            if isinstance(items_data, list):
                for item in items_data:
                    item['extract_date'] = date_str

            with open(local_file, 'w') as f:
                json.dump(items_data, f, default=str)

            logger.info(f"uploading file {i}/{len(playlist_ids)}")
            s3.upload_file(local_file, object_name, bucket_name=bucket_name)

        logger.info("--Uploading completed--")
        if os.path.exists(local_file):
                os.remove(local_file)
    except Exception as e:
        logger.error(f"error: {e}")

if __name__ == "__main__":    
    bucket = os.environ.get('S3_BUCKET_NAME', 'project-zone')
    run_extraction_playlist_item(bucket_name=bucket)