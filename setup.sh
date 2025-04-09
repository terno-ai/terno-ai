#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Apply database migrations
echo "Applying database migrations..."
python /code/terno-ai/terno/manage.py migrate

# Collect static files
echo "Collecting static files..."
python /code/terno-ai/terno/manage.py collectstatic --noinput

# Check if superuser exists
export DJANGO_SUPERUSER_PASSWORD=Superadmin@123
echo -e "Your username: ${CYAN}admin${NC} password:" ${CYAN}$DJANGO_SUPERUSER_PASSWORD${NC}

if python /code/terno-ai/terno/manage.py shell -c 'from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())' | grep -iq "false"; then
    # Create superuser
    echo "Creating superuser..."
    python /code/terno-ai/terno/manage.py createsuperuser --username "admin" --email "admin@example.com" --noinput
else
    echo "Superuser already exists."
fi

if python /code/terno-ai/terno/manage.py shell -c "from django.contrib.auth.models import Group; print(Group.objects.filter(name='org_owner').exists())" | grep -iq "false"; then
    #create a default group for organisation owner org_owner
    echo "Creating a default group for organisation owner org_owner"
    python /code/terno-ai/terno/manage.py shell -c 'from terno.utils import create_org_owner_group; create_org_owner_group()'
else
    echo "Group 'org_owner' already exists"
fi