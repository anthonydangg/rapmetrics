## Description
[Rapmetrics](https://www.instagram.com/rapmetrics/) is an Instagram account that visualizes rap data. This repo contains the code on how the data is obtained and stored.

## ETL Diagram
<img src="assets/etl.jpg" alt="etl diagram">

The project has many different scripts that extract different types of data from Spotify. The scripts, however, follow the general pipeline of extracting data from Spotify's API or through scraping, transforming the data, and loading it into a warehouse. This warehouse is used to create visualizations found on the Rapmetrics account. The pipeline is ran daily with cron to collect Spotify data.

## Types of data collected
- Track streams from albums.
- Monthly listeners of rap artists.
- Top songs of an artist.


## Installation

Clone the repository:
```bash
git clone https://github.com/anthonydangg/rapmetrics
cd rapmetrics
```

Create a virtual environment (optional):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variables

This project requires some environment variables for API keys and database connections. 

Create a `.env` file in the monthly_listeners_scraper directory after filling out `template.env`:
   ```bash
   cp template.env src/monthy_listeners_scraper/.env
