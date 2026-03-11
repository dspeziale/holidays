from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.services import getyourguide_service as gyg

gyg_bp = Blueprint('getyourguide', __name__, url_prefix='/getyourguide')


@gyg_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    risultati = None
    totale = 0
    error = None
    query = ''

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            flash('Inserisci una keyword di ricerca.', 'warning')
        else:
            risultati, totale = gyg.search_activities(query=query)
            if risultati is None:
                error = ('Errore connessione GetYourGuide. '
                         'Verifica la chiave API GETYOURGUIDE_API_KEY nel .env.')
            elif len(risultati) == 0:
                flash('Nessuna attività trovata per la ricerca.', 'info')

    return render_template('getyourguide/index.html',
                           risultati=risultati,
                           totale=totale,
                           error=error,
                           query=query)


@gyg_bp.route('/attivita/<int:tour_id>')
@login_required
def detail(tour_id):
    attivita = gyg.get_activity_detail(tour_id)
    if not attivita:
        flash('Attività non trovata o errore API.', 'danger')
        return render_template('getyourguide/index.html',
                               risultati=None, totale=0, error=None, query='')
    return render_template('getyourguide/detail.html', attivita=attivita)
