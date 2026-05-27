from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.encomenda import Encomenda
from app.models.usuario import Usuario
from app.models.historico import Historico as LogAuditoria
from app import db
import json
from datetime import datetime

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

# Equivalente ao [HttpPost("RegistrarEncomenda")]
@porteiro_bp.route('/api/porteiro/registrar-encomenda', methods=['POST'])
@jwt_required()
def registrar_encomenda():
    claims = get_jwt()
    if claims.get("perfil") != "porteiro":
        return jsonify({"erro": "Acesso negado. Apenas porteiros."}), 403

    porteiro_id = get_jwt_identity()
    dados = request.get_json()

    if not dados:
        return jsonify({"message": "Os dados da encomenda são inválidos."}), 400

    morador_id = dados.get('morador_id')
    descricao = dados.get('descricao')
    codigo_rastreio = dados.get('codigo_rastreio')

    if not morador_id or not descricao:
         return jsonify({"message": "Morador e descrição são obrigatórios."}), 400

    morador = Usuario.query.filter_by(id=morador_id, perfil='morador').first()
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
            morador_id=morador.id
        )

        db.session.add(nova_encomenda)
        db.session.flush() # Salva temporariamente para pegar o ID gerado

        detalhes = {
            "EncomendaId": nova_encomenda.id,
            "MoradorId": morador.id,
            "MoradorNome": morador.nome,
            "Apartamento": morador.apartamento,
            "Descricao": descricao,
            "CodigoRastreio": codigo_rastreio
        }

        # Registra a ação no log global exigido nos Requisitos Não Funcionais
        registrar_historico(
            id_usuario=porteiro_id,
            acao=f"Porteiro registrou: {descricao} p/ Apt {morador.apartamento}",
            tipo="Registro de Encomenda",
            registro_id=nova_encomenda.id,
            detalhes=detalhes
        )

        db.session.commit() # Efetiva a gravação da encomenda e do log no MySQL

        return jsonify({
            "message": "Encomenda registrada com sucesso!", 
            "encomenda_id": nova_encomenda.id
        }), 201

    except Exception as ex:
        db.session.rollback() # Em caso de erro, desfaz a transação no banco
        print(f"Erro em RegistrarEncomenda: {str(ex)}")
        return jsonify({"message": "Erro ao registrar encomenda.", "error": str(ex)}), 500

# Equivalente ao [HttpGet("Encomendas")]
@porteiro_bp.route('/api/porteiro/encomendas', methods=['GET'])
@jwt_required()
def verificar_encomendas():
    claims = get_jwt()
    if claims.get("perfil") != "porteiro":
        return jsonify({"erro": "Acesso negado."}), 403

    status_query = request.args.get('status')

    try:
        query = Encomenda.query

        if status_query:
            query = query.filter_by(status=status_query)

        encomendas = query.order_by(Encomenda.data_registro.desc()).all()

        resultado_formatado = []
        for e in encomendas:
            morador = Usuario.query.get(e.morador_id)
            
            # Busca quem foi o porteiro que registrou
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
                "Apartamento": morador.apartamento if morador else "N/A",
                "Morador": morador.nome if morador else "N/A",
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
        print(f"Erro em VerificarEncomendas: {str(ex)}")
        return jsonify({"message": "Erro ao buscar encomendas.", "error": str(ex)}), 500

# Equivalente ao [HttpGet("BuscarMoradores")]
@porteiro_bp.route('/api/porteiro/buscar-moradores', methods=['GET'])
@jwt_required()
def buscar_moradores():
    claims = get_jwt()
    if claims.get("perfil") != "porteiro":
        return jsonify({"erro": "Acesso negado."}), 403

    termo_busca = request.args.get('query', '')

    # Verifica se a string tem pelo menos 2 caracteres
    if not termo_busca or len(termo_busca) < 2:
        return jsonify([]), 200

    try:
        # Busca usuários ativos do tipo morador onde o nome contenha o termo digitado (case-insensitive no MySQL)
        moradores = Usuario.query.filter(
            Usuario.perfil == 'morador',
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
