"""
Transfer Service — motore demo per prenotazione transfer.
Tipologie: aeroporto→hotel, hotel→aeroporto, punto a punto, tours privati.
"""
import random
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Catalogo veicoli transfer
# ---------------------------------------------------------------------------

_VEICOLI = [
    {
        'tipo': 'Economy',
        'icona': 'car-front',
        'badge': 'secondary',
        'descrizione': 'Berlina compatta (es. Toyota Corolla o simile)',
        'posti': 3,
        'bagagli': 2,
        'prezzo_base': 35,
        'extra_km': 0.8,
    },
    {
        'tipo': 'Business',
        'icona': 'car-front-fill',
        'badge': 'primary',
        'descrizione': 'Berlina premium (es. Mercedes Classe E o simile)',
        'posti': 3,
        'bagagli': 3,
        'prezzo_base': 65,
        'extra_km': 1.2,
    },
    {
        'tipo': 'SUV',
        'icona': 'truck',
        'badge': 'info',
        'descrizione': 'SUV spazioso (es. BMW X5 o simile)',
        'posti': 5,
        'bagagli': 4,
        'prezzo_base': 80,
        'extra_km': 1.4,
    },
    {
        'tipo': 'Minivan',
        'icona': 'bus-front',
        'badge': 'warning',
        'descrizione': 'Minivan (es. Volkswagen Caravelle o simile)',
        'posti': 7,
        'bagagli': 7,
        'prezzo_base': 95,
        'extra_km': 1.6,
    },
    {
        'tipo': 'Minibus',
        'icona': 'bus-front-fill',
        'badge': 'success',
        'descrizione': 'Minibus (fino a 16 passeggeri)',
        'posti': 16,
        'bagagli': 16,
        'prezzo_base': 150,
        'extra_km': 2.2,
    },
    {
        'tipo': 'Van Luxury',
        'icona': 'star-fill',
        'badge': 'danger',
        'descrizione': 'Van di lusso con allestimento VIP',
        'posti': 6,
        'bagagli': 6,
        'prezzo_base': 130,
        'extra_km': 2.0,
    },
]

# Distanze tipiche in km tra destinazioni comuni (approssimate)
_DISTANZE = {
    ('FCO', 'Roma'): 30,
    ('FCO', 'Milano'): 590,
    ('FCO', 'Napoli'): 220,
    ('MXP', 'Milano'): 50,
    ('MXP', 'Torino'): 130,
    ('VCE', 'Venezia'): 15,
    ('NAP', 'Napoli'): 8,
    ('PMO', 'Palermo'): 35,
    ('FLR', 'Firenze'): 12,
    ('Roma', 'Napoli'): 220,
    ('Roma', 'Firenze'): 280,
    ('Milano', 'Torino'): 140,
    ('Milano', 'Venezia'): 270,
}


def _stima_distanza(origine, destinazione):
    """Stima km tra due punti (demo)."""
    key1 = (origine.strip(), destinazione.strip())
    key2 = (destinazione.strip(), origine.strip())
    if key1 in _DISTANZE:
        return _DISTANZE[key1]
    if key2 in _DISTANZE:
        return _DISTANZE[key2]
    # Distanza casuale tra 10 e 300 km se non trovata
    random.seed(hash(origine + destinazione) % 10000)
    return random.randint(15, 250)


def _stima_durata(km):
    """Stima durata in minuti (velocità media 60 km/h + traffico)."""
    base = int(km / 60 * 60)
    traffico = max(10, int(km * 0.15))
    return base + traffico


def cerca_transfer(origine, destinazione, data_str, ora_str, n_passeggeri=1):
    """
    Restituisce lista di transfer disponibili (mock).
    """
    km = _stima_distanza(origine, destinazione)
    durata_min = _stima_durata(km)
    h, m = divmod(durata_min, 60)
    durata_label = f'{h}h {m:02d}min' if h else f'{m} min'

    risultati = []
    for v in _VEICOLI:
        prezzo = round(v['prezzo_base'] + km * v['extra_km'], 2)
        risultati.append({
            'tipo': v['tipo'],
            'icona': v['icona'],
            'badge': v['badge'],
            'descrizione': v['descrizione'],
            'posti': v['posti'],
            'bagagli': v['bagagli'],
            'km': km,
            'durata': durata_label,
            'prezzo': f'{prezzo:.2f}',
            'valuta': 'EUR',
            '_demo': True,
        })

    return risultati, {
        'origine': origine,
        'destinazione': destinazione,
        'data': data_str,
        'ora': ora_str,
        'n_passeggeri': n_passeggeri,
        'km': km,
        'durata': durata_label,
    }
