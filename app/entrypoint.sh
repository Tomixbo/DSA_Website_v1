#!/bin/sh

# Stop the script if any command fails
set -e

# Check if the repository exists and pull the latest changes
if [ -d ".git" ]; then
    echo "Pulling the latest changes from Git..."
    git fetch origin main
    git reset --hard origin/main
else
    echo "Git repository not initialized. Skipping git pull."
fi

# Installer les dépendances
pip install -r requirements.txt

# Navigate to the project directory
cd /src/DSA_Website_v1/local_contest

# Apply migrations safely
echo "Applying database migrations..."
if ! python manage.py makemigrations; then
    echo "Failed to generate migrations. Exiting..."
    exit 1
fi
if ! python manage.py makemigrations attendance; then
    echo "Failed to generate migrations. Exiting..."
    exit 1
fi
if ! python manage.py migrate; then
    echo "Failed to apply migrations. Exiting..."
    exit 1
fi

# Collect static files
python manage.py collectstatic --noinput

# Create a superuser if necessary
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating Django superuser..."
    python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn to serve the application
echo "Starting Gunicorn server..."
exec gunicorn local_contest.wsgi:application --bind 0.0.0.0:8000
