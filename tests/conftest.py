import os
import pytest
import database
from app import app as flask_app

@pytest.fixture
def app():
    """
    Fixture que configura la aplicación Flask para propósitos de prueba.
    Usa una base de datos temporal específica para pruebas.
    """
    # Configurar una ruta de base de datos de pruebas temporal
    test_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    test_db_path = os.path.join(test_db_dir, 'test_events_platform.db')
    
    # Sobrescribir la ruta en el módulo de base de datos
    database.DATABASE_PATH = test_db_path
    
    # Habilitar el modo de prueba en Flask
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "WTF_CSRF_ENABLED": False  # Deshabilitar CSRF para simplificar pruebas de formularios
    })

    # Asegurarnos de que no haya una BD de pruebas previa
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass

    # Inicializar la base de datos de pruebas con el esquema real
    database.init_db(test_db_path)
    
    # Insertar eventos de prueba específicos y controlados
    conn = database.get_db_connection(test_db_path)
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO events (id, title, description, date, price, stock, location, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        (1, "Evento A", "Descripción A", "2026-06-01", 10.00, 10, "Lugar A", "http://example.com/a.jpg"),
        (2, "Evento B", "Descripción B", "2026-07-01", 20.00, 0, "Lugar B", "http://example.com/b.jpg"),  # Sin stock
        (3, "Evento C", "Descripción C", "2026-08-01", 30.00, 5, "Lugar C", "http://example.com/c.jpg")
    ])
    conn.commit()
    conn.close()

    yield flask_app

    # Teardown: Eliminar la base de datos de pruebas al finalizar
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass

@pytest.fixture
def client(app):
    """
    Retorna el cliente de pruebas de Flask.
    """
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """
    Retorna un cliente de pruebas con una sesión de usuario ya activa.
    """
    # Registrar un usuario de prueba en la base de datos temporal
    conn = database.get_db_connection()
    cursor = conn.cursor()
    from werkzeug.security import generate_password_hash
    cursor.execute('''
        INSERT INTO users (id, email, password, name) 
        VALUES (1, 'user.test@example.com', ?, 'Usuario de Prueba')
    ''', (generate_password_hash("password123"),))
    conn.commit()
    conn.close()

    # Iniciar sesión simulando los datos en session
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = 'Usuario de Prueba'
    
    return client
