"""
Skyscanner Service — Integrated with real Kiwi and Amadeus data.
"""
import requests
from flask import current_app
from datetime import datetime
from app.services import kiwi_service as kiwi
from app.services import amadeus_service as amadeus

# ── Catalogo demo (Solo come fallback estremo) ─────────────────────────────────
_DEMO_FLIGHTS = [
    {
        "id": "demo-1",
        "origin": "ROM",
        "destination": "LON",
        "airline": "AZ",
        "airline_name": "ITA Airways",
        "departure_time": "10:30",
        "arrival_time": "13:15",
        "duration": "2h 45m",
        "stops": "Diretto",
        "price": 85.0,
        "currency": "EUR"
    }
]

def get_skyscanner_url(origin, destination, departure_date):
    """Genera il deep link per Skyscanner."""
    try:
        if isinstance(departure_date, str):
            date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        else:
            date_obj = departure_date
        skyscanner_date = date_obj.strftime('%y%m%d')
    except Exception:
        skyscanner_date = str(departure_date).replace('-', '')[2:8]
    
    return f"https://www.skyscanner.it/trasporti/voli/{origin.lower()}/{destination.lower()}/{skyscanner_date}/"

def search_flights(origin, destination, departure_date, adults=1, currency='EUR'):
    """
    Cerca voli REALI usando Kiwi o Amadeus e li formatta per Skyscanner.
    """
    formatted_results = []
    
    # 1. Prova con Kiwi (Real Data)
    try:
        kiwi_results = kiwi.search_flights(origin, destination, departure_date, adults, currency)
        if kiwi_results:
            for r in kiwi_results:
                carrier_code = r.get('airlines', [''])[0]
                formatted_results.append({
                    'source': 'Skyscanner (via Kiwi)',
                    'id': r['id'],
                    'airline': carrier_code,
                    'airline_name': carrier_code,
                    'departure_time': datetime.fromtimestamp(r['dTime']).strftime('%H:%M'),
                    'arrival_time': datetime.fromtimestamp(r['aTime']).strftime('%H:%M'),
                    'duration': r['fly_duration'],
                    'stops': 'Diretto' if len(r.get('route', [])) <= 1 else f"{len(r.get('route', []))-1} scalo/i",
                    'price': float(r['price']),
                    'currency': currency,
                    'skyscanner_url': get_skyscanner_url(origin, destination, departure_date)
                })
            return formatted_results
    except Exception as e:
        current_app.logger.warning(f"Kiwi failed in Skyscanner service: {e}")

    # 2. Prova con Amadeus (Real Data)
    try:
        risultati, dizionari = amadeus.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            adults=adults,
            currency=currency,
            max_results=15
        )
        if risultati:
            for r in risultati:
                carrier_code = r.get('validatingAirlineCodes', [''])[0]
                itinerary = r['itineraries'][0]
                segments = itinerary['segments']
                dep_time_raw = segments[0]['departure']['at']
                arr_time_raw = segments[-1]['arrival']['at']
                
                formatted_results.append({
                    'source': 'Skyscanner (via Amadeus)',
                    'id': r['id'],
                    'airline': carrier_code,
                    'airline_name': dizionari.get('carriers', {}).get(carrier_code, carrier_code),
                    'departure_time': dep_time_raw.split('T')[1][:5],
                    'arrival_time': arr_time_raw.split('T')[1][:5],
                    'duration': itinerary['duration'].replace('PT', '').replace('H', 'h ').replace('M', 'm'),
                    'stops': 'Diretto' if len(segments) == 1 else f"{len(segments)-1} scalo/i",
                    'price': float(r['price']['total']),
                    'currency': currency,
                    'skyscanner_url': get_skyscanner_url(origin, destination, departure_date)
                })
            return formatted_results
    except Exception as e:
        current_app.logger.warning(f"Amadeus failed in Skyscanner service: {e}")

    # 3. Demo fallback solo se tutto il resto fallisce
    results = [f for f in _DEMO_FLIGHTS if f['origin'] == origin.upper()]
    for r in results:
        r['skyscanner_url'] = get_skyscanner_url(origin, destination, departure_date)
    return results
