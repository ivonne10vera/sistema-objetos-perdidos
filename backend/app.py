from routes.catalogo_routes import catalogo_bp
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import get_db_connection
from routes.auth_routes import auth_bp
from routes.reportes_routes import reportes_bp

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'clave-secreta-universidad-2026'
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
app.register_blueprint(catalogo_bp, url_prefix='/api/objetos')

@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM objetos")
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"estado": "Conectado a phpMyAdmin", "objetos_registrados": resultado['total']}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)