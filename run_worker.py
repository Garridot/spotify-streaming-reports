# from app.workers.rabbitmq_worker import RabbitMQWorker
from app.tasks.daily_task import sync_all_users_daily_register
from app import create_app

if __name__ == '__main__':    

    app = create_app()

    with app.app_context():

        sync_all_users_daily_register()
    
    # worker = RabbitMQWorker()
    # try:
    #     worker.connect()
    #     worker.start_worker()
    # except KeyboardInterrupt:
    #     worker.close()
    # except Exception as e:
    #     logger.error(f"Worker error: {str(e)}")
    #     worker.close()