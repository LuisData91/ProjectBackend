from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime  # Para manejar fechas


app = Flask(__name__)
app.secret_key = 'luis'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistema_viaticos'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Configuración de archivos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo

# Función para validar extensiones
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Función para agregar cabeceras de no caché
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Deshabilita la caché
    response.headers["Pragma"] = "no-cache"  # Compatibilidad con HTTP/1.0
    response.headers["Expires"] = "0"  # Fecha de expiración en el pasado
    return response


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))  # Redirige a home si está autenticado
    return redirect(url_for('login'))  # Redirige a login si no está autenticado

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session['username'] = username
            session['fullname']= user[3]
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login'))

    response = make_response(render_template('login.html'))
    return add_no_cache_headers(response)  # Aplica las cabeceras de no caché

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso. Por favor, inicia sesión.')
        return redirect(url_for('login'))

    response = make_response(render_template('register.html'))
    return add_no_cache_headers(response)  # Aplica las cabeceras de no caché

# @app.route('/home')
# def home():
#     if 'username' not in session:
#         return redirect(url_for('login'))  # Redirige a login si no está autenticado
#     response = make_response(render_template('home.html'))
#     return add_no_cache_headers(response)  # Aplica las cabeceras de no caché
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirige si no está autenticado

    cur = mysql.connection.cursor()

    # Obtener el ID y nombre completo del usuario autenticado
    cur.execute("SELECT id_usuario, fullname FROM users WHERE username = %s", (session['username'],))
    user_data = cur.fetchone()

    if user_data:
        user_id = user_data[0]
        session['fullname'] = user_data[1]

        # Traer las facturas que registró este usuario
        cur.execute("""
            SELECT f.id_factura,f.fecha_emision, f.tipo_comprobante, f.num_documento, 
                   p.nombre AS nombre_proyecto, pr.nombre AS nombre_producto, 
                   c.nombre AS ciudad, f.importe, f.incluye_igv, f.urldoc
            FROM facturas f
            JOIN proyectos p ON f.id_proyecto = p.id_proyecto
            JOIN productos pr ON f.id_producto = pr.id_producto
            JOIN ciudades c ON f.id_ciudad = c.id_ciudad
            WHERE f.id_usuario = %s
            ORDER BY f.fecha_emision DESC
        """, (user_id,))
        facturas = cur.fetchall()
        cur.close()

        return render_template('home.html', facturas=facturas)

    flash('Usuario no válido')
    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    response = make_response(redirect(url_for('login')))
    return add_no_cache_headers(response)  # Aplica las cabeceras de no caché




