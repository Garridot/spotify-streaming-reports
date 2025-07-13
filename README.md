
# Spotify Streaming Reports

## Overview
Python project that retrieves and reports a user's Spotify usage, weekly highlights, and patterns while generating personalized recommendations using AI.


## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Scheduled Workflows (GitHub Actions)](#scheduled-workflows-github-actions)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
## About

Spotify Streaming Reports is a Python-based tool that analyzes a user's listening history on Spotify and generates weekly summaries including:

- Listening time breakdown
- Most played artists, genres, and tracks
- Listening trends and variation over time
- Weekly personalized recommendations based on patterns

The project aims to provide insights into your listening habits and help you rediscover music you love.

Spotify Streaming Reports integrates DeepSeek (via OpenRouter) to generate personalized weekly highlights, observations, and music recommendations based on your listening data.

This project uses the model `deepseek/deepseek-r1:free`, which is accessed through the OpenRouter API. The AI analyzes your top genres, artists, and patterns to deliver meaningful insights beyond basic statistics.
## Features

- 🔁 Weekly summary of listening activity
- 📊 Genre and artist usage patterns
- 📈 Time-based trends and visualizations
- 🌟 Personalized recommendations.
- 🤖 AI-generated summaries and recommendations using DeepSeek via OpenRouter
- Developed a website that allows users to visualize each weekly report.
- 🧠 Built with Spotify Web API and Python data tools (pandas, etc)


## Installation

1. Clone the repository:
```bash
git clone https://github.com/Garridot/spotify-streaming-reports.git
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate 
```

3. Install dependencies:
```
pip install -r requirements.txt
```


## Configuration

To use the Spotify API, you must register your application on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/), and set the following environment variables:

```bash
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8000/callback
```

You must store them in a `.env` file.

You will need an OpenRouter API key to access DeepSeek models. You can get yours at [OpenRouter.ai](https://openrouter.ai/).


```bash
OPENROUTER_API_KEY=your_openrouter_api_key
```

Add the following to your `.env` file.

To run this project, you also need to set the following environment variables.

```bash
SECRET_KEY=your_generated_secret_key              # Used for Flask session security
FLASK_ENV=default                                  # Use 'production' to activate DATABASE_URL
DATABASE_URL=your_database_connection_url         # Required when FLASK_ENV is set to 'production'
```

🔐 **Notes**
- **SECRET_KEY**: You can generate a secure key in Python:

```python
import secrets
print(secrets.token_hex(32))
```
- **DATABASE_URL**: Only required if ```FLASK_ENV=production```. It should be a valid SQLAlchemy-compatible connection string, for example:
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Scheduled Workflows (GitHub Actions)

This project uses GitHub Actions to automatically run background tasks at defined intervals:

🕐 ```Daily Spotify Sync```
* Purpose: Collects recent Spotify activity for each user.
* Schedule: Runs every hour at minute 5.
* Script Executed: ```run_worker.py```
```
name: Daily Spotify Sync
  schedule: '5 * * * *'  # Runs at the fifth minute of every hour
```
📅 ```Weekly Report Task```
- Purpose: Generates weekly reports using Spotify data and AI-powered summaries.
- Schedule: Runs every Monday at 01:00 UTC.
- Script Executed: ```run_weekly_worker.py```
- Integrates: DeepSeek via OpenRouter for generating insights and summaries.
```
- name: Weekly Tasks
  schedule: '0 1 * * 1'  # Every Monday at 01:00 UTC
```
🔐 ```Secrets Used```

Both workflows rely on the following environment variables defined as GitHub Secrets:

* ```SPOTIFY_CLIENT_ID```, ```SPOTIFY_CLIENT_SECRET```, ```SPOTIFY_REDIRECT_URI```
* ```DEEPSEEK_API_KEY``` (only for weekly reports)
* ```DATABASE_URL```, ```SECRET_KEY```, ```FLASK_ENV```

**Optional**

You can notify users about their weekly reports by sending emails and adding this task to the ```weekly_task.yml``` file:
```
    process_email_sending_task:         # Define a job called "weekly_report" 
      runs-on: ubuntu-latest              # Run on the latest available Ubuntu
      steps:                              # Steps that the job will execute in sequence       
        - uses: actions/checkout@v2       # Step 1: Checkout the code
        
        - name: Set up Python             # Step 2: Configure Python
          uses: actions/setup-python@v2
          with:
            python-version: '3.8'
            
        - name: Install dependencies      # Step 3: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt          
            
        - name: Run Email Sending Task    # Step 4: Run the script   
          env:
            CLOUDAMQP_URL: ${{ secrets.CLOUDAMQP_URL }}  
            FLASK_ENV: ${{ secrets.FLASK_ENV }}
            DATABASE_URL: ${{ secrets.DATABASE_URL }}
            SECRET_KEY: ${{ secrets.SECRET_KEY }}
            MAIL_SERVER: ${{ secrets.MAIL_SERVER }}
            MAIL_PORT: ${{ secrets.MAIL_PORT }}
            MAIL_USE_TLS: ${{ secrets.MAIL_USE_TLS }} 
            MAIL_USERNAME: ${{ secrets.MAIL_USERNAME }} 
            MAIL_PASSWORD: ${{ secrets.MAIL_PASSWORD }} 
            SPOTIFY_CLIENT_ID: ${{ secrets.SPOTIFY_CLIENT_ID }}
            SPOTIFY_CLIENT_SECRET: ${{ secrets.SPOTIFY_CLIENT_SECRET }}
            SPOTIFY_REDIRECT_URI: ${{ secrets.SPOTIFY_REDIRECT_URI }}
          run: |
            python run_email_sending_worker.py
```

Ensure you add the required email configurations in the ```.env``` file and set them as ```GitHub Secrets```:

```
MAIL_SERVER=YOUR_MAIL_SERVER
MAIL_PORT=YOUR_MAIL_PORT
MAIL_USE_TLS=YOUR_MAIL_USE_TLS
MAIL_USERNAME=YOUR_MAIL_USERNAME
MAIL_PASSWORD=YOUR_MAIL_PASSWORD
```

## Usage

Once you are authenticated, the website will gather your data for the week and provide you with a visual report.

Run:
```bash
python run.py
```
## Screenshots

![Weekly Report Login](screenshots/screenshot_1.jpg)

![Weekly Report Top Tracks](screenshots/screenshot_2.jpg)

![Weekly Report Description](screenshots/screenshot_3.jpg)

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

Don't forget to update tests as appropriate.