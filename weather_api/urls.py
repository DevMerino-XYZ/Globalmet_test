from django.urls import path
from . import views

urlpatterns = [
    # Statistics endpoints
    path('api/estadisticas/temperatura/', views.temperatura_estadisticas, name='temperatura_estadisticas'),
    path('api/estadisticas/humedad/', views.humedad_estadisticas, name='humedad_estadisticas'),
    path('api/estadisticas/viento/', views.viento_estadisticas, name='viento_estadisticas'),
    path('api/estadisticas/rafaga/', views.rafaga_estadisticas, name='rafaga_estadisticas'),
    path('api/estadisticas/presion/', views.presion_estadisticas, name='presion_estadisticas'),
    
    # Summary endpoint
    path('api/resumen/diario/', views.resumen_diario, name='resumen_diario'),
    
    # Export endpoints
    path('api/exportar/estadisticas/', views.exportar_estadisticas, name='exportar_estadisticas'),
    path('api/exportar/mediciones/', views.exportar_mediciones, name='exportar_mediciones'),
] 