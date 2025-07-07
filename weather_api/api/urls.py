from django.urls import path
from .views import (
    TemperatureStatisticsView,
    HumidityStatisticsView,
    WindStatisticsView,
    WindGustStatisticsView,
    PressureStatisticsView,
    DailySummaryView,
    ExportStatisticsView,
    ExportMeasurementsView
)

urlpatterns = [
    # Statistics endpoints
    path('estadisticas/temperatura/', TemperatureStatisticsView.as_view(), name='temperatura_estadisticas'),
    path('estadisticas/humedad/', HumidityStatisticsView.as_view(), name='humedad_estadisticas'),
    path('estadisticas/viento/', WindStatisticsView.as_view(), name='viento_estadisticas'),
    path('estadisticas/rafaga/', WindGustStatisticsView.as_view(), name='rafaga_estadisticas'),
    path('estadisticas/presion/', PressureStatisticsView.as_view(), name='presion_estadisticas'),
    
    # Summary endpoint
    path('resumen/diario/', DailySummaryView.as_view(), name='resumen_diario'),
    
    # Export endpoints
    path('exportar/estadisticas/', ExportStatisticsView.as_view(), name='exportar_estadisticas'),
    path('exportar/mediciones/', ExportMeasurementsView.as_view(), name='exportar_mediciones'),
] 