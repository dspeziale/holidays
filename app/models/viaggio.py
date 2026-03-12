from app import db
from datetime import datetime


viaggio_tours = db.Table(
    'viaggio_tours',
    db.Column('viaggio_id', db.Integer, db.ForeignKey('viaggi.id'), primary_key=True),
    db.Column('tour_id',    db.Integer, db.ForeignKey('tours.id'), primary_key=True),
    db.Column('ordine',     db.Integer, default=0),
)

viaggio_esperienze = db.Table(
    'viaggio_esperienze',
    db.Column('viaggio_id',    db.Integer, db.ForeignKey('viaggi.id'), primary_key=True),
    db.Column('esperienza_id', db.Integer, db.ForeignKey('esperienze.id'), primary_key=True),
    db.Column('ordine',        db.Integer, default=0),
)

viaggio_partecipanti = db.Table(
    'viaggio_partecipanti',
    db.Column('viaggio_id', db.Integer, db.ForeignKey('viaggi.id'), primary_key=True),
    db.Column('cliente_id', db.Integer, db.ForeignKey('clienti.id'), primary_key=True),
)


class Viaggio(db.Model):
    __tablename__ = 'viaggi'

    STATI = {
        'bozza':     'Bozza',
        'confermato':'Confermato',
        'pagato':    'Pagato',
        'completato':'Completato',
        'annullato': 'Annullato',
    }

    id             = db.Column(db.Integer, primary_key=True)
    cliente_id     = db.Column(db.Integer, db.ForeignKey('clienti.id'), nullable=False)
    pacchetto_id   = db.Column(db.Integer, db.ForeignKey('pacchetti.id'), nullable=True)
    nome           = db.Column(db.String(200), nullable=False)
    destinazione   = db.Column(db.String(100))
    data_partenza  = db.Column(db.Date, nullable=True)
    data_rientro   = db.Column(db.Date, nullable=True)
    n_adulti       = db.Column(db.Integer, default=1)
    n_bambini      = db.Column(db.Integer, default=0)
    budget         = db.Column(db.Numeric(10, 2))
    prezzo_totale  = db.Column(db.Numeric(10, 2))
    include_volo   = db.Column(db.Boolean, default=False)
    include_hotel  = db.Column(db.Boolean, default=False)
    include_auto   = db.Column(db.Boolean, default=False)
    include_treno  = db.Column(db.Boolean, default=False)
    volo_json      = db.Column(db.Text)         # JSON del volo selezionato da Amadeus
    auto_json      = db.Column(db.Text)         # JSON dell'auto noleggiata da Amadeus
    hotel_json     = db.Column(db.Text)         # JSON dell'hotel selezionato da Amadeus
    treno_json     = db.Column(db.Text)         # JSON del treno selezionato
    transfer_json  = db.Column(db.Text)         # JSON del transfer selezionato
    pnr_volo       = db.Column(db.String(20))   # Codice prenotazione volo
    include_transfer = db.Column(db.Boolean, default=False)
    note_cliente   = db.Column(db.Text)
    note_interne   = db.Column(db.Text)
    stato          = db.Column(db.String(20), default='bozza', nullable=False)
    is_demo        = db.Column(db.Boolean, default=False, nullable=False)
    
    # Campi per Fatturazione
    ricevuta_emessa = db.Column(db.Boolean, default=False)
    data_ricevuta   = db.Column(db.DateTime)
    fattura_emessa  = db.Column(db.Boolean, default=False)
    data_fattura    = db.Column(db.DateTime)
    numero_ricevuta = db.Column(db.String(20))
    numero_fattura  = db.Column(db.String(20))

    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    cliente    = db.relationship('Cliente',   backref='viaggi', lazy='joined')
    pacchetto  = db.relationship('Pacchetto', backref='viaggi', lazy='joined')
    tours      = db.relationship('Tour',       secondary=viaggio_tours,      backref='viaggi', lazy='subquery')
    esperienze = db.relationship('Esperienza', secondary=viaggio_esperienze, backref='viaggi', lazy='subquery')
    partecipanti = db.relationship('Cliente',  secondary=viaggio_partecipanti, backref='partecipazioni', lazy='subquery')

    def stato_label(self):
        return self.STATI.get(self.stato, self.stato)

    def durata_giorni(self):
        if self.data_partenza and self.data_rientro:
            return (self.data_rientro - self.data_partenza).days
        return None

    def __repr__(self):
        return f'<Viaggio {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cliente': self.cliente.nome_completo() if self.cliente else '',
            'destinazione': self.destinazione,
            'data_partenza': str(self.data_partenza) if self.data_partenza else '',
            'stato': self.stato,
            'stato_label': self.stato_label(),
        }
