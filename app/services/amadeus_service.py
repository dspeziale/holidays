"""
Amadeus API Service
Docs: https://developers.amadeus.com/self-service/apis-docs
Fallback: demo data when API keys are missing or unavailable.
"""
import requests
from flask import current_app

# ---------------------------------------------------------------------------
# Demo / mock data
# ---------------------------------------------------------------------------

_DEMO_CARS = [
    {'descrizione': 'Fiat 500 o simile',      'categoria': 'Mini',        'posti': 4, 'prezzo': '28.00',  'valuta': 'EUR', 'fornitore': 'Hertz'},
    {'descrizione': 'Volkswagen Polo o simile','categoria': 'Economy',     'posti': 5, 'prezzo': '35.00',  'valuta': 'EUR', 'fornitore': 'Europcar'},
    {'descrizione': 'Ford Focus o simile',     'categoria': 'Compact',     'posti': 5, 'prezzo': '42.00',  'valuta': 'EUR', 'fornitore': 'Avis'},
    {'descrizione': 'Toyota Corolla o simile', 'categoria': 'Intermediate','posti': 5, 'prezzo': '52.00',  'valuta': 'EUR', 'fornitore': 'Budget'},
    {'descrizione': 'Opel Astra o simile',     'categoria': 'Standard',    'posti': 5, 'prezzo': '58.00',  'valuta': 'EUR', 'fornitore': 'Sixt'},
    {'descrizione': 'BMW Serie 3 o simile',    'categoria': 'Full-Size',   'posti': 5, 'prezzo': '78.00',  'valuta': 'EUR', 'fornitore': 'Hertz'},
    {'descrizione': 'Mercedes Classe C o simile','categoria':'Premium',    'posti': 5, 'prezzo': '95.00',  'valuta': 'EUR', 'fornitore': 'Avis'},
    {'descrizione': 'Volkswagen Touareg',      'categoria': 'SUV',         'posti': 5, 'prezzo': '85.00',  'valuta': 'EUR', 'fornitore': 'Europcar'},
    {'descrizione': 'Ford Galaxy o simile',    'categoria': 'Minivan',     'posti': 7, 'prezzo': '72.00',  'valuta': 'EUR', 'fornitore': 'Budget'},
    {'descrizione': 'Tesla Model 3',           'categoria': 'Elettrica',   'posti': 5, 'prezzo': '110.00', 'valuta': 'EUR', 'fornitore': 'Sixt'},
]


def _mock_cars():
    result = []
    for c in _DEMO_CARS:
        result.append({
            'vehicle': {
                'description': c['descrizione'],
                'category':    c['categoria'],
                'seatCount':   c['posti'],
                'provider':    c['fornitore'],
            },
            'price': {'amount': c['prezzo'], 'currency': c['valuta']},
            '_demo': True,
        })
    return result


