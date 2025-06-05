from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import logging

db = SQLAlchemy()

def init_db(app):
    """
    Initializes the database with the given Flask app.
    
    Parameters:
    -----------
    app: Flask
        The Flask application instance to bind the database.

    Returns:
    --------
    None
    """
    try:
        # Initialize the SQLAlchemy extension with the Flask application
        db.init_app(app)

        # Check the connection to the database on startup
        with app.app_context():
            engine = db.get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))  # Test query 
                app.logger.info("✅ Database connection successful")
                connection.close()

    except OperationalError as e:
        app.logger.error(f"Database connection failed: {e}")
        raise RuntimeError("Failed to connect to the database. Check your configuration.") from e
