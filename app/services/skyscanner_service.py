from flask import current_app
from datetime import datetime
try:
    from swoop import search as swoop_search
except ImportError:
    swoop_search = None
from boostedtravel import BoostedTravel

def _format_swoop_time(t):
    """Formatta tuple (h, m) in stringa HH:MM."""
    if isinstance(t, tuple) and len(t) >= 2:
        return f"{t[0]:02d}:{t[1]:02d} GMT"
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

def search_flights(origin, destination, departure_date, return_date=None, adults=1, currency='EUR'):
    """
    Cerca voli REALI usando Swoop.
    """
    if swoop_search is None:
        current_app.logger.error("Swoop library not available.")
        return []
        
    try:
        # Assicuriamoci che le date siano in formato YYYY-MM-DD
        def _fmt_date(d):
            if isinstance(d, datetime):
                return d.strftime('%Y-%m-%d')
            return d

        date_str = _fmt_date(departure_date)
        ret_date_str = _fmt_date(return_date) if return_date else None

        # Eseguiamo la ricerca con Swoop
        if ret_date_str:
            results = swoop_search(origin.upper(), destination.upper(), date_str, return_date=ret_date_str)
        else:
            results = swoop_search(origin.upper(), destination.upper(), date_str)
        
        formatted_results = []
        if not results or not results.results:
            return []

        for option in results.results:
            if not option.legs:
                continue
            
            # Per ogni volo, mappiamo tutte le tratte (andata e ritorno)
            legs_data = []
            for leg in option.legs:
                iti = leg.itinerary
                if not iti: continue
                
                # Segmenti dettagliati della tratta
                segments = []
                for f in (iti.flights or []):
                    segments.append({
                        'departure_airport': getattr(f, 'departure_airport_code', '??'),
                        'departure_airport_name': getattr(f, 'departure_airport_name', ''),
                        'arrival_airport': getattr(f, 'arrival_airport_code', '??'),
                        'arrival_airport_name': getattr(f, 'arrival_airport_name', ''),
                        'departure_time': _format_swoop_time(getattr(f, 'departure_time', (0,0))),
                        'arrival_time': _format_swoop_time(getattr(f, 'arrival_time', (0,0))),
                        'airline': getattr(f, 'airline_code', '??'),
                        'airline_name': getattr(f, 'airline_name', 'Unknown'),
                        'flight_number': getattr(f, 'flight_number', ''),
                        'duration': _format_swoop_duration(getattr(f, 'travel_time', 0))
                    })

                legs_data.append({
                    'origin': leg.origin,
                    'destination': leg.destination,
                    'departure_time': _format_swoop_time(iti.departure_time),
                    'duration': _format_swoop_duration(iti.travel_time),
                    'stops': iti.stop_count,
                    'segments': segments
                })

            if not legs_data: continue

            # La compagnia aerea principale (quella della prima tratta dell'andata)
            first_leg = legs_data[0]
            main_airline = first_leg['segments'][0]['airline'] if first_leg['segments'] else '??'
            main_airline_name = first_leg['segments'][0]['airline_name'] if first_leg['segments'] else 'Unknown'
            
            # Orari principali (andata)
            dep_time = first_leg['departure_time']
            # L'arrivo andata è l'ultimo segmento del primo leg
            arr_time_out = first_leg['segments'][-1]['arrival_time'] if first_leg['segments'] else '--:--'
            
            # Se c'è il ritorno, mostriamo i dettagli nella UI
            summary_arrival = arr_time_out
            if len(legs_data) > 1:
                # Per il round-trip, potremmo voler mostrare una sintesi o proprio i due orari
                # Per ora manteniamo la compatibilità con il frontend esistente (dep/arr andata)
                # ma passiamo tutti i dati per l'espansione.
                pass

            formatted_results.append({
                'source': 'Skyscanner (Swoop)',
                'id': f"swoop_{option.price}_{legs_data[0]['departure_time'].replace(':', '')}",
                'airline': main_airline,
                'airline_name': main_airline_name,
                'departure_time': dep_time,
                'arrival_time': summary_arrival,
                'duration': first_leg['duration'],
                'stops': 'Diretto' if first_leg['stops'] == 0 else f"{first_leg['stops']} scalo/i",
                'price': float(option.price) * adults,
                'currency': currency,
                'legs': legs_data, # Passiamo tutto l'itinerario
                'skyscanner_url': get_skyscanner_url(origin, destination, departure_date, adults=adults, airline=main_airline)
            })
            
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
