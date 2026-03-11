"""
Servizio Treni — motore di ricerca mock per treni italiani.

Genera orari e prezzi realistici per le principali tratte italiane.
I risultati includono link di prenotazione su Trenitalia e Italo.
"""
from datetime import datetime, timedelta
import hashlib
from urllib.parse import urlencode, quote_plus

# ── Stazioni principali ────────────────────────────────────────────────────────
STAZIONI = {
    # Codice: (nome completo, regione)
    'MIL': ('Milano Centrale', 'Lombardia'),
    'ROM': ('Roma Termini', 'Lazio'),
    'FIR': ('Firenze Santa Maria Novella', 'Toscana'),
    'NAP': ('Napoli Centrale', 'Campania'),
    'VEN': ('Venezia Santa Lucia', 'Veneto'),
    'TOR': ('Torino Porta Nuova', 'Piemonte'),
    'BOL': ('Bologna Centrale', 'Emilia-Romagna'),
    'GEN': ('Genova Piazza Principe', 'Liguria'),
    'PAL': ('Palermo Centrale', 'Sicilia'),
    'BAR': ('Bari Centrale', 'Puglia'),
    'CAT': ('Catania Centrale', 'Sicilia'),
    'ANK': ('Ancona', 'Marche'),
    'TRI': ('Trieste Centrale', 'Friuli'),
    'VER': ('Verona Porta Nuova', 'Veneto'),
    'BRE': ('Brescia', 'Lombardia'),
    'PAD': ('Padova', 'Veneto'),
    'SAL': ('Salerno', 'Campania'),
    'REG': ('Reggio Calabria Centrale', 'Calabria'),
    'PES': ('Pescara Centrale', 'Abruzzo'),
    'PER': ('Perugia', 'Umbria'),
}

# ── Database tratte (origine, dest): (durata_min, treni_disponibili) ───────────
# durata in minuti, treni = lista di (tipo, operatore, delta_prezzo_base)
_TRATTE = {
    ('ROM','MIL'): (170, [('FR','Trenitalia',0),('FR','Trenitalia',15),('FA','Trenitalia',-10),('IT','Italo',5),('IT','Italo',-5),('IC','Trenitalia',-25)]),
    ('MIL','ROM'): (170, [('FR','Trenitalia',0),('FR','Trenitalia',10),('IT','Italo',0),('IT','Italo',8),('FA','Trenitalia',-8),('IC','Trenitalia',-20)]),
    ('ROM','FIR'): (95,  [('FR','Trenitalia',0),('FR','Trenitalia',5),('IT','Italo',-3),('FA','Trenitalia',-12),('IC','Trenitalia',-20)]),
    ('FIR','ROM'): (95,  [('FR','Trenitalia',0),('IT','Italo',0),('FA','Trenitalia',-10),('IC','Trenitalia',-18)]),
    ('ROM','NAP'): (68,  [('FR','Trenitalia',0),('FR','Trenitalia',8),('IT','Italo',-2),('IT','Italo',4),('IC','Trenitalia',-22)]),
    ('NAP','ROM'): (68,  [('FR','Trenitalia',0),('IT','Italo',3),('FA','Trenitalia',-8),('IC','Trenitalia',-20)]),
    ('MIL','VEN'): (145, [('FR','Trenitalia',0),('IT','Italo',-5),('FA','Trenitalia',-15),('RV','Trenitalia',-30)]),
    ('VEN','MIL'): (145, [('FR','Trenitalia',0),('IT','Italo',0),('FA','Trenitalia',-12),('RV','Trenitalia',-28)]),
    ('MIL','FIR'): (105, [('FR','Trenitalia',0),('IT','Italo',-3),('FA','Trenitalia',-15),('IC','Trenitalia',-25)]),
    ('FIR','MIL'): (105, [('FR','Trenitalia',5),('IT','Italo',0),('FA','Trenitalia',-12),('IC','Trenitalia',-22)]),
    ('MIL','BOL'): (68,  [('FR','Trenitalia',0),('IT','Italo',-4),('FA','Trenitalia',-12),('RV','Trenitalia',-25)]),
    ('BOL','ROM'): (120, [('FR','Trenitalia',0),('IT','Italo',-2),('FA','Trenitalia',-10),('IC','Trenitalia',-20)]),
    ('MIL','TOR'): (55,  [('FR','Trenitalia',0),('IT','Italo',-3),('FA','Trenitalia',-10),('RV','Trenitalia',-20)]),
    ('TOR','MIL'): (55,  [('FR','Trenitalia',0),('IT','Italo',0),('FA','Trenitalia',-8)]),
    ('ROM','BAR'): (215, [('FR','Trenitalia',0),('FA','Trenitalia',-15),('IC','Trenitalia',-30)]),
    ('BAR','ROM'): (215, [('FR','Trenitalia',0),('IC','Trenitalia',-28)]),
    ('ROM','VEN'): (235, [('FR','Trenitalia',0),('IT','Italo',5),('FA','Trenitalia',-15)]),
    ('VEN','ROM'): (235, [('FR','Trenitalia',0),('IT','Italo',3),('FA','Trenitalia',-12)]),
    ('NAP','SAL'): (35,  [('RV','Trenitalia',0),('R','Trenitalia',-10)]),
    ('FIR','VEN'): (130, [('FR','Trenitalia',0),('IT','Italo',-3),('FA','Trenitalia',-18)]),
    ('VEN','PAD'): (28,  [('RV','Trenitalia',0),('R','Trenitalia',-8)]),
    ('MIL','VER'): (60,  [('FR','Trenitalia',0),('FA','Trenitalia',-10),('RV','Trenitalia',-20)]),
    ('VER','MIL'): (60,  [('FR','Trenitalia',0),('FA','Trenitalia',-8)]),
    ('ROM','PES'): (100, [('FR','Trenitalia',0),('IC','Trenitalia',-15),('RV','Trenitalia',-22)]),
    ('TOR','VEN'): (160, [('FR','Trenitalia',0),('IT','Italo',-5),('FA','Trenitalia',-15)]),
}

