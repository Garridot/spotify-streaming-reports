import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.core.config import Config
from app.models.domain.user import User


class JWTManager:
    def __init__(self):
        self.secret_key = None
        self.algorithm = None
        
    def init_app(self, app):
        """Initialization with Flask configuration"""
        self.secret_key = Config.SECRET_KEY
        self.algorithm = Config.JWT_ALGORITHM    

    def create_access_token(self, user_id: int, service_id: str = None) -> str:
        """Create a JWT access token for the user"""
        payload = {
            'sub': str(user_id),
            'service_id': service_id,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'scope': 'access_token'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int, service_id: str = None) -> str:
        """Create a JWT refresh token for the user"""
        payload = {
            'sub': str(user_id),
            'service_id': service_id,
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow(),
            'scope': 'refresh_token'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)    

    def verify_token(self, token: str) -> dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token expirado")
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Token inválido: {str(e)}")
        return None

jwt_manager = JWTManager()

def token_required(f):
    """
    Decorator to protect routes by requiring a valid JWT token in the request header.

    This decorator checks for the presence and validity of a JWT token in the request headers.
    If the token is valid, it allows the request to proceed with the authenticated user. 
    If invalid or missing, it returns an appropriate JSON response with an error message.

    Parameters:
    ----------
    f : function
        The function to be wrapped by this decorator.

    Returns:
    -------
    function : 
        The wrapped function if the token is valid; otherwise, returns a JSON error response.

    JSON Responses:
    ---------------
    403 : {'message': 'Token is missing.'}
        If no token is provided in the request headers.
    404 : {'message': 'User not found.'}
        If the token is valid but no user is found with the ID in the token.
    401 : {'message': 'Token expired. Please refresh your token.'}
        If the token has expired.
    403 : {'message': 'Invalid token.'}
        If the token is malformed or invalid.
    403 : {'message': 'Token is invalid or corrupted.'}
        For any other unexpected errors with the token.

    Usage:
    ------
    @token_required
    def protected_route(current_user):
        # Code for the protected route
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        
        if not token:
            return jsonify({'message': 'Token is missing.'}), 403

        try:
            # Decode the JWT token.
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])       
            
            # Search for the user based on the user_id in the token.
            current_user = User.query.filter_by(id=data['sub']).first()

            # Check if the user exists.
            if current_user is None:
                return jsonify({'message': 'User not found.'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid or corrupted.', 'error': str(e)}), 403

        # Continue executing the function if the token is valid.
        return f(current_user, *args, **kwargs)

    return decorated


def refresh_token_required(f):
    """
    Decorator specific to token refresh endpoints.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token missing or invalid"}), 401
            
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload or payload.get('scope') != 'refresh_token':
            return jsonify({"error": "Invalid refresh token"}), 401
            
        request.user_id = payload['sub']
        return f(*args, **kwargs)
        
    return decorated_function