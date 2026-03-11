"""
GetYourGuide Partner API Service — con fallback demo senza API key.

Se GETYOURGUIDE_API_KEY non e' configurata, restituisce dati di esempio
realistici basati sulla keyword di ricerca.
"""
import requests
from flask import current_app

GYG_BASE = 'https://api.getyourguide.com/1'

# ── Catalogo demo ──────────────────────────────────────────────────────────────
_DEMO_CATALOG = [
    # Roma
    {"id":101,"title":"Tour guidato del Colosseo e Foro Romano","destinazione":"Roma",
     "abstract":"Visita il Colosseo, il Foro Romano e il Palatino con una guida esperta. Salta la fila con i biglietti inclusi.",
     "duration":"3 ore","prezzo":49.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/roma-l33/colosseo-foro-romano-t28503/",
     "img":"https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&q=80"},
    {"id":102,"title":"Tour Vaticano: Musei e Cappella Sistina","destinazione":"Roma",
     "abstract":"Esplora i Musei Vaticani, la Cappella Sistina e la Basilica di San Pietro con guida autorizzata.",
     "duration":"3.5 ore","prezzo":65.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/vaticano-l4748/musei-vaticani-t3948/",
     "img":"https://images.unsplash.com/photo-1531572753322-ad063cecc140?w=600&q=80"},
    {"id":103,"title":"Pizza e Pasta: Corso di cucina romana","destinazione":"Roma",
     "abstract":"Impara a preparare pasta fresca e pizza romana con uno chef locale nel cuore di Trastevere.",
     "duration":"4 ore","prezzo":85.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/roma-l33/corso-cucina-t9812/",
     "img":"https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&q=80"},
    {"id":104,"title":"Tour in E-Bike di Roma al tramonto","destinazione":"Roma",
     "abstract":"Pedalate tra le 7 colline di Roma in bici elettrica al tramonto: Circo Massimo, Aventino, Trastevere.",
     "duration":"3 ore","prezzo":39.0,"categoria":"Sport",
     "url":"https://www.getyourguide.it/roma-l33/ebike-tour-t7341/",
     "img":"https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&q=80"},
    {"id":105,"title":"Degustazione vini dei Castelli Romani","destinazione":"Roma",
     "abstract":"Gita di mezza giornata ai Castelli Romani con visita in cantina e degustazione di vini DOC.",
     "duration":"5 ore","prezzo":72.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/roma-l33/castelli-romani-vino-t5521/",
     "img":"https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=600&q=80"},
    # Firenze
    {"id":201,"title":"Galleria degli Uffizi: tour guidato","destinazione":"Firenze",
     "abstract":"Ammirate Botticelli, Leonardo e Michelangelo con un esperto d'arte. Accesso prioritario garantito.",
     "duration":"2 ore","prezzo":55.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/firenze-l91/uffizi-t1841/",
     "img":"https://images.unsplash.com/photo-1541849546-216549ae216d?w=600&q=80"},
    {"id":202,"title":"Chianti in bici: tour tra le vigne","destinazione":"Firenze",
     "abstract":"Pedalate tra vigneti e borghi medievali nel Chianti Classico con degustazione e pranzo tipico.",
     "duration":"8 ore","prezzo":110.0,"categoria":"Sport",
     "url":"https://www.getyourguide.it/firenze-l91/chianti-bici-t3312/",
     "img":"https://images.unsplash.com/photo-1506377585622-bedcbb027afc?w=600&q=80"},
    {"id":203,"title":"Lezione di gelato artigianale","destinazione":"Firenze",
     "abstract":"Impara l'arte del gelato fiorentino in una gelateria storica del centro.",
     "duration":"2 ore","prezzo":45.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/firenze-l91/gelato-workshop-t9933/",
     "img":"https://images.unsplash.com/photo-1567206563114-c179706e6be6?w=600&q=80"},
    {"id":204,"title":"David e Accademia: visita guidata","destinazione":"Firenze",
     "abstract":"Tour privato alla Galleria dell'Accademia con il David di Michelangelo.",
     "duration":"1.5 ore","prezzo":48.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/firenze-l91/accademia-david-t2241/",
     "img":"https://images.unsplash.com/photo-1534430480872-3498386e7856?w=600&q=80"},
    # Venezia
    {"id":301,"title":"Giro in gondola sul Canal Grande","destinazione":"Venezia",
     "abstract":"Navigazione privata in gondola tra i canali storici di Venezia con gondoliere cantante.",
     "duration":"1 ora","prezzo":80.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/venezia-l42/gondola-t1123/",
     "img":"https://images.unsplash.com/photo-1534113414509-0eec2bfb493f?w=600&q=80"},
    {"id":302,"title":"Tour delle isole: Murano e Burano","destinazione":"Venezia",
     "abstract":"Escursione in barca a Murano (lavorazione del vetro) e Burano (merletti colorati).",
     "duration":"6 ore","prezzo":55.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/venezia-l42/murano-burano-t2841/",
     "img":"https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=600&q=80"},
    {"id":303,"title":"Cicchetti e Bacari: street food veneziano","destinazione":"Venezia",
     "abstract":"Tour gastronomico tra le osterie veneziane: cicchetti, sarde in saor, tramezzini e spritz.",
     "duration":"3 ore","prezzo":65.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/venezia-l42/cicchetti-tour-t7721/",
     "img":"https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80"},
    # Napoli / Amalfi
    {"id":401,"title":"Tour di Pompei ed Ercolano","destinazione":"Napoli",
     "abstract":"Visita guidata agli scavi di Pompei con possibilita' di aggiungere Ercolano. Trasporto incluso.",
     "duration":"7 ore","prezzo":75.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/napoli-l164/pompei-ercolano-t3341/",
     "img":"https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=600&q=80"},
    {"id":402,"title":"Gita in barca alla Costiera Amalfitana","destinazione":"Amalfi",
     "abstract":"Navigazione lungo la Costiera: Positano, Ravello, grotta Smeraldo. Snorkeling incluso.",
     "duration":"8 ore","prezzo":95.0,"categoria":"Natura",
     "url":"https://www.getyourguide.it/amalfi-l2441/boat-tour-t5512/",
     "img":"https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=600&q=80"},
    {"id":403,"title":"Pizza napoletana: lezione con pizzaiolo","destinazione":"Napoli",
     "abstract":"Preparate la vera pizza napoletana nel forno a legna con un maestro pizzaiolo.",
     "duration":"2 ore","prezzo":40.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/napoli-l164/pizza-class-t4421/",
     "img":"https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=600&q=80"},
    # Milano
    {"id":501,"title":"L'Ultima Cena di Leonardo: tour guidato","destinazione":"Milano",
     "abstract":"Visita all'Ultima Cena di Leonardo da Vinci in Santa Maria delle Grazie con guida esperta.",
     "duration":"1.5 ore","prezzo":58.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/milano-l57/ultima-cena-t2219/",
     "img":"https://images.unsplash.com/photo-1520066786-f4218c6d03e4?w=600&q=80"},
    {"id":502,"title":"Tour gastronomico di Milano: aperitivo e Navigli","destinazione":"Milano",
     "abstract":"Scopri la scena culinaria milanese: dai classici aperitivi ai ristoranti del Navigli.",
     "duration":"4 ore","prezzo":70.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/milano-l57/food-tour-t8831/",
     "img":"https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80"},
    # Sicilia
    {"id":601,"title":"Etna: escursione sul vulcano","destinazione":"Sicilia",
     "abstract":"Trekking guidato sull'Etna fino ai crateri sommitali con jeep 4x4.",
     "duration":"8 ore","prezzo":85.0,"categoria":"Natura",
     "url":"https://www.getyourguide.it/catania-l318/etna-tour-t3318/",
     "img":"https://images.unsplash.com/photo-1568544270619-aa4e4312ac2d?w=600&q=80"},
    {"id":602,"title":"Valle dei Templi di Agrigento","destinazione":"Sicilia",
     "abstract":"Tour privato alla Valle dei Templi con guida archeologa.",
     "duration":"3 ore","prezzo":50.0,"categoria":"Arte & Cultura",
     "url":"https://www.getyourguide.it/agrigento-l312/valle-templi-t6612/",
     "img":"https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=600&q=80"},
    # Toscana
    {"id":701,"title":"Tour in elicottero sulla Toscana","destinazione":"Toscana",
     "abstract":"Volo panoramico su Firenze, Siena, Val d'Orcia con champagne e atterraggio in cantina.",
     "duration":"2 ore","prezzo":290.0,"categoria":"Sport",
     "url":"https://www.getyourguide.it/toscana-l2711/elicottero-t9911/",
     "img":"https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80"},
    {"id":702,"title":"Truffle hunting in Val d'Orcia","destinazione":"Toscana",
     "abstract":"Caccia al tartufo con cani addestrati, seguita da pranzo con piatti a base di tartufo.",
     "duration":"5 ore","prezzo":120.0,"categoria":"Food & Wine",
     "url":"https://www.getyourguide.it/siena-l298/truffle-hunting-t7719/",
     "img":"https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80"},
    # Generiche
    {"id":801,"title":"Snorkeling nelle acque cristalline della Sardegna","destinazione":"Sardegna",
     "abstract":"Escursione in barca con snorkeling nelle calette della Costa Smeralda.",
     "duration":"6 ore","prezzo":65.0,"categoria":"Sport",
     "url":"https://www.getyourguide.it/sardegna-l512/snorkeling-t3318/",
     "img":"https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=600&q=80"},
    {"id":802,"title":"Yoga e meditazione all'alba sul lago di Como","destinazione":"Como",
     "abstract":"Sessione di yoga e meditazione guidata all'alba con vista sul lago, seguita da colazione bio.",
     "duration":"3 ore","prezzo":55.0,"categoria":"Benessere",
     "url":"https://www.getyourguide.it/como-l912/yoga-alba-t6612/",
     "img":"https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=600&q=80"},
]


