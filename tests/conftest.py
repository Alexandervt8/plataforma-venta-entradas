import os
import pytest
import database
from app import app as flask_app
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """
    Configura la aplicación Flask para pruebas usando una base de datos SQLite temporal.

    Este fixture:
    - Activa TESTING.
    - Redirige database.DATABASE_PATH hacia test_events_platform.db.
    - Crea el esquema real con database.init_db().
    - Inserta eventos controlados para los casos de prueba.
    - Elimina la base de datos temporal al finalizar.
    """
    test_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    test_db_path = os.path.abspath(os.path.join(test_db_dir, "test_events_platform.db"))

    database.DATABASE_PATH = test_db_path

    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "WTF_CSRF_ENABLED": False,
    })

    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass

    database.init_db(test_db_path)

    conn = database.get_db_connection(test_db_path)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO events (id, title, description, date, price, stock, location, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (
            1,
            "Rock Test 2026",
            "Festival de rock para pruebas automatizadas",
            "2026-06-01",
            10.00,
            10,
            "Lima",
            "http://example.com/rock.jpg",
        ),
        (
            2,
            "Jazz Agotado",
            "Evento sin stock para validar agotados",
            "2026-07-01",
            20.00,
            0,
            "Arequipa",
            "http://example.com/jazz.jpg",
        ),
        (
            3,
            "Tech Conference",
            "Evento tecnológico para historial de compras",
            "2026-08-01",
            30.00,
            5,
            "Cusco",
            "http://example.com/tech.jpg",
        ),
        (
            4,
            "Evento Ultima Entrada",
            "Evento con una sola entrada disponible",
            "2026-09-01",
            15.00,
            1,
            "Lima",
            "http://example.com/ultima.jpg",
        ),
    ])
    conn.commit()
    conn.close()

    yield flask_app

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
def registered_user(app):
    """
    Inserta un usuario válido en la base de datos temporal.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, email, password, name)
        VALUES (?, ?, ?, ?)
    """, (
        1,
        "user.test@example.com",
        generate_password_hash("password123"),
        "Usuario de Prueba",
    ))
    conn.commit()
    conn.close()

    return {
        "id": 1,
        "email": "user.test@example.com",
        "password": "password123",
        "name": "Usuario de Prueba",
    }


@pytest.fixture
def second_user(app):
    """
    Inserta un segundo usuario para validar aislamiento de historial.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, email, password, name)
        VALUES (?, ?, ?, ?)
    """, (
        2,
        "otro.usuario@example.com",
        generate_password_hash("password123"),
        "Otro Usuario",
    ))
    conn.commit()
    conn.close()

    return {
        "id": 2,
        "email": "otro.usuario@example.com",
        "password": "password123",
        "name": "Otro Usuario",
    }


@pytest.fixture
def authenticated_client(client, registered_user):
    """
    Retorna un cliente con sesión activa del usuario principal.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = registered_user["id"]
        sess["user_name"] = registered_user["name"]

    return client


@pytest.fixture
def authenticated_second_client(client, second_user):
    """
    Retorna un cliente con sesión activa del segundo usuario.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = second_user["id"]
        sess["user_name"] = second_user["name"]

    return client


def get_event_stock(event_id):
    """
    Utilidad para consultar el stock actual de un evento.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stock FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    return row["stock"] if row else None


def count_purchases_for_user(user_id):
    """
    Utilidad para contar compras de un usuario.
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM purchases WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count
