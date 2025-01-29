from django.contrib import admin
from .models import OpenAIPricing, LLMCredit


class OpenAIPricingAdmin(admin.ModelAdmin):
    list_display = ('token_type', 'model_name', 'price_per_1ktoken', 'created_at', 'updated_at')

    def has_change_permission(self, request, obj=None):
        # Only allow superusers to view or change the model in admin
        return request.user.is_superuser

    def has_add_permission(self, request):
        # Only allow superusers to add a new record
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only allow superusers to delete a record
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


# Register the model in the admin site
admin.site.register(OpenAIPricing, OpenAIPricingAdmin)