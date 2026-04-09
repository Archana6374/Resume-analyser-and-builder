from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'template', 'user', 'created_at')
    search_fields = ('name', 'email', 'skills')
    list_filter = ('template', 'created_at')
