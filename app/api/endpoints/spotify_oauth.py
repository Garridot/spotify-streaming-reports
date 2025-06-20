from flask import Blueprint, current_app, redirect, request, jsonify, make_response 

oauth_bp = Blueprint('spotify_oauth', __name__, url_prefix='/api/auth')

@oauth_bp.route('/spotify/login')
def login_spotify():    
    """    
    Redirects to Spotify OAuth 2.0 authentication page.
    
    This endpoint initiates the Spotify authentication flow by redirecting the user
    to Spotify's authorization page, where they can grant permissions to the application.
    
    Returns:
    --------
        JSON response containing the Spotify authorization URL.
    """
    sp_oauth_service = current_app.container.sp_oauth_service
    auth_url = sp_oauth_service.get_oauth_url()

    return jsonify({"spotify_auth_url": auth_url})

@oauth_bp.route('/spotify/callback')
def spotify_callback():
    """
    Handles the callback from Spotify after successful authentication and stores access/refresh tokens.
        
    Returns:
    --------
        JSON response confirming successful authentication with Spotify and returns access and refresh tokens.
    """
    try:
        sp_oauth_service = current_app.container.sp_oauth_service
        result = sp_oauth_service.handle_spotify_callback(request.args.get('code'))  

        response = make_response(redirect("http://127.0.0.1:8000/home"))
        response.set_cookie("x-access_token", result["tokens"]["access"], httponly=True, secure=True)
        response.set_cookie("x-refresh_token", result["tokens"]["refresh"], httponly=True, secure=True)

        return response

    except Exception as e:
        current_app.logger.error(f"Auth error: {str(e)}")
        return jsonify({"error": str(e)}), 400