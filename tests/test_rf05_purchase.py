import database
from conftest import get_event_stock, count_purchases_for_user


# ==============================================================================
# RF-05: Compra de Entradas
# ==============================================================================

def test_rf05_pe_com_01_purchase_valid_quantity(authenticated_client):
    """
    PE-COM-01:
    Cantidad permitida dentro del stock.
    Resultado esperado: Compra exitosa.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "3",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert "Rock Test 2026" in html


def test_rf05_pe_com_02_empty_quantity_invalid(authenticated_client):
    """
    PE-COM-02:
    Cantidad vacía.
    Resultado esperado: Error de cantidad requerida.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Debes ingresar una cantidad de entradas." in html


def test_rf05_pe_com_02_non_numeric_quantity_invalid(authenticated_client):
    """
    PE-COM-02:
    Cantidad no numérica.
    Resultado esperado: Error de número entero válido.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "dos",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "La cantidad de entradas debe ser un número entero válido." in html


def test_rf05_pe_com_03_nonexistent_event_invalid(authenticated_client):
    """
    PE-COM-03:
    Evento inexistente.
    Resultado esperado: Error de evento no existente.
    """
    response = authenticated_client.post("/purchase/999", data={
        "quantity": "2",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "El evento seleccionado no existe." in html


def test_rf05_pe_com_04_unauthenticated_user_invalid(client):
    """
    PE-COM-04:
    Usuario no autenticado.
    Resultado esperado: Redirección al inicio de sesión.
    """
    response = client.post("/purchase/1", data={
        "quantity": "2",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "Debes iniciar sesión para realizar una compra." in html
    assert "Iniciar Sesión" in html


def test_rf05_pe_com_05_quantity_exceeds_stock_invalid(authenticated_client):
    """
    PE-COM-05:
    Cantidad superior al stock disponible.
    Resultado esperado: Error de stock insuficiente.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "11",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No es posible comprar 11 entradas. El stock disponible es de 10." in html


def test_rf05_avl_com_01_quantity_zero_invalid(authenticated_client):
    """
    AVL-COM-01:
    Cantidad = 0.
    Resultado esperado: Error de cantidad mayor a cero.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "0",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "La cantidad de entradas debe ser mayor a cero." in html


def test_rf05_avl_com_02_quantity_negative_invalid(authenticated_client):
    """
    AVL-COM-02:
    Cantidad < 0.
    Resultado esperado: Error de cantidad mayor a cero.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "-1",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "La cantidad de entradas debe ser mayor a cero." in html


def test_rf05_avl_com_03_minimum_valid_quantity(authenticated_client):
    """
    AVL-COM-03:
    Cantidad mínima válida.
    Resultado esperado: Compra exitosa.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "1",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html


def test_rf05_avl_com_04_quantity_equal_to_stock(authenticated_client):
    """
    AVL-COM-04:
    Cantidad igual al stock.
    Resultado esperado: Compra exitosa y stock final = 0.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "10",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in html
    assert get_event_stock(1) == 0


def test_rf05_avl_com_05_quantity_above_stock(authenticated_client):
    """
    AVL-COM-05:
    Cantidad superior al stock.
    Resultado esperado: Error de stock insuficiente.
    """
    response = authenticated_client.post("/purchase/1", data={
        "quantity": "11",
    }, follow_redirects=True)

    html = response.get_data(as_text=True)
    assert "No es posible comprar 11 entradas. El stock disponible es de 10." in html


def test_rf05_total_price_is_calculated_correctly(authenticated_client):
    """
    Regla de negocio:
    El sistema debe calcular correctamente el monto total de la compra.
    """
    authenticated_client.post("/purchase/3", data={
        "quantity": "2",
    }, follow_redirects=True)

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT quantity, total_price
        FROM purchases
        WHERE event_id = 3 AND user_id = 1
    """)
    purchase = cursor.fetchone()
    conn.close()

    assert purchase["quantity"] == 2
    assert purchase["total_price"] == 60.00
    assert count_purchases_for_user(1) == 1
