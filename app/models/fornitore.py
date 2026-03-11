from app import db
from datetime import datetime

class Fornitore(db.Model):
    __tablename__ = 'fornitori'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    tipo_servizio = db.Column(db.String(100)) # Hotel, Voli, Transfer, Tour, Esperienze, Altro
    contatto_nome = db.Column(db.String(150))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(50))
    indirizzo = db.Column(db.String(255))
    sito_web = db.Column(db.String(255))
    piva_codfisc = db.Column(db.String(50))
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Fornitore {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo_servizio': self.tipo_servizio,
            'email': self.email,
            'telefono': self.telefono,
            'attivo': self.attivo
        }
