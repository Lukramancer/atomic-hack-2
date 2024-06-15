import logging
from os import getenv
import asyncio

from src import create_database_session, FileStorage, RabbitMQClient, telegram_bot_main


def main(
        tg_bot_token: str,
        s3_url: str, s3_region: str, s3_access_key: str, s3_secret_access_key: str, s3_bucket_name: str,
        database_driver: str, database_host: str, database_port: int, database_username: str, database_password: str,
        database_name: str,
        message_queue_user: str, message_queue_password: str, message_queue_host: str, message_queue_port: str
):
    async def startup():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
        logger = logging.getLogger(__name__)

        file_storage = FileStorage(s3_url, s3_region, s3_access_key, s3_secret_access_key, s3_bucket_name)
        database_session = create_database_session(database_driver, database_host, database_port, database_username, database_password, database_name)
        message_queue_consumer_client = RabbitMQClient(message_queue_user, message_queue_password, message_queue_host, message_queue_port, "tg", logger)
        message_queue_publisher_client = RabbitMQClient(message_queue_user, message_queue_password, message_queue_host, message_queue_port, "ml", logger)

        await telegram_bot_main(tg_bot_token, file_storage, database_session, message_queue_consumer_client, message_queue_publisher_client)

    asyncio.run(startup())


if __name__ == "__main__":
    TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
    S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME = \
        getenv("S3_URL"), getenv("S3_REGION"), getenv("S3_ACCESS_KEY"), getenv("S3_SECRET_ACCESS_KEY"), getenv("S3_BUCKET_NAME")
    DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME = \
        getenv("DATABASE_DRIVER"), getenv("DATABASE_HOST"), int(getenv("DATABASE_PORT")), getenv("DATABASE_USER"), getenv("DATABASE_PASSWORD"), getenv("DATABASE_DBNAME")
    MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD, MESSAGE_QUEUE_HOST, MESSAGE_QUEUE_PORT = \
        getenv("RABBITMQ_DEFAULT_USER", "guest"), getenv("RABBITMQ_DEFAULT_PASS", "guest"), getenv("RABBIT_MQ_HOST", "localhost"), getenv("RABBIT_MQ_PORT", "5672")

    main(
        TG_BOT_TOKEN,
        S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME,
        DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME,
        MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD, MESSAGE_QUEUE_HOST, MESSAGE_QUEUE_PORT
    )
