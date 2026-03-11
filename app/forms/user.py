from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, Length, EqualTo


class UserForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(message='Campo obbligatorio'), Length(min=3, max=80)])
    email = EmailField('Email',
        validators=[DataRequired(message='Campo obbligatorio'), Email(message='Email non valida')])
    role = SelectField('Ruolo', choices=[
        ('operatore', 'Operatore'),
        ('manager', 'Manager'),
        ('admin', 'Amministratore'),
    ], validators=[DataRequired()])
    attivo = BooleanField('Utente attivo', default=True)


class UserPasswordForm(FlaskForm):
    """Cambio password manuale (da admin)."""
    password = PasswordField('Nuova Password',
        validators=[DataRequired(), Length(min=8)])
    conferma = PasswordField('Conferma Password',
        validators=[DataRequired(), EqualTo('password', message='Le password non coincidono')])


class LoginForm(FlaskForm):
    email = EmailField('Email',
        validators=[DataRequired(message='Campo obbligatorio'), Email()])
    password = PasswordField('Password',
        validators=[DataRequired(message='Campo obbligatorio')])


class ResetRequestForm(FlaskForm):
    email = EmailField('Email',
        validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nuova Password',
        validators=[DataRequired(), Length(min=8)])
    conferma = PasswordField('Conferma Password',
        validators=[DataRequired(), EqualTo('password', message='Le password non coincidono')])
