from django.contrib import admin
from main.models import Experience, Achievement, Project
from main.permissions import (
    can_create_content,
    can_delete_content,
    can_update_content,
)


class PortfolioAuthorizationAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return can_create_content(request.user)

    def has_change_permission(self, request, obj=None):
        return can_update_content(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_delete_content(request.user)


admin.site.register(Experience, PortfolioAuthorizationAdmin)
admin.site.register(Achievement, PortfolioAuthorizationAdmin)
admin.site.register(Project, PortfolioAuthorizationAdmin)
