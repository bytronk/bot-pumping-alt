import requests
from bs4 import BeautifulSoup
import time
from config import URL_FUNDING, USER_AGENT, REFERER, INTERVALO_REVISION

def obtener_datos_funding():
    """
    Realiza el scraping de la página de funding rate y extrae los datos de cada fila.
    Retorna una lista de diccionarios con la información de cada cripto.
    Ahora se extrae también el enlace asociado al nombre de la cripto,
    asegurándose de que sea una URL absoluta.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": REFERER
    }
    try:
        response = requests.get(URL_FUNDING, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("Error al acceder a la URL:", e)
        return []
    
    # Procesar el HTML con BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    # Seleccionamos el <tbody> de la tabla que contiene las filas
    tbody = soup.select_one("body > div.body-wrapper > div.main-content > div > div.listing > div.table-wrapper > table > tbody")
    
    if not tbody:
        print("No se encontró la tabla de datos.")
        return []
    
    cryptos = []
    filas = tbody.find_all("tr")
    
    for fila in filas:
        # Seleccionamos los elementos según los selectores proporcionados
        funding_elem = fila.select_one("td.red")
        nombre_elem = fila.select_one("td.coin-name > a > span:nth-of-type(1)")
        id_elem = fila.select_one("td.coin-name > a > span:nth-of-type(2)")
        # Extraemos el enlace asociado a la cripto
        enlace_elem = fila.select_one("td:nth-child(1) > div > ul > li:nth-child(2) > a")
        
        if not (funding_elem and nombre_elem and id_elem and enlace_elem):
            continue
        
        # Extraer y limpiar el texto del funding rate
        funding_text = funding_elem.get_text(strip=True)
        funding_text = funding_text.replace('%', '').replace(',', '.')
        try:
            funding_rate = float(funding_text)
        except ValueError:
            continue
        
        nombre = nombre_elem.get_text(strip=True)
        coin_id = id_elem.get_text(strip=True)
        # Extraer el atributo href del enlace
        enlace = enlace_elem.get("href")
        
        # Si el enlace no es absoluto, se antepone la URL base
        if not enlace.startswith("http"):
            enlace = "https://es.coinalyze.net" + enlace
        
        # Filtrar: solo se muestran las criptos cuyo funding rate sea -0.05% o inferior
        if funding_rate <= -0.05:
            cryptos.append({
                "nombre": nombre,
                "id": coin_id,
                "funding_rate": funding_rate,
                "enlace": enlace
            })
    
    return cryptos

def main():
    while True:
        print("Revisando datos de Funding Rate...")
        cryptos_filtradas = obtener_datos_funding()
        if cryptos_filtradas:
            print("Criptos con Funding Rate <= -0.05%:")
            for cripto in cryptos_filtradas:
                # Se muestra el nombre de la cripto como un enlace (formato Markdown)
                print(f"Moneda: [{cripto['nombre']}]({cripto['enlace']}) (ID: {cripto['id']}), Funding Rate: {cripto['funding_rate']}%")
        else:
            print("No se encontraron criptos que cumplan la condición.")
        
        # Espera el intervalo definido en config.py antes de la siguiente revisión
        time.sleep(INTERVALO_REVISION)

if __name__ == '__main__':
    main()
