from app import db
from datetime import datetime


class Cliente(db.Model):
    __tablename__ = 'clienti'

    DOCUMENTI = ['Carta d\'identità', 'Passaporto', 'Patente']

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    cognome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(30))
    data_nascita = db.Column(db.Date, nullable=True)
    nazionalita = db.Column(db.String(60))
    tipo_documento = db.Column(db.String(30))
    numero_documento = db.Column(db.String(50))
    data_rilascio_documento = db.Column(db.Date, nullable=True)
    data_scadenza_documento = db.Column(db.Date, nullable=True)
    indirizzo = db.Column(db.String(255))
    citta = db.Column(db.String(100))
    cap = db.Column(db.String(10))
    paese = db.Column(db.String(60), default='Italia')
    lingua_preferita = db.Column(db.String(60))
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def nome_completo(self):
        return f'{self.nome} {self.cognome}'

    def __repr__(self):
        return f'<Cliente {self.nome_completo()}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cognome': self.cognome,
            'nome_completo': self.nome_completo(),
            'email': self.email,
            'telefono': self.telefono,
            'citta': self.citta,
            'attivo': self.attivo,
        }
