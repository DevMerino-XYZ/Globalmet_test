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
    """
    Get the current date in America/Hermosillo timezone.
    
    This function returns the current date in the configured timezone
    for the weather station location. It ensures consistent date handling
    across the application.
    
    Returns:
        str: Current date in YYYY-MM-DD format
    """
    hermosillo_tz = pytz.timezone(DEFAULT_TIMEZONE)
    current_date = timezone.now().astimezone(hermosillo_tz).date()
    return current_date.strftime('%Y-%m-%d')


def validate_date_format(date_str):
    """
    Validate if a date string matches the expected YYYY-MM-DD format.
    
    This function checks if the provided date string can be parsed
    using the standard ISO date format. It's used for input validation
    throughout the API.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid format or None/empty, False otherwise
    """
    if not date_str:
        return True  # None/empty is valid (uses current date)
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_temperature_unit(unit):
    """
    Validate if a temperature unit is supported.
    
    This function checks if the provided unit is one of the supported
    temperature units for conversion operations.
    
    Args:
        unit: Temperature unit to validate
        
    Returns:
        bool: True if valid unit, False otherwise
    """
    return unit.lower() in ['celsius', 'fahrenheit', 'kelvin']


def get_temperature_symbol(unit):
    """
    Get the display symbol for a temperature unit.
    
    This function returns the appropriate symbol (°C, °F, K) for
    displaying temperature values in the user interface.
    
    Args:
        unit: Temperature unit name
        
    Returns:
        str: Temperature symbol for display
    """
    return TEMPERATURE_SYMBOLS.get(unit.lower(), '°C')


def safe_float_conversion(value):
    """
    Safely convert a value to float with error handling.
    
    This function attempts to convert various data types to float,
    returning None if the conversion fails. It's used to handle
    potentially invalid or missing data from the API.
    
    Args:
        value: Value to convert to float
        
    Returns:
        float or None: Converted value or None if conversion fails
    """
    if value is None:
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def calculate_average(values):
    """
    Calculate the arithmetic mean of a list of numeric values.
    
    This function computes the average of a list of numbers,
    handling empty lists gracefully by returning None.
    
    Args:
        values: List of numeric values
        
    Returns:
        float or None: Average value or None if no valid values
    """
    if not values:
        return None
    
    return sum(values) / len(values)


def format_filename(base_name, date_str=None):
    """
    Format a filename for CSV export files.
    
    This function creates standardized filenames for exported CSV files,
    incorporating the base name and date information for easy identification.
    
    Args:
        base_name: Base filename without extension
        date_str: Date string or None for current date
        
    Returns:
        str: Formatted filename with .csv extension
    """
    fecha = date_str if date_str else 'hoy'
    return f"{base_name}_{fecha}.csv" 