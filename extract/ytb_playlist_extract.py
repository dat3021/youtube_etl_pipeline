from common.youtube_common import YtbService, YouTubeExtractor
from common.s3_common import s3_service
import json
import logging
import os 
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_playlist_data(local_file='temp.json'):
    try:
        logger.info(f"Extracting playlists...")
        
        service_wrapper = YtbService()
        extractor = YouTubeExtractor(service_wrapper.service)
        playlist = extractor.extract_playlists()

        extract_date = datetime.now().isoformat()
        if isinstance(playlist, list):
            for item in playlist:
                item['extract_date'] = extract_date

        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(playlist, f, default=str)

        return local_file
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")     
        raise e 

def upload_to_s3(data, bucket_name, object_name, local_file='temp.json'):
    try:
        logger.info(f"uploading to {bucket_name}/{object_name}")

        s3 = s3_service()
        success = s3.upload_file(local_file, object_name, bucket_name=bucket_name)

        if os.path.exists(local_file):
            os.remove(local_file)

    except Exception as e:
        logger.error(e)
        if os.path.exists(local_file):
            os.remove(local_file)
        return 

def run_extraction_playlist(bucket_name, **kwargs):
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%Y%m%d%H%M')

    object_name = f'raw/youtube/playlist/{date_str}/playlist_{time_str}.json'
    
    playlist_data = extract_playlist_data()

    upload_to_s3(playlist_data, bucket_name, object_name)

    return

if __name__ == "__main__":
    bucket = os.environ.get('S3_BUCKET_NAME', 'project-zone')
    run_extraction_playlist(bucket_name=bucket)