def _use_demo():
    """Controlla se usare il fallback demo (API key assente)."""
    api_key = current_app.config.get('GETYOURGUIDE_API_KEY')
    return not api_key


def _headers():
    api_key = current_app.config.get('GETYOURGUIDE_API_KEY')
    if not api_key:
        raise ValueError('GETYOURGUIDE_API_KEY non configurata nel .env')
    return {'X-Access-Token': api_key, 'Accept': 'application/json'}


def _mock_search(query):
    """Ricerca nel catalogo demo per keyword."""
    q = query.lower()
    results = [
        a for a in _DEMO_CATALOG
        if q in a['title'].lower()
        or q in a['destinazione'].lower()
        or q in a.get('categoria', '').lower()
        or q in a.get('abstract', '').lower()
    ]
    if not results:
        results = _DEMO_CATALOG[:8]
    return results, len(results)


def search_activities(query, lang='it', currency='EUR', limit=20, offset=0,
                      lat=None, lon=None, radius=None):
    """Cerca attivita' GYG. Usa dati demo se manca la API key o se l'API fallisce."""
    if _use_demo():
        return _mock_search(query)

    try:
        params = {
            'q': query, 'lang': lang, 'currency': currency,
            'count': limit, 'page': (offset // limit) + 1 if limit > 0 else 1,
            'sort_direction': 'DESC', 'sort_field': 'popularity',
        }
        if lat and lon:
            params['latitude'] = lat
            params['longitude'] = lon
            if radius:
                params['radius'] = radius

        r = requests.get(f'{GYG_BASE}/tours', headers=_headers(), params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return (data.get('data', {}).get('tours', []),
                data.get('data', {}).get('available_count', 0))
    except requests.RequestException as e:
        current_app.logger.warning(f'GYG API non disponibile ({e}), uso dati demo.')
        return _mock_search(query)


def get_activity_detail(tour_id, lang='it', currency='EUR'):
    """Dettaglio attivita'. Usa demo se manca la API key o se l'API fallisce."""
    if _use_demo():
        return next((a for a in _DEMO_CATALOG if a['id'] == int(tour_id)), None)

    try:
        r = requests.get(
            f'{GYG_BASE}/tours/{tour_id}',
            headers=_headers(),
            params={'lang': lang, 'currency': currency},
            timeout=15
        )
        r.raise_for_status()
        return r.json().get('data', {}).get('tour')
    except requests.RequestException as e:
        current_app.logger.warning(f'GYG API non disponibile ({e}), uso dati demo.')
        return next((a for a in _DEMO_CATALOG if a['id'] == int(tour_id)), None)


def get_availability(tour_id, date_from, date_to, participants=1, currency='EUR'):
    """Verifica disponibilita' e prezzi per una data specifica."""
    if _use_demo():
        return []   # demo: nessuna disponibilita' live

    try:
        r = requests.get(
            f'{GYG_BASE}/tours/{tour_id}/availabilities',
            headers=_headers(),
            params={'date_from': str(date_from), 'date_to': str(date_to), 'currency': currency},
            timeout=15
        )
        r.raise_for_status()
        return r.json().get('data', {}).get('availabilities', [])
    except requests.RequestException as e:
        current_app.logger.error(f'GYG availability error: {e}')
        return None
