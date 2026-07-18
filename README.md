# Mas ClimApp

Aplicacion web para consultar, registrar y comparar datos meteorologicos usando datos oficiales de AEMET, geolocalizacion del navegador, persistencia local y una API REST documentada.

Mas ClimApp combina una interfaz web en Flask con una API REST en FastAPI. La aplicacion permite consultar el tiempo por GPS o localidad, registrar mediciones manuales, revisar historico, comparar registros manuales con datos AEMET y mostrar alertas climaticas segun niveles de riesgo.

## Proyecto Colaborativo Y Mi Contribución

Este proyecto fue desarrollado en equipo durante el bootcamp de Analisis de datos e Inteligencia Artificial. Este repositorio forma parte de mi portfolio y conserva el historial de desarrollo y las contribuciones realizadas durante el proyecto.

Mi participación se centró principalmente en:

* Integración y estabilización de la API después de combinar las ramas del equipo.
* Corrección de rutas y tests automatizados de la API.
* Desarrollo y mejora del dashboard principal.
* Incorporación de la búsqueda meteorológica por localidad.
* Representación visual de las alertas según su nivel de riesgo.
* Mejora de la comparativa entre registros manuales y datos oficiales de AEMET.
* Preparación de la aplicación y la documentación para la demostración final.
* Resolución de incidencias y conflictos durante la integración.

Estas contribuciones pueden consultarse en el historial de commits y pull requests del repositorio.


## Guia Rapida Para Arrancar

Esta es la forma corta de poner el proyecto en marcha en local.

### 1. Clonar El Repositorio

```bash
git clone https://github.com/elenacarino-max/mas-climapp.git
cd mas-climapp
```

### 2. Crear Y Activar El Entorno Virtual

En Windows:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

En Linux o macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Revisar El Archivo `.env`

En la raiz del proyecto debe existir:

