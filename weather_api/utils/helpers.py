"""
Weather API Utility Functions

This module contains utility functions used throughout the weather API application.
It provides helper functions for date handling, validation, data conversion,
and file operations.
"""

from datetime import datetime
from django.utils import timezone
import pytz
from ..core.constants import DEFAULT_TIMEZONE, TEMPERATURE_SYMBOLS


def get_current_date_hermosillo():
    hermosillo_tz = pytz.timezone(DEFAULT_TIMEZONE)
    current_date = timezone.now().astimezone(hermosillo_tz).date()
    return current_date.strftime('%Y-%m-%d')

def format_timestamp_for_chart(timestamp):
    if not timestamp:
        return ""
    try:
        # If it's already a datetime object
        if isinstance(timestamp, datetime):
            dt = timestamp
        else:
            # Try to parse string timestamp
            # Handle common formats from GlobalMet API
            if 'T' in str(timestamp):
                # ISO format: 2023-01-01T14:30:00
                dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
            else:
                # Try other common formats
                dt = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
        
        # Convert to Hermosillo timezone
        hermosillo_tz = pytz.timezone(DEFAULT_TIMEZONE)
        if dt.tzinfo is None:
            dt = hermosillo_tz.localize(dt)
        else:
            dt = dt.astimezone(hermosillo_tz)
        
        return dt.strftime('%d/%m/%Y %H:%M')
    except (ValueError, TypeError, AttributeError):
        return str(timestamp)


def extract_time_from_timestamp(timestamp):
    if not timestamp:
        return "--"
    try:
        if isinstance(timestamp, datetime):
            dt = timestamp
        else:
            # Try to parse string timestamp
            if 'T' in str(timestamp):
                # ISO format: 2023-01-01T14:30:00
                dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
            else:
                # Try other common formats
                dt = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
        
        # Convert to Hermosillo timezone
        hermosillo_tz = pytz.timezone(DEFAULT_TIMEZONE)
        if dt.tzinfo is None:
            dt = hermosillo_tz.localize(dt)
        else:
            dt = dt.astimezone(hermosillo_tz)
        
        return dt.strftime('%H:%M')
    except (ValueError, TypeError, AttributeError):
        return "--"


def validate_date_format(date_str):
    if not date_str:
        return True  # None/empty is valid (uses current date)
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_temperature_unit(unit):
    return unit.lower() in ['celsius', 'fahrenheit', 'kelvin']

def get_temperature_symbol(unit):

    return TEMPERATURE_SYMBOLS.get(unit.lower(), '°C')


def safe_float_conversion(value):
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def calculate_average(values):
    if not values:
        return None
    
    return sum(values) / len(values)


def format_filename(base_name, date_str=None):
    fecha = date_str if date_str else 'hoy'
    return f"{base_name}_{fecha}.csv" 
