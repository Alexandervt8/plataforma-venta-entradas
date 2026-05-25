# Especificación de Requisitos y Plan de Pruebas de Caja Negra

Este documento detalla los requerimientos funcionales y no funcionales del MVP **Boletix - Plataforma de Venta de Entradas para Eventos**.

---

## 1. Requerimientos Funcionales (RF)

- **RF-01: Registro de Usuarios**: El sistema debe permitir a nuevos usuarios registrarse proporcionando nombre completo, correo electrónico y una contraseña segura.
- **RF-02: Inicio de Sesión / Autenticación**: El sistema debe permitir a los usuarios autenticarse con sus credenciales y mantener una sesión segura basada en cookies.
- **RF-03: Listado de Eventos**: El sistema debe mostrar un catálogo con todos los eventos disponibles, detallando el título, descripción, fecha, ubicación, precio de entrada y stock disponible.
- **RF-04: Búsqueda de Eventos**: El catálogo debe incluir un motor de búsqueda que filtre eventos según palabras clave contenidas en el título, descripción o ubicación.
- **RF-05: Compra de Entradas**: Un usuario autenticado debe poder comprar una cantidad específica de entradas para un evento seleccionado.
- **RF-06: Control de Transacciones**: Al confirmar una compra, el stock del evento debe reducirse de forma atómica y consistente, y la operación debe quedar registrada en el historial.
- **RF-07: Historial de Entradas (Mis Entradas)**: El usuario autenticado debe tener acceso a una sección donde visualice todas las entradas que ha comprado con sus respectivos montos pagados y códigos de transacción únicos.

---

## 2. Requerimientos No Funcionales (RNF)

- **RNF-01: Usabilidad e Interfaz**: La interfaz debe ser intuitiva, con un diseño estético moderno (tema oscuro premium, tipografías dinámicas, animaciones sutiles y diseño adaptable a móviles/escritorio).
- **RNF-02: Seguridad en Almacenamiento**: Las contraseñas no deben almacenarse en texto plano en la base de datos; se debe utilizar un algoritmo de hash seguro (ej. PBKDF2/SHA256 mediante Werkzeug).
- **RNF-03: Consistencia y Concurrencia**: El sistema debe controlar el acceso concurrente al stock de entradas mediante transacciones explícitas de base de datos (`BEGIN TRANSACTION / COMMIT / ROLLBACK`), evitando la sobreventa en caso de compras simultáneas.
- **RNF-04: Portabilidad y Simplicidad**: El sistema debe funcionar con tecnologías ligeras (Flask, SQLite) fáciles de instalar y comprender por estudiantes universitarios, sin necesidad de servidores externos complejos de base de datos.

---

## 3. Casos de Validación y Diseño de Pruebas de Caja Negra

A continuación se muestran las tablas de pruebas diseñadas para certificar las validaciones del sistema.

### 3.1. Validación de Registro de Usuarios

*Reglas de Negocio:*
- Los campos `nombre`, `email` y `password` no pueden estar vacíos.
- El campo `email` debe ser una dirección con formato de correo válido (ej. `nombre@dominio.com`).
- La contraseña debe tener una longitud mínima de 6 caracteres.

#### Tabla de Partición de Equivalencia (PE) - Registro
| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **PE-REG-01** | Datos válidos completos | Válida | Nombre: "Juan", Email: "juan@test.com", Contraseña: "password123" | Registro Exitoso |
| **PE-REG-02** | Algún campo obligatorio vacío | Inválida | Nombre: "", Email: "juan@test.com", Contraseña: "password123" | Error: "Todos los campos son obligatorios" |
| **PE-REG-03** | Correo electrónico con formato inválido | Inválida | Nombre: "Juan", Email: "juan.sin.arroba", Contraseña: "password123" | Error: "Por favor ingresa un correo electrónico válido" |
| **PE-REG-04** | Correo electrónico ya existente | Inválida | Nombre: "Duplicado", Email: "juan@test.com", Contraseña: "password123" | Error: "El correo electrónico ya se encuentra registrado" |

#### Tabla de Análisis de Valores Límite (AVL) - Longitud de Contraseña
*Límite de corte:* $N = 6$ caracteres.
- Valores inválidos: $< 6$ caracteres.
- Valores válidos: $\ge 6$ caracteres.

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba (Contraseña) | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **AVL-REG-01** | Límite inferior inválido ($N - 1$) | Inválido | "abcde" (5 caracteres) | Error: "La contraseña debe tener al menos 6 caracteres" |
| **AVL-REG-02** | Límite mínimo válido ($N$) | Válido | "abcdef" (6 caracteres) | Registro Exitoso |
| **AVL-REG-03** | Valor nominal seguro ($N + 4$) | Válido | "seguro12345" (11 caracteres) | Registro Exitoso |

---

### 3.2. Validación de Compra de Entradas

*Reglas de Negocio:*
- La cantidad de entradas debe ser un número entero.
- La cantidad debe ser estrictamente mayor que cero ($Q > 0$).
- La cantidad no debe exceder el stock actual del evento ($Q \le Stock$).
- El evento a comprar debe existir en el sistema.

#### Tabla de Partición de Equivalencia (PE) - Compra de Entradas
| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **PE-COM-01** | Cantidad permitida dentro de stock | Válida | Evento con Stock: 10, Cantidad: 3 | Compra Exitosa (Stock final = 7) |
| **PE-COM-02** | Cantidad no numérica o vacía | Inválida | Evento con Stock: 10, Cantidad: "" o "dos" | Error: "La cantidad de entradas debe ser un número entero válido" |
| **PE-COM-03** | Evento inexistente en catálogo | Inválida | ID Evento: 999, Cantidad: 1 | Error: "El evento seleccionado no existe" |

#### Tabla de Análisis de Valores Límite (AVL) - Cantidad y Stock
*Supongamos un Evento de prueba con un **Stock disponible = 10**.*
- Límites inferiores de cantidad: Cantidad mínima permitida = 1.
- Límites superiores de stock: Cantidad máxima permitida = 10.

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| **AVL-COM-01** | Límite inferior inválido ($Q = 0$) | Inválido | Cantidad: 0 | Error: "La cantidad de entradas debe ser mayor a cero" |
| **AVL-COM-02** | Límite inferior inválido negativo ($Q < 0$) | Inválido | Cantidad: -1 | Error: "La cantidad de entradas debe ser mayor a cero" |
| **AVL-COM-03** | Límite inferior mínimo válido ($Q = 1$) | Válido | Cantidad: 1 | Compra Exitosa (Stock reduce a 9) |
| **AVL-COM-04** | Límite superior máximo válido ($Q = 9$, stock actual) | Válido | Cantidad: 9 | Compra Exitosa (Stock reduce a 0) |
| **AVL-COM-05** | Límite superior inválido por exceso ($Q = 1$, stock actual 0) | Inválido | Cantidad: 1 | Error: "No es posible comprar... El stock disponible es de 0" |
