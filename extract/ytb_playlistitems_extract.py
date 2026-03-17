from common.youtube_common import YtbService, YouTubeExtractor


def main():
    try:
        service_wrapper = YtbService("/mnt/c/code/playG/client_secret_904269737289-n1eihd068kfj6olcjsbsa48qgip2cnol.apps.googleusercontent.com.json")
        extractor = YouTubeExtractor(service_wrapper.service)
        ply_id = 'PLwDpRmGNbMSwbkbIOZxCFcy15b-UK8aJF'
        playlist = extractor.extract_playlist_items(ply_id)
        count = 0
        for item in playlist:
            count += 1
            video_id = item['contentDetails']['videoId']
            title = item['snippet']['title']
            channel_id = item['snippet']['channelId']
            playlist_id = item['snippet']['playlistId']
            print(f"num: {count} -channelId: {channel_id} -videoId: {video_id} title: {title},(PlaylistId: {playlist_id} )")

    except Exception as e:
        print(f"playlistitem extract error: {e}")


if __name__ == "__main__":
    main()