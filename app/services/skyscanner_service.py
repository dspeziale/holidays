from flask import current_app
from datetime import datetime
from swoop import search as swoop_search
from boostedtravel import BoostedTravel

def _format_swoop_time(t):
    """Formatta tuple (h, m) in stringa HH:MM."""
    if isinstance(t, tuple) and len(t) >= 2:
        return f"{t[0]:02d}:{t[1]:02d}"
    return "--:--"

def _format_swoop_duration(m):
    """Formatta minuti totali in stringa leggibile (es '1h 30m')."""
    if not m: return "0m"
    h = m // 60
    rem = m % 60
    return f"{h}h {rem}m" if h > 0 else f"{rem}m"

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
    Cerca voli REALI usando Swoop.
    """
    try:
        # Assicuriamoci che la data sia in formato YYYY-MM-DD
        if isinstance(departure_date, datetime):
            date_str = departure_date.strftime('%Y-%m-%d')
        else:
            date_str = departure_date

        # Eseguiamo la ricerca con Swoop
        results = swoop_search(origin.upper(), destination.upper(), date_str)
        
        formatted_results = []
        if not results or not results.results:
            return []

        for option in results.results:
            try:
                if not option.legs:
                    continue
                    
                # Prendiamo il primo leg (sola andata per ora)
                leg = option.legs[0]
                iti = leg.itinerary
                if not iti or not iti.flights:
                    continue
                    
                first_flight = iti.flights[0]
                last_flight = iti.flights[-1]
                
                # Formattiamo gli orari usando le tuple di Swoop (h, m)
                dep_time = _format_swoop_time(iti.departure_time)
                # L'arrivo lo prendiamo dall'ultimo volo della tratta
                arr_time = _format_swoop_time(getattr(last_flight, 'arrival_time', (0,0)))
                
                # Info compagnia aerea (preferiamo Itinerary che è più affidabile)
                air_code = getattr(iti, 'airline_code', getattr(first_flight, 'airline_code', '??'))
                air_name = iti.airline_names[0] if (hasattr(iti, 'airline_names') and iti.airline_names) else getattr(first_flight, 'airline_name', air_code)
                
                formatted_results.append({
                    'source': 'Skyscanner (Swoop)',
                    'id': f"swoop_{option.price}_{iti.departure_time[0]}",
                    'airline': air_code,
                    'airline_name': air_name,
                    'departure_time': dep_time,
                    'arrival_time': arr_time,
                    'duration': _format_swoop_duration(iti.travel_time),
                    'stops': 'Diretto' if iti.stop_count == 0 else f"{iti.stop_count} scalo/i",
                    'price': float(option.price),
                    'currency': currency,
                    'skyscanner_url': get_skyscanner_url(origin, destination, departure_date, adults=adults, airline=air_code)
                })
            except Exception as e:
                current_app.logger.error(f"Error processing Swoop option: {e}")
                continue
            
        return formatted_results

    except Exception as e:
        current_app.logger.error(f"Swoop search failed: {e}")
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
