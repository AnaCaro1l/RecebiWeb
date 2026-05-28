from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from flask_cors import cross_origin
from recebi.models import Usuario
from recebi.ext.db import db
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/usuario/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    dados = request.get_json()
    
    if not dados:
        return jsonify({"message": "Dados de login inválidos."}), 400

    email = dados.get('email')
    senha = dados.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"message": "E-mail ou senha incorretos."}), 401

    if not usuario.is_active:
        return jsonify({"message": "Este usuário está inativo."}), 401

    expires = datetime.timedelta(hours=8)
    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil,
            "status": "Ativo" if usuario.is_active else "Inativo"
        },
        expires_delta=expires
    )

    return jsonify({
        "message": "Login realizado com sucesso.",
        "token": token,
        "usuario": {
            "IdUsuario": usuario.id,
            "Nome": usuario.nome,
            "Email": usuario.email,
            "TipoUsuario": usuario.perfil,
            "Apartamento": usuario.apartamento,
            "Status": "Ativo" if usuario.is_active else "Inativo"
        }
    }), 200

@auth_bp.route('/api/usuario/logout/<int:id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def logout(id):
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    usuario = db.session.get(Usuario, id)
    if not usuario:
        return jsonify({"message": "Usuário não encontrado."}), 404

    return jsonify({"message": f"{usuario.nome} saiu do sistema com sucesso."}), 200
