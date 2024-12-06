import django.contrib.auth.models as authmodels
import re
import random


def get_user_name(email):
    username = email.split('@')[0].lower().replace('.', '').replace('+', '')
    if re.match('^[0-9]+$', username):
        username = "user" + username

    if len(username) > 20:
        username = username[:20]
    username = username + str(random.randrange(1000, 9999))
    return username


def get_or_create_user(email):
    """
    Utility to get or create a user by email.
    If the user does not exist, it creates a new user.
    """
    try:
        user = authmodels.User.objects.get(email=email)
    except authmodels.User.DoesNotExist:
        username = get_user_name(email)
        user = authmodels.User.objects.create(
            email=email,
            username=username,
            is_active=True
        )
    return user