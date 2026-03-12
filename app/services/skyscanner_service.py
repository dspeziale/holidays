"""
Skyscanner Service — con fallback demo senza API key.
Segue il paradigma di GetYourGuide e Amadeus.
"""
import requests
from flask import current_app
from datetime import datetime

# ── Catalogo demo ──────────────────────────────────────────────────────────────
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
    },
    {
        "id": "demo-2",
        "origin": "ROM",
        "destination": "LON",
        "airline": "BA",
        "airline_name": "British Airways",
        "departure_time": "14:20",
        "arrival_time": "17:10",
        "duration": "2h 50m",
        "stops": "Diretto",
        "price": 120.0,
        "currency": "EUR"
    },
    {
        "id": "demo-3",
        "origin": "MIL",
        "destination": "PAR",
        "airline": "AF",
        "airline_name": "Air France",
        "departure_time": "09:00",
        "arrival_time": "10:35",
        "duration": "1h 35m",
        "stops": "Diretto",
        "price": 95.0,
        "currency": "EUR"
    },
    {
        "id": "demo-4",
        "origin": "ROM",
        "destination": "NYC",
        "airline": "AZ",
        "airline_name": "ITA Airways",
        "departure_time": "10:00",
        "arrival_time": "14:20",
        "duration": "9h 20m",
        "stops": "1 scalo",
        "price": 550.0,
        "currency": "EUR"
    }
]

def _use_demo():
    """Controlla se usare il fallback demo (API key assente)."""
    # Skyscanner non ha una semplice API key "partner" pubblica come GYG in molti casi,
    # qui simuliamo il controllo di una ipotetica SKYSCANNER_API_KEY.
    api_key = current_app.config.get('SKYSCANNER_API_KEY')
    return not api_key

def get_skyscanner_url(origin, destination, departure_date):
    """Genera il deep link per Skyscanner."""
    try:
        date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        skyscanner_date = date_obj.strftime('%y%m%d')
    except Exception:
        skyscanner_date = departure_date.replace('-', '')[2:]
    
    return f"https://www.skyscanner.it/trasporti/voli/{origin.lower()}/{destination.lower()}/{skyscanner_date}/"

def search_flights(origin, destination, departure_date, adults=1, currency='EUR'):
    """
    Cerca voli. In questa implementazione 'prova', usiamo principalmente i dati demo
    o facciamo da tramite per la costruzione dei risultati con link Skyscanner.
    """
    if _use_demo():
        # Filtro base per la demo
        results = [
            f for f in _DEMO_FLIGHTS 
            if f['origin'] == origin.upper() and f['destination'] == destination.upper()
        ]
        # Se non ci sono match specifici, mostriamo comunque qualcosa per la 'prova'
        if not results:
            results = _DEMO_FLIGHTS[:2]
            
        for r in results:
            r['skyscanner_url'] = get_skyscanner_url(origin, destination, departure_date)
            
        return results

    # Qui andrebbe l'integrazione API reale se SKYSCANNER_API_KEY fosse presente
    return []
