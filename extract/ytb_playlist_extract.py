from common.youtube_common import YtbService, YouTubeExtractor
from common.s3_common import s3_service
import json
import logging
import os 
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_playlist_data(client_secret_path, local_file='temp.json'):
    try:
        logger.info(f"Extracting playlists...")
        
        service_wrapper = YtbService(client_secret_path)
        extractor = YouTubeExtractor(service_wrapper.service)
        playlist = extractor.extract_playlists()

        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(playlist, f, indent=4)

        return local_file
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")      

def upload_to_s3(data, bucket_name, object_name, local_file='temp.json'):
    try:
        logger.info(f"uploading {local_file} to {bucket_name}/{object_name}")

        s3 = s3_service()
        success = s3.upload_file(local_file, object_name, bucket_name=bucket_name)

        if os.path.exists(local_file):
            os.remove(local_file)

        if not success:
            logger.error(f"Failed upload {local_file} to {bucket_name}/{object_name}")

        return True
    
    except Exception as e:
        logger.error(e)
        if os.path.exists(local_file):
            os.remove(local_file)
        return 
    
def run_extraction(bucket_name, client_secret_path="./client_secret.json"):
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')

    object_name = f'raw/youtube/{date_str}/playlist_{time_str}.json'
    
    playlist_data = extract_playlist_data(client_secret_path)
    logger.info(f"Found {len(playlist_data)} playlist")

    upload_to_s3(playlist_data, bucket_name, object_name)

    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # file = extract_playlist_data(client_secret_path='./client_secret.json')
    # print(f'{file}')
    run_extraction(bucket_name="project-zone")
