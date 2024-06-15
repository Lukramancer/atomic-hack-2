from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse

from .database import main as database_main, Upload, Attachment
from .s3 import FileStorage

from dotenv import load_dotenv

load_dotenv()

S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME = \
    getenv("S3_URL"), getenv("S3_REGION"), getenv("S3_ACCESS_KEY"), getenv("S3_SECRET_ACCESS_KEY"), getenv(
        "S3_BUCKET_NAME")
DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME = \
    getenv("DATABASE_DRIVER"), getenv("DATABASE_HOST"), int(getenv("DATABASE_PORT")), getenv("DATABASE_USER"), getenv(
        "DATABASE_PASSWORD"), getenv("DATABASE_DBNAME")


database_session = database_main(DATABASE_DRIVER, DATABASE_HOST, DATABASE_PORT, DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME)
file_storage = FileStorage(S3_URL, S3_REGION, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME)
app = FastAPI()


def dictify(row) -> dict:
    return {column_name.name: getattr(row, column_name.name) for column_name in row.__table__.columns}


app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.post("/api/uploads/{upload_id}/attachments")
async def get_attachments(upload_id: int):
    attachments = database_session.query(Attachment).where(Attachment.upload_id == upload_id).all()
    return list(map(dictify, attachments))


@app.post("/api/uploads/{upload_id}")
async def get_upload(upload_id: int):
    upload = database_session.query(Upload).get(upload_id)

    if upload is None:
        return None

    upload_data = dictify(upload)
    upload_data["attachments"] = await get_attachments(upload_id)
    return upload_data


@app.post("/api/get_uploads")
async def get_uploads(user_id: int):
    uploads_ids = database_session.query(Upload.id).where(Upload.user_id == user_id).all()
    results = list()
    for upload_id in uploads_ids:
        results.append(await get_upload(upload_id[0]))
    return results


@app.get("/resource/{file_key}")
async def get_resource(file_key: str):
    return RedirectResponse(file_storage.get_file_url(file_key))
