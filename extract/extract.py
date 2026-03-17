from common.youtube_common import YtbService, YouTubeExtractor
from common.s3_common import S3Manager
import json
import os

def get_playlist_data(client_secret_path):
    """Fetches playlist data from YouTube API."""
    try:
        service_wrapper = YtbService(client_secret_path)
        extractor = YouTubeExtractor(service_wrapper.service)
        print("Extracting playlists from YouTube...")
        return extractor.extract_playlists()
    except Exception as e:
        print(f"Failed to fetch YouTube data: {e}")
        raise e

def upload_to_s3(data, bucket_name, object_name, local_file='temp_playlists.json'):
    """Saves data to a temporary file and uploads it to S3."""
    try:
        # Save locally
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # Upload
        s3_mgr = S3Manager(default_bucket_name=bucket_name)
        success = s3_mgr.upload_file(local_file, object_name)
        
        # Cleanup
        if os.path.exists(local_file):
            os.remove(local_file)
            
        if not success:
            raise Exception("S3Manager failed to upload file.")
            
        print(f"Successfully uploaded data to s3://{bucket_name}/{object_name}")
        return True
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        if os.path.exists(local_file):
            os.remove(local_file)
        raise e

def run_extraction(bucket_name, client_secret_path="./client_secret.json"):
    """Orchestrator function for Airflow or local execution."""
    object_name = 'youtube/raw/playlists.json'
    
    # Task 1: Get Data
    playlists = get_playlist_data(client_secret_path)
    print(f"Found {len(playlists)} playlists.")
    
    # Task 2: Upload Data
    upload_to_s3(playlists, bucket_name, object_name)

def main():
    # Local Test settings
    MY_BUCKET = 'your-bucket-name' 
    MY_SECRET = "./client_secret.json"
    
    run_extraction(bucket_name=MY_BUCKET, client_secret_path=MY_SECRET)

if __name__ == "__main__":
    main()