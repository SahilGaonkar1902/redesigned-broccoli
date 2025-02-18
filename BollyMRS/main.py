import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

# ---- Spotify API Credentials ----
CLIENT_ID = "5651387a4b7c4dc1bc80d4783a853b30"
CLIENT_SECRET = "2697f07c7b3b4ac8937b22fd6f89b3aa"

# ---- Genius API Credentials ----
GENIUS_ACCESS_TOKEN = "PUbu5fELoSxzz72odLJv_Bn32WehyzqAwRVAhLUwIfYuXUpRpzHsXicBD86DLCU4"

# Initialize APIs
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=5, retries=2)

# Function to fetch lyrics
def get_lyrics(song_name):
    try:
        song = genius.search_song(song_name)
        return song.lyrics if song else "Lyrics not found."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"

# Function to search for different versions of a song
def search_song_versions(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    result = sp.search(q=search_query, type="track", limit=5)

    song_versions = []
    if result and result["tracks"]["items"]:
        for track in result["tracks"]["items"]:
            track_name = track["name"]
            album_name = track["album"]["name"]
            release_date = track["album"]["release_date"]
            image_url = track["album"]["images"][0]["url"] if track["album"]["images"] else "https://i.postimg.cc/0QNxYz4V/social.png"
            
            song_versions.append({
                "name": track_name,
                "album": album_name,
                "release_date": release_date,
                "image_url": image_url
            })
    return song_versions

# Streamlit UI Elements
st.header("Music Recommender System")

# Load data
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Select song and artist
music_list = music['music_name'].values
artist_list = music['singer'].unique()

selected_song = st.selectbox("Select a song", music_list)
selected_artist = st.selectbox("Select an artist", artist_list)

# Button to find different versions of a song
if st.button("Find Versions"):
    song_versions = search_song_versions(selected_song, selected_artist)

    if song_versions:
        version_options = [f"{v['name']} - {v['album']} ({v['release_date']})" for v in song_versions]
        selected_version = st.selectbox("Select the correct version:", version_options)
        
        selected_song_details = next(v for v in song_versions if f"{v['name']} - {v['album']} ({v['release_date']})" == selected_version)

        st.image(selected_song_details["image_url"], caption=selected_version, width=300)
        
        # Fetch lyrics
        lyrics = get_lyrics(selected_song_details["name"])
        st.text_area("Lyrics", lyrics, height=300)
    else:
        st.write("No versions found.")

# Function to fetch artist details
def get_artist_info(artist_name):
    results = sp.search(q=f"artist:{artist_name}", type="artist")
    if results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        artist_image_url = artist["images"][0]["url"] if artist["images"] else "https://i.postimg.cc/0QNxYz4V/social.png"
        artist_popularity = artist["popularity"]
        genres = artist["genres"]
        return artist_image_url, artist_popularity, genres
    return "https://i.postimg.cc/0QNxYz4V/social.png", 0, []

# Show artist details
if st.button("Show Artist Details"):
    artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
    st.image(artist_image_url, caption=selected_artist, width=300)
    st.write(f"**Popularity:** {artist_popularity}")
    st.write(f"**Genres:** {', '.join(genres)}")

# Function to get song album cover
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        return track["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"

# Function to recommend similar songs
def recommend(song):
    index = music[music['music_name'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:  # Get top 5 recommendations
        singer = music.iloc[i[0]].singer
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].music_name, singer))
        recommended_music_names.append(music.iloc[i[0]].music_name)

    return recommended_music_names, recommended_music_posters

# Show song recommendations
if st.button("Show Recommendation"):
    recommended_music_names, recommended_music_posters = recommend(selected_song)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(recommended_music_names[0])
        st.image(recommended_music_posters[0])
    with col2:
        st.text(recommended_music_names[1])
        st.image(recommended_music_posters[1])
    with col3:
        st.text(recommended_music_names[2])
        st.image(recommended_music_posters[2])
    with col4:
        st.text(recommended_music_names[3])
        st.image(recommended_music_posters[3])
    with col5:
        st.text(recommended_music_names[4])
        st.image(recommended_music_posters[4])
