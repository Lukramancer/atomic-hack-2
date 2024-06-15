import logging
from io import BytesIO
from os import getenv
import asyncio

from PIL.Image import Image
from aio_pika import IncomingMessage
from sqlalchemy.orm import Session

from src import predict, Attachment, create_database_session, FileStorage, RabbitMQClient, Upload


def create_listener(database_session: Session, file_storage: FileStorage, message_queue: RabbitMQClient):
    def put_image_in_file_buffer(image: Image, file_format: str = "png") -> BytesIO:
        image_file_buffer = BytesIO()
        image.save(image_file_buffer, format=file_format)
        image_file_buffer.seek(0)
        return image_file_buffer

    def listener(message: IncomingMessage):
        message = message.body.decode("utf-8")
        if not message.endswith("-created"):
            return

        try:
            upload_id = int(message[:message.index("-created")])
        except ValueError:
            return

        upload: Upload = database_session.query(Upload).get(upload_id)
        if upload_id is None:
            return

        input_image_file_buffer = file_storage.download_file(upload.input_image_key)

        prediction_result = predict(input_image_file_buffer)
        if isinstance(prediction_result, str):
            description = prediction_result
            upload.description = description
        else:
            images, description = prediction_result
            main_image, errors_images = images

            main_image_file_buffer = put_image_in_file_buffer(main_image, "png")
            main_image_file_key = file_storage.upload_file(main_image_file_buffer, ".png")

            upload.description = description
            upload.output_image_key = main_image_file_key

            for index, error_image_with_description in enumerate(errors_images):
                error_image, error_image_description = error_image_with_description
                error_image_file_key = file_storage.upload_file(put_image_in_file_buffer(error_image), ".png")
                attachment = Attachment(upload_id=upload.id, in_upload_index=index, image_file_key=error_image_file_key,
                                        description=error_image_description)
                database_session.add(attachment)

        database_session.commit()
        message_queue.publish_message(f"{upload_id}-done")

    return listener


def main(
        s3_url: str, s3_region: str, s3_access_key: str, s3_secret_access_key: str, s3_bucket_name: str,
        database_driver: str, database_host: str, database_port: int, database_username: str, database_password: str, database_name: str,
        message_queue_user: str, message_queue_password: str, message_queue_host: str, message_queue_port: str
):
    async def startup():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
        logger = logging.getLogger(__name__)

        file_storage = FileStorage(s3_url, s3_region, s3_access_key, s3_secret_access_key, s3_bucket_name)
        database_session = create_database_session(database_driver, database_host, database_port, database_username, database_password, database_name)
        message_queue_consumer_client = RabbitMQClient(message_queue_user, message_queue_password, message_queue_host, message_queue_port, "ml", logger)
        message_queue_publisher_client = RabbitMQClient(message_queue_user, message_queue_password, message_queue_host, message_queue_port, "tg", logger)

        await message_queue_consumer_client.consume_messages(create_listener(database_session, file_storage, message_queue_publisher_client))

    asyncio.run(startup())


if __name__ == "__main__":
    S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME = \
        getenv("S3_URL"), getenv("S3_REGION"), getenv("S3_ACCESS_KEY"), getenv("S3_SECRET_ACCESS_KEY"), getenv("S3_BUCKET_NAME")
    DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME = \
        getenv("DATABASE_DRIVER"), getenv("DATABASE_HOST"), int(getenv("DATABASE_PORT")), getenv("DATABASE_USER"), getenv("DATABASE_PASSWORD"), getenv("DATABASE_DBNAME")
    MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD, MESSAGE_QUEUE_HOST, MESSAGE_QUEUE_PORT = \
        getenv("RABBITMQ_DEFAULT_USER", "guest"), getenv("RABBITMQ_DEFAULT_PASS", "guest"), getenv("RABBIT_MQ_HOST", "localhost"), getenv("RABBIT_MQ_PORT", "5672")

    main(
        S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME,
        DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME,
        MESSAGE_QUEUE_USER, MESSAGE_QUEUE_PASSWORD, MESSAGE_QUEUE_HOST, MESSAGE_QUEUE_PORT
    )