# ── Prezzi base per tipo treno ─────────────────────────────────────────────────
_PREZZI_BASE = {
    'FR': 49,    # Frecciarossa
    'FA': 38,    # Frecciargento
    'FB': 28,    # Frecciabianca
    'IT': 45,    # Italo
    'IC': 22,    # Intercity
    'RV': 12,    # Regionale Veloce
    'R':  9,     # Regionale
}

_TIPO_LABEL = {
    'FR': 'Frecciarossa',
    'FA': 'Frecciargento',
    'FB': 'Frecciabianca',
    'IT': 'Italo EVO',
    'IC': 'Intercity',
    'RV': 'Regionale Veloce',
    'R':  'Regionale',
}

_TIPO_CLASSE = {
    'FR': 'Alta velocita\'',
    'FA': 'Alta velocita\'',
    'FB': 'Alta velocita\'',
    'IT': 'Alta velocita\'',
    'IC': 'Lunga percorrenza',
    'RV': 'Regionale',
    'R':  'Regionale',
}

_TIPO_BADGE = {
    'FR': 'danger',
    'FA': 'warning',
    'FB': 'info',
    'IT': 'success',
    'IC': 'secondary',
    'RV': 'light',
    'R':  'light',
}

# Orari di partenza frequenti (ore, minuto)
_ORARI_FR  = [(6,0),(6,30),(7,0),(7,30),(8,0),(8,30),(9,0),(10,0),(11,0),(12,0),(13,0),(14,0),(15,0),(16,0),(17,0),(18,0),(19,0),(20,0),(21,0)]
_ORARI_STD = [(6,15),(7,45),(9,20),(11,10),(13,40),(15,50),(17,25),(19,10),(21,30)]
_ORARI_REG = [(5,30),(6,45),(8,10),(9,50),(11,30),(13,20),(15,40),(17,10),(19,40)]

