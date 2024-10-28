import sqlite3

import datetime
import random

from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#GETTING TOP 10 MOST POPULAR SONGS OF AN ARTIST

link = 'https://kworb.net/spotify/artist/4V8LLVI7PbaPR0K2TGSxFF_songs.html' #paste link here
#later we can replace this with spotify api search. use that search to get kworb link cause it match id

headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)',
            ])
        }

client_id = 'bbc5b8300033433c85dd9ef913665eb7'
client_secret = '1114319592454b78874bdf5a1f3b6cc1'
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

artist_name = sp.artist('4V8LLVI7PbaPR0K2TGSxFF')['name']

conn = sqlite3.connect(f"/Users/anthonydang/Documents/projects/rapmetrics/top_scraper/{artist_name}.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS song_streams(track TEXT, album TEXT, streams INT, date_scraped DATE)''')

def getTopTen(link):
    html_text = requests.get(link, headers=headers).text
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
                link = a_tag['href']
                #get album name from link
                album = sp.track(link)['album']['name']
                
                td_values = tr.find_all('td')
                if len(td_values) > 2:
                    streams = int(td_values[1].text.replace(',',''))
                    count += 1 #this will cause issue if missing data
                    c.execute('''INSERT INTO song_streams VALUES(?,?,?,?)''', (track, album, streams, datetime.datetime.now()))
                    conn.commit()
    return

getTopTen(link)

conn.close()
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('Completed at ' + current_time)
