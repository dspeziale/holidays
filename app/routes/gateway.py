from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from app.services import amadeus_service as amadeus
from app.services import kiwi_service as kiwi
from app.services import skyscanner_service as skyscanner
import random
from datetime import datetime, timedelta

gateway_bp = Blueprint('gateway', __name__, url_prefix='/gateway')

@gateway_bp.route('/voli')
@login_required
def voli():
    """Pagina di ricerca voli (Skyscanner Gateway)."""
    return render_template('gateway/voli.html')

@gateway_bp.route('/api/voli/search')
@login_required
def api_search_voli():
    """Ricerca voli reali tramite Amadeus con link Skyscanner (o Kiwi se configurato)."""
    origin = request.args.get('origin', 'ROM').upper()
    destination = request.args.get('destination', 'LON').upper()
    departure_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    return_date = request.args.get('return_date')
    
    # Mapping loghi esteso
    carrier_logos = {
        'AZ': 'https://upload.wikimedia.org/wikipedia/commons/e/e0/ITA_Airways_logo.svg',
        'LH': 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Lufthansa_Logo_2018.svg',
        'BA': 'https://upload.wikimedia.org/wikipedia/en/d/de/British_Airways_Logo.svg',
        'AF': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Air_France_Logo.svg',
        'FR': 'https://upload.wikimedia.org/wikipedia/it/9/90/Logo-Ryanair.svg',
        'U2': 'https://upload.wikimedia.org/wikipedia/commons/b/b3/EasyJet_logo.svg',
        'VY': 'https://upload.wikimedia.org/wikipedia/commons/3/37/Vueling_Logo.svg',
        'IB': 'https://upload.wikimedia.org/wikipedia/commons/b/b4/Iberia_Logo.svg',
        'W6': 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Wizz_Air_logo.svg'
    }

    formatted_results = []
    
    # 0. Prova con il nuovo Skyscanner Service (Demo Fallback)
    skyscanner_results = skyscanner.search_flights(origin, destination, departure_date)
    if skyscanner_results:
        for r in skyscanner_results:
            # Assicuriamoci che il logo sia presente se manca nella demo
            if not r.get('logo'):
                r['logo'] = carrier_logos.get(r['airline'], '')
            # Il service gestisce già il link specifico (con airline/adulti)
            if not r.get('skyscanner_url'):
                r['skyscanner_url'] = skyscanner.get_skyscanner_url(origin, destination, departure_date)
            formatted_results.append(r)
        return jsonify(formatted_results)

    # 1. Prova con Kiwi se configurato (legacy logic as backup)
    kiwi_results = kiwi.search_flights(origin, destination, departure_date)
    if kiwi_results:
        for r in kiwi_results:
            carrier_code = r.get('airlines', [''])[0]
            skyscanner_url = skyscanner.get_skyscanner_url(origin, destination, departure_date)
            
            formatted_results.append({
                'source': 'Kiwi',
                'id': r['id'],
                'airline': carrier_code,
                'airline_name': carrier_code,
                'logo': carrier_logos.get(carrier_code, ''),
                'departure_time': datetime.fromtimestamp(r['dTime']).strftime('%H:%M'),
                'arrival_time': datetime.fromtimestamp(r['aTime']).strftime('%H:%M'),
                'duration': r['fly_duration'],
                'stops': 'Diretto' if len(r.get('route', [])) <= 1 else f"{len(r.get('route', []))-1} scalo/i",
                'price': float(r['price']),
                'currency': 'EUR',
                'skyscanner_url': skyscanner_url
            })
        return jsonify(formatted_results)

    # 2. Fallback su Amadeus
    risultati, dizionari = amadeus.search_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        max_results=15
    )
    
    if risultati is None:
        return jsonify({'error': 'Errore API (Skyscanner, Kiwi & Amadeus)'}), 500
        
    for i, r in enumerate(risultati):
        carrier_code = r.get('validatingAirlineCodes', [''])[0]
        itinerary = r['itineraries'][0]
        segments = itinerary['segments']
        
        dep_time_raw = segments[0]['departure']['at']
        arr_time_raw = segments[-1]['arrival']['at']
        
        skyscanner_url = skyscanner.get_skyscanner_url(origin, destination, departure_date)
        
        formatted_results.append({
            'source': 'Amadeus',
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
        
    return jsonify(formatted_results)

@gateway_bp.route('/api/locations/search')
@login_required
def api_search_locations():
    """Risolve città/aeroporto in codici IATA tramite BoostedTravel."""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])
    
    locations = skyscanner.resolve_location(query)
    return jsonify(locations)
