"""Django admin module."""
from django.contrib import admin

from .models import ConnectionRate


class ConnectionRateAdmin(admin.ModelAdmin):
    """Admin class for model ConnectionRate."""
    list_display = ('from_time', 'to_time', 'standing_rate', 'minute_rate')
    ordering = ['id']


admin.site.register(ConnectionRate, ConnectionRateAdmin)
