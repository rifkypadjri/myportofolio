from main.permissions import (
    can_create_content,
    can_delete_content,
    can_update_content,
)


def authorization_flags(request):
    """Expose the centralized content authorization policy to templates."""
    user = request.user
    return {
        "can_create_content": can_create_content(user),
        "can_update_content": can_update_content(user),
        "can_delete_content": can_delete_content(user),
    }
