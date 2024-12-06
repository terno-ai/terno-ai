import django.contrib.auth.models as authmodels


def get_or_create_user(email):
    """
    Utility to get or create a user by email.
    If the user does not exist, it creates a new user.
    """
    try:
        user = authmodels.User.objects.get(email=email)
    except authmodels.User.DoesNotExist:
        user = authmodels.User.objects.create(
            email=email,
            username=email.split('@')[0],  # Generate a username from the email
            is_active=True  # Optionally set as active
        )
    return user