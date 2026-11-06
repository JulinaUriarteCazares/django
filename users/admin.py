from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


# UserAdmin hashea la contraseña; con admin.site.register(User) se guardaría en texto plano.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'telefono', 'is_staff')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('telefono',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {'fields': ('email', 'telefono')}),
    )
