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
        "municipio": ["Alicante", None, "Madrid", "Barcelona", "Valencia"],
        "fecha": [
            pd.NaT,
            pd.Timestamp("2024-06-01 10:00:00"),
            pd.Timestamp("2024-06-02 12:00:00"),
            pd.Timestamp("2024-06-04 08:00:00"),
            pd.Timestamp("2024-06-03 08:00:00")
        ],
        "temperatura": [25.5, 30.2, None, None, None],
        "humedad": [60.0, None, None, 55.0, None],
        "viento": [10.0, 15.0, None, None, None],
        "lluvia": [0.0, None, 5.0, None, None]
    }

    df = pd.DataFrame(datos_prueba)
    # Asegurar tipo datos
    resultado = transformar_datos(df)


    # ejecutar limpieza ETL
    limpiar_datos_df = limpiar_datos_nulos(df)

    # comprobar que no quedan municipios nulos
    assert limpiar_datos_df["municipio"].isnull().sum() == 0

    # comprobar que no quedan fechas nulas
    assert limpiar_datos_df["fecha"].isnull().sum() == 0
    # comprobar que fecha es datetime
    assert pd.api.types.is_datetime64_any_dtype(
        limpiar_datos_df["fecha"]
    )

    # No debe existir ninguna fila con TODOS los valores meteorológicos nulos
    columnas_meteo = ["temperatura", "humedad", "viento", "lluvia"]

    filas_todo_nulo = limpiar_datos_df[columnas_meteo].isnull().all(axis=1)

    assert filas_todo_nulo.sum() == 0

    # Debe conservarse Barcelona porque tiene datos meteorológicos válidos
    assert "Barcelona" in limpiar_datos_df["municipio"].values
    # Comprobar que los NULL parciales se conservan como NULL
    fila_barcelona = limpiar_datos_df[
        limpiar_datos_df["municipio"] == "Barcelona"
    ].iloc[0]

    # temperatura sigue siendo NULL
    assert pd.isnull(fila_barcelona["temperatura"])

    # viento sigue siendo NULL
    assert pd.isnull(fila_barcelona["viento"])

    # lluvia sigue siendo NULL
    assert pd.isnull(fila_barcelona["lluvia"])

    # humedad sigue siendo NULL
    assert pd.isnotnull(fila_barcelona["humedad"])

    # Debe conservarse Madrid porque tiene datos meteorológicos válidos
    assert "Madrid" in limpiar_datos_df["municipio"].values
    # Comprobar que los NULL parciales se conservan como NULL
    fila_barcelona = limpiar_datos_df[
        limpiar_datos_df["municipio"] == "Madrid"
    ].iloc[0]

    # temperatura sigue siendo NULL
    assert pd.isnull(fila_barcelona["temperatura"])

    # viento sigue siendo NULL
    assert pd.isnull(fila_barcelona["viento"])

    # lluvia sigue siendo NULL
    assert pd.isnotnull(fila_barcelona["lluvia"])

    # humedad sigue siendo NULL
    assert pd.isnull(fila_barcelona["humedad"])

    # Valencia debe eliminarse porque todos los valores meteorológicos son nulos
    assert "Valencia" not in limpiar_datos_df["municipio"].values



    #Comprobar que los descartados se han incluido en los logs. En el proceso de limpieza, se registran los casos de filas descartadas según lo definido.
    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    # Validar registros descartados
    assert "municipio nulo" in contenido_log
    assert "fecha nula" in contenido_log
    assert "todos los valores meteorológicos nulos" in contenido_log


    ##Comprobar duplicados en el ETL: si el proceso de limpieza funciona, no deberían quedar filas duplicadas en el DataFrame final.
    #Se consideran duplicados aquellos registros que tengan el mismo municipio y la misma fecha de registro. En caso de encontrar duplicados, se eliminará la fila completa.

def test_filas_duplicadas():

    datos_prueba = {
        "municipio": ["Madrid", "Madrid", "Barcelona"],
        "fecha": [
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

    # Comprobar que no hay duplicados. Solo debería guardarse Barcelona 11:00
    duplicados = limpiar_datos_df.duplicated(
        subset=["municipio", "fecha"]
    )

    assert duplicados.sum() == 0

    #Comprobar que los descartados se han incluido en los logs. En el proceso de limpieza, se registran los descartados por duplicidad según lo definido.
    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    # Validar log duplicados
    assert "Duplicado eliminado" in contenido_log


    ## Comprobar tipo de datos en el ETL: después de la limpieza, los tipos de datos deben ser consistentes con lo esperado.

def test_tipos_datos():

    datos_prueba = {
        "municipio": ["Madrid", "Barcelona"],
        "fecha": [
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

    # Comprobar que municipio es string
    assert pd.api.types.is_string_dtype(
        resultado["municipio"]
    ) or pd.api.types.is_object_dtype(
        resultado["municipio"]
    )

    # Comprobar que fecha tiene formato datetime
    assert pd.api.types.is_datetime64_any_dtype(
        resultado["fecha"]
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

    # Leer log
    with open("etllog.txt", "r", encoding="utf-8") as log:
        contenido_log = log.read()

    #Comprobar que los descartados se han incluido en los logs. En el proceso de limpieza, se registran los descartados por tipo de dato según lo definido.
    # Validar errores registrados
    assert "Error convirtiendo municipio" in contenido_log

    assert "Error convirtiendo fecha" in contenido_log

    assert "Error convirtiendo temperatura" in contenido_log

    assert "Error convirtiendo humedad" in contenido_log

    assert "Error convirtiendo viento" in contenido_log

    assert "Error convirtiendo lluvia" in contenido_log