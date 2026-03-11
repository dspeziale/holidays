from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Optional, Length
from app.utils.lists import PAESI, NAZIONALITA, LINGUE


class ClienteForm(FlaskForm):
    nome = StringField('Nome',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=80)])
    cognome = StringField('Cognome',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=80)])
    email = EmailField('Email',
        validators=[DataRequired(message='Campo obbligatorio'), Email(message='Email non valida')])
    telefono = StringField('Telefono', validators=[Optional(), Length(max=30)])
    data_nascita = DateField('Data di nascita', validators=[Optional()])
    nazionalita = SelectField('Nazionalità', choices=NAZIONALITA, validators=[Optional()])
    tipo_documento = SelectField('Tipo documento', choices=[
        ('', '— Seleziona —'),
        ("Carta d'identità", "Carta d'identità"),
        ('Passaporto', 'Passaporto'),
        ('Patente', 'Patente'),
    ], validators=[Optional()])
    numero_documento = StringField('Numero documento', validators=[Optional(), Length(max=50)])
    data_rilascio_documento = DateField('Data rilascio', validators=[Optional()])
    data_scadenza_documento = DateField('Data scadenza', validators=[Optional()])
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=255)])
    citta = StringField('Città', validators=[Optional(), Length(max=100)])
    cap = StringField('CAP', validators=[Optional(), Length(max=10)])
    paese = SelectField('Paese', choices=PAESI, validators=[Optional()])
    lingua_preferita = SelectField('Lingua preferita', choices=LINGUE, validators=[Optional()])
    note = TextAreaField('Note', validators=[Optional()])
    attivo = BooleanField('Cliente attivo', default=True)
