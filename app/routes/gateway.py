from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
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
    """Simulazione ricerca voli Skyscanner."""
    origin = request.args.get('origin', 'Roma')
    destination = request.args.get('destination', 'Londra')
    departure_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Generiamo dati dummy "belli"
    airlines = [
        {'name': 'ITA Airways', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/e/e0/ITA_Airways_logo.svg'},
        {'name': 'Lufthansa', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/b/b8/Lufthansa_Logo_2018.svg'},
        {'name': 'British Airways', 'logo': 'https://upload.wikimedia.org/wikipedia/en/d/de/British_Airways_Logo.svg'},
        {'name': 'Air France', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/4/44/Air_France_Logo.svg'},
        {'name': 'Ryanair', 'logo': 'https://upload.wikimedia.org/wikipedia/it/9/90/Logo-Ryanair.svg'}
    ]
    
    results = []
    for i in range(10):
        airline = random.choice(airlines)
        dep_time = datetime.strptime(departure_date + " 08:00", '%Y-%m-%d %H:%M') + timedelta(minutes=random.randint(0, 720))
        duration_mins = random.randint(60, 300)
        arr_time = dep_time + timedelta(minutes=duration_mins)
        
        results.append({
            'id': i,
            'airline': airline['name'],
            'logo': airline['logo'],
            'departure_time': dep_time.strftime('%H:%M'),
            'arrival_time': arr_time.strftime('%H:%M'),
            'duration': f"{duration_mins // 60}h {duration_mins % 60}m",
            'stops': random.choice(['Diretto', '1 scalo']),
            'price': random.randint(45, 450),
            'origin': origin,
            'destination': destination
        })
    
    # Ordina per prezzo
    results.sort(key=lambda x: x['price'])
    
    return jsonify(results)
