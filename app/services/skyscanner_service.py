"""
Skyscanner Service — Alimentato da BoostedTravel per dati reali.
"""
from flask import current_app
from datetime import datetime
from boostedtravel import BoostedTravel

def get_skyscanner_url(origin, destination, departure_date, adults=1, airline=None):
    """Genera il deep link per Skyscanner con parametri specifici."""
    try:
        if isinstance(departure_date, str):
            date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        else:
            date_obj = departure_date
        # Il path con YYMMDD è il più standard per i deep link
        sk_date = date_obj.strftime('%y%m%d')
    except Exception:
        sk_date = str(departure_date).replace('-', '')[2:8]
    
    url = f"https://www.skyscanner.it/transport/flights/{origin.lower()}/{destination.lower()}/{sk_date}/"
    params = [
        f"adults={adults}",
        "cabinclass=economy",
        "culture=it-IT",
        "market=IT",
        "currency=EUR",
        "ref=home"
    ]
    if airline:
        params.append(f"airlines={airline}")
    
    return f"{url}?{'&'.join(params)}"

def search_flights(origin, destination, departure_date, adults=1, currency='EUR'):
    """
    Cerca voli REALI usando BoostedTravel.
    """
    api_key = current_app.config.get('BOOSTEDTRAVEL_API_KEY')
    if not api_key:
        current_app.logger.warning("BOOSTEDTRAVEL_API_KEY non configurata.")
        return []

    try:
        bt = BoostedTravel(api_key=api_key)
        # Assicuriamoci che la data sia in formato YYYY-MM-DD
        if isinstance(departure_date, datetime):
            date_str = departure_date.strftime('%Y-%m-%d')
        else:
            date_str = departure_date

        flights = bt.search(origin, destination, date_str)
        
        formatted_results = []
        for offer in flights.offers:
            # outbound è di tipo FlightRoute
            route = offer.outbound
            if not route.segments:
                continue
                
            first_seg = route.segments[0]
            last_seg = route.segments[-1]
            
            # Formattiamo gli orari (es. da "2026-04-15T10:00:00" a "10:00")
            try:
                dep_time = first_seg.departure.split('T')[1][:5]
                arr_time = last_seg.arrival.split('T')[1][:5]
            except Exception:
                dep_time = "--:--"
                arr_time = "--:--"
            
            formatted_results.append({
                'source': 'Skyscanner (Boosted)',
                'id': offer.id,
                'airline': first_seg.airline,
                'airline_name': first_seg.airline_name or first_seg.airline,
                'departure_time': dep_time,
                'arrival_time': arr_time,
                'duration': route.duration_human,
                'stops': 'Diretto' if route.stopovers == 0 else f"{route.stopovers} scalo/i",
                'price': float(offer.price),
                'currency': offer.currency,
                'skyscanner_url': get_skyscanner_url(origin, destination, departure_date, adults=adults, airline=first_seg.airline)
            })
            
        return formatted_results

    except Exception as e:
        current_app.logger.error(f"BoostedTravel search failed: {e}")
        return []

def resolve_location(query):
    """Risolve una città o aeroporto in codici IATA tramite BoostedTravel."""
    api_key = current_app.config.get('BOOSTEDTRAVEL_API_KEY')
    if not api_key or not query:
        return []

    try:
        bt = BoostedTravel(api_key=api_key)
        locations = bt.resolve_location(query)
        
        formatted = []
        for loc in locations:
            # mappiamo i campi per consistenza con il frontend
            formatted.append({
                'i': loc.get('iata', ''),
                'n': loc.get('name', ''),
                'c': loc.get('city', ''),
                't': loc.get('type', 'airport')
            })
        return formatted
    except Exception as e:
        current_app.logger.error(f"BoostedTravel resolve_location failed: {e}")
        return []
