from app.tasks.sent_email import email_task
from app.core.config import Config
from app import create_app
from flask_mail import Mail

if __name__ == '__main__': 
    app = create_app()
    with app.app_context():
        # Flask-Mail (Gmail SMTP)
        app.config['MAIL_SERVER'] = Config.MAIL_SERVER
        app.config['MAIL_PORT'] = Config.MAIL_PORT
        app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS 
        app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME 
        app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD  
      
        mail = Mail(app) 

        email_task(mail)