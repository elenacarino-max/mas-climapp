# Documentación de Endpoints — Mas ClimApp

## Arrancar la API

Desde la raíz del proyecto:

```powershell
uvicorn main_api:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 1. Endpoint de estado

### GET `/health`

Comprueba que la API está funcionando.

#### Respuesta esperada

```json
{
  "status": "ok",
  "message": "API funcionando correctamente"
}
```

---

## 2. Endpoints de zonas

Una zona representa un municipio o localización asociada a una estación meteorológica.

### GET `/zonas/`

Lista todas las zonas registradas.

Parámetros opcionales:

```text
skip: registros a saltar
limit: máximo de registros a devolver
```

Ejemplo:

```text
GET /zonas/?skip=0&limit=100
```

### GET `/zonas/{zona_id}`

Busca una zona por su ID.

Ejemplo:

```text
GET /zonas/1
```

Error posible:

```json
{
  "detail": "No existe ninguna zona con id 1"
}
```

### GET `/zonas/cod-ine/{cod_ine}`

Busca una zona por su código INE.

Ejemplo:

```text
GET /zonas/cod-ine/28079
```

### POST `/zonas/`

Crea una nueva zona.

Body JSON:

```json
{
  "municipio": "Madrid",
  "cod_ine": "28079",
  "id_estacion": "3195",
  "estacion_referencia": "Madrid Retiro"
}
```

Respuesta esperada:

```json
{
  "id": 1,
  "municipio": "Madrid",
  "cod_ine": "28079",
  "id_estacion": "3195",
  "estacion_referencia": "Madrid Retiro"
}
```

Error posible:

```json
{
  "detail": "Ya existe una zona con cod_ine 28079"
}
```

### PATCH `/zonas/{zona_id}`

Actualiza parcialmente una zona.

Ejemplo:

```text
PATCH /zonas/1
```

Body JSON:

```json
{
  "municipio": "Madrid Capital"
}
```

### DELETE `/zonas/{zona_id}`

Elimina una zona.

Si la relación está configurada con cascada, también se eliminan sus mediciones asociadas.

Ejemplo:

```text
DELETE /zonas/1
```

Respuesta esperada:

```json
{
  "message": "Zona eliminada correctamente",
  "zona_id": 1
}
```

---

## 3. Endpoints de mediciones

Una medición representa datos climáticos asociados a una zona concreta.

### GET `/mediciones/`

Lista todas las mediciones.

Parámetros opcionales:

```text
skip: registros a saltar
limit: máximo de registros a devolver
```

Ejemplo:

```text
GET /mediciones/?skip=0&limit=100
```

### GET `/mediciones/{medicion_id}`

Busca una medición por ID.

Ejemplo:

```text
GET /mediciones/1
```

Error posible:

```json
{
  "detail": "No existe la medición con id 1"
}
```

### POST `/mediciones/`

Crea una nueva medición asociada a una zona.

Body JSON:

```json
{
  "zona_id": 1,
  "fecha_datos": "2024-06-15",
  "temperatura": 22.5,
  "humedad": 60,
  "viento": 12.4,
  "lluvia": 0
}
```

Respuesta esperada:

```json
{
  "id": 1,
  "zona_id": 1,
  "fecha_datos": "2024-06-15",
  "temperatura": 22.5,
  "humedad": 60,
  "viento": 12.4,
  "lluvia": 0
}
```

### PATCH `/mediciones/{medicion_id}`

Actualiza parcialmente una medición.

Ejemplo:

```text
PATCH /mediciones/1
```

Body JSON:

```json
{
  "temperatura": 24.0,
  "lluvia": 0.5
}
```

### DELETE `/mediciones/{medicion_id}`

Elimina una medición.

Ejemplo:

```text
DELETE /mediciones/1
```

Respuesta esperada:

```json
{
  "message": "Medición eliminada correctamente",
  "medicion_id": 1
}
```

---

## 4. Códigos de estado usados

```text
200 OK          → consulta correcta
201 Created     → recurso creado correctamente
400 Bad Request → datos incorrectos
404 Not Found   → recurso no encontrado
409 Conflict    → recurso duplicado
```

---

## 5. Flujo básico de uso

1. Crear una zona con `POST /zonas/`.
2. Consultar sus datos con `GET /zonas/`.
3. Crear una medición asociada a esa zona con `POST /mediciones/`.
4. Consultar mediciones con `GET /mediciones/`.
5. Actualizar si hace falta con `PATCH`.
6. Eliminar con `DELETE`.

---

## 6. Resumen para presentación

La API REST de Mas ClimApp permite gestionar dos recursos principales:

- Zonas.
- Mediciones climáticas.

Cada recurso tiene operaciones CRUD:

- Crear.
- Leer.
- Actualizar.
- Eliminar.

Además, FastAPI genera documentación automática en Swagger, lo que permite probar los endpoints desde el navegador sin necesidad de usar herramientas externas.
