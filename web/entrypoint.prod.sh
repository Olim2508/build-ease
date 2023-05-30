#!/bin/sh

#if [ "$DATABASE" = "postgres" ]
#then
#    echo "Waiting for postgres..."
#
#    while ! nc -z $SQL_HOST $SQL_PORT; do
#      sleep 0.1
#    done
#
#    echo "PostgreSQL started"
#fi

echo "WAIT DB"
python manage.py wait_for_db

echo "COLLECT STATIC"
python manage.py collectstatic --no-input

echo "MIGRATE"
python manage.py migrate

exec "$@"