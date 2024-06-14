from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.orm import Session

from src.database import Upload, register_user_if_not_exists
from src.s3 import FileStorage
from .messages import get_formatted_message


async def main(token: str, file_storage: FileStorage, database_session: Session):
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        user_id = message.from_user.id
        register_user_if_not_exists(database_session, user_id)

        await message.reply(get_formatted_message("hello", message))

    @dispatcher.message(F.photo)
    async def on_photo_handler(message: Message) -> None:
        user_id = message.from_user.id
        register_user_if_not_exists(database_session, user_id)

        bytes_buffer = BytesIO()
        await bot.download(message.photo[-1], destination=bytes_buffer)
        key = file_storage.upload_file(bytes_buffer)
        upload = Upload(user_id=user_id, input_image_key=key)
        database_session.add(upload)
        database_session.commit()
        await message.reply(get_formatted_message("uploaded", message, {"upload_id": str(upload.id)}))

    @dispatcher.message()
    async def echo_handler(message: Message) -> None:
        await message.reply(get_formatted_message("default", message))

    await dispatcher.start_polling(bot)

