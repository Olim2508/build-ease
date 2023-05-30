###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.6-alpine as builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG TEMP_PATH=/usr/src/web

RUN apk update  \
    # install psycopg2 dependencies
    && apk add postgresql-dev gcc python3-dev musl-dev openssl libffi-dev openssl-dev  \
    # install Pillow dependencies \
    # libpq jpeg-dev zlib-dev libjpeg \
    # freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev


#RUN apk update  \
#    && apk add postgresql-dev gcc musl-dev python3-dev zlib-dev jpeg-dev freetype-dev libjpeg-turbo-dev libpng-dev \
#    libffi-dev

# lint
RUN pip install --upgrade pip
RUN pip install flake8==3.9.2
# RUN flake8 --ignore=E501,F401,E302,E122,E231,E261 .

# install dependencies
COPY ./web/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir $TEMP_PATH/wheels -r ./requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9.6-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add --no-cache postgresql-dev curl \
    gcc musl-dev jpeg-dev zlib-dev libpq libjpeg \
    freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev
COPY --from=builder /usr/src/web/wheels /wheels
COPY --from=builder ./requirements.txt .
RUN pip install --no-cache /wheels/*

# copy entrypoint.prod.sh
COPY ./web/entrypoint.prod.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.prod.sh
RUN chmod +x  $APP_HOME/entrypoint.prod.sh

# copy project
COPY ./web $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.prod.sh
ENTRYPOINT ["/home/app/web/entrypoint.prod.sh"]