# URL base prenotazione
_URL_TRENITALIA_BASE = 'https://www.trenitalia.com/it.html'
_URL_ITALO_BASE      = 'https://www.italotreno.it/it/acquisto'


def _build_trenitalia_url(origine_nome, destinazione_nome, data_str, n_adulti, n_bambini):
    """
    Costruisce l'URL di ricerca Trenitalia con i parametri pre-compilati.
    Trenitalia usa un'app React — i parametri vengono passati come query string
    al widget di prenotazione integrato nella home.
    """
    # Data nel formato dd/mm/yyyy richiesto da Trenitalia
    try:
        dt = datetime.strptime(data_str, '%Y-%m-%d')
        data_it = dt.strftime('%d/%m/%Y')
    except ValueError:
        data_it = data_str

    params = {
        'partenza':    origine_nome,
        'arrivo':      destinazione_nome,
        'data':        data_it,
        'adulti':      str(n_adulti),
        'bambini':     str(n_bambini),
        'sola_andata': '1',
    }
    return f"{_URL_TRENITALIA_BASE}?{urlencode(params, quote_via=quote_plus)}"


def _build_italo_url(origine_nome, destinazione_nome, data_str, n_adulti, n_bambini):
    """
    Costruisce l'URL di ricerca Italo con i parametri pre-compilati.
    Italo accetta origin/destination come nomi di stazione e date in ISO.
    """
    try:
        dt = datetime.strptime(data_str, '%Y-%m-%d')
        data_italo = dt.strftime('%d/%m/%Y')
    except ValueError:
        data_italo = data_str

    params = {
        'from':     origine_nome,
        'to':       destinazione_nome,
        'date':     data_italo,
        'adults':   str(n_adulti),
        'children': str(n_bambini),
    }
    return f"{_URL_ITALO_BASE}?{urlencode(params, quote_via=quote_plus)}"


