from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, URL

class FornitoreForm(FlaskForm):
    nome = StringField('Nome Fornitore', validators=[DataRequired()])
    tipo_servizio = SelectField('Tipo di Servizio', choices=[
        ('Hotel', 'Hotel'),
        ('Voli', 'Voli'),
        ('Transfer', 'Transfer'),
        ('Tour', 'Tour'),
        ('Esperienze', 'Esperienze'),
        ('Altro', 'Altro')
    ])
    contatto_nome = StringField('Nome Contatto')
    email = StringField('Email', validators=[Optional(), Email()])
    telefono = StringField('Telefono')
    indirizzo = StringField('Indirizzo')
    sito_web = StringField('Sito Web', validators=[Optional(), URL()])
    piva_codfisc = StringField('P.IVA / Cod. Fiscale')
    note = TextAreaField('Note')
    attivo = BooleanField('Attivo', default=True)
    submit = SubmitField('Salva')
