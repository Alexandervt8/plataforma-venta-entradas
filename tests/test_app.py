import pytest
import database

# ==============================================================================
# PRUEBAS DE REGISTRO Y AUTENTICACIÓN (Técnica: Partición de Equivalencia - PE)
# ==============================================================================

def test_register_valid_user(client):
    """
    PE - Clase de Equivalencia Válida:
    Registrar un usuario con datos completos, email en formato correcto y contraseña >= 6 caracteres.
    """
    response = client.post('/register', data={
        'name': 'Estudiante Calidad',
        'email': 'estudiante@universidad.edu.pe',
        'password': 'seguro123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Registro exitoso. Por favor inicia sesión." in html

def test_register_empty_fields(client):
    """
    PE - Clase de Equivalencia Inválida:
    Campos de registro vacíos. Debe fallar e indicar que todos los campos son obligatorios.
    """
    # Nombre vacío
    response = client.post('/register', data={
        'name': '',
        'email': 'estudiante@universidad.edu.pe',
        'password': 'seguro123'
    }, follow_redirects=True)
    assert "Todos los campos son obligatorios." in response.get_data(as_text=True)

    # Email vacío
    response = client.post('/register', data={
        'name': 'Estudiante Calidad',
        'email': '',
        'password': 'seguro123'
    }, follow_redirects=True)
    assert "Todos los campos son obligatorios." in response.get_data(as_text=True)

def test_register_invalid_email(client):
    """
    PE - Clase de Equivalencia Inválida:
    Email con formato incorrecto (sin arroba, sin dominio válido).
    """
    invalid_emails = ["correo_sin_arroba.com", "usuario@", "@dominio.com", "usuario@dominio"]
    for email in invalid_emails:
        response = client.post('/register', data={
            'name': 'Estudiante Calidad',
            'email': email,
            'password': 'seguro123'
        }, follow_redirects=True)
        assert "Por favor ingresa un correo electrónico válido." in response.get_data(as_text=True)

def test_register_password_length(client):
    """
    Técnica: Análisis de Valores Límite (AVL) para longitud de contraseña.
    Límite mínimo requerido: 6 caracteres.
    - Caso Límite Inferior Inválido: 5 caracteres (debe fallar).
    - Caso Límite Mínimo Válido: 6 caracteres (debe pasar).
    """
    # AVL - Límite Inferior Inválido (5 caracteres)
    response_invalid = client.post('/register', data={
        'name': 'Estudiante AVL',
        'email': 'avl.cinco@test.com',
        'password': 'abcde'
    }, follow_redirects=True)
    assert "La contraseña debe tener al menos 6 caracteres." in response_invalid.get_data(as_text=True)

    # AVL - Límite Mínimo Válido (6 caracteres)
    response_valid = client.post('/register', data={
        'name': 'Estudiante AVL',
        'email': 'avl.seis@test.com',
        'password': 'abcdef'
    }, follow_redirects=True)
    assert "Registro exitoso. Por favor inicia sesión." in response_valid.get_data(as_text=True)

def test_register_duplicate_email(client):
    """
    PE - Clase de Equivalencia Inválida:
    Intentar registrar un correo que ya existe en la base de datos.
    """
    # Primer registro exitoso
    client.post('/register', data={
        'name': 'Usuario Unico',
        'email': 'duplicado@test.com',
        'password': 'password123'
    })
    
    # Segundo registro con el mismo correo
    response = client.post('/register', data={
        'name': 'Usuario Clon',
        'email': 'duplicado@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert "El correo electrónico ya se encuentra registrado." in response.get_data(as_text=True)

def test_login_success(client):
    """
    PE - Clase de Equivalencia Válida:
    Iniciar sesión con credenciales correctas.
    """
    # Registrar primero
    client.post('/register', data={
        'name': 'Usuario Login',
        'email': 'login.success@test.com',
        'password': 'password123'
    })
    
    # Intentar login
    response = client.post('/login', data={
        'email': 'login.success@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "¡Bienvenido de nuevo, Usuario Login!" in response.get_data(as_text=True)

def test_login_failed_credentials(client):
    """
    PE - Clase de Equivalencia Inválida:
    Iniciar sesión con correo inexistente o contraseña incorrecta.
    """
    response = client.post('/login', data={
        'email': 'no.existe@test.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert "Correo electrónico o contraseña incorrectos." in response.get_data(as_text=True)


# ==============================================================================
# PRUEBAS DE LISTADO Y BÚSQUEDA DE EVENTOS (Técnica: Partición de Equivalencia)
# ==============================================================================

def test_events_list_and_search(client):
    """
    Verifica que el listado muestre los eventos cargados en conftest.py
    y que el buscador filtre adecuadamente por palabras clave.
    """
    # Caso 1: Buscar sin filtros (debe mostrar Evento A y Evento C)
    response = client.get('/')
    html = response.get_data(as_text=True)
    assert "Evento A" in html
    assert "Evento C" in html

    # Caso 2: Búsqueda con coincidencias (PE Válido)
    response_search = client.get('/?q=Evento+A')
    html_search = response_search.get_data(as_text=True)
    assert "Evento A" in html_search
    assert "Evento C" not in html_search

    # Caso 3: Búsqueda sin coincidencias (PE Inválido)
    response_empty = client.get('/?q=Concierto+Inexistente')
    html_empty = response_empty.get_data(as_text=True)
    assert "No se encontraron eventos" in html_empty


# ==============================================================================
# PRUEBAS DE COMPRA DE ENTRADAS (Técnica: PE & Análisis de Valores Límite - AVL)
# ==============================================================================

def test_purchase_unauthenticated(client):
    """
    PE - Clase de Equivalencia Inválida:
    Intentar comprar entradas sin haber iniciado sesión. Debe redirigir a Login.
    """
    response = client.post('/purchase/1', data={'quantity': '2'}, follow_redirects=True)
    assert "Debes iniciar sesión para realizar una compra." in response.get_data(as_text=True)

def test_purchase_nonexistent_event(authenticated_client):
    """
    Manejo de eventos inexistentes:
    Intentar comprar entradas para un evento con ID 999 que no existe.
    """
    response = authenticated_client.post('/purchase/999', data={'quantity': '2'}, follow_redirects=True)
    assert "El evento seleccionado no existe." in response.get_data(as_text=True)

def test_purchase_avl_limits(authenticated_client):
    """
    Técnica: Análisis de Valores Límite (AVL) y PE aplicado a la compra.
    Para el Evento A (id: 1) tenemos un Stock disponible = 10.
    
    1. Límite Mínimo Inválido: Cantidad = 0 (debe fallar).
    2. Límite Mínimo Inválido: Cantidad = -1 (debe fallar).
    3. Límite Inferior Mínimo Válido: Cantidad = 1 (debe tener éxito).
    4. Límite Superior Máximo Válido: Cantidad = 9 (el stock quedó en 9 después de comprar 1. Debe tener éxito).
    5. Límite Superior Inválido (Exceso): Cantidad = 1 (ahora el stock es 0. Debe fallar por falta de stock).
    """
    # 1. AVL - Límite Mínimo Inválido: Cantidad = 0
    response_zero = authenticated_client.post('/purchase/1', data={'quantity': '0'}, follow_redirects=True)
    assert "La cantidad de entradas debe ser mayor a cero." in response_zero.get_data(as_text=True)

    # 2. AVL - Límite Mínimo Inválido (PE negativo): Cantidad = -1
    response_neg = authenticated_client.post('/purchase/1', data={'quantity': '-1'}, follow_redirects=True)
    assert "La cantidad de entradas debe ser mayor a cero." in response_neg.get_data(as_text=True)

    # 3. AVL - Límite Inferior Mínimo Válido: Cantidad = 1 (Stock: 10 -> Nuevo Stock: 9)
    response_min_valid = authenticated_client.post('/purchase/1', data={'quantity': '1'}, follow_redirects=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in response_min_valid.get_data(as_text=True)

    # 4. AVL - Límite Superior Máximo Válido: Cantidad = 9 (Stock: 9 -> Nuevo Stock: 0)
    response_max_valid = authenticated_client.post('/purchase/1', data={'quantity': '9'}, follow_redirects=True)
    assert "¡Compra realizada con éxito! Disfruta del evento." in response_max_valid.get_data(as_text=True)

    # 5. AVL - Límite Superior Inválido (Exceso): Intentar comprar 1 entrada cuando el stock es 0
    response_excess = authenticated_client.post('/purchase/1', data={'quantity': '1'}, follow_redirects=True)
    assert "No es posible comprar 1 entradas. El stock disponible es de 0." in response_excess.get_data(as_text=True)

def test_purchase_insufficient_stock_initial(authenticated_client):
    """
    PE - Clase de Equivalencia Inválida:
    Intentar comprar entradas para un evento que tiene stock inicial = 0 (Evento B, id: 2).
    """
    response = authenticated_client.post('/purchase/2', data={'quantity': '1'}, follow_redirects=True)
    assert "No es posible comprar 1 entradas. El stock disponible es de 0." in response.get_data(as_text=True)

def test_tickets_history_isolated(authenticated_client):
    """
    Verifica que las entradas compradas por el usuario actual
    aparezcan correctamente en su vista de historial (/tickets).
    """
    # Realizar una compra exitosa
    authenticated_client.post('/purchase/3', data={'quantity': '2'})
    
    # Visitar historial
    response = authenticated_client.get('/tickets')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Evento C" in html
    assert "Cantidad" in html
    # 2 entradas a S/ 30.00 c/u = S/ 60.00
    assert "60.00" in html
