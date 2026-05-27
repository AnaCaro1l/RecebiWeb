from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column('id_usuario', db.Integer, primary_key=True, autoincrement=True)
    
    nome = db.Column('nome', db.String(100), nullable=False)
    
    email = db.Column('email', db.String(100), unique=True, nullable=False)
    
    senha = db.Column('senha', db.String(255), nullable=False)
    
    telefone = db.Column('telefone', db.String(15), nullable=True)
    
    apartamento = db.Column('apart', db.String(10), nullable=True)
    
    perfil = db.Column('tipo_usuario', db.Enum('Morador', 'Porteiro', 'Sindico'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Usuario {self.nome} - {self.perfil}>"