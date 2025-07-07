import requests
from datetime import datetime, date
from django.conf import settings
from django.utils import timezone
import pytz
from typing import Dict, List, Optional


class GlobalMetAPIClient:
    """Client for consuming GlobalMet API data"""
    
    def __init__(self):
        self.base_url = settings.GLOBALMET_API_URL
        self.token = settings.GLOBALMET_API_TOKEN
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
    
    def get_measurements_by_date(self, date_str: Optional[str] = None) -> Dict:
        """
        Get measurements for a specific date
        
        Args:
            date_str: Date in YYYY-MM-DD format. If None, uses current date in America/Hermosillo timezone
            
        Returns:
            Dictionary with measurement data
            
        Raises:
            requests.RequestException: If API request fails
            ValueError: If date format is invalid
        """
        if date_str is None:
            # Get current date in America/Hermosillo timezone
            hermosillo_tz = pytz.timezone('America/Hermosillo')
            current_date = timezone.now().astimezone(hermosillo_tz).date()
            date_str = current_date.strftime('%Y-%m-%d')
        else:
            # Validate date format
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        
        url = f"{self.base_url}?dia={date_str}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching data from GlobalMet API: {str(e)}")
    
    def get_measurements_list(self, date_str: Optional[str] = None) -> List[Dict]:
        """
        Get measurements as a list for easier processing
        
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
    """Process weather data and calculate statistics"""
    
    @staticmethod
    def calculate_statistics(measurements: List[Dict], field: str) -> Dict:
        """
        Calculate min, max, and average for a specific field
        
        Args:
            measurements: List of measurement dictionaries
            field: Field name to calculate statistics for
            
        Returns:
            Dictionary with min, max, and promedio (average)
        """
        values = []
        
        for measurement in measurements:
            if field in measurement and measurement[field] is not None:
                try:
                    value = float(measurement[field])
                    values.append(value)
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return {
                'min': None,
                'max': None,
                'promedio': None
            }
        
        return {
            'min': min(values),
            'max': max(values),
            'promedio': sum(values) / len(values)
        }
    
    @staticmethod
    def convert_temperature(temp_celsius: float, unit: str) -> float:
        """
        Convert temperature from Celsius to specified unit
        
        Args:
            temp_celsius: Temperature in Celsius
            unit: Target unit (celsius, fahrenheit, kelvin)
            
        Returns:
            Temperature in specified unit
        """
        if unit.lower() == 'celsius':
            return temp_celsius
        elif unit.lower() == 'fahrenheit':
            return (temp_celsius * 9/5) + 32
        elif unit.lower() == 'kelvin':
            return temp_celsius + 273.15
        else:
            raise ValueError("Unit must be 'celsius', 'fahrenheit', or 'kelvin'")
    
    @staticmethod
    def convert_temperature_stats(stats: Dict, unit: str) -> Dict:
        """
        Convert temperature statistics to specified unit
        
        Args:
            stats: Statistics dictionary with min, max, promedio
            unit: Target unit
            
        Returns:
            Converted statistics dictionary
        """
        if not stats['min'] or not stats['max'] or not stats['promedio']:
            return stats
        
        return {
            'min': WeatherDataProcessor.convert_temperature(stats['min'], unit),
            'max': WeatherDataProcessor.convert_temperature(stats['max'], unit),
            'promedio': WeatherDataProcessor.convert_temperature(stats['promedio'], unit)
        } 