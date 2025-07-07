"""
Weather API REST Endpoints

This module contains Django REST Framework views for the weather API.
It provides RESTful endpoints for weather data statistics, daily summaries,
and CSV export functionality. All views inherit from BaseWeatherView for
consistent error handling and response formatting.
"""

import csv
import io
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..core.services import GlobalMetAPIClient, WeatherDataProcessor
from .serializers import (
    StatisticsSerializer,
    DailySummarySerializer,
    ErrorSerializer,
    WeatherQuerySerializer,
    TemperatureQuerySerializer,
    CSVExportQuerySerializer
)
from ..core.exceptions import (
    WeatherAPIException,
    InvalidDateFormatException,
    InvalidTemperatureUnitException,
    GlobalMetAPIException,
    NoDataFoundException
)
from ..core.constants import WEATHER_FIELDS, CSV_HEADERS, ERROR_MESSAGES
from ..utils.helpers import get_temperature_symbol, format_filename


class BaseWeatherView(APIView):
    """
    Base view class for all weather-related API endpoints.
    
    This class provides common functionality for weather API endpoints,
    including standardized exception handling and error response formatting.
    All weather API views should inherit from this class.
    """
    
    def handle_exception(self, exc):
        """
        Handle custom weather API exceptions with appropriate HTTP status codes.
        
        This method maps custom weather API exceptions to appropriate HTTP
        status codes and response formats for consistent error handling.
        
        Args:
            exc: Exception instance to handle
            
        Returns:
            Response: HTTP response with appropriate status code and error message
        """
        if isinstance(exc, InvalidDateFormatException):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, InvalidTemperatureUnitException):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, GlobalMetAPIException):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        elif isinstance(exc, NoDataFoundException):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, WeatherAPIException):
            return Response(
                {'error': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return super().handle_exception(exc)


class TemperatureStatisticsView(BaseWeatherView):
    """
    API endpoint for temperature statistics with unit conversion.
    
    This view provides temperature statistics (min, max, average) for a given date
    with optional temperature unit conversion (celsius, fahrenheit, kelvin).
    """
    
    @extend_schema(
        summary="Get temperature statistics",
        description="Returns temperature statistics with optional unit conversion",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
            OpenApiParameter(
                name='unidad',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Temperature unit (celsius, fahrenheit, kelvin)',
                required=False,
                enum=['celsius', 'fahrenheit', 'kelvin']
            ),
        ],
        responses={
            200: StatisticsSerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Get temperature statistics for the specified date and unit.
        
        Retrieves temperature measurements from GlobalMet API and calculates
        statistical summary with optional unit conversion.
        """
        serializer = TemperatureQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        unidad = serializer.validated_data.get('unidad', 'celsius')
        
        # Convert date to string if provided
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        # Get data from GlobalMet API
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        # Calculate statistics
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['temperatura'])
        
        # Convert to requested unit
        if unidad != 'celsius':
            stats = processor.convert_temperature_stats(stats, unidad)
        
        return Response(stats)


class HumidityStatisticsView(BaseWeatherView):
    """
    API endpoint for humidity statistics.
    
    This view provides humidity statistics (min, max, average) for a given date.
    Humidity is measured as relative humidity percentage.
    """
    
    @extend_schema(
        summary="Get humidity statistics",
        description="Returns humidity statistics",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
        ],
        responses={
            200: StatisticsSerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Get humidity statistics for the specified date.
        
        Retrieves humidity measurements from GlobalMet API and calculates
        statistical summary (min, max, average).
        """
        serializer = WeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['humedad'])
        
        return Response(stats)


class WindStatisticsView(BaseWeatherView):
    """
    API endpoint for wind speed statistics.
    
    This view provides wind speed statistics (min, max, average) for a given date.
    Wind speed is measured in kilometers per hour (km/h).
    """
    
    @extend_schema(
        summary="Get wind statistics",
        description="Returns wind speed statistics",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
        ],
        responses={
            200: StatisticsSerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Get wind speed statistics for the specified date.
        
        Retrieves wind speed measurements from GlobalMet API and calculates
        statistical summary (min, max, average).
        """
        serializer = WeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['viento'])
        
        return Response(stats)


class WindGustStatisticsView(BaseWeatherView):
    """
    API endpoint for wind gust statistics.
    
    This view provides wind gust statistics (min, max, average) for a given date.
    Wind gusts represent peak wind speeds measured in kilometers per hour (km/h).
    """
    
    @extend_schema(
        summary="Get wind gust statistics",
        description="Returns wind gust statistics",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
        ],
        responses={
            200: StatisticsSerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """Get wind gust statistics"""
        serializer = WeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['rafaga'])
        
        return Response(stats)


class PressureStatisticsView(BaseWeatherView):
    """
    API endpoint for atmospheric pressure statistics.
    
    This view provides atmospheric pressure statistics (min, max, average) for a given date.
    Pressure is measured in millibars (mb).
    """
    
    @extend_schema(
        summary="Get pressure statistics",
        description="Returns pressure statistics",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
        ],
        responses={
            200: StatisticsSerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Get atmospheric pressure statistics for the specified date.
        
        Retrieves pressure measurements from GlobalMet API and calculates
        statistical summary (min, max, average).
        """
        serializer = WeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['presion'])
        
        return Response(stats)


class DailySummaryView(BaseWeatherView):
    """
    API endpoint for comprehensive daily weather summary.
    
    This view provides a complete daily weather summary including statistics
    for all weather parameters (temperature, humidity, wind, gusts, pressure)
    in a single API call. Temperature units can be converted as needed.
    """
    
    @extend_schema(
        summary="Get daily weather summary",
        description="Returns all weather statistics in a single call",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
            OpenApiParameter(
                name='unidad',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Temperature unit (celsius, fahrenheit, kelvin)',
                required=False,
                enum=['celsius', 'fahrenheit', 'kelvin']
            ),
        ],
        responses={
            200: DailySummarySerializer,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Get comprehensive daily weather summary with all parameters.
        
        Retrieves all weather measurements from GlobalMet API and calculates
        statistics for temperature, humidity, wind, gusts, and pressure.
        """
        serializer = TemperatureQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        unidad = serializer.validated_data.get('unidad', 'celsius')
        
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        
        # Calculate all statistics
        temperatura_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['temperatura'])
        if unidad != 'celsius':
            temperatura_stats = processor.convert_temperature_stats(temperatura_stats, unidad)
        
        humedad_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['humedad'])
        viento_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['viento'])
        rafaga_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['rafaga'])
        presion_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['presion'])
        
        resumen = {
            'temperatura': temperatura_stats,
            'humedad': humedad_stats,
            'viento': viento_stats,
            'rafaga': rafaga_stats,
            'presion': presion_stats
        }
        
        return Response(resumen)


class ExportStatisticsView(BaseWeatherView):
    """
    API endpoint for exporting weather statistics to CSV format.
    
    This view generates a CSV file containing weather statistics summary
    for all parameters. The file can be downloaded directly and includes
    min, max, and average values with appropriate units.
    """
    
    @extend_schema(
        summary="Export statistics to CSV",
        description="Generates CSV file with weather statistics",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
            OpenApiParameter(
                name='unidad',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Temperature unit (celsius, fahrenheit, kelvin)',
                required=False,
                enum=['celsius', 'fahrenheit', 'kelvin']
            ),
        ],
        responses={
            200: OpenApiTypes.BINARY,
            400: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Generate and download CSV file with weather statistics.
        
        Creates a CSV file containing statistical summary of all weather
        parameters with appropriate headers and unit information.
        """
        serializer = CSVExportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        unidad = serializer.validated_data.get('unidad', 'celsius')
        
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        processor = WeatherDataProcessor()
        
        # Calculate all statistics
        temperatura_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['temperatura'])
        if unidad != 'celsius':
            temperatura_stats = processor.convert_temperature_stats(temperatura_stats, unidad)
        
        humedad_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['humedad'])
        viento_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['viento'])
        rafaga_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['rafaga'])
        presion_stats = processor.calculate_statistics(measurements, WEATHER_FIELDS['presion'])
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(CSV_HEADERS['statistics'])
        
        # Write data
        temp_unit = get_temperature_symbol(unidad)
        
        writer.writerow([
            CSV_HEADERS['parameter_names']['temperatura'],
            temperatura_stats['min'],
            temperatura_stats['max'],
            temperatura_stats['promedio'],
            temp_unit
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['humedad'],
            humedad_stats['min'],
            humedad_stats['max'],
            humedad_stats['promedio'],
            CSV_HEADERS['units']['humedad']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['viento'],
            viento_stats['min'],
            viento_stats['max'],
            viento_stats['promedio'],
            CSV_HEADERS['units']['viento']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['rafaga'],
            rafaga_stats['min'],
            rafaga_stats['max'],
            rafaga_stats['promedio'],
            CSV_HEADERS['units']['rafaga']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['presion'],
            presion_stats['min'],
            presion_stats['max'],
            presion_stats['promedio'],
            CSV_HEADERS['units']['presion']
        ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        filename = format_filename('estadisticas', dia_str)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class ExportMeasurementsView(BaseWeatherView):
    """
    API endpoint for exporting raw weather measurements to CSV format.
    
    This view generates a CSV file containing all individual weather measurements
    for a given date. Unlike the statistics export, this includes all raw data
    points with their original timestamps and values.
    """
    
    @extend_schema(
        summary="Export measurements to CSV",
        description="Generates CSV file with all measurements",
        parameters=[
            OpenApiParameter(
                name='dia',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date in YYYY-MM-DD format',
                required=False
            ),
        ],
        responses={
            200: OpenApiTypes.BINARY,
            400: ErrorSerializer,
            404: ErrorSerializer,
            503: ErrorSerializer,
        }
    )
    def get(self, request):
        """
        Generate and download CSV file with all raw weather measurements.
        
        Creates a CSV file containing all individual measurement records
        with timestamps and values for each weather parameter.
        """
        serializer = WeatherQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        dia = serializer.validated_data.get('dia')
        dia_str = dia.strftime('%Y-%m-%d') if dia else None
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia_str)
        
        if not measurements:
            raise NoDataFoundException(dia_str or 'today')
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header based on first measurement keys
        if measurements:
            headers = list(measurements[0].keys())
            writer.writerow(headers)
            
            # Write data
            for measurement in measurements:
                row = [measurement.get(header, '') for header in headers]
                writer.writerow(row)
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        filename = format_filename('mediciones', dia_str)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response 