import requests
from bs4 import BeautifulSoup
import time
from config import URL_PCHANGE, USER_AGENT, REFERER, INTERVALO_REVISION

def obtener_datos_pchange():
    """
    Realiza el scraping de la página del cambio de precio en 24h y extrae los datos de cada fila.
    Retorna una lista de diccionarios con la información de cada cripto que cumpla la condición.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER
    }
    
    try:
        response = requests.get(URL_PCHANGE, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error al acceder a la URL:", e)
        return []
    
    # Procesamos el HTML obtenido
    soup = BeautifulSoup(response.text, 'html.parser')
    # Seleccionamos el <tbody> que contiene las filas de la tabla
    tbody = soup.select_one("body > div > div.main-content > div > div.listing > div.table-wrapper > table > tbody")
    
    if not tbody:
        print("No se encontró la tabla de datos.")
        return []
    
    cryptos = []
    filas = tbody.find_all("tr")
    
    for fila in filas:
        # Selector para el cambio de precio en 24h (columna con clase "green")
        pchange_elem = fila.select_one("td.green")
        # Selector para el nombre (Moneda) y para el ID
        nombre_elem = fila.select_one("td.coin-name > a > span:nth-of-type(1)")
        id_elem = fila.select_one("td.coin-name > a > span:nth-of-type(2)")
        
        if not (pchange_elem and nombre_elem and id_elem):
            continue
        
        # Extraer el texto del cambio de precio y limpiarlo (quitamos el símbolo '%' y reemplazamos comas por puntos)
        pchange_text = pchange_elem.get_text(strip=True)
        pchange_text = pchange_text.replace('%', '').replace(',', '.')
        try:
            pchange_value = float(pchange_text)
        except ValueError:
            continue
        
        nombre = nombre_elem.get_text(strip=True)
        coin_id = id_elem.get_text(strip=True)
        
        # Filtrar: solo incluir criptos con cambio en 24h >= 5%
        if pchange_value >= 5:
            cryptos.append({
                "nombre": nombre,
                "id": coin_id,
                "pchange_24h": pchange_value
            })
    
    return cryptos

def main():
    while True:
        print("Revisando datos de Cambio de Precio 24h...")
        cryptos_filtradas = obtener_datos_pchange()
        if cryptos_filtradas:
            print("Criptos con un cambio de precio de + 5%:")
            for cripto in cryptos_filtradas:
                print(f"Moneda: {cripto['nombre']} (ID: {cripto['id']}), Cambio de precio: {cripto['pchange_24h']}%")
        else:
            print("No se encontraron criptos que cumplan la condición.")
        
        # Esperar el intervalo definido en config.py antes de la siguiente revisión
        time.sleep(INTERVALO_REVISION)

if __name__ == '__main__':
    main()
