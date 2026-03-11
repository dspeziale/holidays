from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models.tour import Tour
from app.forms.tour import TourForm
from app.utils.decorators import manager_required

tours_bp = Blueprint('tours', __name__, url_prefix='/tour')


@tours_bp.route('/')
@login_required
def index():
    tours = Tour.query.order_by(Tour.nome).all()
    return render_template('tours/index.html', tours=tours)


@tours_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
@manager_required
def nuovo():
    form = TourForm()
    if form.validate_on_submit():
        tour = Tour()
        form.populate_obj(tour)
        db.session.add(tour)
        db.session.commit()
        flash(f'Tour "{tour.nome}" creato con successo.', 'success')
        return redirect(url_for('tours.index'))
    return render_template('tours/form.html', form=form, title='Nuovo Tour', tour=None)


@tours_bp.route('/<int:id>')
@login_required
def detail(id):
    tour = Tour.query.get_or_404(id)
    return render_template('tours/detail.html', tour=tour)


@tours_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@manager_required
def modifica(id):
    tour = Tour.query.get_or_404(id)
    form = TourForm(obj=tour)
    if form.validate_on_submit():
        form.populate_obj(tour)
        db.session.commit()
        flash('Tour aggiornato con successo.', 'success')
        return redirect(url_for('tours.detail', id=tour.id))
    return render_template('tours/form.html', form=form, title='Modifica Tour', tour=tour)


@tours_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@manager_required
def elimina(id):
    tour = Tour.query.get_or_404(id)
    nome = tour.nome
    db.session.delete(tour)
    db.session.commit()
    flash(f'Tour "{nome}" eliminato.', 'warning')
    return redirect(url_for('tours.index'))


@tours_bp.route('/api/list')
@login_required
def api_list():
    tours = Tour.query.filter_by(attivo=True).order_by(Tour.nome).all()
    return jsonify([t.to_dict() for t in tours])
