import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class YtbService:
    def __init__(self, client_secrets_file, token_env_var='YOUTUBE_TOKEN'):
        self.client_secrets_file = client_secrets_file
        self.token_env_var = token_env_var
        self.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        token_data = os.environ.get(self.token_env_var)
        
        if token_data:
            try:
                creds_info = json.loads(token_data)
                creds = Credentials.from_authorized_user_info(creds_info, self.scopes)
            except Exception as e:
                logger.error(f"Error loading credentials from environment variable: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info(f"Credentials refreshed. Please update {self.token_env_var} with: {creds.to_json()}")
                except Exception:
                    creds = self._get_new_cred()
                    logger.info(f"New credentials obtained. Please set {self.token_env_var} to: {creds.to_json()}")
            else:
                creds = self._get_new_cred()
                logger.info(f"New credentials obtained. Please set {self.token_env_var} to: {creds.to_json()}")

        return build("youtube", "v3", credentials=creds)
    
    def _get_new_cred(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes)
        return flow.run_local_server(port=0, open_browser=False, access_type='offline', prompt='consent')

class YouTubeExtractor:
    def __init__(self, service):
        self.service = service

    def extract_playlists(self):
        
        all_playlist = []
        next_pagetoken = None
        
        while True: 
            request = self.service.playlists().list(part="snippet,contentDetails", 
                                                    mine=True, 
                                                    maxResults=10, 
                                                    pageToken=next_pagetoken)
            respone = request.execute()
            items = respone.get('items', [])
            all_playlist.extend(items)

            next_pagetoken = respone.get('nextPageToken')
            if not next_pagetoken:
                break
        return all_playlist

    def extract_playlist_items(self, playlist_id):
        all_videos = []
        next_page_token = None
        while True:
            request = self.service.playlistItems().list(part="snippet,contentDetails",
                                                        playlistId=playlist_id,
                                                        maxResults=40,
                                                        pageToken=next_page_token)
            respone = request.execute()
            items = respone.get('items', [])
            all_videos.extend(items)
            next_page_token = respone.get('nextPageToken')

            if not next_page_token:
                break

        return all_videos

    def extract_subscriptions(self):
        request = self.service.subscriptions().list(part="snippet", mine=True)
        return request.execute()

    def extract_video_details(self, video_id):
        request = self.service.videos().list(part="snippet,statistics", id=video_id)
        return request.execute()