from flask import Blueprint, redirect, request, current_app, jsonify
from app.core.security import token_required, refresh_token_required

lastfm_stats_bp = Blueprint('lastfm_stats', __name__, url_prefix='/api/lastfm_stats')

@lastfm_stats_bp.route('/stats/diary')
@token_required
def get_diary_stats(current_user):
    """Obtiene estadísticas diarias del usuario"""
    if not current_user.lastfm_account:
        return jsonify({"error": "Last.fm account not connected"}), 400    
    
    try:
        lastfm_user = current_user.lastfm_account
        lastfm_service = current_app.container.lastfm_service

        stats = {"stats": sync_service.get_diary_report(        
                    lastfm_user.lastfm_username, 
                    lastfm_user.lastfm_session_key
                    ),        
        }

        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": "Unable to get diary stats"}), 500

@lastfm_stats_bp.route('/stats/weekly')
@token_required
def get_weekly_stats(current_user):
    """Obtiene estadísticas semanales del usuario"""
    if not current_user.lastfm_account:
        return jsonify({"error": "Last.fm account not connected"}), 400    
    
    try:
        lastfm_user = current_user.lastfm_account
        lastfm_service = current_app.container.lastfm_service

        stats = {"stats": sync_service.get_weekly_report(        
                    lastfm_user.lastfm_username, 
                    lastfm_user.lastfm_session_key
                    ),        
        }

        return jsonify(stats)
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": "Unable to get weekly stats"}), 500