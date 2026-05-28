from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from recebi.models.encomenda import Encomenda
from recebi.models.usuario import Usuario
from recebi.models.historico import Historico as LogAuditoria
from recebi.ext.db import db
import json

encomenda_bp = Blueprint('encomenda', __name__)

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

@encomenda_bp.route('/api/encomenda/todas', methods=['GET'])
@jwt_required()
def listar_todas():
    claims = get_jwt()
    if claims.get("perfil") not in ["Porteiro", "Sindico"]:
        return jsonify({"erro": "Acesso negado. Requer perfil de Porteiro ou Síndico."}), 403

    try:
        encomendas = Encomenda.query.order_by(Encomenda.data_registro.desc()).all()
        
        resultado_formatado = []
        for e in encomendas:
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
                "Apartamento": morador.apartamento if morador else "N/A",
                "Morador": morador.nome if morador else "N/A",
                "Descricao": e.descricao,
                "CodigoRastreio": e.codigo_rastreio,
                "Status": e.status,
                "DataEntrada": e.data_registro.isoformat() if e.data_registro else None,
                "DataRetirada": e.data_retirada.isoformat() if e.data_retirada else None,
                "Porteiro": nome_porteiro
            })

        if not resultado_formatado:
            return jsonify({"message": "Nenhuma encomenda registrada."}), 200

        return jsonify(resultado_formatado), 200

    except Exception as ex:
        print(f"Erro em ListarTodas Encomendas: {str(ex)}")
        return jsonify({"message": "Erro ao listar encomendas.", "error": str(ex)}), 500

@encomenda_bp.route('/api/encomenda/<int:id>', methods=['GET'])
@jwt_required()
def buscar_por_id(id):
    claims = get_jwt()
    if claims.get("perfil") not in ["Porteiro", "Sindico"]:
        return jsonify({"erro": "Acesso negado. Requer perfil de Porteiro ou Síndico."}), 403

    try:
        e = db.session.get(Encomenda, id)
        if not e:
            return jsonify({"message": "Encomenda não encontrada."}), 404

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

        return jsonify({
            "IdEncomenda": e.id,
            "Descricao": e.descricao,
            "CodigoRastreio": e.codigo_rastreio,
            "Status": e.status,
            "DataEntrada": e.data_registro.isoformat() if e.data_registro else None,
            "DataRetirada": e.data_retirada.isoformat() if e.data_retirada else None,
            "Morador": morador.nome if morador else "N/A",
            "Apartamento": morador.apartamento if morador else "N/A",
            "Porteiro": nome_porteiro
        }), 200

    except Exception as ex:
        print(f"Erro em BuscarPorId Encomenda: {str(ex)}")
        return jsonify({"message": "Erro ao buscar encomenda.", "error": str(ex)}), 500

@encomenda_bp.route('/api/encomenda/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_encomenda(id):
    claims = get_jwt()
    if claims.get("perfil") != "Sindico":
        return jsonify({"erro": "Acesso negado. Apenas síndicos podem deletar."}), 403

    try:
        encomenda = db.session.get(Encomenda, id)
        if not encomenda:
            return jsonify({"message": "Encomenda não encontrada."}), 404

        id_usuario_logado = int(get_jwt_identity())

        detalhes = {
            "EncomendaRemovidaId": encomenda.id,
            "Descricao": encomenda.descricao,
            "MoradorId": encomenda.morador_id
        }

        descricao_encomenda = encomenda.descricao

        db.session.delete(encomenda)
        db.session.commit()

        registrar_historico(
            id_usuario=id_usuario_logado,
            acao=f"Encomenda '{descricao_encomenda}' (ID: {id}) foi removida.",
            tipo="Remoção de encomenda",
            registro_id=id,
            detalhes=detalhes
        )

        return jsonify({"message": "Encomenda deletada com sucesso."}), 200

    except Exception as ex:
        db.session.rollback()
        print(f"Erro em DeletarEncomenda: {str(ex)}")
        return jsonify({"message": "Erro ao deletar encomenda (verifique dependências no histórico).", "error": str(ex)}), 400
