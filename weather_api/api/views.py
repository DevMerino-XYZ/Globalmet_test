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
            temperatura_stats['min_time'],
            temperatura_stats['max'],
            temperatura_stats['max_time'],
            temperatura_stats['promedio'],
            temp_unit
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['humedad'],
            humedad_stats['min'],
            humedad_stats['min_time'],
            humedad_stats['max'],
            humedad_stats['max_time'],
            humedad_stats['promedio'],
            CSV_HEADERS['units']['humedad']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['viento'],
            viento_stats['min'],
            viento_stats['min_time'],
            viento_stats['max'],
            viento_stats['max_time'],
            viento_stats['promedio'],
            CSV_HEADERS['units']['viento']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['rafaga'],
            rafaga_stats['min'],
            rafaga_stats['min_time'],
            rafaga_stats['max'],
            rafaga_stats['max_time'],
            rafaga_stats['promedio'],
            CSV_HEADERS['units']['rafaga']
        ])
        writer.writerow([
            CSV_HEADERS['parameter_names']['presion'],
            presion_stats['min'],
            presion_stats['min_time'],
            presion_stats['max'],
            presion_stats['max_time'],
            presion_stats['promedio'],
            CSV_HEADERS['units']['presion']
        ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        filename = format_filename('estadisticas', dia_str)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

class ExportMeasurementsView(BaseWeatherView):
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