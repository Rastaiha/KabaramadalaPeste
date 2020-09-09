# pull official base image
FROM python:3.7.4-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
# install python-dev
#RUN apk update \
#    && apk add --virtual .build-deps gcc libc-dev libxslt-dev
#    && apk add --no-cache libxslt \
#    && pip install lxml==4.5.0

RUN apk update

RUN  apk add --virtual .build-deps gcc libc-dev libxslt-dev \
    && apk add libffi-dev openssl-dev

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install zlib for pillow
RUN apk add --no-cache jpeg-dev zlib-dev

# install dependencies
RUN pip install --upgrade pip

# copy entrypoint-prod.sh
COPY ./entrypoint.prod.sh /usr/src/app/entrypoint.prod.sh

# copy requirements
COPY requirements.txt /usr/src/requirements.txt

RUN pip install -r /usr/src/requirements.txt

# copy project
COPY . /usr/src/app/

# run entrypoint.prod.sh
ENTRYPOINT ["/usr/src/app/entrypoint.prod.sh"]