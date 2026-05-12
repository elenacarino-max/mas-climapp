import pytest
import pandas as pd

#Comprobación de nulos en el ETL: 
#Diseño: Si la fecha o el municipio son nulos, se eliminará la fila completa. 
#Si la temperatura, humedad, viento y lluvia son nulos, se eliminará la fila completa. Si al menos un valor es válido, se mantendrá la fila.
#Traemos la función a probar. 

from etl.transform import limpiar_datos_nulos

#Definir la función de test para la limpieza de nulos. En este caso, comprobamos que se eliminar las filas con nulos. ""

def test_valores_nulos():

    # Datos de ejemplo con nulos
    datos_prueba = {
        "zona_id": [1, None, 2, 4, 3],
        "fecha_datos": [
                None,
                "2024-06-01 10:00:00",
                "2024-06-02 12:00:00",
                "2024-06-04 08:00:00",
                "2024-06-03 08:00:00"
        ],
        "temperatura": [25.5, 30.2, None, None, None],
        "humedad": [60.0, None, None, 55.0, None],
        "viento": [10.0, 15.0, None, None, None],
        "lluvia": [0.0, None, 5.0, None, None]
    }

    df = pd.DataFrame(datos_prueba)

    # ejecutar ETL
    limpiar_datos_df = limpiar_datos_nulos(df)

    # No quedan zona_id nulos
    assert limpiar_datos_df["zona_id"].isnull().sum() == 0

    # No quedan fechas nulas
    assert limpiar_datos_df["fecha_datos"].isnull().sum() == 0

    # comprobar que fecha es datetime
    assert pd.api.types.is_datetime64_any_dtype(
        limpiar_datos_df["fecha_datos"]
    )

    # No debe existir ninguna fila con TODOS los valores meteorológicos nulos
    columnas_meteo = ["temperatura", "humedad", "viento", "lluvia"]

    filas_todo_nulo = limpiar_datos_df[columnas_meteo].isnull().all(axis=1)

    assert filas_todo_nulo.sum() == 0

    # Debe eliminarse zona_id 1 por fecha nula
    assert 1 not in limpiar_datos_df["zona_id"].values

    # Debe eliminarse zona_id None por zona nula
    assert limpiar_datos_df["zona_id"].isnull().sum() == 0

    # Debe eliminarse zona_id 3 por todos los datos meterologicos nulos
    assert 3 not in limpiar_datos_df["zona_id"].values

    # Comprobar que los NULL parciales se conservan como NULL
    assert 2 in limpiar_datos_df["zona_id"].values

    # zona_id 2 debe conservarse
    fila_zona_2 = limpiar_datos_df[
        limpiar_datos_df["zona_id"] == 2
    ].iloc[0]

    # NULL parciales se mantienen
    assert pd.isnull(fila_zona_2["temperatura"])
    assert pd.isnull(fila_zona_2["humedad"])
    assert pd.isnull(fila_zona_2["viento"])
    # lluvia válida se conserva
    assert pd.isnotnull(fila_zona_2["lluvia"])
    assert fila_zona_2["lluvia"] == 5.0

    # zona_id 4 debe conservarse
    assert 4 in limpiar_datos_df["zona_id"].values

    fila_zona_4 = limpiar_datos_df[
        limpiar_datos_df["zona_id"] == 4
    ].iloc[0]

    # NULL parciales se mantienen
    assert pd.isnull(fila_zona_4["temperatura"])
    assert pd.isnull(fila_zona_4["viento"])
    assert pd.isnull(fila_zona_4["lluvia"])
    # humedad válida se conserva
    assert pd.isnotnull(fila_zona_4["humedad"])
    assert fila_zona_4["humedad"] == 55.0


    #Comprobar que los descartados se han incluido en los logs. En el proceso de limpieza, se registran los casos de filas descartadas según lo definido.
    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    # Validar registros descartados
    assert "Registro eliminado por zona nula" in contenido_log
    assert "Registro eliminado por fecha nula" in contenido_log
    assert "Registro eliminado: todos los valores meteorológicos nulos" in contenido_log


    ##Comprobar duplicados en el ETL: si el proceso de limpieza funciona, no deberían quedar filas duplicadas en el DataFrame final.
    #Se consideran duplicados aquellos registros que tengan el mismo zona_id y la misma fecha de registro. En caso de encontrar duplicados, se eliminará la fila completa.

