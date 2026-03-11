from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange


class PacchettoForm(FlaskForm):
    nome = StringField('Nome Pacchetto',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=150)])
    descrizione = TextAreaField('Descrizione', validators=[Optional()])
    destinazione = StringField('Destinazione principale', validators=[Optional(), Length(max=100)])
    durata_giorni = IntegerField('Durata (giorni)',
        validators=[DataRequired(), NumberRange(min=1)], default=1)
    prezzo_base = DecimalField('Prezzo base (€)',
        validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    prezzo_adulto = DecimalField('Prezzo adulto (€)',
        validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    prezzo_bambino = DecimalField('Prezzo bambino (€)',
        validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    include_volo = BooleanField('Include volo', default=False)
    include_hotel = BooleanField('Include hotel', default=False)
    include_auto = BooleanField('Include noleggio auto', default=False)
    note = TextAreaField('Note', validators=[Optional()])
    attivo = BooleanField('Pacchetto attivo', default=True)
