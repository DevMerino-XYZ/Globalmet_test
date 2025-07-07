"""
Weather API Constants

This module contains all the constants used throughout the weather API application.
It includes API configuration, field mappings, units, and error messages.
"""

# API Configuration Constants
GLOBALMET_STATION_ID = "689"
DEFAULT_TIMEZONE = "America/Hermosillo"

# Field mappings for GlobalMet API
WEATHER_FIELDS = {
    'temperatura': 'temperatura_c',
    'humedad': 'humedad_relativa',
    'viento': 'viento_kmh',
    'rafaga': 'viento_rafaga_kmh',
    'presion': 'presion_mb'
}

# Temperature units
TEMPERATURE_UNITS = {
    'celsius': 'C',
    'fahrenheit': 'F',
    'kelvin': 'K'
}

# Temperature unit symbols
TEMPERATURE_SYMBOLS = {
    'celsius': '°C',
    'fahrenheit': '°F',
    'kelvin': 'K'
}

# CSV headers for exports
CSV_HEADERS = {
    'statistics': ['Parametro', 'Minimo', 'Maximo', 'Promedio', 'Unidad'],
    'parameter_names': {
        'temperatura': 'Temperatura',
        'humedad': 'Humedad Relativa',
        'viento': 'Viento',
        'rafaga': 'Rafaga de Viento',
        'presion': 'Presion'
    },
    'units': {
        'humedad': '%',
        'viento': 'km/h',
        'rafaga': 'km/h',
        'presion': 'mb'
    }
}

# API Response messages
ERROR_MESSAGES = {
    'invalid_date': 'Date must be in YYYY-MM-DD format',
    'invalid_unit': 'Unit must be celsius, fahrenheit, or kelvin',
    'api_error': 'Error fetching data from GlobalMet API',
    'no_data': 'No measurements found for the specified date',
    'internal_error': 'Internal server error'
} 