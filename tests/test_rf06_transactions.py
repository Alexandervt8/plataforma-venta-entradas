import database
from conftest import get_event_stock, count_purchases_for_user


# ==============================================================================
# RF-06: Control de Transacciones
# ==============================================================================

def test_rf06_pe_tra_01_valid_purchase_updates_stock_and_registers_purchase(authenticated_client):
    """
    PE-TRA-01:
    Compra válida.
    Resultado esperado: Compra registrada y stock actualizado.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "2",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert get_event_stock(1) == 8
    assert count_purchases_for_user(1) == 1


def test_rf06_pe_tra_02_transaction_error_does_not_create_partial_purchase(authenticated_client, monkeypatch):
    """
    PE-TRA-02:
    Error durante la transacción.
    Resultado esperado: Se ejecuta ROLLBACK y no queda compra parcial.

    Nota:
    Se simula un fallo en el INSERT de purchases interceptando el cursor.
    """

    class FailingCursor:
        def __init__(self, real_cursor):
            self.real_cursor = real_cursor

        def execute(self, sql, params=()):
            if "INSERT INTO purchases" in sql:
                raise RuntimeError("Falla simulada durante inserción de compra")
            return self.real_cursor.execute(sql, params)

        def fetchone(self):
            return self.real_cursor.fetchone()

        def fetchall(self):
            return self.real_cursor.fetchall()

        def executemany(self, sql, seq_of_params):
            return self.real_cursor.executemany(sql, seq_of_params)

    class FailingConnection:
        def __init__(self, real_conn):
            self.real_conn = real_conn

        def cursor(self):
            return FailingCursor(self.real_conn.cursor())

        def execute(self, *args, **kwargs):
            return self.real_conn.execute(*args, **kwargs)

        def commit(self):
            return self.real_conn.commit()

        def close(self):
            return self.real_conn.close()

    original_get_db_connection = database.get_db_connection
    call_counter = {"count": 0}

    def patched_get_db_connection(*args, **kwargs):
        conn = original_get_db_connection(*args, **kwargs)
        call_counter["count"] += 1
        # En la ruta purchase, la primera conexión lee el evento.
        # La segunda procesa la transacción; ahí provocamos el fallo.
        if call_counter["count"] >= 2:
            return FailingConnection(conn)
        return conn

    monkeypatch.setattr(database, "get_db_connection", patched_get_db_connection)

    initial_stock = get_event_stock(1)

    response = authenticated_client.post("/purchase/1", data={
        "quantity": "2",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Hubo un error inesperado al procesar tu compra. Por favor inténtalo de nuevo." in html

    # Tras el rollback, el stock debe permanecer igual y no debe registrarse compra.
    assert get_event_stock(1) == initial_stock
    assert count_purchases_for_user(1) == 0


def test_rf06_pe_tra_03_purchase_consumes_all_stock(authenticated_client):
    """
    PE-TRA-03:
    Compra consume todo el stock.
    Resultado esperado: Stock final = 0.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "10",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert get_event_stock(1) == 0


def test_rf06_pe_tra_04_second_purchase_cannot_oversell_stock(authenticated_client):
    """
    PE-TRA-04:
    Compra simultánea o posterior excede stock.
    Resultado esperado: Se evita sobreventa.
    """
    authenticated_client.post("/purchase/4", data={
        "quantity": "1",
    }, follow_redirects=True)

    response = authenticated_client.post("/purchase/4", data={
        "quantity": "1",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No es posible comprar 1 entradas. El stock disponible es de 0." in html
    assert get_event_stock(4) == 0


def test_rf06_avl_tra_01_stock_final_zero(authenticated_client):
    """
    AVL-TRA-01:
    Stock final = 0.
    Resultado esperado: Compra exitosa y stock agotado.
    """
    response = authenticated_client.post("/purchase/4", data={
        "quantity": "1",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert get_event_stock(4) == 0


def test_rf06_avl_tra_02_stock_negative_is_rejected(authenticated_client):
    """
    AVL-TRA-02:
    Stock final negativo.
    Resultado esperado: Compra rechazada.
    """
    response = authenticated_client.post("/purchase/4", data={
        "quantity": "2",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No es posible comprar 2 entradas. El stock disponible es de 1." in html
    assert get_event_stock(4) == 1


def test_rf06_avl_tra_03_stock_final_positive(authenticated_client):
    """
    AVL-TRA-03:
    Stock final positivo.
    Resultado esperado: Stock final = 6.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "4",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert get_event_stock(1) == 6
