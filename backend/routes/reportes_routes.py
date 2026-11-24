from flask import Blueprint, jsonify
from db import get_db_connection

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('', methods=['GET'])
@reportes_bp.route('/', methods=['GET'])
def obtener_reportes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.id, o.titulo, o.fecha, o.lugar, c.nombre AS categoria
            FROM objetos o
            JOIN categorias c ON o.id_categoria = c.id
            WHERE o.estado = 'entregado'
            ORDER BY o.fecha DESC
        """)
        recuperados = cursor.fetchall()

        cursor.execute("""
            SELECT o.id, o.titulo, o.tipo_reporte, o.fecha, o.lugar, o.estado, c.nombre AS categoria
            FROM objetos o
            JOIN categorias c ON o.id_categoria = c.id
            WHERE o.estado IN ('reportado', 'encontrado', 'reclamado')
            ORDER BY o.fecha DESC
        """)
        pendientes = cursor.fetchall()

        cursor.execute("""
            SELECT lugar, COUNT(*) AS cantidad_reportes
            FROM objetos
            GROUP BY lugar
            ORDER BY cantidad_reportes DESC
        """)
        lugares = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "recuperados": recuperados,
            "pendientes": pendientes,
            "lugares": lugares
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500