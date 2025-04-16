from app.core.security import token_required, refresh_token_required, jwt_manager
from flask import Blueprint, current_app, redirect, request, jsonify

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/refresh', methods=['POST'])
@refresh_token_required
def refresh_token(current_user):   
    """
    Refreshes an expired access token using the refresh token
    Arguments:
    ----------
        current_user: User
            The current user object (from token authentication).
    Returns:
    --------
        dict: new access token:
    """     
    new_access_token = jwt_manager.create_access_token(current_user.id)
    return jsonify({
        "user_id": current_user.id,
        "access_token": new_access_token})