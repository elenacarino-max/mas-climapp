import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def limpiar_datos(df_bruto):
    logger.info("Starting data transformation...")
    
    # ⚠️ TASK 2 FIX: We use 'fint' and 'idema' here because we haven't renamed them yet!
    filas_antes = len(df_bruto)
    df_limpio = df_bruto.drop_duplicates(subset=['fint', 'idema'], keep='last')    
    if len(df_limpio) < filas_antes:
        logger.info(f"Duplicates removed: {filas_antes - len(df_limpio)}")

    filas_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=['idema'])
    if len(df_limpio) < filas_antes:
        logger.warning(f"Records removed due to null station: {filas_antes - len(df_limpio)}")
        
    filas_antes = len(df_limpio)
    df_limpio = df_limpio.dropna(subset=['fint'])
    if len(df_limpio) < filas_antes:
        logger.warning(f"Records removed due to null date: {filas_antes - len(df_limpio)}")

    if 'prec' in df_limpio.columns:
        ip_mask = df_limpio['prec'].astype(str).str.strip() == 'Ip'
        cantidad_ip = ip_mask.sum()
        if cantidad_ip > 0:
            df_limpio.loc[ip_mask, 'prec'] = '0.0'
            logger.info(f"Data modified: Transformed {cantidad_ip} occurrences of 'Ip' rain to 0.0")

    try:
        df_limpio['fint'] = pd.to_datetime(df_limpio['fint'], errors='coerce')
    except Exception as e:
        logger.error(f"Error converting date: {e}")

    metricas = ['ta', 'tamax', 'tamin', 'hr', 'prec', 'vv']
    for col in metricas:
        if col in df_limpio.columns:
            try:
                df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')
            except Exception as e:
                logger.error(f"Error converting column {col}: {e}")

    # 🎯 TASK 4: Column Mapping goes HERE, after all the cleaning is done
    mapeo_columnas = {
        'idema': 'zona_id',
        'fint': 'fecha_datos',
        'ta': 'temperatura',
        'prec': 'lluvia',
        'vv': 'viento',
        'hr': 'humedad'
    }
    
    df_limpio = df_limpio.rename(columns=mapeo_columnas)
    
    columnas_finales = ['zona_id', 'fecha_datos', 'temperatura', 'lluvia', 'viento', 'humedad']
    df_limpio = df_limpio[[col for col in columnas_finales if col in df_limpio.columns]]

    logger.info(f"Transformation complete. {len(df_limpio)} valid rows remain.")
    return df_limpio