import os

"""
config.py
----------
Módulo de configuración común para el Bot de Señales.

Incluye:
  - Intervalo de revisión del bot (en segundos)
  - URLs para scraping
  - Encabezados HTTP comunes
  - Configuración del email (servidor SMTP, credenciales, destinatarios)
  - Configuración del logging (archivo, nivel, rotación)
"""

# Intervalo de revisión para el bot (en segundos)
INTERVALO_REVISION = 120

# URLs para scraping
URL_FUNDING = "https://es.coinalyze.net/?order_by=fr_avg&order_dir=asc&columns=aQ"
URL_PCHANGE = "https://es.coinalyze.net/?order_by=price_24hour_pchange&order_dir=desc&columns=Yg"

# Encabezados HTTP comunes
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36")
REFERER = "https://es.coinalyze.net/"

# Configuración del email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = os.environ.get("USERNAME")  # para el email
PASSWORD = os.environ.get("EMAIL_PASSWORD")  # usa un nombre descriptivo
FROM_EMAIL = USERNAME
# Destinatarios separados por comas (se usará en el código para formar una lista)
TO_EMAIL = "bytronk@hotmail.com" #, josezorzo.jmnz@gmail.com, elnuevodeuron8@gmail.com, miguelangellopezsanz726@gmail.com"

# Configuración del Telegram Bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Configuración del logging
LOG_FILE = "aggregator.log"
LOG_LEVEL = "INFO"
# Rotación de logs: se creará un nuevo archivo cada 1 día y se conservará 1 backup (aprox. 48 horas de registros)
LOG_ROTATION_WHEN = "D"
LOG_ROTATION_INTERVAL = 1
LOG_BACKUP_COUNT = 1
