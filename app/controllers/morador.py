from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.encomenda import Encomenda
from app.models.usuario import Usuario
from app.models.historico import Historico as LogAuditoria
from app import db
import json
from datetime import datetime

morador_bp = Blueprint('morador', __name__)

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

# Equivalente ao [HttpPut("confirmar-recebimento/{idEncomenda}")]
@morador_bp.route('/api/morador/confirmar-recebimento/<int:id_encomenda>', methods=['PUT'])
@jwt_required()
def confirmar_recebimento(id_encomenda):
    claims = get_jwt()
    if claims.get("perfil") != "morador":
        return jsonify({"erro": "Acesso negado. Apenas moradores podem confirmar recebimento."}), 403

    morador_id = get_jwt_identity()

    try:
        # Verifica se o morador existe e está ativo
        morador_atual = Usuario.query.get(morador_id)
        if not morador_atual or not morador_atual.is_active:
             return jsonify({"erro": "Usuário não encontrado ou inativo."}), 403

        encomenda = Encomenda.query.get(id_encomenda)
        if not encomenda:
            return jsonify({"message": "Encomenda não encontrada."}), 404

        # Garante que o morador só confirma as SUAS encomendas
        if str(encomenda.morador_id) != str(morador_id):
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
        print(f"Erro em ConfirmarRecebimento: {str(ex)}")
        return jsonify({"message": "Erro ao confirmar recebimento.", "error": str(ex)}), 500

# Equivalente ao [HttpGet("encomendas")] (substitui o 'pendentes' antigo)
@morador_bp.route('/api/morador/encomendas', methods=['GET'])
@jwt_required()
def consultar_minhas_encomendas():
    claims = get_jwt()
    if claims.get("perfil") != "morador":
        return jsonify({"erro": "Acesso negado. Apenas moradores."}), 403

    morador_id = get_jwt_identity()
    status_query = request.args.get('status')

    try:
        morador_atual = Usuario.query.get(morador_id)
        if not morador_atual or not morador_atual.is_active:
             return jsonify({"erro": "Usuário não encontrado ou inativo."}), 403

        # Constrói a query baseada no ID do morador logado
        query = Encomenda.query.filter_by(morador_id=morador_id)

        # Aplica o filtro de status, se fornecido
        if status_query and status_query.lower() != "todas":
             query = query.filter(Encomenda.status.ilike(status_query))

        encomendas = query.order_by(Encomenda.data_registro.desc()).all()

        resultado_formatado = []
        for e in encomendas:
            log_registro = LogAuditoria.query.filter_by(
                registro_id=e.id, 
                tabela_afetada='encomendas',
                acao='Registro de Encomenda'
            ).first()
            
            nome_porteiro = "N/A"
            if log_registro:
                porteiro = Usuario.query.get(log_registro.usuario_responsavel_id)
                nome_porteiro = porteiro.nome if porteiro else "N/A"

            resultado_formatado.append({
                "IdEncomenda": e.id,
                "Apartamento": morador_atual.apartamento,
                "Morador": morador_atual.nome,
                "Descricao": e.descricao,
                "CodigoRastreio": e.codigo_rastreio,
                "Status": e.status,
                "DataEntrada": e.data_registro,
                "DataRetirada": e.data_retirada,
                "Porteiro": nome_porteiro
            })

        if not resultado_formatado:
            return jsonify({"message": "Nenhuma encomenda encontrada."}), 200

        return jsonify(resultado_formatado), 200

    except Exception as ex:
        print(f"Erro em ConsultarMinhasEncomendas: {str(ex)}")
        return jsonify({"message": "Erro ao buscar suas encomendas.", "error": str(ex)}), 500

# Equivalente ao [HttpGet("encomenda/{idEncomenda}")]
@morador_bp.route('/api/morador/encomenda/<int:id_encomenda>', methods=['GET'])
@jwt_required()
def buscar_minha_encomenda_por_id(id_encomenda):
    claims = get_jwt()
    if claims.get("perfil") != "morador":
        return jsonify({"erro": "Acesso negado."}), 403

    morador_id = get_jwt_identity()

    try:
        e = Encomenda.query.get(id_encomenda)
        if not e:
            return jsonify({"message": "Encomenda não encontrada."}), 404

        if str(e.morador_id) != str(morador_id):
            return jsonify({"erro": "Você não tem permissão para ver esta encomenda."}), 403

        morador_atual = Usuario.query.get(morador_id)

        log_registro = LogAuditoria.query.filter_by(
            registro_id=e.id, 
            tabela_afetada='encomendas',
            acao='Registro de Encomenda'
        ).first()
        
        nome_porteiro = "N/A"
        if log_registro:
            porteiro = Usuario.query.get(log_registro.usuario_responsavel_id)
            nome_porteiro = porteiro.nome if porteiro else "N/A"

        return jsonify({
            "IdEncomenda": e.id,
            "Descricao": e.descricao,
            "CodigoRastreio": e.codigo_rastreio,
            "Status": e.status,
            "DataEntrada": e.data_registro,
            "DataRetirada": e.data_retirada,
            "Morador": morador_atual.nome,
            "Apartamento": morador_atual.apartamento,
            "Porteiro": nome_porteiro
        }), 200

    except Exception as ex:
        print(f"Erro em BuscarMinhaEncomendaPorId: {str(ex)}")
        return jsonify({"message": "Erro ao buscar detalhes.", "error": str(ex)}), 500
