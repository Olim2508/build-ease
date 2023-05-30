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
python web/manage.py wait_for_db

echo "COLLECT STATIC"
python web/manage.py collectstatic --no-input

echo "MIGRATE"
python web/manage.py migrate

exec "$@"