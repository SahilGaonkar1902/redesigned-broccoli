import pickle
import streamlit as st
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests


CLIENT_ID = "5651387a4b7c4dc1bc80d4783a853b30"
CLIENT_SECRET = "2697f07c7b3b4ac8937b22fd6f89b3aa"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_lyrics(song_name, artist_name):
    base_url = f"https://api.lyrics.ovh/v1/{artist_name}/{song_name}"
    response = requests.get(base_url)

    if response.status_code == 200:
       return response.json().get("lyrics","lyrics not found.")
    else:
        return"lyrics not found."
   
st.header('Music Recommender System')

music = pickle.load(open('df.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

artist_list = music['singer'].unique()
selected_artist = st.selectbox("Select an artist",artist_list)

music_list = music['music_name'].values
selected_song = st.selectbox("select a song",music_list)

if st.button("show lyrics"):
    lyrics = get_lyrics("selected_song",selected_artist)
    st.text_area("lyrics",lyrics,height=300)


def get_artist_info(artist_name):
    results = sp.search(q=f"artist:{artist_name}",type="artist")
    if results["artists"]["items"]:
        artist = results["artists"]["items"][0]
        artist_image_url = artist["images"][0]["url"]if artist["images"] else "https://i.postimg.cc/0QNxYz4V/social.png"
        artist_popularity = artist["popularity"]
        genres = artist["genres"]
        return artist_image_url, artist_popularity, genres
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png",0,[]
    
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        print(album_cover_url)
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend(song):
    index = music[music['music_name'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        singer = music.iloc[i[0]].singer
        print(singer)
        print(music.iloc[i[0]].music_name)
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].music_name, singer))
        recommended_music_names.append(music.iloc[i[0]].music_name)

    return recommended_music_names,recommended_music_posters

st.header('Music Recommender System')

music = pickle.load(open('df.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

artist_list = music['singer'].unique()
selected_artist = st.selectbox(
    "Type or select an artist from the dropdown",
    artist_list
)

music_list = music['music_name'].values
selected_movie = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)
if st.button('show Artist Details'):
    artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
    st.image(artist_image_url, caption=selected_artist, width=300)
    st.write(f"**popularity**:{artist_popularity}")
    st.write(f"**Genres**:{', '.join(genres)}")


if st.button('Show Recommendation'):
    recommended_music_names,recommended_music_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5= st.columns(5)
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

