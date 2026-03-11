from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from app.utils.lists import TOUR_CATEGORIE, PAESI


class TourForm(FlaskForm):
    nome = StringField('Nome Tour',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=150)])
    descrizione = TextAreaField('Descrizione', validators=[Optional()])
    destinazione = StringField('Destinazione',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=100)])
    paese = SelectField('Paese', choices=PAESI, validators=[Optional()])
    categoria = SelectField('Categoria', choices=TOUR_CATEGORIE, validators=[Optional()])
    durata_giorni = IntegerField('Durata (giorni)',
        validators=[DataRequired(), NumberRange(min=1)], default=1)
    prezzo_adulto = DecimalField('Prezzo Adulto (€)',
        validators=[DataRequired(), NumberRange(min=0)], places=2, default=0)
    prezzo_bambino = DecimalField('Prezzo Bambino (€)',
        validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    capacita_max = IntegerField('Capacità massima',
        validators=[Optional(), NumberRange(min=1)], default=20)
    incluso = TextAreaField('Cosa è incluso', validators=[Optional()])
    escluso = TextAreaField('Cosa NON è incluso', validators=[Optional()])
    note = TextAreaField('Note', validators=[Optional()])
    attivo = BooleanField('Tour attivo', default=True)
