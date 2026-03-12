from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.services import treni_service as ts
from app.models.viaggio import Viaggio
from datetime import date
import json

treni_bp = Blueprint('treni', __name__, url_prefix='/treni')


@treni_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    risultato = None
    oggi = date.today().isoformat()

    if request.method == 'POST':
        origine      = request.form.get('origine', '').strip()
        destinazione = request.form.get('destinazione', '').strip()
        data_viaggio = request.form.get('data_viaggio') or oggi
        n_adulti     = max(1, int(request.form.get('n_adulti', 1)))
        n_bambini    = max(0, int(request.form.get('n_bambini', 0)))

        risultato = ts.cerca_treni(
            origine=origine,
            destinazione=destinazione,
            data_str=data_viaggio,
            n_adulti=n_adulti,
            n_bambini=n_bambini,
        )
        risultato['_form'] = {
            'origine': origine,
            'destinazione': destinazione,
            'data_viaggio': data_viaggio,
            'n_adulti': n_adulti,
            'n_bambini': n_bambini,
        }

    stazioni = ts.get_stazioni_list()
    viaggi = Viaggio.query.filter(
        Viaggio.stato.in_(['bozza', 'confermato'])
    ).order_by(Viaggio.data_partenza).all()

    return render_template('treni/index.html',
                           risultato=risultato,
                           stazioni=stazioni,
                           viaggi=viaggi,
                           oggi=oggi)


@treni_bp.route('/collega', methods=['POST'])
@login_required
def collega_treno():
    viaggio_id = request.form.get('viaggio_id', type=int)
    treno_json_str = request.form.get('treno_json', '{}')

    if not viaggio_id:
        flash('Seleziona un viaggio.', 'warning')
        return redirect(url_for('treni.index'))

    viaggio = Viaggio.query.get_or_404(viaggio_id)

    try:
        nuovo_treno = json.loads(treno_json_str)
    except Exception:
        nuovo_treno = {}

    if not nuovo_treno:
        flash('Dati treno non validi.', 'danger')
        return redirect(url_for('treni.index'))

    # Gestione lista treni
    import uuid
    nuovo_treno['item_id'] = str(uuid.uuid4())[:8]

    treni_esistenti = []
    if viaggio.treno_json:
        try:
            data = json.loads(viaggio.treno_json)
            if isinstance(data, list):
                treni_esistenti = data
            elif isinstance(data, dict) and data:
                if 'item_id' not in data: data['item_id'] = 'legacy'
                treni_esistenti = [data]
        except Exception:
            treni_esistenti = []

    treni_esistenti.append(nuovo_treno)
    viaggio.treno_json = json.dumps(treni_esistenti)

    prezzo_treno = 0.0
    prezzo_str = nuovo_treno.get('prezzo_tot', '')
    if prezzo_str:
        try:
            prezzo_treno = float(str(prezzo_str).replace(',', '.'))
        except (ValueError, IndexError):
            prezzo_treno = 0.0

    if prezzo_treno > 0:
        attuale = float(viaggio.prezzo_totale or 0)
        viaggio.prezzo_totale = round(attuale + prezzo_treno, 2)

    viaggio.include_treno = True
    db.session.commit()

    desc = f"{nuovo_treno.get('origine','?')} → {nuovo_treno.get('destinazione','?')} ({nuovo_treno.get('partenza','')}-{nuovo_treno.get('arrivo','')})"
    extra = f' (+€{prezzo_treno:.2f} al totale viaggio)' if prezzo_treno > 0 else ''
    flash(f'Treno ({desc}) aggiunto a "{viaggio.nome}"{extra}.', 'success')
    return redirect(url_for('viaggi.detail', id=viaggio_id))
