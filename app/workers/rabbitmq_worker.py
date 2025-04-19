import pika
import json
from datetime import datetime
from app.core.config import Config
from app.tasks.daily_task import sync_all_users_daily_register
from app import create_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQWorker:
    def __init__(self):
        self.app = create_app()
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establishes connection to CloudAMQP"""
        cloudamqp_url = Config.CLOUDAMQP_URL
        params = pika.URLParameters(cloudamqp_url)
        params.socket_timeout = 5
        
        try:
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='daily_sync', durable=True)
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def start_worker(self):
        """Start the worker to process tasks"""
        with self.app.app_context():
            self.channel.basic_consume(
                queue='daily_sync',
                on_message_callback=self.process_task,
                auto_ack=True
            )
            logger.info("Waiting for messages...")
            self.channel.start_consuming()

    def process_task(self, ch, method, properties, body):
        """Process the received message"""
        try:
            message = json.loads(body)
            logger.info(f"Processing task at {datetime.utcnow()}: {message}")
            
            if message.get('task') == 'daily_sync':
                sync_all_users_daily_register()
                
        except Exception as e:
            logger.error(f"Task failed: {str(e)}")

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Connection closed")

if __name__ == '__main__':
    worker = RabbitMQWorker()
    try:
        worker.connect()
        worker.start_worker()
    except KeyboardInterrupt:
        worker.close()
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
        worker.close()