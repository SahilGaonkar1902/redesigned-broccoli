import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius

# ---- Spotify API Credentials ----
CLIENT_ID = "51e2744868b945bcba0fe90d280df346"
CLIENT_SECRET = "1a97f11a318349dbb965ec95513c401b"

# ---- Genius API Credentials ----
GENIUS_ACCESS_TOKEN = "WlrCKwn50uP4B82mQCVYRSPFCpSTdFcH09-OogfgTUInrqUkyELzBKlF7G1NTTmf"

# Initialize APIs
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=5, retries=2)

# Load music data and similarity matrix
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---- Function to Get Lyrics ----
def get_lyrics(song_name):
    try:
        song = genius.search_song(song_name)
        return song.lyrics if song else "Lyrics not found."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"

# ---- Function to Search Song Versions ----
def search_song_versions(song_name):
    search_query = f"track:{song_name}"
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

# ---- Function to Get Artist Info ----
def get_artist_info(artist_name):
    results = sp.search(q=f"artist:{artist_name}", type="artist")
    
    if results and results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        artist_image_url = artist["images"][0]["url"] if artist["images"] else "https://i.postimg.cc/0QNxYz4V/social.png"
        artist_popularity = artist.get("popularity", 0)
        genres = artist.get("genres", [])
        return artist_image_url, artist_popularity, genres
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png", 0, []

# ---- Function to Get Song Album Cover ----
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        return track["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"

# ---- Function to Recommend Songs ----
def recommend(song):
    try:
        index = music[music['music_name'] == song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_music_names = []
        recommended_music_posters = []
        
        for i in distances[1:6]:  # Ensure at least 5 recommendations exist
            singer = music.iloc[i[0]].singer
            recommended_music_names.append(music.iloc[i[0]].music_name)
            recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].music_name, singer))

        return recommended_music_names, recommended_music_posters
    
    except Exception as e:
        return [], []  # Ensure two empty lists are returned if an error occurs


# ---- Streamlit UI ----
st.title("🎵 Music & Artist Explorer")

menu = st.sidebar.radio("📌 Menu", ["Home", "Search Artist", "Find Versions", "Get Lyrics", "Recommendations"])

# ---- Home Page ----
if menu == "Home":
    st.header("🎶 Welcome to the Music Explorer App!")
    st.write("Use the menu on the left to explore different features.")

# ---- Sidebar: Artist Information ----
st.header("🔎 Search Artist Info")
artist_list = music['singer'].unique()
selected_artist = st.sidebar.selectbox("Type or select an artist", artist_list)

if st.button("Show Artist Details"):
    artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
    st.sidebar.image(artist_image_url, caption=selected_artist, width=300)
    st.sidebar.write(f"**Popularity**: {artist_popularity}")
    st.sidebar.write(f"**Genres**: {', '.join(genres) if genres else 'N/A'}")

# ---- Main Section: Song Selection & Recommendation ----
st.header("🎧 Song Recommendations")

music_list = music['music_name'].values
selected_song = st.selectbox("🎶 Select a song", music_list)

if st.button("Show Recommendation"):
    st.session_state["recommendations"] = recommend(selected_song)

# Display recommendations
if "recommendations" in st.session_state:
    recommended_music_names, recommended_music_posters = st.session_state["recommendations"]

    if recommended_music_names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_music_names[i])
                st.image(recommended_music_posters[i])
    else:
        st.warning("No recommendations found for this song.")
else:
    st.info("Select a song and click 'Show Recommendation' to see suggestions.")

# ---- Song Version Finder ----
st.header("🔍 Find Different Versions of a Song")

if st.button("Find Versions"):
    song_versions = search_song_versions(selected_song)

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

# ---- Lyrics Section ----
st.header("📜 Get Lyrics")
if st.button("Show Lyrics"):
    lyrics = get_lyrics(selected_song)
    st.text_area("Lyrics", lyrics, height=300)
