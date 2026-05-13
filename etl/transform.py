import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def limpiar_datos(df_bruto):
    logger.info("Iniciando la transformación de datos...")
    
    filas_antes = len(df_bruto)
    df_limpio = df_bruto.drop_duplicates(subset=['fecha_datos', 'zona_id'], keep='last')    
    if len(df_limpio) < filas_antes:
        logger.info(f"Duplicados eliminados: {filas_antes - len(df_limpio)}")

    filas_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=['idema'])
    if len(df_limpio) < filas_antes:
        logger.warning(f"Registros eliminados por estación nula: {filas_antes - len(df_limpio)}")
        
    filas_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=['fint'])
    if len(df_limpio) < filas_antes:
        logger.warning(f"Registros eliminados por fecha nula: {filas_antes - len(df_limpio)}")

    if 'prec' in df_limpio.columns:
        ip_mask = df_limpio['prec'].astype(str).str.strip() == 'Ip'
        cantidad_ip = ip_mask.sum()
        if cantidad_ip > 0:
            df_limpio.loc[ip_mask, 'prec'] = '0.0'
            logger.info(f"Dato modificado: Transformadas {cantidad_ip} ocurrencias de lluvia 'Ip' a 0.0")

    try:
        df_limpio['fint'] = pd.to_datetime(df_limpio['fint'], errors='coerce')
    except Exception as e:
        logger.error(f"Error convirtiendo fecha: {e}")

    metricas = ['ta', 'tamax', 'tamin', 'hr', 'prec', 'vv']
    for col in metricas:
        if col in df_limpio.columns:
            try:
                df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')
            except Exception as e:
                logger.error(f"Error convirtiendo columna {col}: {e}")

    logger.info(f"Transformación completada. Quedan {len(df_limpio)} filas válidas.")
    return df_limpio

if __name__ == "__main__":
    from extract import extraer_desde_api
    
    df_bruto = extraer_desde_api()
    if df_bruto is not None and not df_bruto.empty:
        df_limpio = limpiar_datos(df_bruto)
        print("\n--- Primeros 3 registros de datos LIMPIOS ---")
        columnas_interes = ['idema', 'ubi', 'fint', 'ta', 'prec']
        columnas_disponibles = [col for col in columnas_interes if col in df_limpio.columns]
        print(df_limpio[columnas_disponibles].head(3))