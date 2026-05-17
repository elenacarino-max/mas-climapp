# Mas ClimApp - Documentacion para presentacion

## Objetivo de la presentacion

Presentar Mas ClimApp como una aplicacion web de consulta climatica que combina datos oficiales de AEMET, geolocalizacion del usuario, persistencia de datos y una API REST documentada. La exposicion esta pensada para durar aproximadamente 10 minutos.

---

# 1. Titulo

## Mas ClimApp

Aplicacion web para consultar clima en tiempo real usando GPS y datos oficiales de AEMET.

### Idea principal

Mas ClimApp permite al usuario consultar informacion meteorologica cercana a su ubicacion real. La aplicacion detecta sus coordenadas mediante GPS, busca la estacion meteorologica mas cercana, obtiene datos de AEMET, normaliza la informacion y la muestra en una interfaz web.

### Mensaje para explicar

El proyecto nace de una necesidad sencilla: consultar datos climaticos reales y cercanos al usuario, pero trabajando con una arquitectura organizada, separando frontend, controladores, servicios, repositorios y modelos.

---

# 2. Problema que resuelve

## Consulta climatica localizada

Muchas aplicaciones muestran datos meteorologicos generales por ciudad, pero no siempre explican de donde salen los datos ni permiten ver el flujo tecnico completo.

Mas ClimApp resuelve esto conectando:

- Ubicacion GPS del usuario.
- Datos oficiales de AEMET.
- Estacion meteorologica mas cercana.
- Normalizacion de datos para el frontend.
- Persistencia en base de datos SQL.
- API REST documentada para pruebas.

### Mensaje para explicar

La aplicacion no se limita a mostrar una temperatura fija. Toma coordenadas reales, consulta AEMET, procesa los datos y devuelve una respuesta preparada para la interfaz y para otros endpoints.

---

# 3. Objetivos del proyecto

## Objetivos tecnicos

- Crear una aplicacion web funcional con Flask.
- Conectar con la API externa de AEMET.
- Usar GPS para obtener la ubicacion del usuario.
- Organizar el codigo por capas.
- Guardar informacion climatica en SQL.
- Crear endpoints REST con FastAPI.
- Documentar y probar endpoints desde Swagger.
- Cubrir la logica principal con tests automaticos.

## Objetivos de aprendizaje

- Trabajar con APIs externas.
- Manejar errores y respuestas incompletas.
- Separar responsabilidades dentro del codigo.
- Usar SQLAlchemy para persistencia.
- Validar datos con schemas.
- Entender el flujo completo entre frontend, backend y servicios.

---

# 4. Arquitectura general

## Capas principales

La aplicacion esta organizada por responsabilidades:

- `templates/`: pantallas HTML que ve el usuario.
- `static/`: CSS y JavaScript del frontend.
- `controllers/`: rutas Flask y control de peticiones.
- `services/`: logica pesada y conexion con AEMET.
- `repositories/`: acceso a datos historicos o persistencia auxiliar.
- `db/`: modelos SQLAlchemy, conexion y CRUD.
- `schemas/`: validacion de datos para API REST.
- `api/`: endpoints FastAPI para zonas y mediciones.
- `tests/`: pruebas automaticas del proyecto.

### Mensaje para explicar

La arquitectura intenta evitar que todo este mezclado en un solo archivo. Cada capa tiene una responsabilidad concreta. Esto hace que el proyecto sea mas mantenible y mas facil de probar.

---

# 5. Flujo principal de la aplicacion

## Flujo GPS + AEMET

1. El usuario entra en la web.
2. El navegador solicita permiso de ubicacion.
3. El frontend obtiene latitud y longitud.
4. Se llama al endpoint Flask `/api/clima`.
5. El controlador valida las coordenadas.
6. El servicio consulta AEMET.
7. Se busca la estacion meteorologica mas cercana.
8. Se resuelve el municipio asociado.
9. Se piden predicciones diaria y horaria.
10. Se normaliza la respuesta.
11. Se muestra en pantalla y se guarda un resumen en SQL.

### Mensaje para explicar

Este flujo es el centro del proyecto. El usuario solo ve una pantalla sencilla, pero por debajo hay varias capas coordinadas para obtener datos reales, transformarlos y mostrarlos.

