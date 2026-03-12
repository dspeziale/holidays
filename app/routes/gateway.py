from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from app.services import amadeus_service as amadeus
import random
from datetime import datetime, timedelta

gateway_bp = Blueprint('gateway', __name__, url_prefix='/gateway')

@gateway_bp.route('/voli')
@login_required
def voli():
    """Pagina di ricerca voli (Skyscanner simulation)."""
    return render_template('gateway/voli.html')

@gateway_bp.route('/api/voli/search')
@login_required
def api_search_voli():
    """Ricerca voli reali tramite Amadeus con link Skyscanner."""
    origin = request.args.get('origin', 'ROM').upper()
    destination = request.args.get('destination', 'LON').upper()
    departure_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    return_date = request.args.get('return_date')
    
    # Ricerca reale tramite Amadeus service
    risultati, dizionari = amadeus.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        max_results=15
    )
    
    if risultati is None:
        return jsonify({'error': 'Errore API'}), 500
        
    formatted_results = []
    
    # Mapping loghi (opzionale, Amadeus non li dà direttamente)
    carrier_logos = {
        'AZ': 'https://upload.wikimedia.org/wikipedia/commons/e/e0/ITA_Airways_logo.svg',
        'LH': 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Lufthansa_Logo_2018.svg',
        'BA': 'https://upload.wikimedia.org/wikipedia/en/d/de/British_Airways_Logo.svg',
        'AF': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Air_France_Logo.svg',
        'FR': 'https://upload.wikimedia.org/wikipedia/it/9/90/Logo-Ryanair.svg',
        'U2': 'https://upload.wikimedia.org/wikipedia/commons/b/b3/EasyJet_logo.svg'
    }

    for i, r in enumerate(risultati):
        carrier_code = r.get('validatingAirlineCodes', [''])[0]
        itinerary = r['itineraries'][0]
        segments = itinerary['segments']
        
        dep_time_raw = segments[0]['departure']['at']
        arr_time_raw = segments[-1]['arrival']['at']
        
        # Formattazione per Skyscanner Deep Link (YYMMDD)
        # Esempio: https://www.skyscanner.it/trasporti/voli/rom/lon/260320/
        date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        skyscanner_date = date_obj.strftime('%y%m%d')
        skyscanner_url = f"https://www.skyscanner.it/trasporti/voli/{origin.lower()}/{destination.lower()}/{skyscanner_date}/"
        
        formatted_results.append({
            'id': r['id'],
            'airline': carrier_code,
            'airline_name': dizionari.get('carriers', {}).get(carrier_code, carrier_code),
            'logo': carrier_logos.get(carrier_code, ''),
            'departure_time': dep_time_raw.split('T')[1][:5],
            'arrival_time': arr_time_raw.split('T')[1][:5],
            'duration': itinerary['duration'].replace('PT', '').replace('H', 'h ').replace('M', 'm'),
            'stops': 'Diretto' if len(segments) == 1 else f"{len(segments)-1} scalo/i",
            'price': float(r['price']['total']),
            'currency': r['price']['currency'],
            'skyscanner_url': skyscanner_url
        })
        
    return jsonify(formatted_results)
