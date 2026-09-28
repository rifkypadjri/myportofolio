from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


EDITOR_GROUP_NAME = "Editor"


def is_editor(user):
    """Return whether an authenticated user belongs to the Editor group."""
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP_NAME).exists()


def can_create_content(user):
    return user.is_authenticated and user.is_superuser


def can_update_content(user):
    return user.is_authenticated and (user.is_superuser or is_editor(user))


def can_delete_content(user):
    return user.is_authenticated and user.is_superuser


def role_required(check):
    """Require login, then return HTTP 403 when the user's role is insufficient."""

    def decorator(view_func):
        @login_required(login_url="main:login")
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


superuser_create_required = role_required(can_create_content)
superuser_delete_required = role_required(can_delete_content)
editor_or_superuser_required = role_required(can_update_content)
