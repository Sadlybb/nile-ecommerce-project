from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet

from . models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'id', 'first_name', 'last_name',
                    'email', 'is_staff', 'is_superuser']
    list_editable = ['is_staff', 'is_superuser']
    list_per_page = 10
    list_filter = ['is_staff', 'is_superuser']
    search_fields = ['first_name', 'lastname', 'username', 'email']
