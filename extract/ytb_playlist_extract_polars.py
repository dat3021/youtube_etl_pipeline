
from youtube_common import YtbService, YouTubeExtractor
import polars as pl
import os

def main():
    try:        
        service_wrapper = YtbService("./client_secret_904269737289-n1eihd068kfj6olcjsbsa48qgip2cnol.apps.googleusercontent.com.json")
        extractor = YouTubeExtractor(service_wrapper.service)
        
        print("Fetching playlists data...")
        playlists = extractor.extract_playlists()
        
        if not playlists:
            print("No playlists found.")
            return

        # Load raw list into Polars and use struct fields to extract nested data
        df = pl.DataFrame(playlists).select([
            pl.col("id").alias("playlist_id"),
            pl.col("snippet").struct.field("title"),
            pl.col("snippet").struct.field("channelId").alias("channel_id"),
            pl.col("contentDetails").struct.field("itemCount").alias("item_count"),
            pl.col("snippet").struct.field("publishedAt").alias("published_at")
        ])
        
        # Display the DataFrame
        print("\n--- Playlists (Polars DataFrame) ---")
        print(df)
        
        # Optional: Save to parquet for backup
        # output_path = os.path.join(os.path.dirname(__file__), "playlists.parquet")
        # df.write_parquet(output_path)
        # print(f"\nSaved to {output_path}")

    except Exception as e:
        print(f"Error in Polars extraction: {e}")

if __name__ == "__main__":
    main()
