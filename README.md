# API de Análisis de Datos Meteorológicos - GlobalMet

API REST desarrollada en Django que consume datos de la API base de GlobalMet y proporciona endpoints analíticos y de exportación para datos meteorológicos.

## Características

- Consumo de datos de la API GlobalMet
- Endpoints de estadísticas diarias (temperatura, humedad, viento, ráfagas, presión)
- Conversión de unidades de temperatura (Celsius, Fahrenheit, Kelvin)
- Endpoint de resumen diario con todas las estadísticas
- Exportación de datos en formato CSV
- Manejo de errores robusto
- Tests unitarios completos
- Timezone configurado para America/Hermosillo

## Instalación

### Prerrequisitos

- Python 3.8+
- pip

### Configuración del Entorno

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd Django_test_globalmet
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\Activate.ps1
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar migraciones:
```bash
python manage.py migrate
```

5. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000/`

## Endpoints de la API

### 1. Estadísticas de Temperatura

**GET** `/api/estadisticas/temperatura/`

Retorna estadísticas de temperatura con conversión opcional de unidades.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD. Si no se especifica, usa la fecha actual en timezone America/Hermosillo
- `unidad` (opcional): Unidad de temperatura (`celsius`, `fahrenheit`, `kelvin`). Por defecto: `celsius`

**Ejemplo de respuesta:**
```json
{
    "min": 18.5,
    "max": 32.1,
    "promedio": 25.3
}
```

**Ejemplos de uso:**
```bash
# Estadísticas del día actual en Celsius
GET /api/estadisticas/temperatura/

# Estadísticas de una fecha específica en Fahrenheit
GET /api/estadisticas/temperatura/?dia=2023-12-01&unidad=fahrenheit

# Estadísticas en Kelvin
GET /api/estadisticas/temperatura/?unidad=kelvin
```

### 2. Estadísticas de Humedad

**GET** `/api/estadisticas/humedad/`

Retorna estadísticas de humedad relativa.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD

**Ejemplo de respuesta:**
```json
{
    "min": 45.2,
    "max": 78.9,
    "promedio": 62.1
}
```

### 3. Estadísticas de Viento

**GET** `/api/estadisticas/viento/`

Retorna estadísticas de velocidad del viento.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD

**Ejemplo de respuesta:**
```json
{
    "min": 2.1,
    "max": 15.8,
    "promedio": 8.4
}
```

### 4. Estadísticas de Ráfagas de Viento

**GET** `/api/estadisticas/rafaga/`

Retorna estadísticas de ráfagas de viento.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD

**Ejemplo de respuesta:**
```json
{
    "min": 5.2,
    "max": 22.3,
    "promedio": 12.7
}
```

### 5. Estadísticas de Presión

**GET** `/api/estadisticas/presion/`

Retorna estadísticas de presión atmosférica.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD

**Ejemplo de respuesta:**
```json
{
    "min": 1008.5,
    "max": 1015.2,
    "promedio": 1012.8
}
```

### 6. Resumen Diario

**GET** `/api/resumen/diario/`

Retorna todas las estadísticas anteriores en un solo llamado.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD
- `unidad` (opcional): Unidad de temperatura para las estadísticas de temperatura

**Ejemplo de respuesta:**
```json
{
    "temperatura": {
        "min": 18.5,
        "max": 32.1,
        "promedio": 25.3
    },
    "humedad": {
        "min": 45.2,
        "max": 78.9,
        "promedio": 62.1
    },
    "viento": {
        "min": 2.1,
        "max": 15.8,
        "promedio": 8.4
    },
    "rafaga": {
        "min": 5.2,
        "max": 22.3,
        "promedio": 12.7
    },
    "presion": {
        "min": 1008.5,
        "max": 1015.2,
        "promedio": 1012.8
    }
}
```

### 7. Exportar Estadísticas

**GET** `/api/exportar/estadisticas/`

Genera un archivo CSV con todas las estadísticas del día.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD
- `unidad` (opcional): Unidad de temperatura

**Respuesta:** Archivo CSV con las estadísticas

**Ejemplo de contenido CSV:**
```csv
Parametro,Minimo,Maximo,Promedio,Unidad
Temperatura,18.5,32.1,25.3,°C
Humedad Relativa,45.2,78.9,62.1,%
Viento,2.1,15.8,8.4,km/h
Rafaga de Viento,5.2,22.3,12.7,km/h
Presion,1008.5,1015.2,1012.8,mb
```

### 8. Exportar Mediciones

**GET** `/api/exportar/mediciones/`

Genera un archivo CSV con todas las mediciones del día.

**Parámetros de consulta:**
- `dia` (opcional): Fecha en formato YYYY-MM-DD

**Respuesta:** Archivo CSV con todas las mediciones individuales

## Manejo de Errores

La API maneja los siguientes tipos de errores:

### Errores de Validación (400 Bad Request)
```json
{
    "error": "Date must be in YYYY-MM-DD format"
}
```

### Errores de la API Externa (503 Service Unavailable)
```json
{
    "error": "Error fetching data: Connection timeout"
}
```

### Errores del Servidor (500 Internal Server Error)
```json
{
    "error": "Internal server error: <descripción>"
}
```

### Datos No Encontrados (404 Not Found)
```json
{
    "error": "No measurements found for the specified date"
}
```

## Configuración

### Variables de Configuración

Las siguientes variables están configuradas en `settings.py`:

```python
# GlobalMet API Configuration
GLOBALMET_API_URL = "https://data.globalmet.mx/api/mediciones/perday/estacion/689/"
GLOBALMET_API_TOKEN = "Token 2c9f700c179a5f18f501167ea286e4203fffc289"

