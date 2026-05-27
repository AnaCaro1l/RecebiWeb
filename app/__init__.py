import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

# Inicializa o banco de dados
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configura CORS com opções mais explícitas
    CORS(app, 
         origins=["http://127.0.0.1:5500", "http://localhost:5500"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"])
    
    # Configurações do Banco de Dados e JWT puxadas do .env de forma segura
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Vincula o banco de dados e o gerenciador JWT à aplicação
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Handler global para erros de banco de dados
    @app.errorhandler(Exception)
    def handle_error(error):
        print(f"Erro na aplicação: {str(error)}")
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(error)}), 500
    
    # Importa e registra os Blueprints (Controllers)
    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.controllers.sindico import sindico_bp
    app.register_blueprint(sindico_bp)
    
    from app.controllers.encomenda import encomenda_bp
    app.register_blueprint(encomenda_bp)
    
    from app.controllers.morador import morador_bp
    app.register_blueprint(morador_bp)
    
    from app.controllers.porteiro import porteiro_bp
    app.register_blueprint(porteiro_bp)
    
    # Rota de teste para ver se a API está viva
    @app.route('/api/ping')
    def ping():
        return {"status": "sucesso", "mensagem": "O backend do Recebi está no ar!"}
        
    return app