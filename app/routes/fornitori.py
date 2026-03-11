from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.fornitore import Fornitore
from app.forms.fornitore import FornitoreForm
from app.utils.decorators import manager_required

fornitori_bp = Blueprint('fornitori', __name__, url_prefix='/fornitori')

@fornitori_bp.route('/')
@login_required
def index():
    fornitori = Fornitore.query.order_by(Fornitore.nome).all()
    return render_template('fornitori/index.html', fornitori=fornitori)

@fornitori_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
@manager_required
def nuovo():
    form = FornitoreForm()
    if form.validate_on_submit():
        fornitore = Fornitore()
        form.populate_obj(fornitore)
        db.session.add(fornitore)
        db.session.commit()
        flash(f'Fornitore "{fornitore.nome}" creato con successo.', 'success')
        return redirect(url_for('fornitori.index'))
    return render_template('fornitori/form.html', form=form, title='Nuovo Fornitore', fornitore=None)

@fornitori_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@manager_required
def modifica(id):
    fornitore = Fornitore.query.get_or_404(id)
    form = FornitoreForm(obj=fornitore)
    if form.validate_on_submit():
        form.populate_obj(fornitore)
        db.session.commit()
        flash(f'Fornitore "{fornitore.nome}" aggiornato.', 'success')
        return redirect(url_for('fornitori.index'))
    return render_template('fornitori/form.html', form=form, title='Modifica Fornitore', fornitore=fornitore)

@fornitori_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@manager_required
def elimina(id):
    fornitore = Fornitore.query.get_or_404(id)
    nome = fornitore.nome
    db.session.delete(fornitore)
    db.session.commit()
    flash(f'Fornitore "{nome}" eliminato.', 'warning')
    return redirect(url_for('fornitori.index'))
