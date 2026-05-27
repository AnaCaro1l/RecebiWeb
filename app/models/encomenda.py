from app import db
from datetime import datetime

class Encomenda(db.Model):
    __tablename__ = 'encomendas'
    
    id_encomenda = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    apartamento = db.Column(db.String(50), nullable=False)
    
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    descricao = db.Column(db.String(255), nullable=False)
    
    codigo_rastreio = db.Column(db.String(100), nullable=True)
    
    status = db.Column(db.String(50), default='Pendente')
    
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    data_retirada = db.Column(db.DateTime, nullable=True)

    # --- Propriedades de Navegação (Relações) ---
    usuario = db.relationship('Usuario', backref='encomendas_recebidas', lazy=True)
    
    historicos = db.relationship('Historico', backref='encomenda_vinculada', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Encomenda {self.descricao} - Apt {self.apartamento}>"