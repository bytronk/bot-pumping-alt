import time
import logging
from logging.handlers import TimedRotatingFileHandler

# Importamos las funciones de los otros scrapers
from funding_scraper import obtener_datos_funding
from pchange_scraper import obtener_datos_pchange

# Importamos las funciones de notificación (email y Telegram) desde notifications.py
from notifications import send_email, send_telegram_message

# Importar configuraciones comunes
from config import (
    INTERVALO_REVISION,
    LOG_FILE,
    LOG_LEVEL,
    LOG_ROTATION_WHEN,
    LOG_ROTATION_INTERVAL,
    LOG_BACKUP_COUNT
)

# ---------------------------
# Configuración del logging
# ---------------------------
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Handler para archivo con rotación (cada 1 día, conservando 1 respaldo)
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when=LOG_ROTATION_WHEN, interval=LOG_ROTATION_INTERVAL, backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler para mostrar logs en la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ---------------------------
# Función para obtener datos agregados
# ---------------------------
def obtener_datos_agregados():
    """
    Obtiene los datos del funding y del cambio de precio (pchange),
    y devuelve una lista con las criptos que se encuentran en ambas listas,
    es decir, que coinciden en nombre o en ID.
    Se incluye el campo 'enlace' extraído en funding_scraper.py.
    """
    funding_data = obtener_datos_funding()
    pchange_data = obtener_datos_pchange()
    
    criptos_coincidentes = []
    for crypto_fund in funding_data:
        for crypto_pchange in pchange_data:
            if (crypto_fund["id"].lower() == crypto_pchange["id"].lower() or 
                crypto_fund["nombre"].lower() == crypto_pchange["nombre"].lower()):
                crypto_combinada = {
                    "nombre": crypto_fund["nombre"],
                    "id": crypto_fund["id"],
                    "funding_rate": crypto_fund["funding_rate"],
                    "pchange_24h": crypto_pchange["pchange_24h"],
                    "enlace": crypto_fund.get("enlace", "#")
                }
                criptos_coincidentes.append(crypto_combinada)
                break  # Salir del ciclo interno al encontrar coincidencia
    return criptos_coincidentes

# ---------------------------
# Función principal
# ---------------------------
def main():
    # Enviar notificación de inicio
    send_email(
        "Bot Pumping Alt iniciado",
        "<p>El bot de señales ha comenzado a ejecutarse. <br>"
        "Recibirás alertas de Criptos con un <strong style='color: #1E90FF;'>Funding Rate negativo</strong> "
        "y un cambio de precio de más de un <strong style='color: #1E90FF;'>5% en 24 horas</strong>.</p>"
    )
    send_telegram_message("<b>Bot Pumping Alt iniciado</b>\nEl bot de señales ha comenzado a ejecutarse.")
    logging.info("Bot Pumping Alt iniciado y notificación de inicio enviada.")

    # Variable para almacenar los IDs de las criptos notificadas en la iteración previa
    previous_ids = set()

    while True:
        logging.info("Obteniendo datos agregados (intersección de funding y cambio de precio)...")
        criptos_agregadas = obtener_datos_agregados()
        
        # Conjunto de IDs de la lista actual (convertidos a minúsculas para consistencia)
        current_ids = {crypto["id"].lower() for crypto in criptos_agregadas}
        # Determinar nuevos IDs que no estaban en la iteración anterior
        new_ids = current_ids - previous_ids

        if new_ids:
            new_coins = [crypto for crypto in criptos_agregadas if crypto["id"].lower() in new_ids]
            for coin in new_coins:
                subject = f"Nueva señal: {coin['nombre']} ({coin['id']})"
                # Mensaje para email (con HTML completo y estilos)
                email_message = (
                    "<p>Se ha detectado una nueva cripto que cumple las condiciones:</p>"
                    f"<p>Nombre: <a href='{coin['enlace']}' target='_blank' style='text-decoration: none;'>{coin['nombre']}</a></p>"
                    f"<p>ID: <a href='{coin['enlace']}' target='_blank' style='text-decoration: none;'>{coin['id']}</a></p>"
                    f"<p>Funding Rate: <span style='color: red;'>{coin['funding_rate']}%</span></p>"
                    f"<p>Cambio de precio en 24h: <span style='color: green;'>{coin['pchange_24h']}%</span></p>"
                )
                # Mensaje para Telegram (formateado solo con etiquetas permitidas)
                telegram_message = (
                    f"<b>{subject}</b>\n"
                    f"Nombre: <a href='{coin['enlace']}'>{coin['nombre']}</a>\n"
                    f"ID: <a href='{coin['enlace']}'>{coin['id']}</a>\n"
                    f"Funding Rate: <b>{coin['funding_rate']}%</b>\n"
                    f"Cambio de precio 24h: <b>{coin['pchange_24h']}%</b>"
                )
                # Envío de notificaciones
                send_email(subject, email_message)
                send_telegram_message(telegram_message)
                logging.info("Notificación enviada para la cripto: %s (%s)", coin["nombre"], coin["id"])
        else:
            logging.info("No hay nuevas criptos para notificar.")

        # Registro de las criptos agregadas para depuración
        if criptos_agregadas:
            for crypto in criptos_agregadas:
                logging.info("Cripto: [%s](%s) (ID: %s), Funding Rate: %s%%, Cambio de precio 24h: %s%%",
                             crypto["nombre"], crypto["enlace"], crypto["id"],
                             crypto["funding_rate"], crypto["pchange_24h"])
        else:
            logging.info("No se encontraron criptos que cumplan ambas condiciones.")

        logging.info("----------------------------------------------------")
        previous_ids = current_ids
        time.sleep(INTERVALO_REVISION)

if __name__ == "__main__":
    main()
