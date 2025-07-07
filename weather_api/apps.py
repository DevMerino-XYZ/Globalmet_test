"""
Weather API Django Application Configuration

This module contains the Django application configuration for the weather API.
It defines the app name and default field configuration for the Django project.
"""

from django.apps import AppConfig


class WeatherApiConfig(AppConfig):
    """
    Django application configuration for the weather API.
    
    This class configures the weather API Django application with
    appropriate settings for auto-generated fields and app identification.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "weather_api"
