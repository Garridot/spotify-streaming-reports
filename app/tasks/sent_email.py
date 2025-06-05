from app.repositories.user_repository import UserRepository
from app.core.config import Config
from flask import current_app
from app.core.database import db
from datetime import datetime, timedelta
from flask import render_template
from flask_mail import Mail, Message
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Flask-Mail (Gmail SMTP)
app.config['MAIL_SERVER'] = Config.MAIL_SERVER
app.config['MAIL_PORT'] = Config.MAIL_PORT
app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS 
app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME 
app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD  

mail = Mail(app)

def highlight_text(text):
    text_format = re.sub(
        r'\*\*(.*?)\*\*',
        r'<span style="color: coral; padding: 0.1rem 0.3rem;">\1</span>',
        text)

    text_format = re.sub(
        r'\*(.*?)\*',
        r'<em style="color:coral;">\1</em>',
        text_format
    )   

    return text_format     


def email_task():

    last_day_of_week = datetime.now().date() - timedelta(days=1)
    first_day_of_week = last_day_of_week - timedelta(days=6)   

    weekly_register_repository = app.container.weekly_register_repository

    users_repo = UserRepository(db.session).get_all_user() 
    for user in users_repo:  

        weekly_register = weekly_register_repository.retrieve_weekly_register(
            user_id = user.id, 
            start_date = first_day_of_week, 
            end_date = last_day_of_week
        )

        top_tracks = weekly_register.top_tracks
        top_artists = weekly_register.top_artists
        top_genres = weekly_register.top_genres
        extra_data = weekly_register.extra_data 
        get_report = weekly_register.report
        

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