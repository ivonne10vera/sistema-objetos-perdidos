import mysql.connector
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection

objetos_bp =Blueprint('objetos',__name__)

CAMPOS=['titulo','descripcion','tipo_reporte','fecha','lugar','id_categoria']
TIPOS=['extraviado','encontrado']

@objetos_bp.route('', methods=['POST'])
@jwt_required()
def crear_objeto():
    datos =request.get_json(silent=True)
    if datos is None:
        datos= {}
    faltan=[]
    for campo in CAMPOS:
        valor= datos.get(campo)
        if valor is None or valor== '':
            faltan.append(campo)
    if len(faltan)>0:
        return jsonify({"mensaje":"Faltan campos: " + ", ".join(faltan)}),400
    if datos['tipo_reporte'] not in TIPOS:
        return jsonify({"mensaje":"tipo_reporte debe ser 'extraviado' o 'encontrado'"}),400
    id_usuario=get_jwt_identity()
    conexion=db.get_db_connection()
    cursor =conexion.cursor()
    try:
        sql=("INSERT INTO objetos (titulo,descripcion,tipo_reporte,fecha,lugar,id_categoria,id_usuario)"
               "VALUES (%s,%s,%s,%s,%s,%s,%s)")
        valores=(datos['titulo'], datos['descripcion'], datos['tipo_reporte'],
                   datos['fecha'], datos['lugar'],datos['id_categoria'],id_usuario)
        cursor.execute(sql, valores)
        conexion.commit()
        return jsonify({"mensaje":"Objeto registrado", "id": cursor.lastrowid}),201
    except mysql.connector.IntegrityError as e:
        conexion.rollback()
        return jsonify({"mensaje":"Esa categoria no existe","error": str(e)}),409
    except mysql.connector.DataError as e:
        conexion.rollback()
        return jsonify({"mensaje": "Dato invalido revisa fecha o texto","error": str(e)}),400
    except mysql.connector.Error as e:
        conexion.rollback()
        return jsonify({"mensaje":"Error en la base de datos","error": str(e)}),500
    finally:        
        cursor.close()
        conexion.close()

@objetos_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def editar_objeto(id):
    datos= request.get_json(silent=True)
    if datos is None:
        datos ={}
    columnas =[]   
    valores =[]   
    for campo in CAMPOS:
        if campo in datos:
            if datos[campo] is None or datos[campo] == '':
                return jsonify({"mensaje": "campo vacio"}), 400
            columnas.append(campo + " = %s")
            valores.append(datos[campo])
    if len(columnas) ==0:
        return jsonify({"mensaje": "Campo vacio"}), 400
    if 'tipo_reporte' in datos and datos['tipo_reporte'] not in TIPOS:
        return jsonify({"mensaje": "tipo_reporte debe ser 'extraviado' o 'encontrado'"}), 400
    valores.append(id)
    conexion = db.get_db_connection()
    cursor = conexion.cursor(buffered=True)
    try:        
        cursor.execute("SELECT id FROM objetos WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            return jsonify({"mensaje": "Objeto no encontrado"}), 404
        sql= "UPDATE objetos SET " + ", ".join(columnas) + " WHERE id = %s"
        cursor.execute(sql, valores)
        conexion.commit()
        return jsonify({"mensaje":"Objeto actualizado"}), 200
    except mysql.connector.IntegrityError as e:
        conexion.rollback()
        return jsonify({"mensaje": "Categoría no existe","error": str(e)}), 409
    except mysql.connector.DataError as e:
        conexion.rollback()
        return jsonify({"mensaje": "Dato invalido revisa fecha o texto","error": str(e)}), 400
    except mysql.connector.Error as e:
        conexion.rollback()
        return jsonify({"mensaje":"Error en la base de datos","error": str(e)}), 500
    finally:
        cursor.close()
        conexion.close()

@objetos_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def eliminar_objeto(id):
    conexion =db.get_db_connection()
    cursor =conexion.cursor()
    try:
        cursor.execute("DELETE FROM objetos WHERE id = %s", (id,))
        if cursor.rowcount== 0:
            return jsonify({"mensaje": "Objeto no encontrado"}), 404
        conexion.commit()
        return jsonify({"mensaje": "Objeto eliminado"}), 200
    except mysql.connector.IntegrityError as e:
        conexion.rollback()
        return jsonify({"mensaje": "Categoria no existe","error": str(e)}), 409
    except mysql.connector.DataError as e:
        conexion.rollback()
        return jsonify({"mensaje": "Dato invalido revisa fecha o texto","error": str(e)}), 400
    except mysql.connector.Error as e:
        conexion.rollback()
        return jsonify({"mensaje":"Error en la base de datos","error": str(e)}), 500
    finally:
        cursor.close()
        conexion.close()

@objetos_bp.route('/mios', methods=['GET'])
@jwt_required()
def mis_objetos():
    id_usuario= get_jwt_identity()
    conexion =db.get_db_connection()
    cursor =conexion.cursor(dictionary=True)
    try:
        sql =("SELECT o.id, o.titulo, o.descripcion, o.tipo_reporte, o.fecha, o.lugar, o.estado, "
               "o.id_categoria, c.nombre AS categoria "
               "FROM objetos o JOIN categorias c ON c.id = o.id_categoria "
               "WHERE o.id_usuario = %s ORDER BY o.id DESC")
        cursor.execute(sql, (id_usuario,))
        objetos =cursor.fetchall()
        for objeto in objetos:
            objeto['fecha'] = objeto['fecha'].isoformat()
        return jsonify(objetos), 200
    except mysql.connector.Error as e:
        return jsonify({"mensaje":"Error en la base de datos","error": str(e)}),500
    finally:
        cursor.close()
        conexion.close()

@objetos_bp.route('/categorias',methods=['GET'])
@jwt_required()
def listar_categorias():
    conexion=db.get_db_connection()
    cursor=conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        categorias= cursor.fetchall()
        return jsonify(categorias), 200
    except mysql.connector.Error as e:
        return jsonify({"mensaje":"Error en la base de datos","error":str(e)}),500
    finally:
        cursor.close()
        conexion.close()