# Use an official Python runtime based on Debian 10 "buster" as a parent image.
# FROM python:3.8-slim-buster
FROM python:3.8-buster

# Add user that will be used in the container.
# RUN useradd -u 5678 wagtail

# set work directory
WORKDIR /usr/src/app

# Set these directories to be owned by the "wagtail" user.
# RUN chown -R wagtail /usr/src/app
# RUN chown -R wagtail /usr/local/lib/python3.8/site-packages

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH /usr/src/app/node_modules/.bin:$PATH
ENV ENV_PATH .envs/.dev.env
ENV PGPASSWORD wagtail_dev_password

# install system dependencies
RUN apt update -y \
    && apt -y install netcat postgresql postgresql-contrib postgis libpq-dev \
    && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install pip-tools
COPY ./requirements.in .
COPY ./requirements.txt .
RUN pip-compile requirements.in
RUN pip-sync

# install Node.js dependencies
RUN curl -sL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt install nodejs -y
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt update -q && apt install yarn -y
RUN npm install -g gulp-cli concurrently sass maildev browser-sync prettier doctoc
COPY package.json .
COPY yarn.lock .
COPY gulpfile.js .
RUN yarn install && gulp cp

# .env files
RUN mkdir -p /usr/src/app/.envs/
COPY ./.envs/.dev.env.sample .envs/.dev.env
COPY ./.envs/.test.env.sample .envs/.test.env

# Postgres Entrypoint
COPY ./entrypoint.sh .
# process the line endings of the shell scripts & convert Windows line endings to UNIX line endings.
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh

# change to the wagtail user
# USER wagtail

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
