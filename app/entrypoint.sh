#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# python manage.py makemigrations --settings=config.settings.dev
# python manage.py migrate --settings=config.settings.dev
python manage.py makemigrations --noinput
python manage.py migrate

exec "$@"
