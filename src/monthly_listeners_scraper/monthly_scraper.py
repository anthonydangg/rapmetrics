import random
import re
import datetime
import time
import os
from dotenv import load_dotenv

import requests

import sqlite3

from bs4 import BeautifulSoup
import lxml

from tqdm import tqdm

load_dotenv()
db_path = os.getenv("DB_PATH", "src/monthly_listeners_scraper/monthly_listeners.db")  # Default for local testing
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS streams(date DATE, artist TEXT, monthly_listeners INT)''')

def get_listeners(artists, retries = 3):
    for artist in tqdm(artists):
        success = False
        attempts = 0

        while not success and attempts < retries:
            try:
                #scrape page
                headers = {
                    'User-Agent': random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)',
                    ])
                }

                response = requests.get(artist, headers=headers)
                r = response.text
                soup = BeautifulSoup(r, 'lxml')

                #get monthly listeners
                monthly_listeners_element = soup.find('div', 
                    attrs={'data-testid': 'monthly-listeners-label'}
                )
                monthly_listeners = monthly_listeners_element.text.replace(',','')

                #add data to table
                current_date = datetime.datetime.now()
                artist = soup.find('meta', property="og:title").get('content')
                streams = int(re.findall(r'\d+', monthly_listeners)[0])

                time.sleep(random.uniform(5, 10))
                c.execute('''INSERT INTO streams VALUES(?,?,?)''', (current_date, artist, streams))
                conn.commit()
                success = True

            except Exception as e:
                print(f"An error occurred: {e}, retrying...\n")
                print(f"Failed to fetch data for {artist}, status code: {response.status_code}")
                attempts += 1
                time.sleep(random.uniform(60, 65))

        if not success:
            print(f"Failed to process {artist} after {retries} attempts")

    return 

#currently tracking
kendrick = 'https://open.spotify.com/artist/2YZyLoL8N0Wb9xBt1NhZWg'
asap_rocky = 'https://open.spotify.com/artist/13ubrt8QOOCPljQ2FL1Kca'
weeknd = 'https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ'
travis_scott = 'https://open.spotify.com/artist/0Y5tJX1MQlPlqiwlOH1tJY'
future = 'https://open.spotify.com/artist/1RyvyyTE3xzB2ZywiAwp0i'
tyler = 'https://open.spotify.com/artist/4V8LLVI7PbaPR0K2TGSxFF'
lil_uzi = 'https://open.spotify.com/artist/4O15NlyKLIASxsJ0PrXPfz'

artists = [kendrick, asap_rocky, weeknd, travis_scott, future, tyler, lil_uzi]
get_listeners(artists)


conn.close()

current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print('Completed at ' + current_time)

