from flask import Blueprint, render_template

site_bp = Blueprint('site', __name__)

@site_bp.route('/')
@site_bp.route('/index.html')
def index():
    return render_template('main/index.html')

@site_bp.route('/sindico.html')
def sindico():
    return render_template('main/sindico.html')

@site_bp.route('/morador.html')
def morador():
    return render_template('main/morador.html')

@site_bp.route('/porteiro.html')
def porteiro():
    return render_template('main/porteiro.html')

@site_bp.route('/carrinho.html')
def carrinho():
    return render_template('main/carrinho.html')

@site_bp.route('/contato.html')
def contato():
    return render_template('main/contato.html')
