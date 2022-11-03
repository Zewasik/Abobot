FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get -y update
RUN apt-get install -y ffmpeg
COPY . .
CMD [ "python3", "main.py"]