from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from app.models.pacchetto import Pacchetto
from app.models.tour import Tour
from app.models.esperienza import Esperienza
from app.forms.pacchetto import PacchettoForm
from app.utils.decorators import manager_required

pacchetti_bp = Blueprint('pacchetti', __name__, url_prefix='/pacchetti')


@pacchetti_bp.route('/')
@login_required
def index():
    pacchetti = Pacchetto.query.order_by(Pacchetto.nome).all()
    return render_template('pacchetti/index.html', pacchetti=pacchetti)


@pacchetti_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
@manager_required
def nuovo():
    form = PacchettoForm()
    tours_disponibili = Tour.query.filter_by(attivo=True).order_by(Tour.nome).all()
    esperienze_disponibili = Esperienza.query.filter_by(attivo=True).order_by(Esperienza.nome).all()

    if form.validate_on_submit():
        pacchetto = Pacchetto()
        form.populate_obj(pacchetto)

        # Associa tour selezionati
        tour_ids = request.form.getlist('tour_ids')
        pacchetto.tours = Tour.query.filter(Tour.id.in_(tour_ids)).all() if tour_ids else []

        # Associa esperienze selezionate
        esp_ids = request.form.getlist('esperienza_ids')
        pacchetto.esperienze = Esperienza.query.filter(Esperienza.id.in_(esp_ids)).all() if esp_ids else []

        db.session.add(pacchetto)
        db.session.commit()
        flash(f'Pacchetto "{pacchetto.nome}" creato con successo.', 'success')
        return redirect(url_for('pacchetti.index'))

    return render_template('pacchetti/form.html', form=form, title='Nuovo Pacchetto',
                           pacchetto=None,
                           tours_disponibili=tours_disponibili,
                           esperienze_disponibili=esperienze_disponibili)


@pacchetti_bp.route('/<int:id>')
@login_required
def detail(id):
    pacchetto = Pacchetto.query.get_or_404(id)
    return render_template('pacchetti/detail.html', pacchetto=pacchetto)


@pacchetti_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@manager_required
def modifica(id):
    pacchetto = Pacchetto.query.get_or_404(id)
    form = PacchettoForm(obj=pacchetto)
    tours_disponibili = Tour.query.filter_by(attivo=True).order_by(Tour.nome).all()
    esperienze_disponibili = Esperienza.query.filter_by(attivo=True).order_by(Esperienza.nome).all()

    if form.validate_on_submit():
        form.populate_obj(pacchetto)

        tour_ids = request.form.getlist('tour_ids')
        pacchetto.tours = Tour.query.filter(Tour.id.in_(tour_ids)).all() if tour_ids else []

        esp_ids = request.form.getlist('esperienza_ids')
        pacchetto.esperienze = Esperienza.query.filter(Esperienza.id.in_(esp_ids)).all() if esp_ids else []

        db.session.commit()
        flash('Pacchetto aggiornato con successo.', 'success')
        return redirect(url_for('pacchetti.detail', id=pacchetto.id))

    selected_tours = [t.id for t in pacchetto.tours]
    selected_esperienze = [e.id for e in pacchetto.esperienze]

    return render_template('pacchetti/form.html', form=form, title='Modifica Pacchetto',
                           pacchetto=pacchetto,
                           tours_disponibili=tours_disponibili,
                           esperienze_disponibili=esperienze_disponibili,
                           selected_tours=selected_tours,
                           selected_esperienze=selected_esperienze)


@pacchetti_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@manager_required
def elimina(id):
    pacchetto = Pacchetto.query.get_or_404(id)
    nome = pacchetto.nome
    db.session.delete(pacchetto)
    db.session.commit()
    flash(f'Pacchetto "{nome}" eliminato.', 'warning')
    return redirect(url_for('pacchetti.index'))


@pacchetti_bp.route('/api/list')
@login_required
def api_list():
    pacchetti = Pacchetto.query.filter_by(attivo=True).order_by(Pacchetto.nome).all()
    return jsonify([p.to_dict() for p in pacchetti])
