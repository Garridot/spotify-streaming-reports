import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import Config
import time

class SpotifyService:
    
    def get_user_info(self, access_token: str) -> dict:
        """
        Retrieve current user's profile info
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
        Retrieve recently played tracks
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
           

    def get_artist_info(self, artists, code: str,):
        """
        Retrieve information about the required artists
        Args:
            code: User access token
            artists_id: List of the required artist IDs.
        Returns:    
            List of basic information about artists:
            - id
            - artist
            - genres   
        """
        
        sp = self.get_spotify_client(code)
        artists_res = []        

        for artist in artists:          
            
            try:
                if artist["artist_id"] is not None:
                    artist_info = sp.artist(artist["artist_id"])                     
                    
                    data = {
                        'artist_id': str(artist_info.get('id', '')),
                        'artist': str(artist_info.get('name', '')),
                        'artist_image': str(artist_info.get("images","")[0]["url"]),
                        'genres': list(artist_info.get('genres', [])),   
                    }  
                else:
                    artist_info = sp.search(q='artist:' + artist["artist_name"], type='artist', limit=1)                        

                    data = {
                        'artist_id': str(artist_info["artists"]["items"][0]['id']),
                        'artist': str(artist_info["artists"]["items"][0]['name']),
                        'artist_image': str(artist_info["artists"]["items"][0]["images"][0]["url"]),
                        'genres': list(artist_info["artists"]["items"][0]['genres']),
                    }            
                         
                artists_res.append(data)                
            except Exception as e:
                print(f"Error getting info for artist: {str(e)}")              

            time.sleep(0.2) # delay to avoid rate limiting      
                
        return artists_res

    
   