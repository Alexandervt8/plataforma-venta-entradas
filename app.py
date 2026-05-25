import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import database

app = Flask(__name__)
app.secret_key = 'super_secret_session_key_for_testing_and_production'

# Expresión regular robusta para validación de email
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para realizar esta acción.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """
    Listado y búsqueda de eventos.
    """
    query = request.args.get('q', '').strip()
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    if query:
        # Búsqueda segura usando placeholders de SQLite
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
        ''', (search_pattern, search_pattern, search_pattern))
    else:
        cursor.execute('SELECT * FROM events')
        
    events = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', events=events, query=query)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de nuevos usuarios con validaciones de backend estrictas.
    """
    # Si el usuario ya está autenticado, redirigir al index
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # 1. Validación: Campos vacíos
        if not name or not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return render_template('register.html')

        # 2. Validación: Email inválido
        if not re.match(EMAIL_REGEX, email):
            flash('Por favor ingresa un correo electrónico válido.', 'error')
            return render_template('register.html')

        # 3. Validación: Contraseña menor a 6 caracteres
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('register.html')

        # Conectar a la base de datos para registrar el usuario
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_pw = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (email, password, name) 
                VALUES (?, ?, ?)
            ''', (email, hashed_pw, name))
            conn.commit()
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
        except database.sqlite3.IntegrityError:
            # Capturar correo electrónico duplicado
            flash('El correo electrónico ya se encuentra registrado.', 'error')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Inicio de sesión de usuarios.
    """
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Validación: Campos vacíos
        if not email or not password:
            flash('Todos los campos son obligatorios.', 'error')
            return render_template('login.html')

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        # Validar contraseña usando hash seguro
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'¡Bienvenido de nuevo, {user["name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Cierre de sesión.
    """
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/purchase/<int:event_id>', methods=['GET', 'POST'])
def purchase(event_id):
    """
    Formulario de compra y lógica de backend para adquisición de entradas.
    Maneja transacciones seguras de base de datos para evitar sobreventa.
    """
    # Buscar el evento
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()
    conn.close()

    # Validación obligatoria: Evento inexistente
    if not event:
        flash('El evento seleccionado no existe.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Validación obligatoria de autenticación
        if 'user_id' not in session:
            flash('Debes iniciar sesión para realizar una compra.', 'warning')
            return redirect(url_for('login'))

        # Obtener cantidad
        qty_str = request.form.get('quantity', '').strip()

        # 1. Validación: Campo vacío
        if not qty_str:
            flash('Debes ingresar una cantidad de entradas.', 'error')
            return render_template('purchase.html', event=event)

        try:
            quantity = int(qty_str)
        except ValueError:
            flash('La cantidad de entradas debe ser un número entero válido.', 'error')
            return render_template('purchase.html', event=event)

        # 2. Validación: Cantidades negativas o cero
        if quantity <= 0:
            flash('La cantidad de entradas debe ser mayor a cero.', 'error')
            return render_template('purchase.html', event=event)

        # 3. Validación: No permitir comprar más entradas que el stock (primera verificación rápida)
        if quantity > event['stock']:
            flash(f'No es posible comprar {quantity} entradas. El stock disponible es de {event["stock"]}.', 'error')
            return render_template('purchase.html', event=event)

        # Procesar la transacción de compra en la base de datos de manera atómica
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Comenzar transacción explícita
            conn.execute('BEGIN TRANSACTION;')
            
            # Bloquear la fila del evento para lectura y verificar stock real dentro de la transacción
            cursor.execute('SELECT stock FROM events WHERE id = ?', (event_id,))
            current_stock = cursor.fetchone()['stock']
            
            # Segunda verificación rigurosa de stock
            if quantity > current_stock:
                conn.execute('ROLLBACK;')
                flash(f'Lo sentimos, el stock cambió recientemente. Stock actual: {current_stock}.', 'error')
                return render_template('purchase.html', event=event)
            
            # Calcular precio total
            total_price = quantity * event['price']
            
            # Actualizar el stock
            cursor.execute('UPDATE events SET stock = stock - ? WHERE id = ?', (quantity, event_id))
            
            # Registrar la compra
            cursor.execute('''
                INSERT INTO purchases (user_id, event_id, quantity, total_price, purchase_date) 
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (session['user_id'], event_id, quantity, total_price))
            
            conn.execute('COMMIT;')
            flash('¡Compra realizada con éxito! Disfruta del evento.', 'success')
            return redirect(url_for('tickets'))
            
        except Exception as e:
            conn.execute('ROLLBACK;')
            flash('Hubo un error inesperado al procesar tu compra. Por favor inténtalo de nuevo.', 'error')
            return render_template('purchase.html', event=event)
        finally:
            conn.close()

    return render_template('purchase.html', event=event)

@app.route('/tickets')
@login_required
def tickets():
    """
    Despliega el historial de entradas compradas por el usuario actual.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            p.id as purchase_id, 
            p.quantity, 
            p.total_price, 
            p.purchase_date, 
            e.title as event_title, 
            e.date as event_date, 
            e.location as event_location
        FROM purchases p 
        JOIN events e ON p.event_id = e.id 
        WHERE p.user_id = ? 
        ORDER BY p.purchase_date DESC
    ''', (session['user_id'],))
    
    purchases = cursor.fetchall()
    conn.close()
    
    return render_template('tickets.html', purchases=purchases)

if __name__ == '__main__':
    # Inicializar la base de datos automáticamente si no existe al iniciar la app
    database.init_db()
    database.seed_db()
    
    print("Iniciando servidor de desarrollo Boletix en http://127.0.0.1:5000")
    app.run(debug=True)
