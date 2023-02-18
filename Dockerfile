# syntax = docker/dockerfile:1.2
FROM python:3.8-slim-buster
# Updating and installing dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get -y update && \
    apt-get install -y ffmpeg --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
# Creating Virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
# Activating Virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Installing requirements in venv
COPY requirements.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r /tmp/requirements.txt
# Creating APP_USER
ARG APP_USER=appuser
ARG APP_USER_UID=15000
ARG APP_GROUP_GID=15001
ARG APP_ROOT=/home/${APP_USER}/app
RUN groupadd -g ${APP_GROUP_GID} ${APP_USER} && \
   useradd --create-home -u ${APP_USER_UID} -g ${APP_GROUP_GID} ${APP_USER}
# Copying application
WORKDIR ${APP_ROOT}
COPY --chown=${APP_USER}:${APP_USER} . ${APP_ROOT}
# Passing secrets
RUN --mount=type=secret,id=bot_env,required=true \
    (cat /run/secrets/bot_env) > ${APP_ROOT}/.env && \
    chown ${APP_USER_UID}:${APP_GROUP_GID} ${APP_ROOT}/.env
# Running application as APP_USER
USER ${APP_USER}:${APP_USER}
CMD ["python3", "main.py"]
