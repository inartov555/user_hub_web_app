from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profile", {"fields": ("avatar", "phone", "city", "last_seen")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "last_seen")
