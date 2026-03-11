"""
Wizard multi-step per creare un Viaggio legato a un Cliente.

Flusso sessione:
  Step 1 — Seleziona o crea cliente
  Step 2 — Dati viaggio (nome, destinazione, date, partecipanti, servizi)
  Step 3 — Scegli pacchetto base (opzionale) e tour (drag & drop)
  Step 4 — Scegli esperienze (drag & drop)
  Step 5 — Riepilogo e conferma
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from flask_login import login_required
from app import db
from app.models.cliente import Cliente
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.models.pacchetto import Pacchetto
from app.models.viaggio import Viaggio

wizard_bp = Blueprint('wizard', __name__, url_prefix='/wizard')

SESSION_KEY = 'wizard_viaggio'


def _wiz():
    """Legge/inizializza i dati wizard dalla sessione."""
    return session.setdefault(SESSION_KEY, {})


def _save(data: dict):
    session[SESSION_KEY] = data
    session.modified = True


def _reset():
    session.pop(SESSION_KEY, None)


# ── STEP 1: Cliente ────────────────────────────────────────────────────────────
@wizard_bp.route('/step1', methods=['GET', 'POST'])
@login_required
def step1():
    clienti = Cliente.query.filter_by(attivo=True).order_by(Cliente.cognome).all()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'select':
            cliente_id = request.form.get('cliente_id')
            if not cliente_id:
                flash('Seleziona un cliente.', 'warning')
                return render_template('wizard/step1.html', clienti=clienti, step=1)
            data = _wiz()
            data['cliente_id'] = int(cliente_id)
            _save(data)
            return redirect(url_for('wizard.step2'))
        elif action == 'new':
            # Redirect al form cliente con parametro di ritorno wizard
            return redirect(url_for('clienti.nuovo', next='wizard'))

    return render_template('wizard/step1.html', clienti=clienti, step=1,
                           wiz=_wiz())


# ── STEP 2: Dati viaggio ───────────────────────────────────────────────────────
@wizard_bp.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    data = _wiz()
    if not data.get('cliente_id'):
        flash('Prima seleziona un cliente.', 'warning')
        return redirect(url_for('wizard.step1'))

    cliente = Cliente.query.get_or_404(data['cliente_id'])

    if request.method == 'POST':
        nome       = request.form.get('nome', '').strip()
        destinazione = request.form.get('destinazione', '').strip()
        data_partenza  = request.form.get('data_partenza')
        data_rientro   = request.form.get('data_rientro')
        n_adulti   = int(request.form.get('n_adulti', 1))
        n_bambini  = int(request.form.get('n_bambini', 0))
        budget     = request.form.get('budget')
        include_volo  = bool(request.form.get('include_volo'))
        include_hotel = bool(request.form.get('include_hotel'))
        include_auto  = bool(request.form.get('include_auto'))
        include_treno = bool(request.form.get('include_treno'))
        include_transfer = bool(request.form.get('include_transfer'))
        note_cliente  = request.form.get('note_cliente', '')

        if not nome:
            flash('Il nome del viaggio è obbligatorio.', 'warning')
            return render_template('wizard/step2.html', cliente=cliente, step=2, wiz=data)

        data.update({
            'nome': nome,
            'destinazione': destinazione,
            'data_partenza': data_partenza,
            'data_rientro': data_rientro,
            'n_adulti': n_adulti,
            'n_bambini': n_bambini,
            'budget': budget,
            'include_volo': include_volo,
            'include_hotel': include_hotel,
            'include_auto': include_auto,
            'include_treno': include_treno,
            'include_transfer': include_transfer,
            'note_cliente': note_cliente,
        })
        _save(data)
        return redirect(url_for('wizard.step3'))

    return render_template('wizard/step2.html', cliente=cliente, step=2, wiz=data)


# ── STEP 3: Pacchetto + Tour ───────────────────────────────────────────────────
@wizard_bp.route('/step3', methods=['GET', 'POST'])
@login_required
def step3():
    data = _wiz()
    if not data.get('nome'):
        return redirect(url_for('wizard.step2'))

    pacchetti   = Pacchetto.query.filter_by(attivo=True).order_by(Pacchetto.nome).all()
    tours_disp  = Tour.query.filter_by(attivo=True).order_by(Tour.nome).all()

    if request.method == 'POST':
        pacchetto_id = request.form.get('pacchetto_id') or None
        tour_ids = [int(x) for x in request.form.getlist('tour_ids') if x]

        # Se sceglie un pacchetto, pre-carica i suoi tour
        if pacchetto_id:
            pkg = Pacchetto.query.get(int(pacchetto_id))
            if pkg:
                pkg_tours = [t.id for t in pkg.tours]
                # Unisci senza duplicati preservando ordine
                for tid in pkg_tours:
                    if tid not in tour_ids:
                        tour_ids.insert(0, tid)

        data['pacchetto_id'] = int(pacchetto_id) if pacchetto_id else None
        data['tour_ids'] = tour_ids
        _save(data)
        return redirect(url_for('wizard.step4'))

    # Preselezionati
    selected_tours = data.get('tour_ids', [])
    # Se ha già un pacchetto scelto pre-carica
    pkg_tour_ids = []
    if data.get('pacchetto_id'):
        pkg = Pacchetto.query.get(data['pacchetto_id'])
        if pkg:
            pkg_tour_ids = [t.id for t in pkg.tours]

    return render_template('wizard/step3.html', step=3, wiz=data,
                           pacchetti=pacchetti,
                           tours_disp=tours_disp,
                           selected_tours=selected_tours,
                           pkg_tour_ids=pkg_tour_ids)


# ── STEP 4: Esperienze ────────────────────────────────────────────────────────
@wizard_bp.route('/step4', methods=['GET', 'POST'])
@login_required
def step4():
    data = _wiz()
    if not data.get('nome'):
        return redirect(url_for('wizard.step2'))

    esp_disp = Esperienza.query.filter_by(attivo=True).order_by(Esperienza.nome).all()

    if request.method == 'POST':
        esp_ids = [int(x) for x in request.form.getlist('esperienza_ids') if x]

        # Se ha un pacchetto, pre-carica le sue esperienze
        if data.get('pacchetto_id'):
            pkg = Pacchetto.query.get(data['pacchetto_id'])
            if pkg:
                for e in pkg.esperienze:
                    if e.id not in esp_ids:
                        esp_ids.insert(0, e.id)

        data['esperienza_ids'] = esp_ids
        _save(data)
        return redirect(url_for('wizard.step5'))

    selected_esperienze = data.get('esperienza_ids', [])
    return render_template('wizard/step4.html', step=4, wiz=data,
                           esp_disp=esp_disp,
                           selected_esperienze=selected_esperienze)


# ── STEP 5: Riepilogo + Salva ─────────────────────────────────────────────────
@wizard_bp.route('/step5', methods=['GET', 'POST'])
@login_required
def step5():
    data = _wiz()
    if not data.get('nome'):
        return redirect(url_for('wizard.step1'))

    cliente    = Cliente.query.get_or_404(data['cliente_id'])
    tours      = Tour.query.filter(Tour.id.in_(data.get('tour_ids', []))).all()
    esperienze = Esperienza.query.filter(Esperienza.id.in_(data.get('esperienza_ids', []))).all()
    pacchetto  = Pacchetto.query.get(data['pacchetto_id']) if data.get('pacchetto_id') else None

    # Calcola prezzo totale
    prezzo = sum(float(t.prezzo_adulto or 0) * data.get('n_adulti', 1)
                 + float(t.prezzo_bambino or 0) * data.get('n_bambini', 0)
                 for t in tours)
    prezzo += sum(float(e.prezzo_adulto or 0) * data.get('n_adulti', 1)
                  + float(e.prezzo_bambino or 0) * data.get('n_bambini', 0)
                  for e in esperienze)
    if pacchetto:
        prezzo += float(pacchetto.prezzo_base or 0)

    if request.method == 'POST':
        from datetime import date as ddate
        def parse_date(s):
            try:
                from datetime import datetime
                return datetime.strptime(s, '%Y-%m-%d').date()
            except Exception:
                return None

        viaggio = Viaggio(
            cliente_id    = data['cliente_id'],
            pacchetto_id  = data.get('pacchetto_id'),
            nome          = data['nome'],
            destinazione  = data.get('destinazione'),
            data_partenza = parse_date(data.get('data_partenza', '')),
            data_rientro  = parse_date(data.get('data_rientro', '')),
            n_adulti      = data.get('n_adulti', 1),
            n_bambini     = data.get('n_bambini', 0),
            budget        = data.get('budget') or None,
            prezzo_totale = round(prezzo, 2),
            include_volo  = data.get('include_volo', False),
            include_hotel = data.get('include_hotel', False),
            include_auto  = data.get('include_auto', False),
            include_treno = data.get('include_treno', False),
            include_transfer = data.get('include_transfer', False),
            note_cliente  = data.get('note_cliente', ''),
            stato         = request.form.get('stato', 'bozza'),
        )
        viaggio.tours      = tours
        viaggio.esperienze = esperienze
        db.session.add(viaggio)
        db.session.commit()
        _reset()
        flash(f'Viaggio "{viaggio.nome}" creato con successo!', 'success')
        return redirect(url_for('viaggi.detail', id=viaggio.id))

    return render_template('wizard/step5.html', step=5, wiz=data,
                           cliente=cliente, tours=tours, esperienze=esperienze,
                           pacchetto=pacchetto, prezzo_totale=round(prezzo, 2))


@wizard_bp.route('/reset')
@login_required
def reset():
    _reset()
    return redirect(url_for('wizard.step1'))