_DEMO_HOTELS = [
    {'nome': 'Grand Hotel de la Minerve', 'citta': 'Roma', 'stelle': 5,
     'prezzo': '320.00', 'valuta': 'EUR', 'camera': 'Deluxe Double'},
    {'nome': 'Hotel Artemide', 'citta': 'Roma', 'stelle': 4,
     'prezzo': '185.00', 'valuta': 'EUR', 'camera': 'Superior Twin'},
    {'nome': 'Hotel Hassler Roma', 'citta': 'Roma', 'stelle': 5,
     'prezzo': '580.00', 'valuta': 'EUR', 'camera': 'Classic Room'},
    {'nome': 'Four Seasons Milano', 'citta': 'Milano', 'stelle': 5,
     'prezzo': '680.00', 'valuta': 'EUR', 'camera': 'Superior Room'},
    {'nome': 'Hotel Principe di Savoia', 'citta': 'Milano', 'stelle': 5,
     'prezzo': '450.00', 'valuta': 'EUR', 'camera': 'Deluxe King'},
    {'nome': 'Boscolo Venezia Autograph', 'citta': 'Venezia', 'stelle': 5,
     'prezzo': '390.00', 'valuta': 'EUR', 'camera': 'Classic Canal View'},
    {'nome': 'Hotel Danieli', 'citta': 'Venezia', 'stelle': 5,
     'prezzo': '720.00', 'valuta': 'EUR', 'camera': 'Superior Room'},
    {'nome': 'Grand Hotel Vesuvio', 'citta': 'Napoli', 'stelle': 5,
     'prezzo': '260.00', 'valuta': 'EUR', 'camera': 'Classic Double'},
    {'nome': 'Hotel Excelsior Palermo', 'citta': 'Palermo', 'stelle': 4,
     'prezzo': '140.00', 'valuta': 'EUR', 'camera': 'Standard Double'},
    {'nome': 'Grand Hotel Timeo', 'citta': 'Taormina', 'stelle': 5,
     'prezzo': '510.00', 'valuta': 'EUR', 'camera': 'Deluxe Garden View'},
    {'nome': 'Hotel Lungarno', 'citta': 'Firenze', 'stelle': 4,
     'prezzo': '270.00', 'valuta': 'EUR', 'camera': 'River View Room'},
    {'nome': 'Belmond Villa San Michele', 'citta': 'Firenze', 'stelle': 5,
     'prezzo': '850.00', 'valuta': 'EUR', 'camera': 'Garden Suite'},
    {'nome': 'Grand Hotel Excelsior Vittoria', 'citta': 'Sorrento', 'stelle': 5,
     'prezzo': '380.00', 'valuta': 'EUR', 'camera': 'Classic Room'},
]


def _use_demo():
    key = current_app.config.get('AMADEUS_API_KEY')
    return not key or key.strip() == ''


def _mock_hotels(city_code, n=6):
    """Restituisce hotel demo filtrati per city_code (best-effort)."""
    city_map = {
        'ROM': 'Roma', 'FCO': 'Roma', 'CIA': 'Roma',
        'MXP': 'Milano', 'LIN': 'Milano', 'BGY': 'Milano',
        'VCE': 'Venezia',
        'NAP': 'Napoli',
        'PMO': 'Palermo',
        'FLR': 'Firenze',
    }
    city = city_map.get(city_code.upper())
    if city:
        matches = [h for h in _DEMO_HOTELS if h['citta'] == city]
        if matches:
            return _to_amadeus_format(matches[:n])
    # Nessun match → restituisce i primi n qualsiasi
    return _to_amadeus_format(_DEMO_HOTELS[:n])


def _to_amadeus_format(hotels):
    """Normalizza i demo hotel nel formato Amadeus per il template."""
    result = []
    for h in hotels:
        result.append({
            'hotel': {
                'name': h['nome'],
                'rating': str(h['stelle']),
                'address': {'cityName': h['citta']},
            },
            'offers': [{
                'room': {'typeEstimated': {'category': h['camera']}},
                'price': {'total': h['prezzo'], 'currency': h['valuta']},
            }],
            '_demo': True,
        })
    return result


# ---------------------------------------------------------------------------
# Token / auth
# ---------------------------------------------------------------------------

def _get_token():
    """Ottieni access token Amadeus (OAuth2 client_credentials)."""
    env = current_app.config.get('AMADEUS_ENV', 'test')
    base = 'https://test.api.amadeus.com' if env == 'test' else 'https://api.amadeus.com'

    r = requests.post(
        f'{base}/v1/security/oauth2/token',
        data={
            'grant_type': 'client_credentials',
            'client_id': current_app.config.get('AMADEUS_API_KEY', ''),
            'client_secret': current_app.config.get('AMADEUS_API_SECRET', ''),
        },
        timeout=10
    )
    r.raise_for_status()
    token_data = r.json()
    if 'access_token' not in token_data:
        raise ValueError(f"Amadeus auth error: {token_data}")
    return token_data['access_token'], base


# ---------------------------------------------------------------------------
# Hotel search
# ---------------------------------------------------------------------------

