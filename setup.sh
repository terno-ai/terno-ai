#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Apply database migrations
echo "Applying database migrations..."
python /code/mysite/manage.py migrate

# Collect static files
echo "Collecting static files..."
python /code/mysite/manage.py collectstatic --noinput

# Check if superuser exists
export DJANGO_SUPERUSER_PASSWORD=Superadmin@123
echo -e "Your username: ${CYAN}admin${NC} password:" ${CYAN}$DJANGO_SUPERUSER_PASSWORD${NC}

if python /code/mysite/manage.py shell -c 'from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())' | grep -iq "false"; then
    # Create superuser
    echo "Creating superuser..."
    python /code/mysite/manage.py createsuperuser --username "admin" --email "admin@example.com" --noinput
else
    echo "Superuser already exists."
fi
