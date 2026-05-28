import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from recebi.ext.db import db
from recebi.ext.auth import jwt
from recebi.ext.cors import cors

def create_app():
    # Root relative template and static folders
    app = Flask(
        __name__, 
        template_folder='../templates', 
        static_folder='../static'
    )
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-key-recebi')
    
    # Bind extensions
    db.init_app(app)
    jwt.init_app(app)
    
    cors.init_app(
        app, 
        origins=["http://127.0.0.1:5500", "http://localhost:5500"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )
    
    # Global error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        import traceback
        traceback.print_exc()
        print(f"Erro na aplicação: {str(error)}")
        return jsonify({"erro": "Erro interno do servidor", "detalhes": str(error)}), 500
        
    # Ensure models are registered on metadata
    from recebi import models

    # Blueprints
    from recebi.views.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from recebi.views.sindico import sindico_bp
    app.register_blueprint(sindico_bp)
    
    from recebi.views.encomenda import encomenda_bp
    app.register_blueprint(encomenda_bp)
    
    from recebi.views.morador import morador_bp
    app.register_blueprint(morador_bp)
    
    from recebi.views.porteiro import porteiro_bp
    app.register_blueprint(porteiro_bp)
    
    from recebi.views.site import site_bp
    app.register_blueprint(site_bp)
    
    @app.route('/api/ping')
    def ping():
        return {"status": "sucesso", "mensagem": "O backend do Recebi está no ar!"}
        
    return app
