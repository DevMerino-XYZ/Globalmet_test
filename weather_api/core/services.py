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
    def __init__(self):
        """Initialize the GlobalMet API client with configuration settings."""
        self.base_url = settings.GLOBALMET_API_URL
        self.token = settings.GLOBALMET_API_TOKEN
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
    
    def get_measurements_by_date(self, date_str: Optional[str] = None) -> Dict:
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
    @staticmethod
    def calculate_statistics(measurements: List[Dict], field: str) -> Dict:
        if not measurements:
            raise NoDataFoundException("No measurements provided")
        values_with_timestamps = []
        for measurement in measurements:
            if field in measurement and measurement[field] is not None:
                value = safe_float_conversion(measurement[field])
                if value is not None:
                    timestamp = measurement.get('fecha_medicion', None)
                    values_with_timestamps.append((value, timestamp))
        
        if not values_with_timestamps:
            return {
                'min': None,
                'max': None,
                'promedio': None,
                'min_time': None,
                'max_time': None
            }
        
        try:
            # Separar valores y timestamps
            values = [item[0] for item in values_with_timestamps]
            
            # Encontrar min y max con sus timestamps
            min_value = min(values)
            max_value = max(values)
            
            # Encontrar timestamps correspondientes
            min_timestamp = None
            max_timestamp = None
            
            for value, timestamp in values_with_timestamps:
                if value == min_value and min_timestamp is None:
                    min_timestamp = timestamp
                if value == max_value and max_timestamp is None:
                    max_timestamp = timestamp
            
            # Formatear timestamps
            from ..utils.helpers import extract_time_from_timestamp
            
            return {
                'min': min_value,
                'max': max_value,
                'promedio': calculate_average(values),
                'min_time': extract_time_from_timestamp(min_timestamp),
                'max_time': extract_time_from_timestamp(max_timestamp)
            }
        except Exception as e:
            raise DataProcessingException(f"Error calculating statistics for {field}: {str(e)}", field)
    
    @staticmethod
    def convert_temperature(temp_celsius: Optional[float], unit: str) -> Optional[float]:

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
        if not validate_temperature_unit(unit):
            raise InvalidTemperatureUnitException(unit)
        
        if not stats.get('min') and not stats.get('max') and not stats.get('promedio'):
            return stats
        
        return {
            'min': WeatherDataProcessor.convert_temperature(stats.get('min'), unit),
            'max': WeatherDataProcessor.convert_temperature(stats.get('max'), unit),
            'promedio': WeatherDataProcessor.convert_temperature(stats.get('promedio'), unit)
        } 