import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app, make_response, redirect
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

        Parameters:
        ----------
        f : function
            The function to be wrapped by this decorator.
        Returns:
        -------
        function : 
            The wrapped function if the token is valid; otherwise, returns a JSON error response.
        
        Usage:
        ------
        @token_required
        def protected_route(current_user):
            # Code for the protected route
        """
        @wraps(f)
        def decorated(*args, **kwargs):            

            try:
                token = request.headers.get('x-access-token') or request.cookies.get('x-access_token')
                if not token: return make_response(redirect("http://127.0.0.1:8000/"))
                # Decode the JWT token.
                data = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])                
                # Search for the user based on the user_id in the token.
                current_user = User.query.filter_by(id=data['sub']).first()
                # Check if the user exists.
                if current_user is None:  return jsonify({'message': 'User not found.'}), 404

            except jwt.ExpiredSignatureError:
                
                refresh_token = request.cookies.get('x-refresh_token')
                if not refresh_token:
                    return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
                try:
                    refresh_data = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
                    if refresh_data['scope'] != 'refresh_token':
                        return jsonify({'message': 'Invalid refresh token.'}), 403

                    current_user = User.query.filter_by(id=refresh_data['sub']).first()
                    if current_user is None:
                        return jsonify({'message': 'User not found.'}), 404

                    # Crear nuevo access token
                    new_access_token = jwt_manager.create_access_token(current_user.id)
                    
                    # Crear respuesta intermedia con nuevo token en cookies
                    response = make_response(f(current_user, *args, **kwargs))
                    response.set_cookie("x-access_token", new_access_token, httponly=True, samesite='Lax')
                    return response  
                except jwt.ExpiredSignatureError:
                    return jsonify({'message': 'Refresh token expired. Please login again.'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'message': 'Invalid refresh token.'}), 403 

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
    def decorated(*args, **kwargs):

        try:
            token = request.headers.get('x-refresh-token')
            if not token: return jsonify({'message': 'x-refresh-token is missing.'}), 403
            # Decode the JWT token.
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])                
            
            if not data or data['scope'] != 'refresh_token': 
                return jsonify({"error": "Invalid refresh token"}), 401
            
            # Search for the user based on the user_id in the token.
            current_user = User.query.filter_by(id=data['sub']).first()
            # Check if the user exists.
            if current_user is None:  return jsonify({'message': 'User not found.'}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired. Please refresh your token.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 403
        except Exception as e:
            return jsonify({'message': 'Token is invalid or corrupted.', 'error': str(e)}), 403

        # Continue executing the function if the token is valid.
        return f(current_user, *args, **kwargs)

    return decorated 