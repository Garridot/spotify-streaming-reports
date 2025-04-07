import requests
from requests import Session
from app.core.config import Config
from urllib.parse import urlencode
import hashlib
import httpx
from urllib.parse import quote_plus

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
        
        # Generar firma antes de codificar los valores
        params["api_sig"] = self._generate_api_sig(params)
        
        # Codificar todos los valores para el envío POST
        encoded_params = {
            k: v for k, v in params.items()
        }
        
        response = requests.post(
            self.BASE_URL,
            data=encoded_params,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()         