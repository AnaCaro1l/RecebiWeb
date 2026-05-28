from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from recebi.models.usuario import Usuario
from recebi.models.historico import Historico as LogAuditoria
from recebi.models.encomenda import Encomenda
from recebi.ext.db import db
import json
from datetime import datetime

sindico_bp = Blueprint('sindico', __name__)

def registrar_historico(id_usuario, acao, tipo, registro_id=None, detalhes=None):
    log = LogAuditoria(
        acao=acao,
        tabela_afetada='usuarios' if tipo in ["Criação de usuário", "Atualização de usuário"] else 'geral',
        registro_id=registro_id or 0,
        estado_posterior=json.dumps(detalhes) if detalhes else None,
        usuario_responsavel_id=id_usuario,
        data_acao=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

# --- CRUD DE USUÁRIOS ---

@sindico_bp.route('/api/sindico/criar', methods=['POST'])
@jwt_required()
def criar_usuario():
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado. Apenas síndicos."}), 403

    dados = request.get_json()
    if not dados:
        return jsonify({"message": "Os dados do usuário são obrigatórios."}), 400

    sindico_id = int(get_jwt_identity())

    try:
        if Usuario.query.filter_by(email=dados.get('email')).first():
             return jsonify({"message": "Erro: E-mail já cadastrado."}), 400

        senha = dados.get('senha')
        if not senha:
             return jsonify({"message": "A senha é obrigatória para novos usuários."}), 400

        novo_usuario = Usuario(
            nome=dados.get('nome'),
            email=dados.get('email'),
            senha=generate_password_hash(senha),
            perfil=dados.get('tipoUsuario', 'morador').capitalize(),
            apartamento=dados.get('apartamento'),
            telefone=dados.get('telefone'),
            is_active=True
        )

        db.session.add(novo_usuario)
        db.session.flush()

        detalhes = {
            "UsuarioCriadoId": novo_usuario.id, 
            "Nome": novo_usuario.nome, 
            "Email": novo_usuario.email, 
            "TipoUsuario": novo_usuario.perfil, 
            "Apartamento": novo_usuario.apartamento,
            "Telefone": dados.get('telefone')
        }

        registrar_historico(
            id_usuario=sindico_id, 
            acao=f"Síndico criou: {novo_usuario.nome} ({novo_usuario.perfil})",
            tipo="Criação de usuário", 
            registro_id=novo_usuario.id,
            detalhes=detalhes
        )

        db.session.commit()

        return jsonify({
            "message": "Usuário criado com sucesso!", 
            "usuario": {
                "IdUsuario": novo_usuario.id, 
                "Nome": novo_usuario.nome, 
                "Email": novo_usuario.email, 
                "TipoUsuario": novo_usuario.perfil, 
                "Apartamento": novo_usuario.apartamento, 
                "Status": "Ativo"
            }
        }), 201

    except Exception as ex:
        db.session.rollback()
        print(f"Erro em CriarUsuario: {str(ex)}")
        return jsonify({"message": "Erro ao criar usuário.", "error": str(ex)}), 500

@sindico_bp.route('/api/sindico/atualizar/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_usuario(id):
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado."}), 403

    dados = request.get_json()
    if not dados or id <= 0:
        return jsonify({"message": "Dados inválidos."}), 400

    usuario_para_atualizar = db.session.get(Usuario, id)
    if not usuario_para_atualizar:
        return jsonify({"message": "Usuário não encontrado."}), 404

    sindico_id = int(get_jwt_identity())

    status_novo = dados.get('status')
    if str(usuario_para_atualizar.id) == str(sindico_id) and status_novo == "Inativo":
        return jsonify({"message": "Você não pode inativar a si mesmo."}), 400

    detalhes_alteracao = {}

    try:
        if dados.get('nome') and usuario_para_atualizar.nome != dados['nome']:
            detalhes_alteracao["Nome"] = {"Old": usuario_para_atualizar.nome, "New": dados['nome']}
            usuario_para_atualizar.nome = dados['nome']

        if dados.get('email') and usuario_para_atualizar.email != dados['email']:
            detalhes_alteracao["Email"] = {"Old": usuario_para_atualizar.email, "New": dados['email']}
            usuario_para_atualizar.email = dados['email']

        if dados.get('senha'):
            if not check_password_hash(usuario_para_atualizar.senha, dados['senha']):
                detalhes_alteracao["Senha"] = {"Info": "Senha alterada"}
                usuario_para_atualizar.senha = generate_password_hash(dados['senha'])

        if dados.get('apartamento') is not None and usuario_para_atualizar.apartamento != dados['apartamento']:
            detalhes_alteracao["Apartamento"] = {"Old": usuario_para_atualizar.apartamento, "New": dados['apartamento']}
            usuario_para_atualizar.apartamento = dados['apartamento']

        if status_novo in ["Ativo", "Inativo"]:
            novo_is_active = (status_novo == "Ativo")
            if usuario_para_atualizar.is_active != novo_is_active:
                detalhes_alteracao["Status"] = {
                    "Old": "Ativo" if usuario_para_atualizar.is_active else "Inativo", 
                    "New": status_novo
                }
                usuario_para_atualizar.is_active = novo_is_active

        if detalhes_alteracao:
            db.session.commit()
            registrar_historico(
                id_usuario=sindico_id, 
                acao=f"Síndico atualizou o usuário {usuario_para_atualizar.nome}", 
                tipo="Atualização de usuário", 
                registro_id=usuario_para_atualizar.id,
                detalhes=detalhes_alteracao
            )
            return jsonify({"message": "Usuário atualizado com sucesso!", "alteracoes": detalhes_alteracao}), 200
        else:
            return jsonify({"message": "Nenhuma alteração detectada."}), 200

    except Exception as ex:
        db.session.rollback()
        print(f"Erro em grid atualiza: {str(ex)}")
        return jsonify({"message": "Erro inesperado ao atualizar usuário.", "error": str(ex)}), 500

@sindico_bp.route('/api/sindico/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado."}), 403

    status_query = request.args.get('status')

    try:
        query = Usuario.query

        if status_query and status_query.lower() != "todos":
            is_active_filter = (status_query.lower() == "ativo")
            query = query.filter_by(is_active=is_active_filter)

        usuarios = query.order_by(Usuario.nome).all()
        resultado = []

        for u in usuarios:
            resultado.append({
                "IdUsuario": u.id, 
                "Nome": u.nome, 
                "Email": u.email, 
                "Apartamento": u.apartamento, 
                "TipoUsuario": u.perfil, 
                "Status": "Ativo" if u.is_active else "Inativo"
            })

        if not resultado:
             return jsonify({"message": "Nenhum usuário encontrado."}), 200

        return jsonify(resultado), 200

    except Exception as ex:
        return jsonify({"message": "Erro ao listar usuários.", "error": str(ex)}), 500

@sindico_bp.route('/api/sindico/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def buscar_usuario_por_id(id):
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado."}), 403

    try:
        u = db.session.get(Usuario, id)
        if not u:
            return jsonify({"message": "Usuário não encontrado."}), 404

        return jsonify({
            "IdUsuario": u.id, 
            "Nome": u.nome, 
            "Email": u.email, 
            "Apartamento": u.apartamento, 
            "TipoUsuario": u.perfil, 
            "Status": "Ativo" if u.is_active else "Inativo"
        }), 200

    except Exception as ex:
        return jsonify({"message": "Erro ao buscar usuário.", "error": str(ex)}), 500

# --- AUDITORIA E LOGS ---

@sindico_bp.route('/api/sindico/logs', methods=['GET'])
@jwt_required()
def consultar_logs():
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado."}), 403

    try:
        historicos = LogAuditoria.query.order_by(LogAuditoria.data_acao.desc()).all()
        resultado = []

        for h in historicos:
            usuario = db.session.get(Usuario, h.usuario_responsavel_id)
            
            encomenda_descricao = "Sem referência"
            encomenda_apartamento = "Sem apartamento"
            
            if h.tabela_afetada == 'encomendas':
                encomenda = db.session.get(Encomenda, h.registro_id)
                if encomenda:
                    encomenda_descricao = encomenda.descricao
                    morador = db.session.get(Usuario, encomenda.morador_id)
                    encomenda_apartamento = morador.apartamento if morador else "Sem apartamento"

            resultado.append({
                "IdHistorico": h.id,
                "Usuario": usuario.nome if usuario else "Usuário removido",
                "Acao": h.acao,
                "Tipo": h.acao, 
                "DataHora": h.data_acao.isoformat(),
                "EncomendaDescricao": encomenda_descricao,
                "EncomendaApartamento": encomenda_apartamento,
                "Detalhes": json.loads(h.estado_posterior) if h.estado_posterior else None
            })

        if not resultado:
            return jsonify({"message": "Nenhum histórico encontrado."}), 200

        return jsonify(resultado), 200

    except Exception as ex:
        print(f"Erro em ConsultarLogs: {str(ex)}")
        return jsonify({"message": "Erro ao consultar logs.", "error": str(ex)}), 500

@sindico_bp.route('/api/sindico/logs/<int:id>', methods=['GET'])
@jwt_required()
def buscar_log_por_id(id):
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado."}), 403

    try:
        h = db.session.get(LogAuditoria, id)
        if not h:
            return jsonify({"message": "Registro de histórico não encontrado."}), 404

        usuario = db.session.get(Usuario, h.usuario_responsavel_id)
        
        encomenda_descricao = "Sem referência"
        encomenda_apartamento = "Sem apartamento"
        
        if h.tabela_afetada == 'encomendas':
            encomenda = db.session.get(Encomenda, h.registro_id)
            if encomenda:
                encomenda_descricao = encomenda.descricao
                morador = db.session.get(Usuario, encomenda.morador_id)
                encomenda_apartamento = morador.apartamento if morador else "Sem apartamento"

        return jsonify({
            "IdHistorico": h.id,
            "IdUsuario": h.usuario_responsavel_id,
            "Usuario": usuario.nome if usuario else "Usuário removido",
            "Acao": h.acao,
            "Tipo": h.acao,
            "DataHora": h.data_acao.isoformat(),
            "IdEncomenda": h.registro_id if h.tabela_afetada == 'encomendas' else None,
            "EncomendaDescricao": encomenda_descricao,
            "EncomendaApartamento": encomenda_apartamento,
            "Detalhes": json.loads(h.estado_posterior) if h.estado_posterior else None
        }), 200

    except Exception as ex:
        return jsonify({"message": "Erro ao buscar registro.", "error": str(ex)}), 500
