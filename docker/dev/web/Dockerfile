# pull official base image
FROM python:3.9.6-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/usr/src/web

# set work directory
WORKDIR $HOME

# install psycopg2 dependencies
RUN apk update  \
    && apk add postgresql-dev gcc musl-dev python3-dev zlib-dev jpeg-dev freetype-dev libjpeg-turbo-dev libpng-dev \
    libffi-dev


# install dependencies
RUN pip install --upgrade pip
COPY ./web/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

# copy entrypoint.sh
COPY ./web/entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/web/entrypoint.sh
RUN chmod +x /usr/src/web/entrypoint.sh

# copy project
COPY ./web $HOME

# run entrypoint.sh
ENTRYPOINT ["/usr/src/web/entrypoint.sh"]
