import pika
import json
from datetime import datetime
from app.core.config import Config

def dispatch_daily_task():
    """Envía la tarea diaria a la cola RabbitMQ"""
    connection = pika.BlockingConnection(pika.URLParameters(Config.CLOUDAMQP_URL))
    channel = connection.channel()
    
    channel.queue_declare(queue='daily_sync', durable=True)
    
    message = {
        'task': 'daily_sync',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='daily_sync',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # hace el mensaje persistente
        )
    )
    
    connection.close()