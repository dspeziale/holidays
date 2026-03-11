from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models.esperienza import Esperienza
from app.forms.esperienza import EsperienzaForm
from app.utils.decorators import manager_required

esperienze_bp = Blueprint('esperienze', __name__, url_prefix='/esperienze')


@esperienze_bp.route('/')
@login_required
def index():
    esperienze = Esperienza.query.order_by(Esperienza.nome).all()
    return render_template('esperienze/index.html', esperienze=esperienze)


@esperienze_bp.route('/nuova', methods=['GET', 'POST'])
@login_required
@manager_required
def nuova():
    form = EsperienzaForm()
    if form.validate_on_submit():
        esp = Esperienza()
        form.populate_obj(esp)
        db.session.add(esp)
        db.session.commit()
        flash(f'Esperienza "{esp.nome}" creata con successo.', 'success')
        return redirect(url_for('esperienze.index'))
    return render_template('esperienze/form.html', form=form, title='Nuova Esperienza', esperienza=None)


@esperienze_bp.route('/<int:id>')
@login_required
def detail(id):
    esp = Esperienza.query.get_or_404(id)
    return render_template('esperienze/detail.html', esperienza=esp)


@esperienze_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@manager_required
def modifica(id):
    esp = Esperienza.query.get_or_404(id)
    form = EsperienzaForm(obj=esp)
    if form.validate_on_submit():
        form.populate_obj(esp)
        db.session.commit()
        flash('Esperienza aggiornata con successo.', 'success')
        return redirect(url_for('esperienze.detail', id=esp.id))
    return render_template('esperienze/form.html', form=form, title='Modifica Esperienza', esperienza=esp)


@esperienze_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@manager_required
def elimina(id):
    esp = Esperienza.query.get_or_404(id)
    nome = esp.nome
    db.session.delete(esp)
    db.session.commit()
    flash(f'Esperienza "{nome}" eliminata.', 'warning')
    return redirect(url_for('esperienze.index'))


@esperienze_bp.route('/api/list')
@login_required
def api_list():
    esperienze = Esperienza.query.filter_by(attivo=True).order_by(Esperienza.nome).all()
    return jsonify([e.to_dict() for e in esperienze])
