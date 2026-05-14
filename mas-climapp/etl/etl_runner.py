import logging
from extract import extraer_desde_api
from transform import limpiar_datos
from load import cargar_datos

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ejecutar_pipeline():
    logger.info("=== INICIANDO PIPELINE ETL ===")
    
    logger.info("Fase 1: Extrayendo datos de AEMET...")
    df_bruto = extraer_desde_api()
    
    if df_bruto is not None and not df_bruto.empty:
        logger.info("Fase 2: Limpiando y transformando datos...")
        df_limpio = limpiar_datos(df_bruto)
        
        if df_limpio is not None and not df_limpio.empty:
            logger.info("Fase 3: Cargando datos en la base de datos SQL...")
            exito = cargar_datos(df_limpio, nombre_tabla="medicion")
            
            if exito:
                logger.info("=== PIPELINE ETL FINALIZADO CON ÉXITO ===")
            else:
                logger.error("=== PIPELINE ETL TERMINÓ CON ERRORES EN LA CARGA ===")
        else:
            logger.error("El proceso se detuvo: La transformación eliminó todos los datos o falló.")
    else:
        logger.error("El proceso se detuvo: Falló la extracción de la API.")

if __name__ == "__main__":
    ejecutar_pipeline()