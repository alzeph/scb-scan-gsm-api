from django.contrib import admin
from auths.models import User, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')
