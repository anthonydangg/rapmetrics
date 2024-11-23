from dotenv import load_dotenv
from pathlib import Path
import os
import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import requests
from bs4 import BeautifulSoup

import random

import pandas as pd
import sqlite3


def sp_conn():
    env_path = Path(__file__).parents[2] / ".env"
    load_dotenv(dotenv_path=env_path)

    client_id: str = os.getenv('CLIENT_ID')
    client_secret: str = os.getenv('CLIENT_SECRET')

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    return sp

def get_tracks():
    sp = sp_conn()
    album = sp.album_tracks(album_id='0hvT3yIEysuuvkK73vgdcW')['items'] #hardcoded album. change later

    track_names = []
    for track in album:
        track_names.append(track['name'])

    return track_names

def get_kworb_data(track_names):
    kworb_link = 'https://kworb.net/spotify/artist/2YZyLoL8N0Wb9xBt1NhZWg_songs.html'
    #hardcoded kendrick. change later

    headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)',
                ])
            }

    html_text = requests.get(kworb_link, headers=headers).text
    soup = BeautifulSoup(html_text, 'lxml')

    tr_elements = soup.find_all('tr')
    data = []
    for tr in tr_elements:
        td_text = tr.find('td', class_='text')
        if td_text:
            a_tag = td_text.find('a')
            if a_tag:
                track = a_tag.text
                # sp_link = a_tag['href']
                td_values = tr.find_all('td')
                streams = int(td_values[1].text.replace(',',''))
                data.append({'track_name': track,
                            "streams": streams,
                            "date" : datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
                            })
    df = pd.DataFrame(data)
    df["track_name"] = pd.Categorical(df["track_name"], categories=track_names, ordered=True)
    df = df.sort_values("track_name").reset_index(drop=True)
    filtered_df = df[df['track_name'].isin(track_names)]
    if filtered_df.empty:
        print('Data is not available yet. Ran at: ' + datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))
        exit()

    sorted_data = filtered_df.reset_index().drop(columns = 'index')

    return sorted_data

def run():
    env_path = Path(__file__).parents[2] / ".env"
    load_dotenv(dotenv_path=env_path)
    db_path = os.getenv("KWORB_DB_PATH")
    conn = sqlite3.connect(db_path)
    df = get_kworb_data(get_tracks())
    df.to_sql('streams', conn, if_exists='append', index=False)
    conn.close()

    print('Ran: ' + datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))

if __name__ == '__main__':
    run()




