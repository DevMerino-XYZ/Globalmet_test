"""
Weather API Services

This module contains the core business logic services for the weather API application.
It includes the GlobalMet API client and weather data processing services.
"""

import requests
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
import pytz
from typing import Dict, List, Optional

from .constants import WEATHER_FIELDS, TEMPERATURE_UNITS
from .exceptions import (
    InvalidDateFormatException,
    InvalidTemperatureUnitException,
    GlobalMetAPIException,
    NoDataFoundException,
    DataProcessingException,
    TemperatureConversionException
)
from ..utils.helpers import (
    get_current_date_hermosillo,
    validate_date_format,
    validate_temperature_unit,
    safe_float_conversion,
    calculate_average
)


class GlobalMetAPIClient:
    """
    Client service for consuming GlobalMet API weather data.
    
    This class handles all communication with the external GlobalMet API,
    including authentication, request formatting, and response processing.
    It provides a clean interface for fetching weather measurements.
    """
    
    def __init__(self):
        """Initialize the GlobalMet API client with configuration settings."""
        self.base_url = settings.GLOBALMET_API_URL
        self.token = settings.GLOBALMET_API_TOKEN
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
    
    def get_measurements_by_date(self, date_str: Optional[str] = None) -> Dict:
        """
        Fetch weather measurements for a specific date from GlobalMet API.
        
        This method makes an HTTP request to the GlobalMet API to retrieve
        weather measurements for the specified date. If no date is provided,
        it uses the current date in America/Hermosillo timezone.
        
        Args:
            date_str: Date in YYYY-MM-DD format. If None, uses current date in America/Hermosillo timezone
            
        Returns:
            Dictionary with measurement data from the API
            
        Raises:
            InvalidDateFormatException: If date format is invalid
            GlobalMetAPIException: If API request fails
        """
        if date_str is None:
            date_str = get_current_date_hermosillo()
        else:
            # Validate date format
            if not validate_date_format(date_str):
                raise InvalidDateFormatException(date_str)
        
        url = f"{self.base_url}?dia={date_str}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            raise GlobalMetAPIException(str(e), status_code)
    
    def get_measurements_list(self, date_str: Optional[str] = None) -> List[Dict]:
        """
        Get weather measurements as a standardized list format.
        
        This method normalizes the API response into a consistent list format,
        regardless of how the external API structures its response data.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            List of measurement dictionaries
        """
        data = self.get_measurements_by_date(date_str)
        
        # The API might return data in different formats, handle both cases
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # If it's a dict, look for common keys that might contain the measurements
            if 'results' in data:
                return data['results']
            elif 'data' in data:
                return data['data']
            elif 'mediciones' in data:
                return data['mediciones']
            else:
                # If it's a single measurement, wrap it in a list
                return [data]
        else:
            return []


class WeatherDataProcessor:
    """
    Service for processing and analyzing weather data.
    
    This class provides statistical analysis capabilities for weather measurements,
    including calculating min/max/average values and temperature unit conversions.
    It handles data validation and error management during processing operations.
    """
    
    @staticmethod
    def calculate_statistics(measurements: List[Dict], field: str) -> Dict:
        """
        Calculate statistical summary (min, max, average) for a specific weather parameter.
        
        This method processes a list of weather measurements and computes
        basic statistical metrics for the specified field. It handles missing
        values and invalid data gracefully.
        
        Args:
            measurements: List of measurement dictionaries
            field: Field name to calculate statistics for
            
        Returns:
            Dictionary with min, max, and promedio (average) values
            
        Raises:
            DataProcessingException: If there's an error processing the data
            NoDataFoundException: If no measurements are provided
        """
        if not measurements:
            raise NoDataFoundException("No measurements provided")
        
        values = []
        
        for measurement in measurements:
            if field in measurement and measurement[field] is not None:
                value = safe_float_conversion(measurement[field])
                if value is not None:
                    values.append(value)
        
        if not values:
            return {
                'min': None,
                'max': None,
                'promedio': None
            }
        
        try:
            return {
                'min': min(values),
                'max': max(values),
                'promedio': calculate_average(values)
            }
        except Exception as e:
            raise DataProcessingException(f"Error calculating statistics for {field}: {str(e)}", field)
    
    @staticmethod
    def convert_temperature(temp_celsius: Optional[float], unit: str) -> Optional[float]:
        """
        Convert temperature from Celsius to the specified unit.
        
        This method performs temperature unit conversion from Celsius to
        Fahrenheit or Kelvin. It validates the target unit and handles
        null values appropriately.
        
        Args:
            temp_celsius: Temperature in Celsius
            unit: Target unit (celsius, fahrenheit, kelvin)
            
        Returns:
            Temperature in specified unit, or None if input is None
            
        Raises:
            InvalidTemperatureUnitException: If unit is invalid
            TemperatureConversionException: If conversion fails
        """
        if not validate_temperature_unit(unit):
            raise InvalidTemperatureUnitException(unit)
        
        if temp_celsius is None:
            return None
        
        try:
            unit_lower = unit.lower()
            if unit_lower == 'celsius':
                return temp_celsius
            elif unit_lower == 'fahrenheit':
                return (temp_celsius * 9/5) + 32
            elif unit_lower == 'kelvin':
                return temp_celsius + 273.15
        except Exception as e:
            raise TemperatureConversionException(temp_celsius, unit)
    
    @staticmethod
    def convert_temperature_stats(stats: Dict, unit: str) -> Dict:
        """
        Convert temperature statistics to the specified unit.
        
        This method applies temperature unit conversion to all statistical
        values (min, max, average) in a statistics dictionary.
        
        Args:
            stats: Statistics dictionary with min, max, promedio
            unit: Target unit for conversion
            
        Returns:
            Converted statistics dictionary
            
        Raises:
            InvalidTemperatureUnitException: If unit is invalid
        """
        if not validate_temperature_unit(unit):
            raise InvalidTemperatureUnitException(unit)
        
        if not stats.get('min') and not stats.get('max') and not stats.get('promedio'):
            return stats
        
        return {
            'min': WeatherDataProcessor.convert_temperature(stats.get('min'), unit),
            'max': WeatherDataProcessor.convert_temperature(stats.get('max'), unit),
            'promedio': WeatherDataProcessor.convert_temperature(stats.get('promedio'), unit)
        } 