```env
AEMET_API_KEY=tu_api_key_de_aemet
SECRET_KEY=una_clave_secreta_para_flask
```
La API key puede obtenerse en [AEMET OpenData](https://opendata.aemet.es/).

### 4. Arrancar La App Web Flask

```powershell
python app.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000/
```

### 5. Arrancar La API FastAPI

En otra terminal, con el entorno virtual activado:

```powershell
python -m uvicorn main_api:app --reload
```

Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

### 6. Comprobar Que Todo Funciona

- Dashboard Flask: `http://127.0.0.1:5000/`
- Panel API Flask: `http://127.0.0.1:5000/api`
- Swagger FastAPI: `http://127.0.0.1:8000/docs`
- Estado de servicios: `http://127.0.0.1:5000/api/status`

### 7. Ejecutar Tests

```powershell
pytest -q
```

## Estado Del Proyecto

El proyecto esta orientado a una demo funcional de bootcamp. Incluye:

- Aplicacion web Flask para usuario final.
- API REST FastAPI con Swagger.
- Conexion con AEMET OpenData.
- Persistencia en SQLite y JSON.
- Registro manual de datos climaticos.
- Consulta de historico.
- Comparativa manual vs AEMET.
- Alertas climaticas por umbrales.
- Tests automatizados con Pytest.

## Funcionalidades

### Dashboard Principal

La pantalla inicial muestra una vision general de la aplicacion:

- Consulta climatica desde GPS.
- Busqueda del tiempo por localidad.
- Temperatura, humedad, viento, lluvia y fuente de datos.
- Estado de Flask, FastAPI y SQLite.
- Riesgo climatico con indicador de color.
- Accesos rapidos a historico, registro, comparativa y Swagger.

### Consulta Con AEMET

La app consulta AEMET OpenData mediante un cliente propio:

- `services/aemet_client.py`: gestiona la comunicacion HTTP con AEMET.
- `services/weather_api_service.py`: localiza la estacion mas cercana y enriquece la respuesta.
- `services/municipality_service.py`: resuelve municipios y coordenadas.
- `services/normalizer_service.py`: transforma datos AEMET al formato que entiende el frontend.

Flujo principal:

1. El navegador obtiene coordenadas GPS o el usuario introduce una localidad.
2. Flask recibe la peticion en `/api/clima` o `/api/clima/localidad`.
3. El servicio consulta AEMET.
4. Se selecciona la estacion meteorologica mas cercana.
5. Se normalizan los datos.
6. Se devuelven al frontend y se guarda un resumen util.

### Registro Manual

Desde `/registro` se pueden introducir mediciones manuales:

- Municipio.
- Estacion asociada.
- Fecha.
- Temperatura.
- Humedad.
- Viento.
- Lluvia.

Estos registros se usan para historico, comparativas y validacion frente a AEMET.

### Historico

Desde `/consulta` se pueden revisar registros guardados y filtrarlos por:

- Municipio.
- Fecha.

El historico usa datos persistidos localmente, principalmente en `data/registros_climaticos.json`, y tambien convive con la capa SQL usada por la API REST.

### Comparativa Manual Vs AEMET

Desde `/comparar` se compara un registro manual con datos oficiales de AEMET.

La comparativa calcula diferencias en:

- Temperatura.
- Humedad.
- Viento.
- Lluvia.

Tambien marca visualmente cada campo:

- Verde: diferencia dentro del rango aceptado.
- Rojo: diferencia considerada discrepancia.

Umbrales actuales:

| Campo | Discrepancia si supera |
| --- | ---: |
| Temperatura | 3 grados |
| Humedad | 10 puntos |
| Viento | 10 km/h |
| Lluvia | 5 mm |

Nota importante: AEMET devuelve observaciones actuales. La comparativa no consulta un historico oficial completo de AEMET para cualquier fecha pasada. Si la estacion exacta del registro manual no aparece en las observaciones actuales, la aplicacion intenta resolver el municipio y usar una estacion cercana disponible.

### Alertas Climaticas

El servicio de alertas evalua los datos climaticos y devuelve niveles como:

- `VERDE`
- `NARANJA_CALOR`
- `ROJA_CALOR`
- `NARANJA_FRIO`
- `ROJA_FRIO`
- `NARANJA_VIENTO`
- `ROJA_VIENTO`
- `NARANJA_LLUVIA`
- `ROJA_LLUVIA`
- `NARANJA_HUMEDAD`

En el dashboard, el riesgo climatico se muestra como un estado compacto con color:

- Verde: sin riesgo.
- Naranja: riesgo medio.
- Rojo: riesgo alto.

## Arquitectura

El proyecto esta organizado por capas para separar responsabilidades.

## Arbol De La Aplicacion

```text
.
├── app.py                     # Entrada principal de Flask
├── main_api.py                # Entrada principal de FastAPI
├── api/                       # Routers FastAPI
├── controllers/               # Controladores Flask
├── db/                        # SQLAlchemy, modelos y CRUD
├── models/                    # Modelos de dominio usados por Flask
├── repositories/              # Persistencia JSON
├── schemas/                   # Schemas Pydantic
├── services/                  # Logica de negocio y conexion AEMET
├── static/                    # CSS, JS y recursos estaticos
├── templates/                 # Vistas HTML Jinja2
├── tests/                     # Tests automatizados
├── utils/                     # Validadores y utilidades
├── data/                      # Datos JSON locales
├── logs/                      # Logs de ejecucion
├── requirements.txt
└── README.md
```

Carpetas principales:

| Carpeta / archivo | Funcion |
| --- | --- |
| `app.py` | Arranca la aplicacion web Flask en el puerto 5000. |
| `main_api.py` | Arranca la API REST FastAPI en el puerto 8000. |
| `api/` | Endpoints FastAPI para health, zonas y mediciones. |
| `controllers/` | Controladores Flask: vistas, API clima, registro, comparativa y autenticacion. |
| `services/` | Logica pesada: AEMET, normalizacion, municipios, alertas y reintentos. |
| `repositories/` | Acceso a datos JSON. |
| `db/` | Conexion SQLite, modelos SQLAlchemy y CRUD. |
| `schemas/` | Schemas Pydantic para validar datos de la API. |
| `models/` | Modelos usados por la app Flask. |
| `templates/` | Plantillas HTML renderizadas con Jinja2. |
| `static/` | CSS, JavaScript y recursos estaticos. |
| `data/` | Datos locales en JSON. |
| `tests/` | Suite de pruebas automatizadas. |
| `logs/` | Logs generados por la aplicacion. |
| `utils/` | Validadores, fechas y funciones auxiliares. |

### Templates

Contienen las vistas HTML renderizadas por Flask:

- `templates/index.html`: dashboard principal.
- `templates/registro.html`: registro manual.
- `templates/consulta.html`: historico.
- `templates/comparar.html`: comparativa manual vs AEMET.
- `templates/api.html`: panel para probar la API Flask.
- `templates/login.html` y `templates/registro_usuario.html`: autenticacion.

### Controllers

Coordinan peticiones, vistas y servicios:

- `view_controller.py`: rutas de paginas HTML.
- `api_controller.py`: endpoints Flask para clima, estado y AEMET.
- `manual_controller.py`: guardado de registros manuales.
- `compare_controller.py`: comparativa entre registros manuales y AEMET.
- `auth_controller.py`: login, registro y sesion.
- `scheduler_controller.py`: tareas automaticas.

### Services

Contienen la logica pesada:

- `aemet_client.py`: cliente AEMET OpenData.
- `weather_api_service.py`: orquestacion de clima por coordenadas.
- `municipality_service.py`: municipios, coordenadas y cache.
- `normalizer_service.py`: normalizacion de datos.
- `alert_service.py`: reglas de riesgo climatico.
- `retry_service.py`: sesion HTTP con reintentos.
- `logging_service.py`: logs de aplicacion.

### Repositories

Gestionan persistencia JSON:

- `json_repository.py`: lectura, filtrado y escritura en `data/registros_climaticos.json`.

### Base De Datos SQL

La parte SQL esta en `db/`:

- `database.py`: conexion SQLite y sesiones.
- `models.py`: modelos SQLAlchemy.
- `crud.py`: operaciones sobre zonas y mediciones.

La base local es `clima.db`.

### API REST FastAPI

FastAPI expone endpoints documentados automaticamente en Swagger:

- `/health/`
- `/health/db`
- `/zonas`
- `/mediciones`

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Tecnologias

| Tecnologia | Uso |
| --- | --- |
| Python | Lenguaje principal |
| Flask | Aplicacion web y rutas de usuario |
| FastAPI | API REST documentada |
| Jinja2 | Plantillas HTML |
| JavaScript | GPS, fetch y actualizacion dinamica |
| CSS | Interfaz visual |
| SQLite | Base de datos local |
| SQLAlchemy | ORM |
| Pydantic | Validacion de datos API |
| Requests / HTTPX | Conexion HTTP |
| AEMET OpenData | Fuente oficial meteorologica |
| Pytest | Tests automatizados |

## Rutas Principales

### Flask

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/` | Dashboard principal |
| GET | `/registro` | Formulario de registro manual |
| GET/POST | `/consulta` | Historico de registros |
| GET/POST | `/comparar` | Comparativa manual vs AEMET |
| GET | `/api` | Panel de prueba de API Flask |
| GET | `/api/status` | Estado de Flask, FastAPI y SQLite |
| GET | `/api/clima?lat=40.4168&lon=-3.7038` | Consulta clima por coordenadas |
| GET | `/api/clima/localidad?nombre=Madrid` | Consulta clima por localidad |
| POST | `/api/registrar` | Guarda registro manual |

### FastAPI

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/` | Estado basico de API |
| GET | `/health/` | Health check |
| GET | `/health/db` | Health check de base de datos |
| GET/POST/PATCH/DELETE | `/zonas` | Gestion de zonas |
| GET/POST/PATCH/DELETE | `/mediciones` | Gestion de mediciones |

## Tests

Ejecutar todos los tests:

```powershell
pytest -q
```

Tests frecuentes durante el desarrollo:

```powershell
pytest tests/test_api_service.py tests/test_municipality_service.py -q
pytest tests/test_compare_controller.py tests/test_json_repository.py -q
pytest tests/test_services.py -q
```

## Datos Y Persistencia

El proyecto usa varias fuentes de datos locales:

- `clima.db`: base SQLite.
- `data/registros_climaticos.json`: registros manuales y algunos datos AEMET guardados.
- `data/usuarios.json`: usuarios locales.
- `logs/app.log`: logs de ejecucion.

En general, `clima.db`, `logs/` y datos generados durante pruebas no deberian subirse si solo contienen estado local.

## Limitaciones Conocidas

- AEMET OpenData puede fallar puntualmente por red, limites o respuestas temporales.
- La comparativa usa observaciones actuales de AEMET; no garantiza historico oficial para cualquier fecha pasada.
- Algunas estaciones de referencia pueden no aparecer en la observacion actual. En ese caso la app intenta usar una estacion cercana por municipio.
- La persistencia esta en transicion entre JSON y SQL.
- El proyecto esta pensado para demo/local, no para despliegue productivo completo.

## Flujo De Trabajo Recomendado Para Demo

1. Arrancar Flask:

```powershell
python app.py
```

2. Abrir:

```text
http://127.0.0.1:5000/
```

3. Permitir GPS o buscar una localidad.
4. Revisar estado de servicios en el dashboard.
5. Registrar un dato manual en `/registro`.
6. Consultar historico en `/consulta`.
7. Comparar manual vs AEMET en `/comparar`.
8. Arrancar FastAPI:

```powershell
python -m uvicorn main_api:app --reload
```

9. Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

## Posibles Mejoras

- Consolidar completamente la persistencia en SQL.
- Mejorar el historico AEMET usando endpoints historicos si se incorporan al alcance.
- Anadir graficos para evolucion temporal.
- Exportar historicos a CSV/PDF.
- Mejorar autenticacion y roles de usuario.
- Preparar despliegue en entorno cloud.

## Autores

Proyecto desarrollado como parte del Bootcamp IA.

- Elena de Vicente
- Veronica Melero
- Gema Villanueva
- Luis Ahmedel Allali
- Gianmario Conforto
- Anas Fady Moustafa

## Documentacion Complementaria

- [Ver informe del proyecto en PDF](docs/assets/ClimApp.pdf)
