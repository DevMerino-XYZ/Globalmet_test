# Weather API - GlobalMet Data Analysis

REST API built with Django that consumes GlobalMet's weather API and provides analytical endpoints with statistical calculations and data export capabilities.

## 🚀 Quick Start

### Installation
```bash
git clone <repository-url>
cd Django_test_globalmet
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Access Points
- **API Base**: `http://localhost:8000/api/`
- **Dashboard**: `http://localhost:8000/`
- **API Documentation**: `http://localhost:8000/api/docs/`

## 📊 Key Features

- **Weather Statistics**: Min/max/average calculations for all weather parameters
- **Temperature Conversion**: Support for Celsius, Fahrenheit, and Kelvin
- **Data Export**: CSV export for statistics and raw measurements
- **Interactive Dashboard**: Modern web interface with real-time charts
- **Comprehensive API**: RESTful endpoints with automatic documentation

## 🔧 Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/estadisticas/temperatura/` | Temperature statistics with unit conversion |
| `/api/estadisticas/humedad/` | Humidity statistics |
| `/api/estadisticas/viento/` | Wind speed statistics |
| `/api/estadisticas/rafaga/` | Wind gust statistics |
| `/api/estadisticas/presion/` | Atmospheric pressure statistics |
| `/api/resumen/diario/` | Complete daily summary |
| `/api/exportar/estadisticas/` | Export statistics to CSV |
| `/api/exportar/mediciones/` | Export raw measurements to CSV |

## 🏗️ Architecture

```
weather_api/
├── api/          # REST endpoints and serializers
├── core/         # Business logic and services  
├── utils/        # Helper functions
├── templates/    # Frontend templates
├── static/       # CSS/JS assets
└── tests.py      # Unit tests (25 tests, all passing)
```

## ⚙️ Configuration

**External API**: GlobalMet Station 689  
**Timezone**: America/Hermosillo  
**Database**: In-memory SQLite (minimal setup)

## 🧪 Testing

```bash
python manage.py test  # Run all 25 unit tests
```

## 📋 Dependencies

- Django 4.2.7 + DRF 3.14.0
- Bootstrap 5.3.0 + Chart.js (frontend)
- Comprehensive documentation with English docstrings

## 🌟 Recent Updates

- ✅ Complete project restructuring with modular architecture
- ✅ Interactive dashboard with real-time charts and export functionality  
- ✅ Comprehensive English documentation for all major components
- ✅ All unit tests updated and passing
- ✅ Professional-grade error handling and validation

---

**Built for GlobalMet** - Professional weather data analysis platform 