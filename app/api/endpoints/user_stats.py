from app.core.security import token_required, refresh_token_required, jwt_manager, redirect
from flask import Blueprint, current_app, redirect, request, jsonify
from flask import current_app
import json
import datetime

stats_bp = Blueprint('stats', __name__, url_prefix='/api/user_stats')

@stats_bp.route("/weekly_history", methods=['GET'])
@token_required  
def get_user_weekly_history(current_user): 

    weekly_register_repository = current_app.container.weekly_register_repository  

    weekly_register = weekly_register_repository.retrieve_all_weekly_register_by_user(                
        user_id = current_user.id             
        )

    if len(weekly_register) == 0:
        return jsonify({"user_history_stats": None})  
    
    stats = []      
   
    for register in weekly_register:          
        data = {}
        data["time_period"] = {"start_date": register.week_start_date.strftime("%Y-%m-%d"), "end_date": register.week_end_date.strftime("%Y-%m-%d") }
        data["weekly_id"] = register.id

        stats.append(data)                  
        
    return jsonify({"user_history_stats": stats}) 

@stats_bp.route("/weekly_stats", methods=['GET'])
@token_required  
def get_user_weekly_stats(current_user): 

    weekly_id = request.headers.get('X-Weekly-Id')     

    weekly_register_repository = current_app.container.weekly_register_repository  

    register = weekly_register_repository.retrieve_required_weekly_register_by_user(   
        user_id = current_user.id, 
        weekly_id = weekly_id, 
        )    

    if not register :
        return jsonify({"user_stats": None})  
    
    stats = []      
      
    data = {}
    data["time_period"] = {"start_date": register.week_start_date.strftime("%Y-%m-%d"), "end_date": register.week_end_date.strftime("%Y-%m-%d") }
    data["top_tracks"] = register.top_tracks
    data["top_artists"] = register.top_artists
    data["top_genres"] = register.top_genres
    data["extra_data"] = register.extra_data 
    

    get_report = register.report       

    report = {
        "title" : get_report["title"],
        "description" : get_report["description"],
        'summary': get_report["report"]['summary'],
        'patterns': get_report["report"]['patterns'],
        'highlight': get_report["report"]['highlight'],
        'recommendations': get_report["report"]['recommendations'],
        'insight': get_report["report"]['insight'],
    }         

    data["report"] = report                     
        
    return jsonify({"user_stats": data}) 