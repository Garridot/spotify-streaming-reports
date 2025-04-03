from flask import Blueprint, current_app, redirect, request, jsonify
from app.dependencies import DIContainer

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/spotify/login')
def login_spotify():
    """    
    Redirects to Spotify OAuth 2.0 authentication page.
    
    This endpoint initiates the Spotify authentication flow by redirecting the user
    to Spotify's authorization page where they can grant permissions to your application.
    
    Responses:    
        HTTP 302: Redirect to Spotify's authorization URL.
    """
    container = current_app.container
    auth_url = container.spotify_service.get_oauth_url()
    return redirect(auth_url)

@auth_bp.route('/spotify/callback')
def spotify_callback():
    """
    Maneja el callback de autenticación de Spotify.   
    
    Args:
        code: Código de autorización de Spotify        
        
    Returns:
        TokenResponse: Tokens de acceso.
        
    Raises:
        HTTPException: Si ocurre algún error en el proceso
    """    
    try:
        # Obtener servicio del contenedor        
        auth_service = current_app.container.auth_service
        result = auth_service.handle_spotify_callback(request.args.get('code'))
        print(result)
        # Convertir datetime a string ISO format
        expires_at = result["tokens"].expires_at.isoformat() if result["tokens"].expires_at else None

        return jsonify({
            "user_id": result["user_info"]["id"],
            "access_token": result["tokens"].access_token,
            "token_type": result["tokens"].token_type,
            "expires_at": expires_at,
            "spotify_id": result["user_info"]["spotify_id"]
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Auth error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500