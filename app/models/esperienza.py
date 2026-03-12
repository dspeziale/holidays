from app import db
from datetime import datetime


class Esperienza(db.Model):
    __tablename__ = 'esperienze'

    CATEGORIE = ['Arte & Cultura', 'Food & Wine', 'Natura', 'Sport', 'Benessere', 'Shopping', 'Nightlife', 'Family']

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.Text)
    destinazione = db.Column(db.String(100), nullable=False)
    paese = db.Column(db.String(60))
    categoria = db.Column(db.String(50))
    durata_ore = db.Column(db.Numeric(4, 1), default=2)
    prezzo_adulto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    prezzo_bambino = db.Column(db.Numeric(10, 2), default=0)
    fornitore = db.Column(db.String(150))
    url_getyourguide = db.Column(db.String(500))  # link GYG per prenotazione
    gyg_activity_id = db.Column(db.String(50))     # ID attività GetYourGuide
    lingua = db.Column(db.String(30), default='Italiano')
    punto_incontro = db.Column(db.String(255))
    note = db.Column(db.Text)
    is_demo = db.Column(db.Boolean, default=False, nullable=False)  # Flag per dati demo
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Esperienza {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'destinazione': self.destinazione,
            'categoria': self.categoria,
            'durata_ore': float(self.durata_ore) if self.durata_ore else 0,
            'prezzo_adulto': float(self.prezzo_adulto) if self.prezzo_adulto else 0,
            'fornitore': self.fornitore,
            'attivo': self.attivo,
        }
