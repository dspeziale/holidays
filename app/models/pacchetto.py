from app import db
from datetime import datetime


# Tabelle associative many-to-many
pacchetto_tours = db.Table(
    'pacchetto_tours',
    db.Column('pacchetto_id', db.Integer, db.ForeignKey('pacchetti.id'), primary_key=True),
    db.Column('tour_id', db.Integer, db.ForeignKey('tours.id'), primary_key=True),
    db.Column('ordine', db.Integer, default=0)
)

pacchetto_esperienze = db.Table(
    'pacchetto_esperienze',
    db.Column('pacchetto_id', db.Integer, db.ForeignKey('pacchetti.id'), primary_key=True),
    db.Column('esperienza_id', db.Integer, db.ForeignKey('esperienze.id'), primary_key=True),
    db.Column('ordine', db.Integer, default=0)
)


class Pacchetto(db.Model):
    __tablename__ = 'pacchetti'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.Text)
    destinazione = db.Column(db.String(100))
    durata_giorni = db.Column(db.Integer, default=1)
    prezzo_base = db.Column(db.Numeric(10, 2), default=0)
    prezzo_adulto = db.Column(db.Numeric(10, 2), default=0)
    prezzo_bambino = db.Column(db.Numeric(10, 2), default=0)
    include_volo = db.Column(db.Boolean, default=False)
    include_hotel = db.Column(db.Boolean, default=False)
    include_auto = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    is_demo = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    tours = db.relationship('Tour', secondary=pacchetto_tours, backref='pacchetti', lazy='subquery')
    esperienze = db.relationship('Esperienza', secondary=pacchetto_esperienze, backref='pacchetti', lazy='subquery')

    def prezzo_calcolato(self):
        """Somma prezzi tours + esperienze + base."""
        tot = float(self.prezzo_base or 0)
        for t in self.tours:
            tot += float(t.prezzo_adulto or 0)
        for e in self.esperienze:
            tot += float(e.prezzo_adulto or 0)
        return round(tot, 2)

    def __repr__(self):
        return f'<Pacchetto {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'destinazione': self.destinazione,
            'durata_giorni': self.durata_giorni,
            'prezzo_adulto': float(self.prezzo_adulto) if self.prezzo_adulto else 0,
            'n_tours': len(self.tours),
            'n_esperienze': len(self.esperienze),
            'attivo': self.attivo,
        }
