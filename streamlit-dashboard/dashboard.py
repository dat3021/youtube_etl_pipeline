import streamlit as st
import duckdb
import pandas as pd
import os

# Cấu hình trang Dashboard
st.set_page_config(page_title="YouTube Iceberg Dashboard", layout="wide")

@st.cache_data
def get_data():
    con = duckdb.connect()
    # Bước 1: Setup môi trường
    con.execute("""
        INSTALL httpfs; LOAD httpfs;
        INSTALL aws; LOAD aws;
        INSTALL iceberg; LOAD iceberg;
        CALL load_aws_credentials();
        SET s3_region='ap-southeast-2';
    """)
    
    metadata_query = "SELECT max(file) FROM glob('s3://project-zone/stg/youtube_analytics/playlists_iceberg/metadata/*.metadata.json')"
    metadata_query_items = "SELECT max(file) FROM glob('s3://project-zone/stg/youtube_analytics/playlist_items_iceberg/metadata/*.metadata.json')"
    latest_metadata_pl = con.execute(metadata_query).fetchone()[0]
    latest_metadata_items = con.execute(metadata_query_items).fetchone()[0]

    query_playlist = f""" SELECT * FROM iceberg_scan('{latest_metadata_pl}');"""
    query_items = f""" SELECT * FROM iceberg_scan('{latest_metadata_items}');"""

    df_playlists = con.execute(query_playlist).df()
    df_items = con.execute(query_items).df()
    return df_playlists, df_items

# Thực thi lấy data
try:
    with st.spinner("Fetching data from S3 Iceberg..."):
        df_playlists, df_items = get_data()

    # Sidebar Navigation
    st.sidebar.title("Analytics Menu")
    page = st.sidebar.radio("Navigation", ["Main Page", "Raw Data"])

    if page == "Main Page":
        st.title("YouTube Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Playlists", f"{len(df_playlists):,}")
        with col2:
            st.metric("Total Videos", f"{len(df_items):,}")
            
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Number of video each Playlist")
            chart_data = df_items.merge(df_playlists, on='playlist_id', how='right')
            v_counts = chart_data['playlist_title'].value_counts()
            v_counts_sorted = v_counts.sort_values( ascending=True)
            st.bar_chart(v_counts, horizontal=True, color="#3853DB", sort='-count', width=700, height=450)
        with col2:
            st.subheader("Search and Explore Playlists")

            playlist_options = df_playlists['playlist_title'].unique().tolist()
            selected_playlist = st.selectbox("Choose a playlist:", options=playlist_options)

            target_id = df_playlists[df_playlists['playlist_title'] == selected_playlist]['playlist_id'].values[0]

            filtered_items = df_items[df_items['playlist_id'] == target_id]

            c1, c2 = st.columns(2)
            c1.metric("Videos", len(filtered_items))
            c2.metric("Extract Date", str(filtered_items['extract_date'].max()))

            display_cols = ['video_title', 'video_id', 'position']
            st.dataframe(
                filtered_items[display_cols].sort_values('position'), 
                use_container_width=True,
                hide_index=True
            )

    elif page == "Raw Data":
        st.title("📁 Iceberg Raw Data")
        
        st.subheader("Playlists (youtube_analytics.playlists_iceberg)")
        st.dataframe(df_playlists, use_container_width=True)
        
        st.subheader("Playlist Items (youtube_analytics.playlist_items_iceberg)")
        st.dataframe(df_items, use_container_width=True)

    
        p1, p2 = st.columns(2)
        with p1:
            st.write("### Playlist data columns:")
            st.write(df_playlists.columns.tolist())
        with p2:
            st.write("### Playlist Items columns:")
            st.write(df_items.columns.tolist())

except Exception as e:
    st.error(f"❌ Lỗi: {e}")