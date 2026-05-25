import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'events_platform.db')

def get_db_connection(db_path=None):
    """
    Establece una conexión con la base de datos SQLite.
    Configura row_factory para retornar diccionarios.
    """
    if db_path is None:
        db_path = DATABASE_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Habilitar soporte para llaves foráneas en SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=None):
    """
    Inicializa el esquema de la base de datos creando las tablas necesarias.
    """
    if db_path is None:
        db_path = DATABASE_PATH
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Tabla de Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')

    # Tabla de Eventos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            location TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')

    # Tabla de Compras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def seed_db(db_path=None):
    """
    Inserta datos iniciales de eventos si la tabla 'events' está vacía.
    """
    if db_path is None:
        db_path = DATABASE_PATH
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]

    if count == 0:
        events = [
            (
                "Rock en la Ciudad 2026",
                "El festival de rock más grande del año con bandas nacionales e internacionales en vivo.",
                "2026-06-15",
                45.00,
                100,
                "Estadio Nacional de Lima",
                "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=500&auto=format&fit=crop&q=60"
            ),
            (
                "Festival de Jazz & Blues",
                "Una noche mágica bajo las estrellas disfrutando de la mejor selección de jazz contemporáneo.",
                "2026-07-20",
                60.00,
                50,
                "Teatro Municipal",
                "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=500&auto=format&fit=crop&q=60"
            ),
            (
                "Obra de Teatro: Hamlet",
                "La aclamada tragedia de William Shakespeare adaptada por un elenco estelar contemporáneo.",
                "2026-08-05",
                25.00,
                80,
                "Auditorio Central de Miraflores",
                "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=500&auto=format&fit=crop&q=60"
            ),
            (
                "Conferencia Internacional Tech 2026",
                "Aprende sobre Inteligencia Artificial, computación cuántica y el futuro de la web con expertos mundiales.",
                "2026-09-12",
                15.00,
                150,
                "Centro de Convenciones del Prado",
                "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=500&auto=format&fit=crop&q=60"
            )
        ]

        cursor.executemany('''
            INSERT INTO events (title, description, date, price, stock, location, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', events)
        conn.commit()

    conn.close()

if __name__ == '__main__':
    # Ejecutar de forma independiente para preparar la base de datos
    print("Inicializando base de datos...")
    init_db()
    print("Insertando datos iniciales...")
    seed_db()
    print("¡Base de datos lista!")
