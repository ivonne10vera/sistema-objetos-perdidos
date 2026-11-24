from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    correo = datos.get('correo')
    password = datos.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, correo, rol FROM usuarios WHERE correo = %s AND password = %s", (correo, password))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if not usuario:
        return jsonify({"mensaje": "Correo o contraseña incorrectos"}), 401

    token = create_access_token(identity=str(usuario['id']), additional_claims={"rol": usuario['rol'], "nombre": usuario['nombre']})
    return jsonify({"mensaje": "Login exitoso", "token": token, "usuario": usuario}), 200