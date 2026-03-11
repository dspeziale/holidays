from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from app.utils.lists import ESPERIENZA_CATEGORIE, PAESI, LINGUE


class EsperienzaForm(FlaskForm):
    nome = StringField('Nome Esperienza',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=150)])
    descrizione = TextAreaField('Descrizione', validators=[Optional()])
    destinazione = StringField('Destinazione',
        validators=[DataRequired(message='Campo obbligatorio'), Length(max=100)])
    paese = SelectField('Paese', choices=PAESI, validators=[Optional()])
    categoria = SelectField('Categoria', choices=ESPERIENZA_CATEGORIE, validators=[Optional()])
    durata_ore = DecimalField('Durata (ore)',
        validators=[Optional(), NumberRange(min=0.5)], places=1, default=2)
    prezzo_adulto = DecimalField('Prezzo Adulto (€)',
        validators=[DataRequired(), NumberRange(min=0)], places=2, default=0)
    prezzo_bambino = DecimalField('Prezzo Bambino (€)',
        validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    fornitore = StringField('Fornitore', validators=[Optional(), Length(max=150)])
    url_getyourguide = StringField('URL GetYourGuide', validators=[Optional(), Length(max=500)])
    gyg_activity_id = StringField('ID Attività GYG', validators=[Optional(), Length(max=50)])
    lingua = SelectField('Lingua', choices=LINGUE, validators=[Optional()])
    punto_incontro = StringField('Punto di incontro', validators=[Optional(), Length(max=255)])
    note = TextAreaField('Note', validators=[Optional()])
    attivo = BooleanField('Esperienza attiva', default=True)
