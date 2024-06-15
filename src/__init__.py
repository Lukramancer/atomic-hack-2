from .database import main as create_database_session
from .s3 import FileStorage
from .bot import main as telegram_bot_main
from .ml import predict


async def main(
        tg_bot_token: str,
        database_driver: str, database_host: str, database_port: int, database_username: str, database_password: str, database_name: str,
        endpoint_url: str, region: str, access_key: str, private_access_key: str, bucket_name: str
):
    database_session = create_database_session(database_driver, database_host, database_port, database_username, database_password, database_name)
    file_storage = FileStorage(endpoint_url, region, access_key, private_access_key, bucket_name)
    await telegram_bot_main(tg_bot_token, file_storage, database_session, predict)
