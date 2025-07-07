"""
Weather API Frontend Views

This module contains Django views for the weather dashboard frontend.
It includes the main dashboard view and AJAX endpoints for dynamic
data loading and chart updates.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .core.services import GlobalMetAPIClient, WeatherDataProcessor
from .core.exceptions import WeatherAPIException
from .utils.helpers import get_current_date_hermosillo
import json


def dashboard(request):
    """
    Main dashboard view for the weather application.
    
    This view renders the main dashboard page with weather data visualization.
    It provides the initial HTML structure and context for the interactive
    weather dashboard interface.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered dashboard template
    """
    context = {
        'title': 'Dashboard Meteorológico',
        'current_date': get_current_date_hermosillo()
    }
    return render(request, 'dashboard.html', context)


class WeatherDataView(View):
    """
    AJAX endpoint for fetching weather data for the dashboard.
    
    This view provides a JSON API endpoint for the frontend dashboard
    to fetch weather data dynamically. It processes the data and formats
    it for chart visualization and statistics display.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Override dispatch to exempt CSRF validation for AJAX requests."""
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Fetch and process weather data for dashboard display.
        
        This method retrieves weather measurements from the GlobalMet API,
        calculates statistics for all weather parameters, and formats the
        data for use in charts and dashboard widgets.
        
        Args:
            request: HTTP request object with optional 'dia' parameter
            
        Returns:
            JsonResponse: Weather data formatted for dashboard consumption
        """
        try:
            # Obtener fecha del parámetro o usar fecha actual
            date_param = request.GET.get('dia')
            if date_param:
                date_str = date_param
            else:
                date_str = get_current_date_hermosillo()
            
            # Inicializar servicios
            api_client = GlobalMetAPIClient()
            processor = WeatherDataProcessor()
            
            # Obtener datos de la API
            raw_data = api_client.get_measurements_list(date_str)
            
            # Procesar estadísticas
            temperature_stats = processor.calculate_statistics(raw_data, 'temperatura_c')
            humidity_stats = processor.calculate_statistics(raw_data, 'humedad_relativa')
            wind_stats = processor.calculate_statistics(raw_data, 'viento_kmh')
            gust_stats = processor.calculate_statistics(raw_data, 'viento_rafaga_kmh')
            pressure_stats = processor.calculate_statistics(raw_data, 'presion_mb')
            
            # Preparar datos para gráficos
            chart_data = self._prepare_chart_data(raw_data)
            
            # Respuesta JSON
            response_data = {
                'success': True,
                'date': date_str,
                'statistics': {
                    'temperature': temperature_stats,
                    'humidity': humidity_stats,
                    'wind': wind_stats,
                    'gust': gust_stats,
                    'pressure': pressure_stats
                },
                'chart_data': chart_data,
                'raw_data_count': len(raw_data)
            }
            
            return JsonResponse(response_data)
            
        except WeatherAPIException as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'error_type': 'weather_api_error'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}',
                'error_type': 'internal_error'
            }, status=500)
    
    def _prepare_chart_data(self, raw_data):
        """
        Prepare weather data for chart visualization.
        
        This method processes raw weather measurements and formats them
        for use in Chart.js visualizations. It extracts time series data
        and structures it according to Chart.js dataset requirements.
        
        Args:
            raw_data: List of raw weather measurement dictionaries
            
        Returns:
            dict: Formatted chart data with labels and datasets
        """
        if not raw_data:
            return {}
        
        # Extraer datos para gráficos
        timestamps = []
        temperatures = []
        humidity = []
        wind_speeds = []
        wind_gusts = []
        pressures = []
        
        for record in raw_data:
            # Usar el timestamp si está disponible, sino usar un índice
            if 'timestamp' in record:
                timestamps.append(record['timestamp'])
            else:
                timestamps.append(f"Registro {len(timestamps) + 1}")
            
            temperatures.append(record.get('temperatura_c'))
            humidity.append(record.get('humedad_relativa'))
            wind_speeds.append(record.get('viento_kmh'))
            wind_gusts.append(record.get('viento_rafaga_kmh'))
            pressures.append(record.get('presion_mb'))
        
        return {
            'labels': timestamps[:24],  # Limitar a 24 puntos para mejor visualización
            'datasets': {
                'temperature': {
                    'label': 'Temperatura (°C)',
                    'data': temperatures[:24],
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1
                },
                'humidity': {
                    'label': 'Humedad (%)',
                    'data': humidity[:24],
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1
                },
                'wind': {
                    'label': 'Viento (km/h)',
                    'data': wind_speeds[:24],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1
                },
                'gust': {
                    'label': 'Ráfagas (km/h)',
                    'data': wind_gusts[:24],
                    'borderColor': 'rgb(255, 205, 86)',
                    'backgroundColor': 'rgba(255, 205, 86, 0.2)',
                    'tension': 0.1
                },
                'pressure': {
                    'label': 'Presión (mb)',
                    'data': pressures[:24],
                    'borderColor': 'rgb(153, 102, 255)',
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'tension': 0.1
                }
            }
        } 