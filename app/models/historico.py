from app import db
from datetime import datetime

class Historico(db.Model):
    __tablename__ = 'historicos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    id_encomenda = db.Column(db.Integer, db.ForeignKey('encomendas.id_encomenda'), nullable=False)
    
    acao = db.Column(db.String(255), nullable=False)
    
    data_acao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    responsavel = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    usuario_responsavel = db.relationship('Usuario', backref='historicos_gerados', lazy=True)

    def __repr__(self):
        return f"<Historico Acao: {self.acao} - Data: {self.data_acao}>"