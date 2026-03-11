from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from app.models.cliente import Cliente
from app.forms.cliente import ClienteForm

clienti_bp = Blueprint('clienti', __name__, url_prefix='/clienti')


@clienti_bp.route('/')
@login_required
def index():
    clienti = Cliente.query.order_by(Cliente.cognome, Cliente.nome).all()
    return render_template('clienti/index.html', clienti=clienti)


@clienti_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente()
        form.populate_obj(cliente)
        cliente.email = cliente.email.lower().strip()
        db.session.add(cliente)
        db.session.commit()
        flash(f'Cliente {cliente.nome_completo()} creato con successo.', 'success')
        return redirect(url_for('clienti.index'))
    return render_template('clienti/form.html', form=form, title='Nuovo Cliente', cliente=None)


@clienti_bp.route('/<int:id>')
@login_required
def detail(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('clienti/detail.html', cliente=cliente)


@clienti_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        form.populate_obj(cliente)
        cliente.email = cliente.email.lower().strip()
        db.session.commit()
        flash('Cliente aggiornato con successo.', 'success')
        return redirect(url_for('clienti.detail', id=cliente.id))
    return render_template('clienti/form.html', form=form, title='Modifica Cliente', cliente=cliente)


@clienti_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
def elimina(id):
    cliente = Cliente.query.get_or_404(id)
    nome = cliente.nome_completo()
    db.session.delete(cliente)
    db.session.commit()
    flash(f'Cliente {nome} eliminato.', 'warning')
    return redirect(url_for('clienti.index'))


@clienti_bp.route('/api/list')
@login_required
def api_list():
    clienti = Cliente.query.order_by(Cliente.cognome).all()
    return jsonify([c.to_dict() for c in clienti])