def test_filas_duplicadas():

    datos_prueba = {
        "zona_id": [1, 1, 2],
        "fecha_datos": [
            pd.Timestamp("2024-06-01 10:00:00"),
            pd.Timestamp("2024-06-01 10:00:00"),
            pd.Timestamp("2024-06-02 12:00:00")
        ],
        "temperatura": [25.0, 26.0, 30.0],
        "humedad": [60.0, 62.0, 55.0],
        "viento": [10.0, 12.0, 8.0],
        "lluvia": [0.0, 0.0, 5.0]
    }

    df = pd.DataFrame(datos_prueba)

    #Asegurar tipo datos
    resultado = transformar_datos(df)

    # Comprobar que no hay duplicados
    duplicados = resultado.duplicated(
        subset=["zona_id", "fecha_datos"]
    )

    assert duplicados.sum() == 0

    # Debe conservarse zona_id 2
    assert 2 in resultado["zona_id"].values

    # Solo debe quedar un registro para zona_id 1
    assert (resultado["zona_id"] == 1).sum() == 1

    #Comprobar que los descartados se han incluido en los logs. En el proceso de limpieza, se registran los descartados por duplicidad según lo definido.
    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    # Validar log duplicados
    assert "Duplicado eliminado" in contenido_log


    ## Comprobar tipo de datos correctos en el ETL. 

def test_tipos_datos():

    datos_prueba = {
        "zona_id": [1, 2],
        "fecha_datos": [
            "2024-06-01 10:00:00",
            "2024-06-02 12:00:00"
        ],
        "temperatura": ["25.5", "30.2"],
        "humedad": ["60.0", "55.0"],
        "viento": ["10.0", "15.0"],
        "lluvia": ["0.0", "5.0"]
    }

    df = pd.DataFrame(datos_prueba)
        #Ejecutar ETL de transformar tipos de datos
    resultado = transformar_datos(df)

        # Comprobar que zona_id es entero
    assert pd.api.types.is_integer_dtype(
        resultado["zona_id"]
    )

        # Comprobar que fecha tiene formato datetime
    assert pd.api.types.is_datetime64_any_dtype(
        resultado["fecha_datos"]
    )

        # Comprobar que los datos meteorológicos son float
    columnas_float = [
        "temperatura",
        "humedad",
        "viento",
        "lluvia"
    ]

    for columna in columnas_float:
        assert pd.api.types.is_float_dtype(
            resultado[columna]
        )


        ##Comprobar que los errores de tipo se registran en los logs: 
        #Si el proceso de transformación encuentra valores que no se pueden convertir al tipo esperado, estos casos deben ser registrados en el log con un mensaje de error específico.

def test_tipos_invalidos_logs():

    datos_prueba = {
        "zona_id": ["zona_erronea"],
        "fecha_datos": ["fecha_invalida"],
        "temperatura": ["temp_error"],
        "humedad": ["hum_error"],
        "viento": ["viento_error"],
        "lluvia": ["lluvia_error"]
    }

    df = pd.DataFrame(datos_prueba)

    # Ejecutar ETL
    resultado = transformar_datos(df)

    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    # Validar registro en los LOGS de registros rechazados por tipo incorrecto
    assert "Error convirtiendo zona" in contenido_log

    assert "Error convirtiendo fecha" in contenido_log

    assert "Error convirtiendo temperatura" in contenido_log

    assert "Error convirtiendo humedad" in contenido_log

    assert "Error convirtiendo viento" in contenido_log

    assert "Error convirtiendo lluvia" in contenido_log