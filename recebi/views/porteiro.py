from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from recebi.models.encomenda import Encomenda
from recebi.models.usuario import Usuario
from recebi.models.historico import Historico as LogAuditoria
from recebi.ext.db import db
import json
from datetime import datetime
from sqlalchemy import or_

porteiro_bp = Blueprint('porteiro', __name__)

def registrar_historico(id_usuario, acao, tipo, registro_id, detalhes=None):
    log = LogAuditoria(
        acao=tipo,  
        tabela_afetada='encomendas',
        registro_id=registro_id,
        estado_posterior=json.dumps(detalhes) if detalhes else None,
        usuario_responsavel_id=id_usuario
    )
    db.session.add(log)
    db.session.commit()

@porteiro_bp.route('/api/porteiro/registrar-encomenda', methods=['POST'])
@jwt_required()
def registrar_encomenda():
    claims = get_jwt()
    if claims.get("perfil") != "Porteiro":
        return jsonify({"erro": "Acesso negado. Apenas porteiros."}), 403

    porteiro_id = int(get_jwt_identity())
    dados = request.get_json()

    if not dados:
        return jsonify({"message": "Os dados da encomenda são inválidos."}), 400

    morador_id = dados.get('morador_id')
    descricao = dados.get('descricao')
    codigo_rastreio = dados.get('codigo_rastreio')

    if not morador_id or not descricao:
         return jsonify({"message": "Morador e descrição são obrigatórios."}), 400

    try:
        morador_id = int(morador_id)
    except (ValueError, TypeError):
        return jsonify({"message": "ID do morador inválido."}), 400

    morador = Usuario.query.filter(Usuario.id == morador_id, Usuario.perfil.in_(['Morador', 'morador'])).first()
    if not morador:
        return jsonify({"message": "Morador não encontrado."}), 404
    if not morador.is_active:
        return jsonify({"message": f"O morador {morador.nome} está inativo."}), 400

    try:
        nova_encomenda = Encomenda(
            descricao=descricao,
            codigo_rastreio=codigo_rastreio,
            status="Pendente",
            data_registro=datetime.utcnow(),
            morador_id=morador.id,
            apartamento=morador.apartamento
        )

        db.session.add(nova_encomenda)
        db.session.flush()

        detalhes = {
            "EncomendaId": nova_encomenda.id,
            "MoradorId": morador.id,
            "MoradorNome": morador.nome,
            "Apartamento": morador.apartamento,
            "Descricao": descricao,
            "CodigoRastreio": codigo_rastreio
        }

        registrar_historico(
            id_usuario=porteiro_id,
            acao=f"Porteiro registrou: {descricao} p/ Apt {morador.apartamento}",
            tipo="Registro de Encomenda",
            registro_id=nova_encomenda.id,
            detalhes=detalhes
        )

        db.session.commit()

        return jsonify({
            "message": "Encomenda registrada com sucesso!", 
            "encomenda_id": nova_encomenda.id
        }), 201

    except Exception as ex:
        db.session.rollback()
        print(f"Erro em RegistrarEncomenda: {str(ex)}")
        return jsonify({"message": "Erro ao registrar encomenda.", "error": str(ex)}), 500

@porteiro_bp.route('/api/porteiro/encomendas', methods=['GET'])
@jwt_required()
def verificar_encomendas():
    claims = get_jwt()
    if claims.get("perfil") != "Porteiro":
        return jsonify({"erro": "Acesso negado. Requer perfil de Porteiro."}), 403

    pagina = request.args.get('page', 1, type=int)
    por_pagina = request.args.get('per_page', 10, type=int)
    status_query = request.args.get('status', '').strip()
    data_query = request.args.get('data', '').strip()
    termo_busca = request.args.get('query', '').strip()

    try:
        query = Encomenda.query.join(Usuario, Encomenda.morador_id == Usuario.id)

        if status_query:
            query = query.filter(Encomenda.status == status_query)
            
        if data_query:
            try:
                data_objeto = datetime.strptime(data_query, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Encomenda.data_registro) == data_objeto)
            except ValueError:
                pass

        if termo_busca:
            query = query.filter(
                (Encomenda.apartamento.ilike(f"%{termo_busca}%")) | 
                (Usuario.nome.ilike(f"%{termo_busca}%"))
            )

        query = query.order_by(Encomenda.data_registro.desc())

        paginacao = query.paginate(page=pagina, per_page=por_pagina, error_out=False)

        resultado_formatado = []
        for e in paginacao.items:
            morador = db.session.get(Usuario, e.morador_id)
            
            log_registro = LogAuditoria.query.filter_by(
                registro_id=e.id, 
                tabela_afetada='encomendas',
                acao='Registro de Encomenda'
            ).first()
            
            nome_porteiro = "N/A"
            if log_registro:
                porteiro = db.session.get(Usuario, log_registro.usuario_responsavel_id)
                nome_porteiro = porteiro.nome if porteiro else "N/A"

            resultado_formatado.append({
                "IdEncomenda": e.id,
                "Descricao": e.descricao,
                "CodigoRastreio": e.codigo_rastreio,
                "Status": e.status,
                "Apartamento": e.apartamento if e.apartamento else (morador.apartamento if morador else "N/A"),
                "Morador": morador.nome if morador else "N/A",
                "DataEntrada": e.data_registro.isoformat() if e.data_registro else None,
                "DataRetirada": e.data_retirada.isoformat() if e.data_retirada else None,
                "Porteiro": nome_porteiro
            })

        if not resultado_formatado:
            return jsonify({"message": "Nenhuma encomenda encontrada."}), 200

        return jsonify({
            "encomendas": resultado_formatado,
            "paginacao": {
                "pagina_atual": paginacao.page,
                "total_paginas": paginacao.pages,
                "tem_anterior": paginacao.has_prev,
                "tem_proximo": paginacao.has_next
            }
        }), 200

    except Exception as ex:
        print(f"Erro em VerificarEncomendas: {str(ex)}")
        return jsonify({"message": "Erro ao buscar encomendas.", "error": str(ex)}), 500

@porteiro_bp.route('/api/porteiro/buscar-moradores', methods=['GET'])
@jwt_required()
def buscar_moradores():
    claims = get_jwt()
    if claims.get("perfil") != "Porteiro":
        return jsonify({"erro": "Acesso negado."}), 403

    termo_busca = request.args.get('query', '')

    if not termo_busca or len(termo_busca) < 2:
        return jsonify([]), 200

    try:
        moradores = Usuario.query.filter(
            Usuario.perfil.in_(['Morador', 'morador']),
            Usuario.is_active == True,
            Usuario.nome.ilike(f"%{termo_busca}%")
        ).order_by(Usuario.nome).limit(10).all()

        resultado = [{
            "IdUsuario": m.id, 
            "Nome": m.nome, 
            "Apartamento": m.apartamento
        } for m in moradores]

        return jsonify(resultado), 200

    except Exception as ex:
        print(f"Erro em BuscarMoradores: {str(ex)}")
        return jsonify({"message": "Erro ao buscar moradores.", "error": str(ex)}), 500
