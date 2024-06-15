from io import BytesIO
from typing import Callable, Any

from PIL.Image import Image
from aio_pika import IncomingMessage
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.orm import Session

from ..mq import RabbitMQClient
from ..database import Upload, User, register_user_if_not_exists
from ..s3 import FileStorage

from .messages import get_formatted_message


def put_image_in_file_buffer(image: Image, file_format: str = "png") -> BytesIO:
    image_file_buffer = BytesIO()
    image.save(image_file_buffer, format=file_format)
    image_file_buffer.seek(0)
    return image_file_buffer


async def main(token: str, file_storage: FileStorage, database_session: Session, message_queue_consumer_client: RabbitMQClient, message_queue_publisher_client: RabbitMQClient):
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        user_id = message.from_user.id
        register_user_if_not_exists(database_session, user_id)

        await message.reply(get_formatted_message("hello", message))

    @dispatcher.message(F.text.startswith("/get_upload"))
    async def command_get_upload(message: Message):
        user_id = message.from_user.id
        register_user_if_not_exists(database_session, user_id)

        user_role = database_session.query(User).get(user_id).role

        if user_role != "admin":
            await message.reply(get_formatted_message("get_upload_command/permission_denied", message))
            return

        try:
            upload_id = int(message.text.split(' ')[1])
        except IndexError:
            await message.reply(get_formatted_message("get_upload_command/no_upload_id", message))
            return
        except ValueError:
            await message.reply(get_formatted_message("get_upload_command/upload_id_parse_error", message))
            return

        upload: Upload | None = database_session.query(Upload).get(upload_id)
        if upload is None:
            await message.reply(get_formatted_message("get_upload_command/not_found_upload", message, {
                "upload_id": str(upload_id)}))
        else:
            await message.reply(get_formatted_message("get_upload_command/result", message, {
                "input_image_url": file_storage.get_file_url(upload.input_image_key),
                "output_image_url": file_storage.get_file_url(upload.output_image_key)}))

    @dispatcher.message(F.photo)
    async def on_photo_handler(message: Message) -> None:
        user_id = message.from_user.id
        register_user_if_not_exists(database_session, user_id)

        image_file_buffer = BytesIO()
        await bot.download(message.photo[-1], destination=image_file_buffer)
        key = file_storage.upload_file(image_file_buffer)

        upload = Upload(user_id=user_id, input_image_key=key)
        database_session.add(upload)
        database_session.commit()

        bot_reply_message = await message.reply(get_formatted_message("uploaded", message, {"upload_id": str(upload.id)}))
        upload.chat_id = bot_reply_message.chat.id
        upload.bot_message_id = bot_reply_message.message_id
        database_session.commit()

        await message_queue_publisher_client.publish_message(f"{upload.id}-created")

    @dispatcher.message()
    async def echo_handler(message: Message) -> None:
        await message.reply(get_formatted_message("default", message))

    async def listener(message: IncomingMessage):
        message = message.body.decode("utf-8")
        print(message)
        if not message.endswith("-done"):
            return

        try:
            upload_id = int(message[:message.index("-done")])
        except ValueError:
            return

        upload: Upload = database_session.query(Upload).get(upload_id)
        if upload_id is None:
            return

        await bot.edit_message_text(get_formatted_message("description", None, {
            "description": upload.description,
            "image_url": file_storage.get_file_url(upload.output_image_key)
        }), upload.chat_id, upload.bot_message_id)


    await message_queue_consumer_client.consume_messages(listener)

    await dispatcher.start_polling(bot)

