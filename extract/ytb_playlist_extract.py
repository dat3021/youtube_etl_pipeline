from common.youtube_common import YtbService, YouTubeExtractor
import json

def main():
    try:
        service_wrapper = YtbService("./client_secret.json")
        extractor = YouTubeExtractor(service_wrapper.service)
        playlists = extractor.extract_playlists()
     
        count = 0
        for pl in playlists:
            count += 1
            pl_id = pl['id']
            title = pl['snippet']['title']
            channel_id = pl['snippet']['channelId']
            amount = pl['contentDetails']['itemCount']
            print(f"num: {count} -channelId: {channel_id} title: {title},(PlaylistId: {pl_id} )") #amount: {amount} (PlaylistId: {pl_id}
        
        # json_output = json.dumps(playlists, indent=4)
        # print(f"\n ------- {json_output}")
        print(f"\nFound: {len(playlists)} playlists")
    except Exception as e:
        print(f"error when execute: {e}")

if __name__ == "__main__":
    main()