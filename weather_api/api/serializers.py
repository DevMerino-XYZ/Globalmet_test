"""
Weather API Serializers

This module contains Django REST Framework serializers for the weather API.
Serializers handle data validation, serialization, and deserialization
for API requests and responses.
"""

from rest_framework import serializers


class StatisticsSerializer(serializers.Serializer):
    """
    Serializer for basic weather statistics.
    
    This serializer handles the standard statistical output format
    used across all weather parameters (min, max, average).
    """
    min = serializers.FloatField(allow_null=True)
    max = serializers.FloatField(allow_null=True)
    promedio = serializers.FloatField(allow_null=True)


class TemperatureStatisticsSerializer(StatisticsSerializer):
    """
    Serializer for temperature statistics with unit information.
    
    Extends the basic statistics serializer to include temperature
    unit information for proper display and interpretation.
    """
    unidad = serializers.CharField(max_length=10, required=False)


class DailySummarySerializer(serializers.Serializer):
    """
    Serializer for daily weather summary containing all parameters.
    
    This serializer structures the complete daily weather summary
    with statistics for all measured parameters.
    """
    temperatura = StatisticsSerializer()
    humedad = StatisticsSerializer()
    viento = StatisticsSerializer()
    rafaga = StatisticsSerializer()
    presion = StatisticsSerializer()


class ErrorSerializer(serializers.Serializer):
    """
    Serializer for API error responses.
    
    Provides a consistent structure for error messages across
    all API endpoints, including optional details and timestamps.
    """
    error = serializers.CharField()
    details = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(required=False)


class WeatherQuerySerializer(serializers.Serializer):
    """
    Serializer for basic weather query parameters.
    
    Handles validation of common query parameters used across
    multiple weather API endpoints, particularly date validation.
    """
    dia = serializers.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        help_text="Date in YYYY-MM-DD format"
    )
    
    def validate_dia(self, value):
        """
        Validate that the requested date is not in the future.
        
        This validation ensures users cannot request weather data
        for dates that haven't occurred yet.
        """
        from datetime import date
        if value and value > date.today():
            raise serializers.ValidationError("Date cannot be in the future")
        return value


class TemperatureQuerySerializer(WeatherQuerySerializer):
    """
    Serializer for temperature-specific query parameters.
    
    Extends the basic weather query serializer to include
    temperature unit selection for conversion operations.
    """
    unidad = serializers.ChoiceField(
        choices=['celsius', 'fahrenheit', 'kelvin'],
        default='celsius',
        help_text="Temperature unit"
    )


class CSVExportQuerySerializer(TemperatureQuerySerializer):
    """
    Serializer for CSV export query parameters.
    
    Currently identical to TemperatureQuerySerializer but provides
    a separate class for potential future CSV-specific validations.
    """
    pass


class MeasurementSerializer(serializers.Serializer):
    """
    Serializer for individual weather measurements.
    
    This serializer handles the structure of individual weather
    measurement records from the GlobalMet API, including all
    measured parameters and optional timestamp information.
    """
    temperatura_c = serializers.FloatField(allow_null=True)
    humedad_relativa = serializers.FloatField(allow_null=True)
    viento_kmh = serializers.FloatField(allow_null=True)
    viento_rafaga_kmh = serializers.FloatField(allow_null=True)
    presion_mb = serializers.FloatField(allow_null=True)
    timestamp = serializers.DateTimeField(required=False)
    
    class Meta:
        # Allow additional fields from the API
        extra_kwargs = {
            'temperatura_c': {'required': False},
            'humedad_relativa': {'required': False},
            'viento_kmh': {'required': False},
            'viento_rafaga_kmh': {'required': False},
            'presion_mb': {'required': False},
        } 