from recebi.ext.db import db
from datetime import datetime

class Encomenda(db.Model):
    __tablename__ = 'encomendas'
    
    id = db.Column('id_encomenda', db.Integer, primary_key=True, autoincrement=True)
    apartamento = db.Column('apartamento', db.String(50), nullable=True)
    morador_id = db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    descricao = db.Column('descricao', db.String(255), nullable=False)
    codigo_rastreio = db.Column('codigo_rastreio', db.String(100), nullable=True)
    status = db.Column('status', db.String(50), default='Pendente')
    data_registro = db.Column('data_entrada', db.DateTime, default=datetime.utcnow, nullable=False)
    data_retirada = db.Column('data_retirada', db.DateTime, nullable=True)

    usuario = db.relationship('Usuario', backref='encomendas_recebidas', lazy=True)

    def __init__(self, morador_id=None, descricao=None, codigo_rastreio=None, status='Pendente', apartamento=None, data_registro=None, data_retirada=None, **kwargs):
        super().__init__(**kwargs)
        self.morador_id = morador_id
        self.descricao = descricao
        self.codigo_rastreio = codigo_rastreio
        self.status = status
        self.apartamento = apartamento
        if data_registro is not None:
            self.data_registro = data_registro
        self.data_retirada = data_retirada
    
    def __repr__(self):
        return f"<Encomenda {self.descricao} - ID {self.id}>"
