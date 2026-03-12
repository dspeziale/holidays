import requests
from flask import current_app
from datetime import datetime

def search_flights(origin, destination, date_from, adults=1, currency='EUR'):
    """
    Search flights using Kiwi.com Tequila API.
    Docs: https://tequila.kiwi.com/portal/docs/tequila_api/search_api
    """
    api_key = current_app.config.get('KIWI_API_KEY')
    if not api_key:
        current_app.logger.warning("KIWI_API_KEY non configurata. Ricerca Kiwi saltata.")
        return None

    # Kiwi requires date in dd/mm/yyyy
    try:
        date_obj = datetime.strptime(date_from, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
    except Exception:
        formatted_date = date_from # Fallback
        
    url = "https://api.tequila.kiwi.com/v2/search"
    headers = {
        "apikey": api_key,
        "accept": "application/json"
    }
    params = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": formatted_date,
        "date_to": formatted_date,
        "adults": adults,
        "curr": currency,
        "limit": 15,
        "vehicle_type": "aircraft"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        current_app.logger.error(f"Errore durante la ricerca Kiwi: {e}")
        return None
