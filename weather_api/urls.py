from django.urls import path, include
from . import views

urlpatterns = [
    # Frontend routes
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('weather-data/', views.WeatherDataView.as_view(), name='weather_data'),
    
    # API routes
    path('api/', include('weather_api.api.urls')),
] 