from dotenv import load_dotenv
import os
import datetime
import random
import requests
from pathlib import Path

import sqlite3

from bs4 import BeautifulSoup

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#GETTING TOP 10 MOST POPULAR SONGS OF AN ARTIST

load_dotenv('.env')
client_id: str = os.getenv('CLIENT_ID')
client_secret: str = os.getenv('CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


url = os.getenv("SPOTIFY_ARTIST_URL")
artist_id = url.split("/artist/")[-1]

kworb_link = f'https://kworb.net/spotify/artist/{artist_id}_songs.html' 
artist_name = sp.artist(artist_id)['name']

headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)',
            ])
        }

conn = sqlite3.connect(os.path.join("src/top_10_songs_scraper", f"{artist_name}.db"))
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS song_streams(track TEXT, album TEXT, streams INT, date_scraped DATE)''')

def getTopTen(kworb_link):
    html_text = requests.get(kworb_link, headers=headers).text
    soup = BeautifulSoup(html_text, 'lxml')
    tr_elements = soup.find_all('tr')

    # Loop through the tr elements
    count = 0
    for tr in tr_elements:
        if count == 10:
            break
        # Find the 'td' with the class 'text'
        td_text = tr.find('td', class_='text')
        if td_text:
            a_tag = td_text.find('a')
            if a_tag:
                track = a_tag.text
                sp_link = a_tag['href']
                album = sp.track(sp_link)['album']['name']
                td_values = tr.find_all('td')
                if len(td_values) > 2:
                    streams = int(td_values[1].text.replace(',',''))
                    count += 1 #this will cause issue if missing data
                    c.execute('''INSERT INTO song_streams VALUES(?,?,?,?)''', (track, album, streams, datetime.datetime.now()))
                    conn.commit()
    return

getTopTen(kworb_link)

conn.close()
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('Completed at ' + current_time)
