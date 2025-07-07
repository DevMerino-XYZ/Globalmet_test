from django.test import TestCase
import json
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from .core.services import GlobalMetAPIClient, WeatherDataProcessor
from .core.exceptions import (
    InvalidDateFormatException,
    InvalidTemperatureUnitException,
    GlobalMetAPIException,
    NoDataFoundException
)
import requests


class GlobalMetAPIClientTests(TestCase):
    """Tests for GlobalMetAPIClient"""
    
    def setUp(self):
        self.client = GlobalMetAPIClient()
    
    @patch('weather_api.core.services.requests.get')
    def test_get_measurements_by_date_success(self, mock_get):
        """Test successful API call"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {'temperatura_c': 25.5, 'humedad_relativa': 60, 'viento_kmh': 10}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_measurements_by_date('2023-01-01')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['temperatura_c'], 25.5)
        mock_get.assert_called_once()
    
    @patch('weather_api.core.services.requests.get')
    def test_get_measurements_by_date_api_error(self, mock_get):
        """Test API error handling"""
        mock_get.side_effect = requests.RequestException("API Error")
        
        with self.assertRaises(GlobalMetAPIException):
            self.client.get_measurements_by_date('2023-01-01')
    
    def test_get_measurements_by_date_invalid_date(self):
        """Test invalid date format"""
        with self.assertRaises(InvalidDateFormatException):
            self.client.get_measurements_by_date('invalid-date')
    
    @patch('weather_api.core.services.requests.get')
    def test_get_measurements_list_dict_response(self, mock_get):
        """Test handling dict response with results key"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [{'temperatura_c': 25.5}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_measurements_list('2023-01-01')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['temperatura_c'], 25.5)


class WeatherDataProcessorTests(TestCase):
    """Tests for WeatherDataProcessor"""
    
    def setUp(self):
        self.processor = WeatherDataProcessor()
        self.sample_data = [
            {'temperatura_c': 20.0, 'humedad_relativa': 50},
            {'temperatura_c': 25.0, 'humedad_relativa': 60},
            {'temperatura_c': 30.0, 'humedad_relativa': 70},
        ]
    
    def test_calculate_statistics_success(self):
        """Test successful statistics calculation"""
        stats = self.processor.calculate_statistics(self.sample_data, 'temperatura_c')
        
        self.assertEqual(stats['min'], 20.0)
        self.assertEqual(stats['max'], 30.0)
        self.assertEqual(stats['promedio'], 25.0)
    
    def test_calculate_statistics_empty_data(self):
        """Test statistics calculation with empty data"""
        with self.assertRaises(NoDataFoundException):
            self.processor.calculate_statistics([], 'temperatura_c')
    
    def test_calculate_statistics_missing_field(self):
        """Test statistics calculation with missing field"""
        data = [{'other_field': 10}]
        stats = self.processor.calculate_statistics(data, 'temperatura_c')
        
        self.assertIsNone(stats['min'])
        self.assertIsNone(stats['max'])
        self.assertIsNone(stats['promedio'])
    
    def test_convert_temperature_celsius(self):
        """Test temperature conversion to Celsius"""
        result = self.processor.convert_temperature(25.0, 'celsius')
        self.assertEqual(result, 25.0)
    
    def test_convert_temperature_fahrenheit(self):
        """Test temperature conversion to Fahrenheit"""
        result = self.processor.convert_temperature(25.0, 'fahrenheit')
        self.assertEqual(result, 77.0)
    
    def test_convert_temperature_kelvin(self):
        """Test temperature conversion to Kelvin"""
        result = self.processor.convert_temperature(25.0, 'kelvin')
        self.assertEqual(result, 298.15)
    
    def test_convert_temperature_invalid_unit(self):
        """Test temperature conversion with invalid unit"""
        with self.assertRaises(InvalidTemperatureUnitException):
            self.processor.convert_temperature(25.0, 'invalid')
    
    def test_convert_temperature_stats(self):
        """Test temperature statistics conversion"""
        stats = {'min': 20.0, 'max': 30.0, 'promedio': 25.0}
        result = self.processor.convert_temperature_stats(stats, 'fahrenheit')
        
        self.assertEqual(result['min'], 68.0)
        self.assertEqual(result['max'], 86.0)
        self.assertEqual(result['promedio'], 77.0)


