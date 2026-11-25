"""
Integrante 3 - Consultas y Filtros (Catálogo)
Ubicación: backend/routes/catalogo_routes.py

Endpoints (con url_prefix='/api/objetos'):
  GET /api/objetos            -> lista con filtros opcionales
  GET /api/objetos/filtros    -> categorías y lugares para llenar los <select>

Filtros por query string:
  ?categoria=2            (id de la categoría)
  &lugar=biblioteca       (búsqueda parcial)
  &fecha_desde=2026-11-01
  &fecha_hasta=2026-11-30
  &tipo=extraviado        (extraviado | encontrado)
  &estado=reportado       (reportado | encontrado | reclamado | entregado)
  &q=mochila              (título o descripción)
"""
from flask import Blueprint, request, jsonify
from db import get_db_connection

catalogo_bp = Blueprint("catalogo", __name__)


@catalogo_bp.route("", methods=["GET"])
@catalogo_bp.route("/", methods=["GET"])
def listar_objetos():
    condiciones = []
    params = []

    categoria = request.args.get("categoria")
    lugar = request.args.get("lugar")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    tipo = request.args.get("tipo")
    estado = request.args.get("estado")
    q = request.args.get("q")

    # WHERE dinámico: solo se agrega la condición si el filtro viene en la URL.
    # Siempre con %s (parámetros) para evitar SQL Injection.
    if categoria:
        condiciones.append("o.id_categoria = %s")
        params.append(categoria)
    if lugar:
        condiciones.append("o.lugar LIKE %s")
        params.append(f"%{lugar}%")
    if fecha_desde:
        condiciones.append("o.fecha >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        condiciones.append("o.fecha <= %s")
        params.append(fecha_hasta)
    if tipo:
        condiciones.append("o.tipo_reporte = %s")
        params.append(tipo)
    if estado:
        condiciones.append("o.estado = %s")
        params.append(estado)
    if q:
        condiciones.append("(o.titulo LIKE %s OR o.descripcion LIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])

    sql = """
        SELECT o.id, o.titulo, o.descripcion, o.tipo_reporte, o.fecha,
               o.lugar, o.estado, o.id_categoria,
               c.nombre AS categoria,
               u.nombre AS reportado_por
        FROM objetos o
        INNER JOIN categorias c ON o.id_categoria = c.id
        INNER JOIN usuarios u ON o.id_usuario = u.id
    """
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY o.fecha DESC, o.id DESC"

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        objetos = cursor.fetchall()
        cursor.close()

        for o in objetos:
            o["fecha"] = o["fecha"].isoformat() if o["fecha"] else None

        return jsonify(objetos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


@catalogo_bp.route("/filtros", methods=["GET"])
def opciones_filtros():
    """Datos para llenar los selects de la barra de filtros."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        categorias = cursor.fetchall()

        cursor.execute("SELECT DISTINCT lugar FROM objetos ORDER BY lugar")
        lugares = [fila["lugar"] for fila in cursor.fetchall()]

        cursor.close()
        return jsonify({"categorias": categorias, "lugares": lugares}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()