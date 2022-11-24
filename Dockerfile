FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \ 
    rm requirements.txt && \
    apt-get -y update && \
    apt-get install -y ffmpeg --no-install-recommends
COPY . .
CMD [ "python3", "main.py"]