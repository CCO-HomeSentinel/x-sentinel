from flask import Flask, render_template, request
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from dotenv import load_dotenv
from .config.auth import generate_token, token_required


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.logger import logger
from service.clientes import get_mapeamento, logar

load_dotenv()

FLASK_ENDPOINT = os.getenv("FLASK_ENDPOINT")

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        logger.log("info", "Endpoint / acessado.")
        return render_template('index.html')
    

    @app.route('/main')
    def main():
        return render_template('main.html')
    
    @app.route('/residencia/<int:id>')
    def residencia(id):
        return render_template('residencia.html')
    
    
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        email = data['email']
        password = data['password']

        cliente = logar(email, password)

        if cliente:
            token = generate_token(email)

            if isinstance(token, bytes):
                token = token.decode('utf-8')

            return jsonify({'token': token, 'nome': cliente[1]}), 200

        return jsonify({"message": "Usuário ou senha inválidos."}), 401

    
    @app.route('/clientes', methods=['GET'])
    @token_required
    def clientes(current_user):
        mapeamento = get_mapeamento()

        return jsonify(mapeamento), 200
    

    return app


def accepted(message):
    return jsonify({"message": message}), 202


def bad_request(message):
    return jsonify({"error": message}), 400