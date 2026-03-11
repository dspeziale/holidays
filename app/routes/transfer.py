from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.services import transfer_service as ts
from app.models.viaggio import Viaggio
from datetime import date
import json

transfer_bp = Blueprint('transfer', __name__, url_prefix='/transfer')


@transfer_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    risultati = None
    info = None
    oggi = date.today().isoformat()

    if request.method == 'POST':
        origine      = request.form.get('origine', '').strip()
        destinazione = request.form.get('destinazione', '').strip()
        data_str     = request.form.get('data_transfer') or oggi
        ora_str      = request.form.get('ora_transfer', '10:00')
        n_pass       = max(1, int(request.form.get('n_passeggeri', 1)))

        if not origine or not destinazione:
            flash('Inserisci origine e destinazione.', 'warning')
        else:
            risultati, info = ts.cerca_transfer(
                origine=origine,
                destinazione=destinazione,
                data_str=data_str,
                ora_str=ora_str,
                n_passeggeri=n_pass,
            )

    viaggi = Viaggio.query.filter(
        Viaggio.stato.in_(['bozza', 'confermato'])
    ).order_by(Viaggio.data_partenza).all()

    return render_template('transfer/index.html',
                           risultati=risultati,
                           info=info,
                           viaggi=viaggi,
                           oggi=oggi)


@transfer_bp.route('/collega', methods=['POST'])
@login_required
def collega_transfer():
    viaggio_id = request.form.get('viaggio_id', type=int)
    transfer_json_str = request.form.get('transfer_json', '{}')

    if not viaggio_id:
        flash('Seleziona un viaggio.', 'warning')
        return redirect(url_for('transfer.index'))

    viaggio = Viaggio.query.get_or_404(viaggio_id)

    try:
        nuovo_tr = json.loads(transfer_json_str)
    except Exception:
        nuovo_tr = {}

    if not nuovo_tr:
        flash('Dati transfer non validi.', 'danger')
        return redirect(url_for('transfer.index'))

    # Gestione lista transfer
    import uuid
    nuovo_tr['item_id'] = str(uuid.uuid4())[:8]

    tr_esistenti = []
    if viaggio.transfer_json:
        try:
            data = json.loads(viaggio.transfer_json)
            if isinstance(data, list):
                tr_esistenti = data
            elif isinstance(data, dict) and data:
                if 'item_id' not in data: data['item_id'] = 'legacy'
                tr_esistenti = [data]
        except Exception:
            tr_esistenti = []

    tr_esistenti.append(nuovo_tr)
    viaggio.transfer_json = json.dumps(tr_esistenti)

    prezzo_tr = 0.0
    prezzo_str = nuovo_tr.get('prezzo', '')
    if prezzo_str:
        try:
            prezzo_tr = float(str(prezzo_str).split()[0])
        except (ValueError, IndexError):
            prezzo_tr = 0.0

    if prezzo_tr > 0:
        attuale = float(viaggio.prezzo_totale or 0)
        viaggio.prezzo_totale = round(attuale + prezzo_tr, 2)

    viaggio.include_transfer = True
    db.session.commit()

    desc = f"{nuovo_tr.get('tipo', 'transfer')} — {nuovo_tr.get('origine', '?')} → {nuovo_tr.get('destinazione', '?')}"
    extra = f' (+€{prezzo_tr:.2f} al totale viaggio)' if prezzo_tr > 0 else ''
    flash(f'Transfer ({desc}) aggiunto a "{viaggio.nome}"{extra}.', 'success')
    return redirect(url_for('viaggi.detail', id=viaggio_id))
