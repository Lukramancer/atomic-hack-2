from io import BytesIO
from typing import Callable, Any

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.orm import Session

from src.database import Upload, register_user_if_not_exists, User
from src.s3 import FileStorage
from .messages import get_formatted_message


async def main(token: str, file_storage: FileStorage, database_session: Session, predict: Callable[[Any], tuple[BytesIO, str]]):
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

        image_file_buffer, second_image_file_buffer = BytesIO(), BytesIO()
        await bot.download(message.photo[-1], destination=image_file_buffer)
        key = file_storage.upload_file(image_file_buffer)

        upload = Upload(user_id=user_id, input_image_key=key)
        database_session.add(upload)
        database_session.commit()

        bot_reply_message = await message.reply(get_formatted_message("uploaded", message, {"upload_id": str(upload.id)}))

        await bot.download(message.photo[-1], destination=second_image_file_buffer)
        highlighted_image_file_buffer, description = predict(second_image_file_buffer)

        highlighted_image_file_buffer.seek(0)
        highlighted_image_file_key = file_storage.upload_file(highlighted_image_file_buffer, ".jpg")

        upload.description = description
        upload.output_image_key = highlighted_image_file_key
        database_session.commit()

        await message.reply(file_storage.get_file_url(highlighted_image_file_key))
        await bot_reply_message.edit_text(get_formatted_message("description", message, {"description": description}))

    @dispatcher.message()
    async def echo_handler(message: Message) -> None:
        await message.reply(get_formatted_message("default", message))

    await dispatcher.start_polling(bot)
