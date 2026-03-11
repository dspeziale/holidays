from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.forms.user import UserForm, UserPasswordForm
from app.services.email_service import send_benvenuto_utente
from app.utils.decorators import admin_required

utenti_bp = Blueprint('utenti', __name__, url_prefix='/utenti')


@utenti_bp.route('/')
@login_required
@admin_required
def index():
    utenti = User.query.order_by(User.username).all()
    return render_template('utenti/index.html', utenti=utenti)


@utenti_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuovo():
    form = UserForm()
    if form.validate_on_submit():
        # Controlla duplicati
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash('Email già in uso.', 'danger')
            return render_template('utenti/form.html', form=form, title='Nuovo Utente', utente=None)
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash('Username già in uso.', 'danger')
            return render_template('utenti/form.html', form=form, title='Nuovo Utente', utente=None)

        # Genera password automatica
        password_generata = User.generate_password()

        utente = User(
            username=form.username.data.strip(),
            email=form.email.data.lower().strip(),
            role=form.role.data,
            attivo=form.attivo.data
        )
        utente.set_password(password_generata)
        db.session.add(utente)
        db.session.commit()

        # Invia email con credenziali
        try:
            send_benvenuto_utente(utente, password_generata)
            flash(f'Utente {utente.username} creato. Credenziali inviate a {utente.email}.', 'success')
        except Exception as e:
            flash(f'Utente creato, ma errore invio email: {str(e)}', 'warning')

        return redirect(url_for('utenti.index'))
    return render_template('utenti/form.html', form=form, title='Nuovo Utente', utente=None)


@utenti_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@admin_required
def modifica(id):
    utente = User.query.get_or_404(id)
    form = UserForm(obj=utente)
    if form.validate_on_submit():
        # Controlla duplicati (escludi l'utente corrente)
        dup_email = User.query.filter(
            User.email == form.email.data.lower().strip(),
            User.id != id
        ).first()
        if dup_email:
            flash('Email già in uso da un altro utente.', 'danger')
            return render_template('utenti/form.html', form=form, title='Modifica Utente', utente=utente)

        utente.username = form.username.data.strip()
        utente.email = form.email.data.lower().strip()
        utente.role = form.role.data
        utente.attivo = form.attivo.data
        db.session.commit()
        flash('Utente aggiornato con successo.', 'success')
        return redirect(url_for('utenti.index'))
    return render_template('utenti/form.html', form=form, title='Modifica Utente', utente=utente)


@utenti_bp.route('/<int:id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password_admin(id):
    utente = User.query.get_or_404(id)
    form = UserPasswordForm()
    if form.validate_on_submit():
        utente.set_password(form.password.data)
        db.session.commit()
        flash(f'Password di {utente.username} aggiornata.', 'success')
        return redirect(url_for('utenti.index'))
    return render_template('utenti/reset_password.html', form=form, utente=utente)


@utenti_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@admin_required
def elimina(id):
    utente = User.query.get_or_404(id)
    if utente.id == current_user.id:
        flash('Non puoi eliminare il tuo account.', 'danger')
        return redirect(url_for('utenti.index'))
    nome = utente.username
    db.session.delete(utente)
    db.session.commit()
    flash(f'Utente {nome} eliminato.', 'warning')
    return redirect(url_for('utenti.index'))
