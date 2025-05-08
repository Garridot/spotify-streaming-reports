import requests
from requests import Session
from app.core.config import Config
from urllib.parse import urlencode
import hashlib
import httpx
from urllib.parse import quote_plus
import time
from datetime import datetime, timedelta
import pandas as pd

class LastfmService:
    BASE_URL = "https://ws.audioscrobbler.com/2.0/"

    def __init__(self):
        self.api_key = Config.LASTFM_API_KEY
        self.shared_secret = Config.LASTFM_API_SECRET 

    def get_oauth_url(self, callback_url: str) -> str:
        """Generate Last.fm authentication URL"""
        params = {
            'api_key': self.api_key,
            'cb': callback_url
        }
        return f"https://www.last.fm/api/auth/?{urlencode(params)}"    

    def _generate_api_sig(self, params: dict) -> str:
        """
        Generates an API signature to authenticate requests to the Last.fm API.

        The signature is required by Last.fm to verify the authenticity of API requests and is calculated as an MD5 hash of the sorted parameters concatenated with the shared secret.

        Parameters:
        params (dict): Dictionary of parameters to be included in the API request.
        Must contain all parameters except 'format' (which is excluded from the signature).

        Returns:
        str: 32-character hexadecimal string representing the MD5 signature.

        Important Notes:
        - The 'format' parameter must be present in the request, but is NOT included in the signature.
        - The shared secret is never sent directly; it is only used to generate the signature.
        - The signature must be unique for each set of parameters.
        - Last.fm will verify this signature on its end to authenticate the request.

        API Reference:
        https://www.last.fm/api/authentication
        """
        # Exclude the 'format' parameter from the signature if it exists
        filtered_params = {k: v for k, v in params.items() if k != 'format'}
        
        # Sort and concatenate
        sorted_params = sorted(filtered_params.items())
        param_str = "".join([f"{k}{v}" for k, v in sorted_params])
        
        # Add secret and calculate MD5
        signature_data = param_str + self.shared_secret
        return hashlib.md5(signature_data.encode()).hexdigest()

    def get_session(self, token: str) -> dict:
        params = {
            "method": "auth.getSession",
            "api_key": self.api_key,
            "token": token,
            "format": "json"
        }
        
        # Generate signature before encoding values
        params["api_sig"] = self._generate_api_sig(params)
        
        # Encode values ​​for POST submission
        encoded_params = {
            k: v for k, v in params.items()
        }
        
        response = requests.post(
            self.BASE_URL,
            data=encoded_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()  
               
    
    def _make_request(self, method: str, params: dict, session_key: str = None) -> dict:
        """Base method for all API calls"""
        params.update({
            'method': method,
            'api_key': self.api_key,
            'format': 'json'
        })
        
        if session_key:
            params['sk'] = session_key
        
        params['api_sig'] = self._generate_api_sig(params)
        
        response = requests.post(
            self.BASE_URL,
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()

    def get_diary_report(self, username: str, session_key: str) -> dict:
        """
        Retrieve user statistics for the entire day prior.
        Arguments:
            username (str):
            session_key (str):
        Returns:
            List of basic information about tracks:            
            - artist 
            - streamable 
            - image: 'sizes': ['small', 'medium', 'large', 'extralarge'] 
            - mbid 
            - album 
            - name 
            - url 
            - date
        """

        yesterday = datetime.now() - timedelta(days=1)        
        start_date = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
        end_date = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())
        
        all_tracks = []
        page = 1
        total_pages = 1
        while page <= total_pages:
            
            data = self._make_request(
                'user.getRecentTracks',
                {
                    'user': username,
                    'from': start_date,
                    'to': end_date,
                    'limit': 200,  # maximum allowed per request
                    'page': page,                    
                    "format": "json"
                },
                session_key
            )
            
            # exclude tracks that are currently playing
            tracks = [track for track in data['recenttracks']['track'] 
                if not track.get('@attr', {}).get('nowplaying')]

            all_tracks.extend(tracks)
            total_pages = int(data['recenttracks']['@attr']['totalPages'])
            page += 1

            time.sleep(0.2) # delay to avoid rate limiting
        return all_tracks    