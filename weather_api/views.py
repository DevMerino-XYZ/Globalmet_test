from django.shortcuts import render
import csv
import io
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import GlobalMetAPIClient, WeatherDataProcessor
import requests


@api_view(['GET'])
def temperatura_estadisticas(request):
    """
    GET /api/estadisticas/temperatura
    Returns temperature statistics with optional unit conversion
    """
    try:
        # Get query parameters
        dia = request.GET.get('dia')
        unidad = request.GET.get('unidad', 'celsius').lower()
        
        # Validate unit
        if unidad not in ['celsius', 'fahrenheit', 'kelvin']:
            return Response(
                {'error': 'Unit must be celsius, fahrenheit, or kelvin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get data from GlobalMet API
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        # Calculate statistics
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, 'temperatura_c')
        
        # Convert to requested unit
        if unidad != 'celsius':
            stats = processor.convert_temperature_stats(stats, unidad)
        
        return Response(stats)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def humedad_estadisticas(request):
    """
    GET /api/estadisticas/humedad
    Returns humidity statistics
    """
    try:
        dia = request.GET.get('dia')
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, 'humedad_relativa')
        
        return Response(stats)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def viento_estadisticas(request):
    """
    GET /api/estadisticas/viento
    Returns wind speed statistics
    """
    try:
        dia = request.GET.get('dia')
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, 'viento_kmh')
        
        return Response(stats)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def rafaga_estadisticas(request):
    """
    GET /api/estadisticas/rafaga
    Returns wind gust statistics
    """
    try:
        dia = request.GET.get('dia')
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, 'viento_rafaga_kmh')
        
        return Response(stats)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def presion_estadisticas(request):
    """
    GET /api/estadisticas/presion
    Returns pressure statistics
    """
    try:
        dia = request.GET.get('dia')
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        stats = processor.calculate_statistics(measurements, 'presion_mb')
        
        return Response(stats)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def resumen_diario(request):
    """
    GET /api/resumen/diario
    Returns all statistics in a single call
    """
    try:
        dia = request.GET.get('dia')
        unidad = request.GET.get('unidad', 'celsius').lower()
        
        # Validate unit
        if unidad not in ['celsius', 'fahrenheit', 'kelvin']:
            return Response(
                {'error': 'Unit must be celsius, fahrenheit, or kelvin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        
        # Calculate all statistics
        temperatura_stats = processor.calculate_statistics(measurements, 'temperatura_c')
        if unidad != 'celsius':
            temperatura_stats = processor.convert_temperature_stats(temperatura_stats, unidad)
        
        humedad_stats = processor.calculate_statistics(measurements, 'humedad_relativa')
        viento_stats = processor.calculate_statistics(measurements, 'viento_kmh')
        rafaga_stats = processor.calculate_statistics(measurements, 'viento_rafaga_kmh')
        presion_stats = processor.calculate_statistics(measurements, 'presion_mb')
        
        resumen = {
            'temperatura': temperatura_stats,
            'humedad': humedad_stats,
            'viento': viento_stats,
            'rafaga': rafaga_stats,
            'presion': presion_stats
        }
        
        return Response(resumen)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def exportar_estadisticas(request):
    """
    GET /api/exportar/estadisticas
    Exports all statistics to CSV
    """
    try:
        dia = request.GET.get('dia')
        unidad = request.GET.get('unidad', 'celsius').lower()
        
        # Validate unit
        if unidad not in ['celsius', 'fahrenheit', 'kelvin']:
            return Response(
                {'error': 'Unit must be celsius, fahrenheit, or kelvin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        processor = WeatherDataProcessor()
        
        # Calculate all statistics
        temperatura_stats = processor.calculate_statistics(measurements, 'temperatura_c')
        if unidad != 'celsius':
            temperatura_stats = processor.convert_temperature_stats(temperatura_stats, unidad)
        
        humedad_stats = processor.calculate_statistics(measurements, 'humedad_relativa')
        viento_stats = processor.calculate_statistics(measurements, 'viento_kmh')
        rafaga_stats = processor.calculate_statistics(measurements, 'viento_rafaga_kmh')
        presion_stats = processor.calculate_statistics(measurements, 'presion_mb')
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Parametro', 'Minimo', 'Maximo', 'Promedio', 'Unidad'])
        
        # Write data
        temp_unit = unidad if unidad != 'celsius' else '°C'
        if unidad == 'fahrenheit':
            temp_unit = '°F'
        elif unidad == 'kelvin':
            temp_unit = 'K'
        
        writer.writerow(['Temperatura', temperatura_stats['min'], temperatura_stats['max'], 
                        temperatura_stats['promedio'], temp_unit])
        writer.writerow(['Humedad Relativa', humedad_stats['min'], humedad_stats['max'], 
                        humedad_stats['promedio'], '%'])
        writer.writerow(['Viento', viento_stats['min'], viento_stats['max'], 
                        viento_stats['promedio'], 'km/h'])
        writer.writerow(['Rafaga de Viento', rafaga_stats['min'], rafaga_stats['max'], 
                        rafaga_stats['promedio'], 'km/h'])
        writer.writerow(['Presion', presion_stats['min'], presion_stats['max'], 
                        presion_stats['promedio'], 'mb'])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        fecha = dia if dia else 'hoy'
        response['Content-Disposition'] = f'attachment; filename="estadisticas_{fecha}.csv"'
        
        return response
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def exportar_mediciones(request):
    """
    GET /api/exportar/mediciones
    Exports all measurements to CSV
    """
    try:
        dia = request.GET.get('dia')
        
        client = GlobalMetAPIClient()
        measurements = client.get_measurements_list(dia)
        
        if not measurements:
            return Response(
                {'error': 'No measurements found for the specified date'},
                status=status.HTTP_404_NOT_FOUND
            )
        
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
        fecha = dia if dia else 'hoy'
        response['Content-Disposition'] = f'attachment; filename="mediciones_{fecha}.csv"'
        
        return response
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except requests.RequestException as e:
        return Response(
            {'error': f'Error fetching data: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
