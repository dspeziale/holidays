import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_kiwi():
    api_key = os.environ.get('KIWI_API_KEY')
    
    if not api_key:
        print("❌ KIWI_API_KEY non trovata in .env")
        return

    print(f"Testing Kiwi Tequila API...")
    
    url = "https://api.tequila.kiwi.com/v2/search"
    headers = {
        "apikey": api_key,
        "accept": "application/json"
    }
    params = {
        "fly_from": "ROM",
        "fly_to": "LON",
        "date_from": "15/06/2026",
        "date_to": "15/06/2026",
        "adults": 1,
        "curr": "EUR",
        "limit": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get('data', [])
        print(f"✅ Successo! Trovati {len(results)} voli.")
        if results:
            print(f"Esempio: {results[0]['airlines'][0]} - Prezzo: {results[0]['price']} EUR")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_kiwi()
