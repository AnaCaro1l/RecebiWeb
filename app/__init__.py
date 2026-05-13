import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Puxa a URI do banco de dados de forma segura
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Puxa a chave secreta dos tokens JWT (que vamos usar depois na autenticação)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    db.init_app(app)
    
    @app.route('/api/ping')
    def ping():
        return {"status": "sucesso", "mensagem": "O backend do Recebi está no ar!"}
        
    return app