@app.route('/facturas/crear', methods=['GET', 'POST'])
def crear_factura():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Obtener datos para dropdowns (para GET y POST si hay error)
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_proyecto, nombre FROM proyectos")
    proyectos = cur.fetchall()
    cur.execute("SELECT id_producto, nombre FROM productos")
    productos = cur.fetchall()
    cur.execute("SELECT id_ciudad, nombre FROM ciudades")
    ciudades = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        try:
            # 1. Validar archivo primero
            if 'documento' not in request.files:
                flash('No se seleccionó ningún archivo', 'danger')
                return render_template('crear.html', 
                                     proyectos=proyectos, 
                                     productos=productos, 
                                     ciudades=ciudades)

            file = request.files['documento']
            
            # Si el usuario no selecciona archivo, permitir continuar
            if file.filename == '':
                filename = None
            else:
                # Validar extensión
                if not allowed_file(file.filename):
                    flash('Tipo de archivo no permitido. Use PDF, PNG o JPG', 'danger')
                    return render_template('crear.html',
                                         proyectos=proyectos,
                                         productos=productos,
                                         ciudades=ciudades)
                
                # Crear nombre único para evitar colisiones
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                original_name = secure_filename(file.filename)
                filename = f"{timestamp}_{original_name}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # 2. Obtener otros datos del formulario
            form_data = {
                'ruc': request.form.get('ruc'),
                'serie': request.form.get('serie'),
                'num_documento': request.form.get('num_documento'),
                'modalidad': request.form.get('modalidad'),
                'fecha_emision': request.form.get('fecha_emision'),
                'tipo_comprobante': request.form.get('tipo_comprobante'),
                'id_producto': request.form.get('id_producto'),
                'id_proyecto': request.form.get('id_proyecto'),
                'id_ciudad': request.form.get('id_ciudad'),
                'importe': request.form.get('importe'),
                'incluye_igv': 1 if request.form.get('incluye_igv') else 0,
                'urldoc': filename
            }

            # 3. Validar campos requeridos
            required_fields = ['ruc', 'serie', 'num_documento', 'fecha_emision', 
                             'tipo_comprobante', 'id_producto', 'id_proyecto', 
                             'id_ciudad', 'importe']
            
            for field in required_fields:
                if not form_data[field]:
                    flash(f'El campo {field} es requerido', 'danger')
                    return render_template('crear.html',
                                         proyectos=proyectos,
                                         productos=productos,
                                         ciudades=ciudades)

            # 4. Obtener ID de usuario
            cur = mysql.connection.cursor()
            cur.execute("SELECT id_usuario FROM users WHERE username = %s", (session['username'],))
            user_id = cur.fetchone()[0]

            # 5. Insertar en BD
            cur.execute("""
                INSERT INTO facturas (
                    ruc, serie, num_documento, modalidad, fecha_emision, 
                    tipo_comprobante, id_producto, id_proyecto, id_usuario, 
                    id_ciudad, importe, incluye_igv, urldoc
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                form_data['ruc'], form_data['serie'], form_data['num_documento'],
                form_data['modalidad'], form_data['fecha_emision'],
                form_data['tipo_comprobante'], form_data['id_producto'],
                form_data['id_proyecto'], user_id, form_data['id_ciudad'],
                form_data['importe'], form_data['incluye_igv'], form_data['urldoc']
            ))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Factura registrada exitosamente!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            print(f"Error completo: {str(e)}")  # Para depuración
            flash(f'Error al registrar la factura: {str(e)}', 'danger')
            return render_template('crear.html',
                                 proyectos=proyectos,
                                 productos=productos,
                                 ciudades=ciudades)

    return render_template('crear.html',
                         proyectos=proyectos,
                         productos=productos,
                         ciudades=ciudades)


@app.route('/facturas/editar/<int:id_factura>', methods=['GET', 'POST'])
def editar_factura(id_factura):
    if 'username' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Obtener los combos para el formulario
    cur.execute("SELECT id_proyecto, nombre FROM proyectos")
    proyectos = cur.fetchall()
    cur.execute("SELECT id_producto, nombre FROM productos")
    productos = cur.fetchall()
    cur.execute("SELECT id_ciudad, nombre FROM ciudades")
    ciudades = cur.fetchall()

    # Obtener datos actuales de la factura
    cur.execute("SELECT * FROM facturas WHERE id_factura = %s", (id_factura,))
    factura = cur.fetchone()

    if not factura:
        flash("Factura no encontrada", "danger")
        return redirect(url_for('home'))

    # Convertir a lista para poder modificarla (ej: fecha)
    factura = list(factura)
    factura[5] = factura[5].isoformat() if factura[5] else ''
    urldoc_anterior = factura[13]  # Guarda el archivo anterior

    if request.method == 'POST':
        try:
            # Leer datos del formulario
            ruc = request.form.get('ruc')
            serie = request.form.get('serie')
            num_documento = request.form.get('num_documento')
            modalidad = request.form.get('modalidad')
            fecha_emision = request.form.get('fecha_emision')
            tipo_comprobante = request.form.get('tipo_comprobante')
            id_producto = request.form.get('id_producto')
            id_proyecto = request.form.get('id_proyecto')
            id_ciudad = request.form.get('id_ciudad')
            importe = request.form.get('importe')
            incluye_igv = 1 if request.form.get('incluye_igv') else 0

            # ---------- MANEJO DEL ARCHIVO ----------
            file = request.files.get('documento')
            filename = urldoc_anterior  # Por defecto, conserva el archivo anterior

            if file and file.filename:
                if allowed_file(file.filename):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    original_name = secure_filename(file.filename)
                    filename = f"{timestamp}_{original_name}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Opcional: eliminar archivo anterior
                    if urldoc_anterior:
                        anterior_path = os.path.join(app.config['UPLOAD_FOLDER'], urldoc_anterior)
                        if os.path.exists(anterior_path):
                            os.remove(anterior_path)
                else:
                    flash('Tipo de archivo no permitido. Usa PDF, JPG, PNG.', 'danger')
                    return render_template('editar.html', factura=factura, proyectos=proyectos, productos=productos, ciudades=ciudades)
            # ---------- FIN DEL MANEJO DE ARCHIVO ----------

            # Actualizar en la base de datos
            cur.execute("""
                UPDATE facturas SET 
                    ruc=%s, serie=%s, num_documento=%s, modalidad=%s, 
                    fecha_emision=%s, tipo_comprobante=%s, id_producto=%s,
                    id_proyecto=%s, id_ciudad=%s, importe=%s, incluye_igv=%s, urldoc=%s
                WHERE id_factura = %s
            """, (
                ruc, serie, num_documento, modalidad, fecha_emision, tipo_comprobante,
                id_producto, id_proyecto, id_ciudad, importe, incluye_igv, filename, id_factura
            ))

            mysql.connection.commit()
            flash("Factura actualizada correctamente", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Error al actualizar la factura: {str(e)}", "danger")

    cur.close()
    return render_template('editar.html', factura=factura, proyectos=proyectos, productos=productos, ciudades=ciudades)

@app.route('/facturas/eliminar/<int:id_factura>', methods=['POST'])
def eliminar_factura(id_factura):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        cur = mysql.connection.cursor()

        # Obtener nombre del archivo antes de eliminar
        cur.execute("SELECT urldoc FROM facturas WHERE id_factura = %s", (id_factura,))
        result = cur.fetchone()

        if result and result[0]:
            archivo = result[0]
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo)
            if os.path.exists(ruta):
                os.remove(ruta)

        # Eliminar factura
        cur.execute("DELETE FROM facturas WHERE id_factura = %s", (id_factura,))
        mysql.connection.commit()
        cur.close()

        flash("Factura eliminada correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "danger")

    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)

