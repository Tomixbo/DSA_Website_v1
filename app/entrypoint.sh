#!/bin/sh

# Stop the script if any command fails
set -e

# Navigate to the project directory
cd /src/DSA_Website_v1

# Check if the repository exists and pull the latest changes
if [ -d ".git" ]; then
    echo "Pulling the latest changes from Git..."
    git fetch origin main
    git reset --hard origin/main
else
    echo "Git repository not initialized. Skipping git pull."
fi

# Navigate to the project directory
cd /src/DSA_Website_v1/local_contest

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser if necessary
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating Django superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn to serve the application
exec gunicorn local_contest.wsgi:application --bind 0.0.0.0:8000
