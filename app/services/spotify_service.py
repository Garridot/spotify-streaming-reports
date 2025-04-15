import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import Config

class SpotifyService:
    
    def get_user_info(self, access_token: str) -> dict:
        """
        Get current user's profile info
        Arguments:
            code: User access token
        """
        sp = spotipy.Spotify(auth=access_token)
        return sp.current_user()    

    def get_spotify_client(self, access_token: str):
        """
        Create an authenticated Spotify client
        Arguments:
            code: User access token
        """
        return spotipy.Spotify(auth=access_token)

    def get_recently_played(self, code: str, limit: int = 50):
        """
        Gets recently played tracks
        Arguments:
            code: User access token
            limit: Maximum number of tracks to return (max 50)
        Returns:
            List of basic information about tracks: 
            - id
            - name
            - artists
            - artists_id
            - album    
            - image
            - played_at
            - duration_ms
        """
        sp = self.get_spotify_client(code)
        results = sp.current_user_recently_played(limit=limit)           
        
        tracks = []        
        for item in results['items']:
            track = item['track']             

            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artists': track['artists'][0]['name'],
                'artists_id': track['artists'][0]['id'],
                'album': track['album']['name'],                
                'image': track['album']['images'][0]["url"],
                'played_at': item['played_at'],
                'duration_ms': track['duration_ms'],
            }) 
        return tracks            
           

    def get_artist_info(self, artists_id, code: str,):
        """
        Gets information about the required artists
        Args:
            code: User access token
            artists_id: List of the required artist IDs. Returns:
        Returns:    
            List of basic information about artists:
            - id
            - artist
            - genres   
        """
        
        sp = self.get_spotify_client(code)
        artists_res = []
        for artist_id in artists_id:
            artist_info = sp.artist(artist_id) 

            artists_res.append({
                'id': artist_info['id'],
                'artist': artist_info['name'],
                'genres': artist_info['genres'],   
            }
        )          
        return artists_res

    
   