# Timezone
TIME_ZONE = "America/Hermosillo"
```

### Estructura del Proyecto

```
Django_test_globalmet/
├── venv/                     # Entorno virtual
├── globalmet_api/           # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # URLs principales
│   └── wsgi.py
├── weather_api/             # Aplicación principal
│   ├── __init__.py
│   ├── services.py          # Servicios para API externa
│   ├── views.py             # Vistas de la API
│   ├── urls.py              # URLs de la aplicación
│   └── tests.py             # Tests unitarios
├── requirements.txt         # Dependencias
├── manage.py               # Comando de Django
└── README.md               # Documentación
```

## Tests

Para ejecutar los tests unitarios:

```bash
python manage.py test
```

Los tests cubren:
- Servicios de la API externa
- Procesamiento de datos meteorológicos
- Todos los endpoints de la API
- Manejo de errores
- Conversión de unidades
- Exportación de datos

### Ejecutar Tests Específicos

```bash
# Tests del cliente API
python manage.py test weather_api.tests.GlobalMetAPIClientTests

# Tests del procesador de datos
python manage.py test weather_api.tests.WeatherDataProcessorTests

# Tests de las vistas
python manage.py test weather_api.tests.WeatherAPIViewsTests
```

## Dependencias

- **Django 4.2.7**: Framework web
- **djangorestframework 3.14.0**: Para crear APIs REST
- **requests 2.31.0**: Para realizar peticiones HTTP
- **pytz 2023.3**: Para manejo de timezones
- **python-dateutil 2.8.2**: Para manipulación de fechas

## Desarrollo

### Agregar Nuevos Endpoints

1. Agregar la vista en `weather_api/views.py`
2. Agregar la URL en `weather_api/urls.py`
3. Agregar tests en `weather_api/tests.py`

### Agregar Nuevas Estadísticas

1. Modificar `WeatherDataProcessor` en `weather_api/services.py`
2. Actualizar las vistas correspondientes
3. Agregar tests para la nueva funcionalidad

## Producción

Para desplegar en producción:

1. Configurar `DEBUG = False` en settings.py
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Usar una base de datos de producción (PostgreSQL recomendado)
4. Configurar servidor web (nginx + gunicorn)
5. Configurar variables de entorno para información sensible

## Licencia

Este proyecto fue desarrollado como parte de una prueba técnica para GlobalMet.

## Soporte

Para soporte técnico o preguntas sobre la implementación, contactar al equipo de desarrollo. 