---

# 6. Frontend

## Interfaz web

La aplicacion tiene una pantalla principal que muestra:

- Municipio o estacion detectada.
- Temperatura.
- Humedad.
- Viento.
- Lluvia.
- Fuente de datos.
- Estado visual del clima.

Tambien se creo una pagina auxiliar en:

`http://127.0.0.1:5000/api`

Esta pagina sirve para:

- Probar la conexion GPS con AEMET.
- Introducir coordenadas manuales.
- Ver la respuesta JSON.
- Abrir Swagger de FastAPI.

### Mensaje para explicar

El frontend esta pensado para que la experiencia sea simple: aceptar ubicacion y ver datos climaticos. La pagina de API sirve como herramienta de prueba para demostrar el funcionamiento tecnico.

---

# 7. Backend Flask

## App principal

El archivo `app.py` levanta la aplicacion Flask y registra los blueprints:

- Vistas HTML.
- Registro manual.
- Login y registro de usuarios.
- API de clima.
- Scheduler.

## Endpoint principal

`GET /api/clima?lat=40.4168&lon=-3.7038`

Este endpoint:

- Recibe coordenadas.
- Valida que sean numericas.
- Llama al servicio meteorologico.
- Normaliza la respuesta.
- Guarda un resumen en SQL.
- Devuelve JSON al frontend.

### Mensaje para explicar

Flask es la parte que conecta la experiencia del usuario con la logica de negocio. El endpoint `/api/clima` es el puente entre el navegador y AEMET.

---

# 8. Conexion con AEMET

## Cliente AEMET

El archivo `services/aemet_client.py` encapsula las llamadas a AEMET.

Actualmente se mantienen solo las conexiones necesarias:

- Observaciones actuales de todas las estaciones.
- Catalogo de municipios.
- Prediccion diaria por municipio.
- Prediccion horaria por municipio.

## Manejo de errores

El cliente controla errores como:

- Timeout.
- Error HTTP.
- Error de conexion.
- Respuestas JSON invalidas.
- Payload con formato inesperado.

### Mensaje para explicar

Una mejora importante fue no capturar todos los errores con un `except Exception` generico. Ahora se capturan errores mas concretos y se dejan logs mas claros, lo que facilita depurar problemas con AEMET.

---

# 9. Servicios y normalizacion

## WeatherAPIService

`services/weather_api_service.py` coordina la logica principal:

- Convierte coordenadas a numeros.
- Pide observaciones a AEMET.
- Calcula la estacion mas cercana.
- Obtiene municipio asociado.
- Pide predicciones.
- Devuelve datos enriquecidos.

## NormalizerService

`services/normalizer_service.py` transforma datos crudos de AEMET en un formato estable para el frontend:

- Temperatura.
- Humedad.
- Viento.
- Lluvia.
- Fecha.
- Coordenadas.
- Municipio detectado.
- Predicciones.
- Alertas.

### Mensaje para explicar

AEMET devuelve datos con nombres y estructuras propias. El normalizador adapta esa informacion para que el frontend no dependa directamente del formato original de AEMET.

---

# 10. Persistencia y base de datos

## SQLAlchemy

La capa `db/` contiene:

- `database.py`: conexion y sesiones.
- `models.py`: modelos SQL.
- `crud.py`: operaciones de crear, leer, actualizar y eliminar.

## Modelos principales

- `Zona`: municipio o localizacion asociada a una estacion.
- `Medicion`: datos climaticos vinculados a una zona.

## Guardado de datos

Cuando se consulta `/api/clima`, la aplicacion intenta guardar un resumen:

- Municipio.
- Codigo INE.
- Estacion.
- Fecha.
- Temperatura.
- Humedad.
- Viento.
- Lluvia.

### Mensaje para explicar

La base de datos permite conservar informacion estructurada. Aunque AEMET sea la fuente original, la aplicacion puede guardar un resumen util para futuras consultas o historico.

---

# 11. API REST con FastAPI

## Swagger

FastAPI se puede arrancar con:

`python -m uvicorn api.main:app --reload`

Y se prueba en:

`http://127.0.0.1:8000/docs`

