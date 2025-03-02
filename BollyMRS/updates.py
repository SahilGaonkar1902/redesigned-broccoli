import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import time
import login

# ---- Spotify API Credentials ----
CLIENT_ID = "51e2744868b945bcba0fe90d280df346"
CLIENT_SECRET = "1a97f11a318349dbb965ec95513c401b"

# ---- Genius API Credentials ----
GENIUS_ACCESS_TOKEN = "WlrCKwn50uP4B82mQCVYRSPFCpSTdFcH09-OogfgTUInrqUkyELzBKlF7G1NTTmf"

# ---- Initialize APIs ----
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=5, retries=2)

# Load music data and similarity matrix
music = pickle.load(open('df.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

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
logo = "img/Music.png"
st.logo(logo, size="small")

st.subheader("Songs Recommendation System",divider="gray")
st.text("")
st.text("")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["| Home |", "| Recommendations |", "| Lyrics |", "| Song Info |", "| Artist Info |", "| Login Page |"])

with tab1:
    con0 = st.container(border=True)
    con0.header("Welcome to the Music Explorer App!", divider="rainbow")
    con0.write("Explore tabs for different features.")
    
    # ---- Feature Overview ----
    con0.write("### What You Can Do:")
    con0.write("✔ **Get Song Recommendations** - Find songs similar to your favorites.")
    con0.write("✔ **Search for Artists** - Explore artist details, popularity, and genres.")
    con0.write("✔ **Find Different Song Versions** - See multiple versions of a song.")
    con0.write("✔ **Fetch Song Lyrics** - Instantly get lyrics for any song.")

    # ---- Feature Cards ----
    col1, col2 = con0.columns(2)

    with col1:
        container = st.container(border = True)
        container.write("#### 🎧 Song Recommendations")
        container.write("Discover songs similar to the ones you love based on an advanced similarity algorithm.")

        container1 = st.container(border = True)
        container1.write("#### 🔍 Artist Search")
        container1.write("Find detailed information about your favorite artists, including genres and popularity.")

    with col2:
        container2 = st.container(border = True)
        container2.write("### Song version.")
        container2.write("Check out different versions of your favorite songs, from covers to remixes")

        container3 = st.container(border = True)
        container3.write("#### 📜 Get Lyrics")
        container3.write("Instantly fetch lyrics for any song and sing along!")


with tab2:
    con1 = st.container(border=True)
    con1.header("Recommend",divider="violet")
    music_list1 = music['music_name'].values
    selected_song = con1.selectbox("🎶 Select a song", music_list1)
        
    if con1.button("Show Recommendation"):
            con1.divider()
            recommendations = recommend(selected_song)
            if recommendations[0]:
                with st.spinner("Loading..."):
                    time.sleep(5)
                cols = con1.columns(5)
                for i, col in enumerate(cols):
                    with col:
                        con1.text(recommendations[0][i])
                        con1.image(recommendations[1][i])
            else:
                con1.warning("No recommendations found.")

with tab4:
    con2 = st.container(border=True)
    con2.header("Song Info",divider="orange")
    music_list3 = music['music_name'].values
    selected_song = con2.selectbox("🎵Select A Song", music_list3)
        
    if con2.button("Search"):
            con2.divider()
            versions = search_song_versions(selected_song)
            if versions:
                with st.spinner("Loading..."):
                    time.sleep(5)
                version_options = [f"{v['name']} - {v['album']} ({v['release_date']})" for v in versions]
                selected_version = con2.selectbox("Select a version:", version_options)
                details = next(v for v in versions if f"{v['name']} - {v['album']} ({v['release_date']})" == selected_version)
                con2.image(details["image_url"], caption=selected_version, width=300)
                con2.text_area("Lyrics", get_lyrics(details["name"]), height=300)
            else:
                con2.write("No versions found.")

with tab3:
    con3 = st.container(border=True)
    con3.header("Lyrics", divider="blue")
    music_list2 = music['music_name'].values
    selected_song = con3.selectbox("🎼Enter A Song", music_list2)
    if con3.button("Show Lyrics"):
            con3.divider()
            with st.spinner("Loading..."):
                    time.sleep(5)
            con3.text_area("Lyrics:", get_lyrics(selected_song), height=500)

with tab5:
    con4 = st.container(border=True)
    con4.header("Artist Info",divider="green")
    artist_list = music['singer'].unique()
    selected_artist = con4.selectbox("👤Select An Artist", artist_list)
        
    if con4.button("Show Artist Details"):
            con4.divider()
            artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
            with st.spinner("Loading..."):
                    time.sleep(5)
            con4.image(artist_image_url, caption=selected_artist, width=300)
            con4.write(f"*Popularity*: {artist_popularity}")
            con4.write(f"*Genres*: {', '.join(genres) if genres else 'N/A'}")
            
with tab6:
    login.log()
