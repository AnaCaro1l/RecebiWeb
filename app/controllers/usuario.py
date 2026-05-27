from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app.models.usuario import Usuario
import datetime

# Equivalente ao [Route("api/[controller]")]
auth_bp = Blueprint('auth', __name__)

# Equivalente ao [HttpPost("login")]
@auth_bp.route('/api/usuario/login', methods=['POST'])
def login():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"message": "Dados de login inválidos."}), 400

    email = dados.get('email')
    senha = dados.get('senha')

    # Busca o usuário pelo email
    usuario = Usuario.query.filter_by(email=email).first()

    # Validação segura (equivalente ao u.Senha == login.Senha, mas com hash)
    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({"message": "E-mail ou senha incorretos."}), 401

    # Equivalente ao if (user.Status != "Ativo")
    if not usuario.is_active:
        return jsonify({"message": "Este usuário está inativo."}), 401

    # Equivalente ao GerarTokenJwt()
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

# Equivalente ao [HttpPost("logout/{id}")]
@auth_bp.route('/api/usuario/logout/<int:id>', methods=['POST'])
def logout(id):
    usuario = Usuario.query.get(id)
    
    if not usuario:
        return jsonify({"message": "Usuário não encontrado."}), 404

    # Num sistema JWT (Stateless), o logout real é feito no Frontend apagando o Token do navegador.
    # Esta rota foi mantida para replicar o comportamento exato do teu código C#.
    return jsonify({"message": f"{usuario.nome} saiu do sistema com sucesso."}), 200