## Endpoints principales

- `/health/`: comprueba que la API funciona.
- `/zonas/`: CRUD de zonas.
- `/mediciones/`: CRUD de mediciones.

### Mensaje para explicar

FastAPI se usa para exponer una API REST documentada automaticamente. Swagger permite probar los endpoints desde el navegador sin Postman ni herramientas externas.

---

# 12. Tests y validacion

## Pruebas automaticas

El proyecto incluye tests para:

- Cliente AEMET.
- Servicio de clima.
- Servicio de municipios.
- Normalizador.
- Repositorios.
- Endpoints de zonas.
- Endpoints de mediciones.
- Validadores.
- Controladores.

## Resultado de validacion

Se ejecuto la suite completa:

`pytest -q`

Resultado:

`97 passed`

### Mensaje para explicar

Los tests ayudan a comprobar que la aplicacion sigue funcionando despues de integrar cambios. Tambien fueron clave para detectar errores despues de los merges y corregir conflictos.

---

# 13. Cambios importantes realizados

## Mejoras despues de las revisiones

- Mejora del manejo de errores en `AemetClient`.
- Eliminacion de codigo AEMET no necesario.
- Creacion de pagina `/api` para probar GPS y endpoints.
- Ajuste de rutas de zonas para usar funciones CRUD correctas.
- Compatibilidad de imports con `mas_climapp.main`.
- Correccion de tests de API despues del merge.
- Limpieza minima de caches y `.gitignore`.

### Mensaje para explicar

Durante el proyecto no solo se programo funcionalidad nueva. Tambien se corrigieron comentarios de revision, conflictos de GitHub y problemas detectados por tests.

---

# 14. Dificultades encontradas

## Retos tecnicos

- Gestion de conflictos de merge en GitHub.
- Diferencia entre Flask y FastAPI dentro del mismo proyecto.
- Manejo de datos reales de AEMET.
- Respuestas incompletas o inesperadas de una API externa.
- Persistencia entre tests por el uso de SQLite local.
- Diferenciar datos generados localmente de cambios reales de codigo.

### Mensaje para explicar

Una parte importante del aprendizaje fue entender que un proyecto real no solo falla por el codigo de negocio, sino tambien por integraciones, merges, entornos, dependencias y datos generados.

---

# 15. Demo sugerida para clase

## Orden de demostracion

1. Abrir la app Flask:

   `http://127.0.0.1:5000/`

2. Aceptar permiso GPS.

3. Mostrar datos climaticos cargados desde AEMET.

4. Abrir pagina de prueba:

   `http://127.0.0.1:5000/api`

5. Probar coordenadas manuales o GPS.

6. Arrancar FastAPI y abrir Swagger:

   `http://127.0.0.1:8000/docs`

7. Probar `/health/`, `/zonas/` o `/mediciones/`.

### Mensaje para explicar

La demo debe mostrar primero la experiencia de usuario y despues la parte tecnica. Asi se entiende tanto el producto como la arquitectura.

---

# 16. Mejoras futuras

## Evolucion posible

- Separar aun mas `normalizer_service.py` en modulos pequenos.
- Mejorar el frontend principal.
- Crear un sistema de historico mas completo.
- Unificar criterios entre Flask y FastAPI.
- Anadir autenticacion mas robusta.
- Crear despliegue en la nube.
- Anadir graficas de evolucion meteorologica.
- Mejorar la gestion de cache para evitar llamadas innecesarias a AEMET.

### Mensaje para explicar

El proyecto ya funciona como aplicacion local, pero tiene margen para crecer hacia una aplicacion mas completa, desplegable y visual.

---

# 17. Cierre

## Conclusion

Mas ClimApp demuestra un flujo completo de aplicacion web:

- Frontend con GPS.
- Backend Flask.
- Conexion con AEMET.
- Servicios desacoplados.
- Normalizacion de datos.
- Persistencia SQL.
- API REST con Swagger.
- Tests automaticos.

### Mensaje final

La aplicacion integra varias piezas reales de desarrollo: consumo de API externa, geolocalizacion, arquitectura por capas, base de datos, pruebas y documentacion. El resultado es una base funcional que puede seguir evolucionando.

