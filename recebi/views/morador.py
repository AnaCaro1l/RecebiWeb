from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from recebi.models.encomenda import Encomenda
from recebi.models.usuario import Usuario
from recebi.models.historico import Historico as LogAuditoria
from recebi.ext.db import db
import json
from datetime import datetime

morador_bp = Blueprint('morador', __name__)

def registrar_historico(id_usuario, acao, tipo, registro_id, detalhes=None):
    log = LogAuditoria(
        acao=acao,
        tabela_afetada='encomendas',
        registro_id=registro_id,
        estado_posterior=json.dumps(detalhes) if detalhes else None,
        usuario_responsavel_id=id_usuario
    )
    db.session.add(log)
    db.session.commit()

@morador_bp.route('/api/morador/confirmar-recebimento/<int:id_encomenda>', methods=['PUT'])
@jwt_required()
def confirmar_recebimento(id_encomenda):
    claims = get_jwt()
    if claims.get("perfil") != "Morador":
        return jsonify({"erro": "Acesso negado. Apenas moradores podem confirmar recebimento."}), 403

    morador_id = int(get_jwt_identity())

    try:
        morador_atual = db.session.get(Usuario, morador_id)
        if not morador_atual or not morador_atual.is_active:
             return jsonify({"erro": "Usuário não encontrado ou inativo."}), 403

        encomenda = db.session.get(Encomenda, id_encomenda)
        if not encomenda:
            return jsonify({"message": "Encomenda não encontrada."}), 404

        if encomenda.morador_id != morador_id:
            return jsonify({"erro": "Você não tem permissão para confirmar esta encomenda."}), 403

        if encomenda.status == "Retirada":
            return jsonify({"message": "Esta encomenda já foi retirada."}), 400

        encomenda.status = "Retirada"
        encomenda.data_retirada = datetime.utcnow()
        encomenda.retirado_por = "Próprio morador"
        
        db.session.commit()

        detalhes = {
            "EncomendaId": encomenda.id, 
            "Descricao": encomenda.descricao, 
            "StatusAnterior": "Pendente"
        }

        registrar_historico(
            id_usuario=morador_id,
            acao=f"Morador confirmou recebimento: {encomenda.descricao}",
            tipo="Confirmação de retirada",
            registro_id=encomenda.id,
            detalhes=detalhes
        )

        return jsonify({"message": "Encomenda confirmada como recebida.", "id": encomenda.id}), 200

    except Exception as ex:
        db.session.rollback()
        print(f"Erro em ConfirmarRecebimento: {str(ex)}")
        return jsonify({"message": "Erro ao confirmar recebimento.", "error": str(ex)}), 500

@morador_bp.route('/api/morador/encomendas', methods=['GET'])
@jwt_required()
def consultar_minhas_encomendas():
    claims = get_jwt()
    if claims.get("perfil") != "Morador":
        return jsonify({"erro": "Acesso negado. Apenas moradores."}), 403

    morador_id = int(get_jwt_identity())
    
    # Captura os parâmetros enviados pelo JavaScript
    pagina = request.args.get('page', 1, type=int)
    status_query = request.args.get('status', 'Ambos').strip()
    data_query = request.args.get('data', '').strip()

    try:
        morador_atual = db.session.get(Usuario, morador_id)
        if not morador_atual or not morador_atual.is_active:
             return jsonify({"erro": "Usuário não encontrado ou inativo."}), 403

        query = Encomenda.query.filter_by(morador_id=morador_id)

        # Filtro por Status (Pendente / Retirada)
        if status_query and status_query.lower() != "ambos":
             query = query.filter(Encomenda.status.ilike(status_query))

        if data_query:
            try:
                data_objeto = datetime.strptime(data_query, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Encomenda.data_registro) == data_objeto)
            except ValueError:
                pass

        # Ordenação por encomendas mais recentes
        query = query.order_by(Encomenda.data_registro.desc())

        # Limita de forma nativa a exibição em no máximo 10 registros por página
        paginacao = query.paginate(page=pagina, per_page=10, error_out=False)

        resultado_formatado = []
        for e in paginacao.items:
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
                "Apartamento": morador_atual.apartamento,
                "Morador": morador_atual.nome,
                "Descricao": e.descricao,
                "CodigoRastreio": e.codigo_rastreio,
                "Status": e.status,
                "DataEntrada": e.data_registro.isoformat() if e.data_registro else None,
                "DataRetirada": e.data_retirada.isoformat() if e.data_retirada else None,
                "Porteiro": nome_porteiro
            })

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
        print(f"Erro em ConsultarMinhasEncomendas: {str(ex)}")
        return jsonify({"message": "Erro ao buscar suas encomendas.", "error": str(ex)}), 500

@morador_bp.route('/api/morador/encomenda/<int:id_encomenda>', methods=['GET'])
@jwt_required()
def buscar_minha_encomenda_por_id(id_encomenda):
    claims = get_jwt()
    if claims.get("perfil") != "Morador":
        return jsonify({"erro": "Acesso negado."}), 403

    morador_id = int(get_jwt_identity())

    try:
        e = db.session.get(Encomenda, id_encomenda)
        if not e:
            return jsonify({"message": "Encomenda não encontrada."}), 404

        if e.morador_id != morador_id:
            return jsonify({"erro": "Você não tem permissão para ver esta encomenda."}), 403

        morador_atual = db.session.get(Usuario, morador_id)

        log_registro = LogAuditoria.query.filter_by(
            registro_id=e.id, 
            tabela_afetada='encomendas',
            acao='Registro de Encomenda'
        ).first()
        
        nome_porteiro = "N/A"
        if log_registro:
            porteiro = db.session.get(Usuario, log_registro.usuario_responsavel_id)
            nome_porteiro = porteiro.nome if porteiro else "N/A"

        return jsonify({
            "IdEncomenda": e.id,
            "Descricao": e.descricao,
            "CodigoRastreio": e.codigo_rastreio,
            "Status": e.status,
            "DataEntrada": e.data_registro.isoformat() if e.data_registro else None,
            "DataRetirada": e.data_retirada.isoformat() if e.data_retirada else None,
            "Morador": morador_atual.nome,
            "Apartamento": morador_atual.apartamento,
            "Porteiro": nome_porteiro
        }), 200

    except Exception as ex:
        print(f"Erro em BuscarMinhaEncomendaPorId: {str(ex)}")
        return jsonify({"message": "Erro ao buscar detalhes.", "error": str(ex)}), 500
