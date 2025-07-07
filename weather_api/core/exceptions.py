"""
Custom Exceptions for Weather API

This module defines custom exceptions used throughout the weather API application.
All exceptions inherit from WeatherAPIException for consistent error handling.
"""


class WeatherAPIException(Exception):
    """
    Base exception for all weather API errors.
    
    This is the parent class for all custom exceptions in the weather API.
    It provides a consistent interface for error handling across the application.
    """
    pass


class InvalidDateFormatException(WeatherAPIException):
    """
    Raised when a date string doesn't match the expected YYYY-MM-DD format.
    
    This exception is thrown when user input contains invalid date formats
    or when date validation fails during API requests.
    """
    def __init__(self, date_str):
        self.date_str = date_str
        super().__init__(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


class InvalidTemperatureUnitException(WeatherAPIException):
    """
    Raised when an invalid temperature unit is provided.
    
    Valid units are: celsius, fahrenheit, kelvin.
    This exception helps ensure temperature conversions use only supported units.
    """
    def __init__(self, unit):
        self.unit = unit
        super().__init__(f"Invalid temperature unit: {unit}. Must be celsius, fahrenheit, or kelvin")


class GlobalMetAPIException(WeatherAPIException):
    """
    Raised when the external GlobalMet API returns an error or is unavailable.
    
    This exception wraps HTTP errors, timeouts, and other issues that occur
    when communicating with the GlobalMet weather service.
    """
    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(f"GlobalMet API error: {message}")


class NoDataFoundException(WeatherAPIException):
    """
    Raised when no weather measurements are found for the requested date.
    
    This typically occurs when requesting data for dates that don't exist
    in the GlobalMet database or when the API returns empty results.
    """
    def __init__(self, date_str):
        self.date_str = date_str
        super().__init__(f"No measurements found for date: {date_str}")


class DataProcessingException(WeatherAPIException):
    """
    Raised when there's an error processing weather data.
    
    This exception covers errors in statistical calculations, data parsing,
    or any other data manipulation operations.
    """
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(f"Data processing error: {message}")


class TemperatureConversionException(WeatherAPIException):
    """
    Raised when temperature unit conversion fails.
    
    This exception is thrown when mathematical operations during temperature
    conversion encounter errors or invalid input values.
    """
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit
        super().__init__(f"Failed to convert temperature {value} to {unit}")


class CSVExportException(WeatherAPIException):
    """
    Raised when CSV file generation or export operations fail.
    
    This covers errors in CSV formatting, file writing, or data serialization
    during export operations.
    """
    def __init__(self, message):
        super().__init__(f"CSV export error: {message}") 