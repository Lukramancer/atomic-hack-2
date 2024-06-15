from botocore.config import Config
from boto3 import client

from random import sample
from string import ascii_letters


class FileStorage:
    def __init__(self, endpoint_url: str, region: str, access_key: str, private_access_key: str, bucket_name: str, key_length: int = 40):
        self.endpoint_url = endpoint_url
        self.region = region
        self.access_key = access_key
        self.private_access_key = private_access_key
        self.bucket_name = bucket_name

        self.key_length = key_length

        self.client = client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.private_access_key,
            config=Config(s3={"addressing_style": "path"})
        )

    def generate_key(self, suffix: str = "") -> str:
        return str().join(sample(list(ascii_letters), self.key_length)) + suffix

    def upload_file(self, file, suffix: str = "") -> str:
        key = self.generate_key(suffix)
        self.client.upload_fileobj(file, self.bucket_name, key)
        return key

    def get_file_url(self, file_key: str) -> str:
        return f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
