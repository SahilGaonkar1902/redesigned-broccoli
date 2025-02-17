import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import random

# ---- API Credentials ----
CLIENT_ID = "5651387a4b7c4dc1bc80d4783a853b30"
CLIENT_SECRET = "2697f07c7b3b4ac8937b22fd6f89b3aa"
GENIUS_ACCESS_TOKEN = "PUbu5fELoSxzz72odLJv_Bn32WehyzqAwRVAhLUwIfYuXUpRpzHsXicBD86DLCU4"

# ---- Initialize APIs ----
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=5, retries=2)

# Load music data and similarity matrix
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ---- Page Configuration ----
st.set_page_config(page_title="Music Explorer", page_icon="🎵", layout="wide")

# ---- Dynamic Background Colors ----
colors = ["#1DB954", "#FF5733", "#FFC300", "#C70039", "#900C3F"]
background_color = random.choice(colors)
st.markdown(
    f"""
    <style>
        .main {{ background-color: {background_color}; }}
        .title {{ color: white; text-align: center; font-size: 50px; font-weight: bold; }}
        .subtitle {{ color: white; text-align: center; font-size: 25px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Header Section ----
st.markdown("<div class='title'>🎵 Music Explorer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Discover, explore, and enjoy music like never before!</div>", unsafe_allow_html=True)

# ---- Feature Overview ----
st.write("### What You Can Do:")
st.write("✔ **Get Song Recommendations** - Find songs similar to your favorites.")
st.write("✔ **Search for Artists** - Explore artist details, popularity, and genres.")
st.write("✔ **Find Different Song Versions** - See multiple versions of a song.")
st.write("✔ **Fetch Song Lyrics** - Instantly get lyrics for any song.")

# ---- Feature Cards ----
col1, col2 = st.columns(2)

with col1:
    container = st.container(border = True)
    container.image("https://i.postimg.cc/tJvLxK7M/recommendations.jpg", use_column_width=True)
    container.write("#### 🎧 Song Recommendations")
    container.write("Discover songs similar to the ones you love based on an advanced similarity algorithm.")

    container1 = st.container(border = True)
    container1.image("https://i.postimg.cc/PxXcknLP/artist.jpg", use_column_width=True)
    container1.write("#### 🔍 Artist Search")
    container1.write("Find detailed information about your favorite artists, including genres and popularity.")

with col2:
    container2 = st.container(border = True)
    container2.image("https://i.postimg.cc/kGjL3Nyz/versions.jpg", use_column_width=True)
    container2.write("### Song version.")
    container2.write("Check out different versions of your favorite songs, from covers to remixes")

    container3 = st.container(border = True)
    container3.image("https://i.postimg.cc/y8V5XKNX/lyrics.jpg", use_column_width=True)
    container3.write("#### 📜 Get Lyrics")
    container3.write("Instantly fetch lyrics for any song and sing along!")


# ---- Functions ----
def get_lyrics(song_name):
    """Fetches lyrics for a given song."""
    try:
        song = genius.search_song(song_name)
        return song.lyrics if song else "Lyrics not found."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"


def search_song_versions(song_name):
    """Fetches different versions of a song."""
    search_query = f"track:{song_name}"
    result = sp.search(q=search_query, type="track", limit=5)
    
    song_versions = []
    if result and result["tracks"]["items"]:
        for track in result["tracks"]["items"]:
            song_versions.append({
                "name": track["name"],
                "album": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "image_url": track["album"]["images"][0]["url"] if track["album"]["images"] else "https://i.postimg.cc/0QNxYz4V/social.png"
            })
    return song_versions


def get_song_album_cover_url(song_name, artist_name):
    """Fetches album cover for a given song."""
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")
    
    if results and results["tracks"]["items"]:
        return results["tracks"]["items"][0]["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"


def recommend(song):
    """Recommends similar songs."""
    try:
        index = music[music['music_name'] == song].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_music_names = []
        recommended_music_posters = []
        
        for i in distances[1:6]:  # Top 5 recommendations
            singer = music.iloc[i[0]].singer
            recommended_music_names.append(music.iloc[i[0]].music_name)
            recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].music_name, singer))

        return recommended_music_names, recommended_music_posters
    except Exception:
        return [], []


def get_artist_info(artist_name):
    """Fetches artist details."""
    results = sp.search(q=f"artist:{artist_name}", type="artist")
    
    if results and results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        return (
            artist["images"][0]["url"] if artist["images"] else "https://i.postimg.cc/0QNxYz4V/social.png",
            artist.get("popularity", 0),
            artist.get("genres", [])
        )
    return "https://i.postimg.cc/0QNxYz4V/social.png", 0, []


# ---- Streamlit UI ----
menu = st.sidebar.radio("📌 Menu", ["Home", "Search Artist", "Find Versions", "Get Lyrics", "Recommendations"])

if menu == "Recommendations":
    st.header("Song Recommendations")
    music_list = music['music_name'].values
    selected_song = st.selectbox("🎶 Select a song", music_list)
    
    if st.button("Show Recommendation"):
        recommendations = recommend(selected_song)
        if recommendations[0]:
            cols = st.columns(5)
            for i, col in enumerate(cols):
                with col:
                    st.text(recommendations[0][i])
                    st.image(recommendations[1][i])
        else:
            st.warning("No recommendations found.")

elif menu == "Find Versions":
    st.header("Find Different Versions of a Song")
    music_list = music['music_name'].values
    selected_song = st.selectbox("🎶 Select a song", music_list)
    
    if st.button("Find Versions"):
        versions = search_song_versions(selected_song)
        if versions:
            version_options = [f"{v['name']} - {v['album']} ({v['release_date']})" for v in versions]
            selected_version = st.selectbox("Select a version:", version_options)
            details = next(v for v in versions if f"{v['name']} - {v['album']} ({v['release_date']})" == selected_version)
            st.image(details["image_url"], caption=selected_version, width=300)
            st.text_area("Lyrics", get_lyrics(details["name"]), height=300)
        else:
            st.write("No versions found.")

elif menu == "Get Lyrics":
    st.header("Get Lyrics")
    music_list = music['music_name'].values
    selected_song = st.selectbox("🎶 Select a song", music_list)
    
    if st.button("Show Lyrics"):
        st.text_area("Lyrics", get_lyrics(selected_song), height=300)

elif menu == "Search Artist":
    st.header("🔎 Search Artist Info")
    artist_list = music['singer'].unique()
    selected_artist = st.selectbox("Type or select an artist", artist_list)
    
    if st.button("Show Artist Details"):
        artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
        st.image(artist_image_url, caption=selected_artist, width=300)
        st.write(f"**Popularity**: {artist_popularity}")
        st.write(f"**Genres**: {', '.join(genres) if genres else 'N/A'}")
