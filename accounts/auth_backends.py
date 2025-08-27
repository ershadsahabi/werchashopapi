# accounts/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, identifier=None, **kwargs):
        User = get_user_model()
        login_value = identifier or email or username
        if not login_value or not password:
            return None
        try:
            user = User.objects.get(
                Q(email__iexact=login_value) | Q(username__iexact=login_value)
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
