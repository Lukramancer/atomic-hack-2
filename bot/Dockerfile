FROM python:3.12
WORKDIR /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-m", "src" ]