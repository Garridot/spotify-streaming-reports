from app.workers.rabbitmq_worker import RabbitMQWorker


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