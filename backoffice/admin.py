from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import AgentProfile, ActivityLog, SystemSettings

class AgentProfileInline(admin.StackedInline):
    model = AgentProfile
    can_delete = False
    verbose_name_plural = 'Profil Agent'

class UserAdmin(BaseUserAdmin):
    inlines = (AgentProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone_number']
    list_editable = ['role', 'is_active']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['agent', 'action', 'description', 'timestamp']
    list_filter = ['action', 'timestamp', 'agent']
    search_fields = ['agent__username', 'description']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False  # Les logs ne peuvent pas être ajoutés manuellement
    
    def has_change_permission(self, request, obj=None):
        return False  # Les logs ne peuvent pas être modifiés

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'description', 'updated_at', 'updated_by']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

