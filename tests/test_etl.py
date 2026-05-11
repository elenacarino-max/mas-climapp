import pytest
import pandas as pd

#Comprobación de nulos en el ETL: si el proceso de limpieza funciona, no deberían quedar valores nulos en el DataFrame final.
#Traemos la función a probar. 

from etl.transform import limpiar_datos_nulos

#Definir la función de test para la limpieza de nulos. En este caso, comprobamos que se eliminar las filas con nulos. ""

def test_valores_nulos():

    # Datos de ejemplo con nulos
    datos_prueba = {
        "municipio": ["Madrid", None, "Barcelona"],
        "fecha": ["None", "2024-06-01", "2024-06-02"],
        "temperatura": [25.5, 30.2, None],
        "humedad": [60, None, 55],
        "viento": [10, 15, None],
        "lluvia": [0, None, 5]
    }

    df = pd.DataFrame(datos_prueba)

    # ejecutar limpieza ETL
    limpiar_datos_df = limpiar_datos_nulos(df)

    # comprobar que no quedan nulos
    assert limpiar_datos_df.isnull().sum().sum() == 0

    #Comprobar duplicados en el ETL: si el proceso de limpieza funciona, no deberían quedar filas duplicadas en el DataFrame final.