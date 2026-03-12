from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from app import db
from app.services import amadeus_service as amadeus
from app.models.viaggio import Viaggio
from datetime import date, datetime
import json

amadeus_bp = Blueprint('amadeus', __name__, url_prefix='/amadeus')


@amadeus_bp.route('/hotels', methods=['GET', 'POST'])
@login_required
def hotels():
    risultati = None
    error = None
    if request.method == 'POST':
        city_code = request.form.get('city_code', '').upper().strip()
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        adults = int(request.form.get('adults', 1))
        rooms = int(request.form.get('rooms', 1))

        if not all([city_code, check_in, check_out]):
            flash('Compila tutti i campi obbligatori.', 'warning')
        else:
            risultati = amadeus.search_hotels(
                city_code=city_code,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                rooms=rooms
            )
            if risultati is None:
                error = 'Errore nella ricerca. Verifica le credenziali Amadeus o riprova.'
            elif len(risultati) == 0:
                flash('Nessun hotel trovato per i criteri selezionati.', 'info')

    viaggi = Viaggio.query.filter(
        Viaggio.stato.in_(['bozza', 'confermato'])
    ).order_by(Viaggio.data_partenza).all()

    return render_template('amadeus/hotels.html',
                           risultati=risultati,
                           error=error,
                           viaggi=viaggi,
                           today=date.today().isoformat())


@amadeus_bp.route('/hotels/collega', methods=['POST'])
@login_required
def collega_hotel():
    viaggio_id = request.form.get('viaggio_id', type=int)
    hotel_json_str = request.form.get('hotel_json', '{}')

    if not viaggio_id:
        flash('Seleziona un viaggio.', 'warning')
        return redirect(url_for('amadeus.hotels'))

    viaggio = Viaggio.query.get_or_404(viaggio_id)

    try:
        nuovo_hotel = json.loads(hotel_json_str)
    except Exception:
        nuovo_hotel = {}

    if not nuovo_hotel:
        flash('Dati hotel non validi.', 'danger')
        return redirect(url_for('amadeus.hotels'))

    # Gestione lista hotel
    import uuid
    nuovo_hotel['item_id'] = str(uuid.uuid4())[:8]

    hotel_esistenti = []
    if viaggio.hotel_json:
        try:
            data = json.loads(viaggio.hotel_json)
            if isinstance(data, list):
                hotel_esistenti = data
            elif isinstance(data, dict) and data:
                if 'item_id' not in data: data['item_id'] = 'legacy'
                hotel_esistenti = [data]
        except Exception:
            hotel_esistenti = []

    hotel_esistenti.append(nuovo_hotel)
    viaggio.hotel_json = json.dumps(hotel_esistenti)

    prezzo_hotel = 0.0
    prezzo_str = nuovo_hotel.get('prezzo', '')
    if prezzo_str:
        try:
            prezzo_hotel = float(prezzo_str.split()[0])
        except (ValueError, IndexError):
            prezzo_hotel = 0.0

    if prezzo_hotel > 0:
        attuale = float(viaggio.prezzo_totale or 0)
        viaggio.prezzo_totale = round(attuale + prezzo_hotel, 2)

    viaggio.include_hotel = True
    db.session.commit()

    desc = nuovo_hotel.get('nome', 'hotel selezionato')
    extra = f' (+€{prezzo_hotel:.2f} al totale viaggio)' if prezzo_hotel > 0 else ''
    flash(f'Hotel ({desc}) aggiunto a "{viaggio.nome}"{extra}.', 'success')
    return redirect(url_for('viaggi.detail', id=viaggio_id))


@amadeus_bp.route('/voli', methods=['GET', 'POST'])
@login_required
def voli():
    risultati = None
    dizionari = {}
    error = None
    if request.method == 'POST':
        origin = request.form.get('origin', '').upper().strip()
        destination = request.form.get('destination', '').upper().strip()
        departure_date = request.form.get('departure_date')
        return_date = request.form.get('return_date') or None
        adults = int(request.form.get('adults', 1))

        if not all([origin, destination, departure_date]):
            flash('Compila tutti i campi obbligatori.', 'warning')
        else:
            risultati, dizionari = amadeus.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
            )
            if risultati is None:
                error = 'Errore nella ricerca voli. Verifica le credenziali Amadeus.'
            elif len(risultati) == 0:
                flash('Nessun volo trovato.', 'info')

    viaggi = Viaggio.query.filter(
        Viaggio.stato.in_(['bozza', 'confermato'])
    ).order_by(Viaggio.data_partenza).all()

    return render_template('amadeus/voli.html',
                           risultati=risultati,
                           dizionari=dizionari,
                           error=error,
                           viaggi=viaggi,
                           today=date.today().isoformat())