def _seed(s):
    """Genera un intero deterministico da una stringa (per rendere i dati stabili)."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def _normalize(city):
    """Tenta di trovare il codice stazione dalla stringa libera."""
    if not city:
        return None
    c = city.strip().upper()
    # Match diretto codice
    if c in STAZIONI:
        return c
    # Match parziale su nome
    c_lower = city.strip().lower()
    for code, (nome, _) in STAZIONI.items():
        if c_lower in nome.lower() or nome.lower().startswith(c_lower):
            return code
    return None


def cerca_treni(origine, destinazione, data_str, n_adulti=1, n_bambini=0):
    """
    Cerca treni tra due citta'.

    Args:
        origine, destinazione: stringa libera o codice
        data_str: 'YYYY-MM-DD'
        n_adulti, n_bambini: numero passeggeri

    Returns:
        dict con 'treni', 'origine_nome', 'destinazione_nome', 'is_demo', 'data',
                 'url_trenitalia', 'url_italo', 'error'
    """
    cod_or  = _normalize(origine)
    cod_dst = _normalize(destinazione)

    if not cod_or:
        return {'error': f'Stazione di partenza "{origine}" non trovata. Prova con una citta\' principale.', 'treni': []}
    if not cod_dst:
        return {'error': f'Stazione di arrivo "{destinazione}" non trovata. Prova con una citta\' principale.', 'treni': []}
    if cod_or == cod_dst:
        return {'error': 'Partenza e arrivo non possono essere uguali.', 'treni': []}

    nome_or  = STAZIONI[cod_or][0]
    nome_dst = STAZIONI[cod_dst][0]

    # Cerca tratta diretta
    key = (cod_or, cod_dst)
    key_rev = (cod_dst, cod_or)
    tratta = _TRATTE.get(key) or _TRATTE.get(key_rev)

    if not tratta:
        return {
            'error': None,
            'treni': [],
            'origine_nome': nome_or,
            'destinazione_nome': nome_dst,
            'is_demo': True,
            'data': data_str,
            'n_adulti': n_adulti,
            'n_bambini': n_bambini,
            'url_trenitalia': _build_trenitalia_url(nome_or, nome_dst, data_str, n_adulti, n_bambini),
            'url_italo':      _build_italo_url(nome_or, nome_dst, data_str, n_adulti, n_bambini),
            'nessuna_tratta': True,
        }

    durata_min, treni_tipi = tratta

    # Parse data
    try:
        data_dt = datetime.strptime(data_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        data_dt = datetime.today()

    passeggeri = n_adulti + n_bambini
    risultati = []

    seed_base = _seed(f'{cod_or}{cod_dst}{data_str}')

    for i, (tipo, operatore, delta) in enumerate(treni_tipi):
        # Orario partenza
        if tipo in ('FR', 'FA', 'IT'):
            orari = _ORARI_FR
        elif tipo in ('IC', 'FB'):
            orari = _ORARI_STD
        else:
            orari = _ORARI_REG

        idx = (seed_base + i * 37) % len(orari)
        h, m = orari[idx]
        partenza = data_dt.replace(hour=h, minute=m, second=0, microsecond=0)
        arrivo   = partenza + timedelta(minutes=durata_min)

        # Prezzo con leggera variazione deterministica
        prezzo_base = _PREZZI_BASE.get(tipo, 30) + delta
        variazione = ((seed_base + i * 13) % 11) - 5   # da -5 a +5
        prezzo_adu = max(prezzo_base + variazione, 5)
        prezzo_bam = round(prezzo_adu * 0.5, 0) if n_bambini else 0
        prezzo_tot = prezzo_adu * n_adulti + prezzo_bam * n_bambini

        # Disponibilita' posti
        rand_posti = (seed_base + i * 7) % 120
        if rand_posti < 5:
            posti_label = 'Ultimi posti'
            posti_class = 'danger'
        elif rand_posti < 20:
            posti_label = 'Pochi posti'
            posti_class = 'warning'
        else:
            posti_label = 'Disponibile'
            posti_class = 'success'

        # Numero treno
        prefissi = {'FR':'FR','FA':'FA','FB':'FB','IT':'EVO','IC':'IC','RV':'RV','R':'R'}
        num_treno = f"{prefissi.get(tipo,'TR')}{9000 + (seed_base + i*31) % 900}"

        risultati.append({
            'tipo':          tipo,
            'tipo_label':    _TIPO_LABEL.get(tipo, tipo),
            'tipo_classe':   _TIPO_CLASSE.get(tipo, ''),
            'tipo_badge':    _TIPO_BADGE.get(tipo, 'secondary'),
            'operatore':     operatore,
            'num_treno':     num_treno,
            'partenza':      partenza.strftime('%H:%M'),
            'arrivo':        arrivo.strftime('%H:%M'),
            'durata':        f'{durata_min // 60}h {durata_min % 60:02d}m',
            'prezzo_adulto': prezzo_adu,
            'prezzo_bambino':prezzo_bam,
            'prezzo_totale': prezzo_tot,
            'passeggeri':    passeggeri,
            'posti_label':   posti_label,
            'posti_class':   posti_class,
        })

    # Ordina per orario partenza
    risultati.sort(key=lambda x: x['partenza'])

    return {
        'treni':             risultati,
        'origine_nome':      nome_or,
        'destinazione_nome': nome_dst,
        'is_demo':           True,
        'data':              data_str,
        'n_adulti':          n_adulti,
        'n_bambini':         n_bambini,
        'url_trenitalia':    _build_trenitalia_url(nome_or, nome_dst, data_str, n_adulti, n_bambini),
        'url_italo':         _build_italo_url(nome_or, nome_dst, data_str, n_adulti, n_bambini),
        'error':             None,
    }


def get_stazioni_list():
    """Restituisce lista ordinata di stazioni per autocomplete."""
    return sorted([(c, n) for c, (n, _) in STAZIONI.items()], key=lambda x: x[1])
