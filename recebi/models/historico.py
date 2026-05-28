from recebi.ext.db import db
from datetime import datetime

class Historico(db.Model):
    __tablename__ = 'historicos'
    
    id = db.Column('id_historico', db.Integer, primary_key=True, autoincrement=True)
    id_encomenda = db.Column('id_encomenda', db.Integer, db.ForeignKey('encomendas.id_encomenda', ondelete='SET NULL'), nullable=True)
    acao = db.Column('acao', db.String(255), nullable=False)
    tabela_afetada = db.Column('tabela_afetada', db.String(50), nullable=False)
    registro_id = db.Column('registro_id', db.Integer, nullable=False)
    estado_posterior = db.Column('estado_posterior', db.Text, nullable=True)
    usuario_responsavel_id = db.Column('responsavel', db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    data_acao = db.Column('data_acao', db.DateTime, default=datetime.utcnow, nullable=False)

    usuario_responsavel = db.relationship('Usuario', backref='historicos_gerados', lazy=True)

    def __init__(self, acao=None, tabela_afetada=None, registro_id=None, usuario_responsavel_id=None, id_encomenda=None, estado_posterior=None, data_acao=None, **kwargs):
        super().__init__(**kwargs)
        self.acao = acao
        self.tabela_afetada = tabela_afetada
        self.registro_id = registro_id
        self.usuario_responsavel_id = usuario_responsavel_id
        self.id_encomenda = id_encomenda
        self.estado_posterior = estado_posterior
        if data_acao is not None:
            self.data_acao = data_acao

    def __repr__(self):
        return f"<Historico Acao: {self.acao} - Data: {self.data_acao}>"
