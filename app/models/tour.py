from app import db
from datetime import datetime


class Tour(db.Model):
    __tablename__ = 'tours'

    CATEGORIE = ['Culturale', 'Avventura', 'Gastronomia', 'Benessere', 'Mare', 'Montagna', 'Città', 'Safari', 'Crociera']

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.Text)
    destinazione = db.Column(db.String(100), nullable=False)
    paese = db.Column(db.String(60))
    categoria = db.Column(db.String(50))
    durata_giorni = db.Column(db.Integer, nullable=False, default=1)
    prezzo_adulto = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    prezzo_bambino = db.Column(db.Numeric(10, 2), default=0)
    capacita_max = db.Column(db.Integer, default=20)
    incluso = db.Column(db.Text)  # cosa è incluso
    escluso = db.Column(db.Text)  # cosa non è incluso
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Tour {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'destinazione': self.destinazione,
            'categoria': self.categoria,
            'durata_giorni': self.durata_giorni,
            'prezzo_adulto': float(self.prezzo_adulto) if self.prezzo_adulto else 0,
            'attivo': self.attivo,
        }
