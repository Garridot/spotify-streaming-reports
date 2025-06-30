from app.repositories.user_repository import UserRepository
from app.utils.format_text import highlight_text
from flask import current_app
from app.core.database import db
from datetime import datetime, timedelta
from flask import render_template
from flask_mail import Mail, Message
import logging
import re


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



def email_task(mail):   

    weekly_register_repository = current_app.container.weekly_register_repository

    users_repo = UserRepository(db.session).get_all_user() 
    for user in users_repo:          

        week_register =  weekly_register_repository.retrieve_all_weekly_register_by_user(                                
                user_id = user.id             
            )    
        
        weekly_register = week_register[0]

        top_tracks = weekly_register.top_tracks
        top_artists = weekly_register.top_artists
        top_genres = weekly_register.top_genres
        extra_data = weekly_register.extra_data 
        get_report = weekly_register.report

        first_day_of_week = week_register.week_start_date
        last_day_of_week = week_register.week_end_date        

        report = {
            "title" : get_report["title"],
            "description" : get_report["description"],
            'summary': highlight_text(get_report["report"]['summary']),
            'patterns': highlight_text(get_report["report"]['patterns']),
            'highlight': highlight_text(get_report["report"]['highlight']),
            'recommendations': highlight_text(get_report["report"]['recommendations']),
            'insight': highlight_text(get_report["report"]['insight']),
        }          
        
        try:
            html_content = render_template(
                "email.html",
                start_date = first_day_of_week, 
                end_date = last_day_of_week,
                top_tracks = top_tracks,
                top_artists = top_artists,
                top_genres = top_genres,
                extra_data = extra_data,
                report = report, 
                )
            
            msg = Message(
                subject=f"¡Your Weekly Summary is Here! 🎧", 
                sender="miniwrapped@gmail.com",  
                recipients=[user.email],       
            )
            msg.html = html_content  

            mail.send(msg)
            logging.info(f"Successfully sent the email regarding the weekly report for the period from {first_day_of_week} to {last_day_of_week} by user {user.id}.")
        except Exception as e:
            logging.error(f"An error occurred while attempting to send the email regarding the weekly report for the period from {first_day_of_week} to {last_day_of_week} by user {user.id}: {str(e)}")