def search_hotels(city_code, check_in, check_out, adults=1, rooms=1, radius=5, currency='EUR'):
    if _use_demo():
        return _mock_hotels(city_code)

    try:
        token, base = _get_token()
        headers = {'Authorization': f'Bearer {token}'}

        r1 = requests.get(
            f'{base}/v1/reference-data/locations/hotels/by-city',
            headers=headers,
            params={
                'cityCode': city_code,
                'radius': radius,
                'radiusUnit': 'KM',
                'hotelSource': 'ALL',
            },
            timeout=15
        )
        r1.raise_for_status()
        hotels_list = r1.json().get('data', [])
        if not hotels_list:
            return []

        hotel_ids = [h['hotelId'] for h in hotels_list[:20]]

        r2 = requests.get(
            f'{base}/v3/shopping/hotel-offers',
            headers=headers,
            params={
                'hotelIds': ','.join(hotel_ids),
                'checkInDate': str(check_in),
                'checkOutDate': str(check_out),
                'adults': adults,
                'roomQuantity': rooms,
                'currency': currency,
                'bestRateOnly': 'true',
                'includeClosed': 'false',
            },
            timeout=20
        )
        r2.raise_for_status()
        return r2.json().get('data', [])

    except Exception as e:
        current_app.logger.error(f'Amadeus hotel search error: {e}')
        return _mock_hotels(city_code)   # fallback demo


# ---------------------------------------------------------------------------
# Flight search
# ---------------------------------------------------------------------------

def search_flights(origin, destination, departure_date, adults=1,
                   return_date=None, currency='EUR', max_results=10):
    if _use_demo():
        return [], {}

    try:
        token, base = _get_token()
        headers = {'Authorization': f'Bearer {token}'}

        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': str(departure_date),
            'adults': adults,
            'currencyCode': currency,
            'max': max_results,
            'nonStop': 'false',
        }
        if return_date:
            params['returnDate'] = str(return_date)

        r = requests.get(
            f'{base}/v2/shopping/flight-offers',
            headers=headers,
            params=params,
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        return data.get('data', []), data.get('dictionaries', {})

    except Exception as e:
        current_app.logger.error(f'Amadeus flight search error: {e}')
        return None, {}


# ---------------------------------------------------------------------------
# Car search
# ---------------------------------------------------------------------------

def search_cars(pickup_location, pickup_datetime, dropoff_datetime,
                dropoff_location=None, currency='EUR'):
    if _use_demo():
        return _mock_cars()

    try:
        token, base = _get_token()
        headers = {'Authorization': f'Bearer {token}'}

        params = {
            'pickUpLocation': pickup_location,
            'pickUpDateTime': str(pickup_datetime),
            'dropOffDateTime': str(dropoff_datetime),
            'currency': currency,
        }
        if dropoff_location:
            params['dropOffLocation'] = dropoff_location

        r = requests.get(
            f'{base}/v1/shopping/availability/car-availabilities',
            headers=headers,
            params=params,
            timeout=20
        )
        r.raise_for_status()
        data = r.json().get('data', [])
        return data if data else _mock_cars()

    except Exception as e:
        current_app.logger.error(f'Amadeus car search error: {e}')
        return _mock_cars()   # fallback demo invece di None


# ---------------------------------------------------------------------------
# Airport IATA lookup
# ---------------------------------------------------------------------------

def get_airport_iata(keyword):
    """Cerca codice IATA per nome città/aeroporto (autocomplete)."""
    if _use_demo():
        return []
    try:
        token, base = _get_token()
        r = requests.get(
            f'{base}/v1/reference-data/locations',
            headers={'Authorization': f'Bearer {token}'},
            params={
                'keyword': keyword,
                'subType': 'AIRPORT,CITY',
                'view': 'LIGHT',
                'page[limit]': 10,
            },
            timeout=10
        )
        r.raise_for_status()
        return r.json().get('data', [])
    except Exception:
        return []
