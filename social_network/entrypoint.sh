#!/bin/bash

# Exit on any error
set -e

# Check if MySQL is ready
if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for MySQL..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "MySQL started"
fi

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files (if using AWS S3, this might not be needed locally)
echo "Collecting static files..."
python manage.py collectstatic --noinput


# Start the Gunicorn server
echo "Starting Gunicorn..."
gunicorn social_network.wsgi:application --bind 0.0.0.0:8000 --workers 3