@amadeus_bp.route('/voli/collega', methods=['POST'])
@login_required
def collega_volo():
    viaggio_id = request.form.get('viaggio_id', type=int)
    volo_json_str = request.form.get('volo_json', '{}')

    if not viaggio_id:
        flash('Seleziona un viaggio.', 'warning')
        return redirect(url_for('amadeus.voli'))

    viaggio = Viaggio.query.get_or_404(viaggio_id)

    # Analizza il JSON del nuovo volo
    try:
        nuovo_volo = json.loads(volo_json_str)
    except Exception:
        nuovo_volo = {}

    if not nuovo_volo:
        flash('Dati volo non validi.', 'danger')
        return redirect(url_for('amadeus.voli'))

    # Gestione lista voli (migrazione graduale)
    import uuid
    nuovo_volo['item_id'] = str(uuid.uuid4())[:8] # ID breve per rimozione

    voli_esistenti = []
    if viaggio.volo_json:
        try:
            data = json.loads(viaggio.volo_json)
            if isinstance(data, list):
                voli_esistenti = data
            elif isinstance(data, dict) and data:
                # Migrazione da singolo oggetto a lista
                if 'item_id' not in data: data['item_id'] = 'legacy'
                voli_esistenti = [data]
        except Exception:
            voli_esistenti = []

    voli_esistenti.append(nuovo_volo)
    viaggio.volo_json = json.dumps(voli_esistenti)

    # Estrai il prezzo numerico
    prezzo_volo = 0.0
    prezzo_str = nuovo_volo.get('prezzo', '')
    if prezzo_str:
        try:
            prezzo_volo = float(prezzo_str.split()[0])
        except (ValueError, IndexError):
            prezzo_volo = 0.0

    # Aggiorna prezzo_totale del viaggio
    if prezzo_volo > 0:
        attuale = float(viaggio.prezzo_totale or 0)
        viaggio.prezzo_totale = round(attuale + prezzo_volo, 2)

    viaggio.include_volo = True
    db.session.commit()

    desc = f"{nuovo_volo.get('da','?')} → {nuovo_volo.get('a','?')} · {prezzo_str}"
    extra = f' (+€{prezzo_volo:.2f} al totale viaggio)' if prezzo_volo > 0 else ''
    flash(f'Volo ({desc}) aggiunto a "{viaggio.nome}"{extra}.', 'success')
    return redirect(url_for('viaggi.detail', id=viaggio_id))


@amadeus_bp.route('/auto', methods=['GET', 'POST'])
@login_required
def auto():
    risultati = None
    error = None
    if request.method == 'POST':
        pickup = request.form.get('pickup_location', '').upper().strip()
        pickup_date = request.form.get('pickup_date')
        pickup_time = request.form.get('pickup_time', '10:00')
        dropoff_date = request.form.get('dropoff_date')
        dropoff_time = request.form.get('dropoff_time', '10:00')
        dropoff_loc = request.form.get('dropoff_location', '').upper().strip() or None

        if not all([pickup, pickup_date, dropoff_date]):
            flash('Compila tutti i campi obbligatori.', 'warning')
        else:
            pickup_dt = f'{pickup_date}T{pickup_time}:00'
            dropoff_dt = f'{dropoff_date}T{dropoff_time}:00'
            risultati = amadeus.search_cars(
                pickup_location=pickup,
                pickup_datetime=pickup_dt,
                dropoff_datetime=dropoff_dt,
                dropoff_location=dropoff_loc
            )
            if risultati is None or len(risultati) == 0:
                flash('Nessun veicolo disponibile per i criteri selezionati.', 'info')

    viaggi = Viaggio.query.filter(
        Viaggio.stato.in_(['bozza', 'confermato'])
    ).order_by(Viaggio.data_partenza).all()

    return render_template('amadeus/auto.html',
                           risultati=risultati,
                           error=error,
                           viaggi=viaggi,
                           today=date.today().isoformat())


@amadeus_bp.route('/auto/collega', methods=['POST'])
@login_required
def collega_auto():
    viaggio_id = request.form.get('viaggio_id', type=int)
    auto_json_str = request.form.get('auto_json', '{}')

    if not viaggio_id:
        flash('Seleziona un viaggio.', 'warning')
        return redirect(url_for('amadeus.auto'))

    viaggio = Viaggio.query.get_or_404(viaggio_id)

    try:
        nuova_auto = json.loads(auto_json_str)
    except Exception:
        nuova_auto = {}

    if not nuova_auto:
        flash('Dati auto non validi.', 'danger')
        return redirect(url_for('amadeus.auto'))

    # Gestione lista auto
    import uuid
    nuova_auto['item_id'] = str(uuid.uuid4())[:8]

    auto_esistenti = []
    if viaggio.auto_json:
        try:
            data = json.loads(viaggio.auto_json)
            if isinstance(data, list):
                auto_esistenti = data
            elif isinstance(data, dict) and data:
                if 'item_id' not in data: data['item_id'] = 'legacy'
                auto_esistenti = [data]
        except Exception:
            auto_esistenti = []

    auto_esistenti.append(nuova_auto)
    viaggio.auto_json = json.dumps(auto_esistenti)

    prezzo_auto = 0.0
    prezzo_str = nuova_auto.get('prezzo', '')
    if prezzo_str:
        try:
            prezzo_auto = float(prezzo_str.split()[0])
        except (ValueError, IndexError):
            prezzo_auto = 0.0

    if prezzo_auto > 0:
        attuale = float(viaggio.prezzo_totale or 0)
        viaggio.prezzo_totale = round(attuale + prezzo_auto, 2)

    viaggio.include_auto = True
    db.session.commit()

    desc = nuova_auto.get('descrizione', 'auto selezionata')
    extra = f' (+€{prezzo_auto:.2f} al totale viaggio)' if prezzo_auto > 0 else ''
    flash(f'Auto ({desc}) aggiunta a "{viaggio.nome}"{extra}.', 'success')
    return redirect(url_for('viaggi.detail', id=viaggio_id))
