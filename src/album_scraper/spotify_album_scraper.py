import time
import csv
import random
import re
from pathlib import Path
import requests


from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By


link = input('Paste your Spotify album url:\n')

driver = webdriver.Chrome()
driver.get(link)
time.sleep(5)

def get_metadata():
    '''Get album name, artist name'''
    headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)',
            ])
        }

    html_text = requests.get(link, headers=headers).text
    soup = BeautifulSoup(html_text, 'lxml')
    
    album_name = soup.find('meta', property="og:title").get('content')
    text = soup.find('meta', property="og:description").get('content')
    match = re.match(r'^(.*?) ·', text)
    artist_name = match.group(1)
    return [album_name, artist_name]

def selenium_scraper(): 
    track_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]')
    track_links = [track.get_attribute('href') for track in track_elements]

    track_streams = {}
    name = []
    plays = []

    for link in track_links:
        driver.get(link)
        time.sleep(5)

        name.append(driver.find_element(By.CSS_SELECTOR, 'h1[data-encore-id="text"]').text)
        plays.append(driver.find_element(By.CSS_SELECTOR, 'span[data-testid="playcount"]').text)
        
    track_streams['Name'] = name
    track_streams['Plays'] = plays
    print(track_streams)
    return track_streams, name

track_streams,name = selenium_scraper()
driver.quit()

current_dir = Path(__file__).parent 
filename = f'{get_metadata()[0]}_{get_metadata()[1]}_data.csv'
file_path = current_dir / "csv" / filename  

with open(file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(track_streams.keys())
    for i in range(len(name)):
        writer.writerow([val[i] for val in track_streams.values()])