class WeatherAPIViewsTests(TestCase):
    """Tests for Weather API views"""
    
    def setUp(self):
        self.client = Client()
        self.sample_measurements = [
            {
                'temperatura_c': 20.0,
                'humedad_relativa': 50.0,
                'viento_kmh': 8.0,
                'viento_rafaga_kmh': 12.0,
                'presion_mb': 1012.0
            },
            {
                'temperatura_c': 25.0,
                'humedad_relativa': 60.0,
                'viento_kmh': 10.0,
                'viento_rafaga_kmh': 15.0,
                'presion_mb': 1013.25
            },
            {
                'temperatura_c': 30.0,
                'humedad_relativa': 70.0,
                'viento_kmh': 12.0,
                'viento_rafaga_kmh': 18.0,
                'presion_mb': 1015.0
            }
        ]
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_temperatura_estadisticas_success(self, mock_client_class):
        """Test temperature statistics endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/temperatura/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 20.0)
        self.assertEqual(data['max'], 30.0)
        self.assertEqual(data['promedio'], 25.0)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_temperatura_estadisticas_fahrenheit(self, mock_client_class):
        """Test temperature statistics with Fahrenheit conversion"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/temperatura/?unidad=fahrenheit')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 68.0)
        self.assertEqual(data['max'], 86.0)
        self.assertEqual(data['promedio'], 77.0)
    
    def test_temperatura_estadisticas_invalid_unit(self):
        """Test temperature statistics with invalid unit"""
        response = self.client.get('/api/estadisticas/temperatura/?unidad=invalid')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.content)
        self.assertIn('unidad', data)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_humedad_estadisticas_success(self, mock_client_class):
        """Test humidity statistics endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/humedad/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 50.0)
        self.assertEqual(data['max'], 70.0)
        self.assertEqual(data['promedio'], 60.0)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_viento_estadisticas_success(self, mock_client_class):
        """Test wind statistics endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/viento/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 8.0)
        self.assertEqual(data['max'], 12.0)
        self.assertEqual(data['promedio'], 10.0)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_rafaga_estadisticas_success(self, mock_client_class):
        """Test wind gust statistics endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/rafaga/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 12.0)
        self.assertEqual(data['max'], 18.0)
        self.assertEqual(data['promedio'], 15.0)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_presion_estadisticas_success(self, mock_client_class):
        """Test pressure statistics endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/presion/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['min'], 1012.0)
        self.assertEqual(data['max'], 1015.0)
        self.assertAlmostEqual(data['promedio'], 1013.42, places=1)  # Average of the three values
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_resumen_diario_success(self, mock_client_class):
        """Test daily summary endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/resumen/diario/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['temperatura']['min'], 20.0)
        self.assertEqual(data['temperatura']['max'], 30.0)
        self.assertEqual(data['humedad']['min'], 50.0)
        self.assertEqual(data['viento']['min'], 8.0)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_exportar_estadisticas_success(self, mock_client_class):
        """Test statistics export endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/exportar/estadisticas/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_exportar_mediciones_success(self, mock_client_class):
        """Test measurements export endpoint success"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/exportar/mediciones/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_api_error_handling(self, mock_client_class):
        """Test API error handling"""
        from weather_api.core.exceptions import GlobalMetAPIException
        mock_client = Mock()
        mock_client.get_measurements_list.side_effect = GlobalMetAPIException("API Error")
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/temperatura/')
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_date_parameter(self, mock_client_class):
        """Test date parameter handling"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = self.sample_measurements
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/estadisticas/temperatura/?dia=2023-01-01')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_client.get_measurements_list.assert_called_with('2023-01-01')
    
    @patch('weather_api.api.views.GlobalMetAPIClient')
    def test_exportar_mediciones_no_data(self, mock_client_class):
        """Test measurements export with no data"""
        mock_client = Mock()
        mock_client.get_measurements_list.return_value = []
        mock_client_class.return_value = mock_client
        
        response = self.client.get('/api/exportar/mediciones/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
