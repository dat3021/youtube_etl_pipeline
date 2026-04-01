import os
import json
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class YtbService:
    def __init__(self, token_env_var='YOUTUBE_TOKEN'):
        self.token_env_var = token_env_var
        self.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        self.service = self._authenticate()

    def _authenticate(self):
        token_data = os.environ.get(self.token_env_var)
        if not token_data:
            raise ValueError(f"Environment variable {self.token_env_var} is missing. Run locally to generate it.")

        creds = Credentials.from_authorized_user_info(json.loads(token_data), self.scopes)

        # Silent Refresh: This works on ECS because it's a direct API call, no browser needed.
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Token refreshed silently using refresh_token.")
            except Exception as e:
                logger.error(f"Silent refresh failed: {e}")
                raise

        return build("youtube", "v3", credentials=creds)

class YouTubeExtractor:
    def __init__(self, service):
        self.service = service

    def extract_playlists(self):
        playlist, next_page_token = [], None
        while True: 
            request = self.service.playlists().list(
                part="snippet,contentDetails", 
                mine=True, 
                maxResults=50, 
                pageToken=next_page_token
            )
            response = request.execute()
            playlist.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        return playlist

    def extract_playlist_items(self, playlist_id):
        all_videos, next_page_token = [], None
        while True:
            request = self.service.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()
            all_videos.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        return all_videos
