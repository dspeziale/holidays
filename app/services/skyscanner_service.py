"""
Skyscanner Service — Alimentato da BoostedTravel per dati reali.
"""
from flask import current_app
from datetime import datetime
from boostedtravel import BoostedTravel

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
                'skyscanner_url': get_skyscanner_url(origin, destination, departure_date)
            })
            
        return formatted_results

    except Exception as e:
        current_app.logger.error(f"BoostedTravel search failed: {e}")
        return []
