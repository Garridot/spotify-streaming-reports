from flask import Blueprint, redirect, request, current_app, jsonify
from app.core.security import token_required, refresh_token_required

oauth_bp = Blueprint('lastfm_oauth', __name__, url_prefix='/api/lastfm')

@oauth_bp.route('/login')
@token_required
def lastfm_login(current_user):
    lastfm_service = current_app.container.lastfm_service
    callback_url = f"{request.host_url}api/lastfm/callback"
    auth_url = lastfm_service.get_oauth_url(callback_url)
    return jsonify({"auth_url":auth_url}) 

@oauth_bp.route('/callback')
@token_required
def lastfm_callback(current_user):
    """Handles the Last.fm callback"""
    token = request.args.get('token')
    if not token:return jsonify({"error": "Token missing"}), 400
    
    try:
        # Get services from the container
        lastfm_service = current_app.container.lastfm_service     
        lastfm_oauth = current_app.container.fm_oauth_service  
        
        # Get Last.fm session
        session_data = lastfm_service.get_session(token)                  

        # Save credentials
        credentials = lastfm_oauth.save_credentials(session_data, current_user)        
        
        return jsonify({
            "message": "connection to last.fm completed",           
            "user" : credentials["user"],
            "username": credentials["user"],
            "session_key": credentials["session_key"] 
        })

    except Exception as e:
        current_app.logger.error(f"Last.fm error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500