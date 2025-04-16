from flask import Blueprint, current_app, redirect, request, jsonify
from app.core.security import token_required, refresh_token_required

spotify_stats_bp = Blueprint('spotify_stats', __name__, url_prefix='/api')

@spotify_stats_bp.route('/spotify/recently-played')
@token_required
def get_recently_played(current_user):    
    """ 
    Retrieve the recently played tracks on Spotify by the user.

    Parameters:
    -----------
    current_user: User
        The current user object (from token authentication).
    
    Returns:
    --------
        JSON response of the list of recently played tracks on Spotify by the user.
    """
    try:
        user_token = current_user.spotify_account.access_token        
        spotify_service = current_app.container.spotify_service
        tracks = spotify_service.get_recently_played(
           user_token
        )
        
        return jsonify(tracks)
        
    except Exception as e:
        current_app.logger.error(f"Error getting recently played: {str(e)}")
        return jsonify({"error": "No se pudieron obtener los tracks recientes"}), 500