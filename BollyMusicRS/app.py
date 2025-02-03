import pickle
import streamlit as st
import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

CLIENT_ID = "51e2744868b945bcba0fe90d280df346"
CLIENT_SECRET = "1a97f11a318349dbb965ec95513c401b"
GENIUS_ACCESS_TOKEN = "Fr9UV8JlaKa92tqDKYBO2dkOaHUxAI8eAfyHIy0TyX39pmGgZ2CqC2kpDMtZWgoO"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, timeout=5, retries=2)

def get_lyrics(song_name):
    """Fetch lyrics using Genius API"""
    try:
        print(f"Searching for: {song_name}")  # Debugging line
        song = genius.search_song(song_name)
        if song:
            print("Lyrics Found!")  # Debugging line
            return song.lyrics
        else:
            return "Lyrics not found."
    except Exception as e:
        return f"Error fetching lyrics: {str(e)}"

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
    index = music[music['Song-Name'] == song].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        artist = music.iloc[i[0]]['Singer/Artists']
        print(artist)
        print(music.iloc[i[0]]['Song-Name'])
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]]['Song-Name'], artist))
        recommended_music_names.append(music.iloc[i[0]]['Song-Name'])

    return recommended_music_names,recommended_music_posters

st.header('Bollywood Songs Recommender')
music = pickle.load(open('df','rb'))
similarity = pickle.load(open('similarity','rb'))

artist_list = music['Singer/Artists'].unique()
selected_artist = st.selectbox("Select an artist",artist_list)

if st.button('show Artist Details'):
    artist_image_url, artist_popularity, genres = get_artist_info(selected_artist)
    st.image(artist_image_url, caption=selected_artist, width=300)
    st.write(f"**popularity**:{artist_popularity}")
    st.write(f"**Genres**:{', '.join(genres)}")

music_list = music['Song-Name'].values
selected_movie = st.selectbox(
    "Type or select a song from the dropdown",
    music_list
)

if st.button("show lyrics"):
    lyrics = get_lyrics("selected_song")
    st.text_area("lyrics",lyrics,height=300)

if st.button('Search'):
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
