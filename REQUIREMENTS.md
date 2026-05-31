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

### 3.2. Validación de Inicio de Sesión / Autenticación (RF-02)

#### Tabla de Partición de Equivalencia (PE) - Inicio de Sesión

| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| PE-LOG-01 | Credenciales correctas | Válida | Email: "juan@test.com", Contraseña: "password123" | Inicio de sesión exitoso |
| PE-LOG-02 | Correo no registrado | Inválida | Email: "noexiste@test.com" | Error: "Credenciales inválidas" |
| PE-LOG-03 | Contraseña incorrecta | Inválida | Email válido, contraseña incorrecta | Error: "Credenciales inválidas" |
| PE-LOG-04 | Campos vacíos | Inválida | Email: "", Contraseña: "" | Error: "Todos los campos son obligatorios" |

#### Tabla de Análisis de Valores Límite (AVL) - Inicio de Sesión

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| AVL-LOG-01 | Email vacío | Inválido | Email: "" | Error de validación |
| AVL-LOG-02 | Contraseña vacía | Inválido | Contraseña: "" | Error de validación |
| AVL-LOG-03 | Campos completos | Válido | Email y contraseña válidos | Inicio de sesión exitoso |

---

### 3.3. Validación de Listado de Eventos (RF-03)

#### Tabla de Partición de Equivalencia (PE) - Listado de Eventos

| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| PE-EVE-01 | Existen eventos registrados | Válida | Base de datos con eventos | Se muestra el catálogo |
| PE-EVE-02 | No existen eventos registrados | Válida | Tabla events vacía | Se muestra mensaje informativo |
| PE-EVE-03 | Evento con stock disponible | Válida | Stock > 0 | Evento disponible |
| PE-EVE-04 | Evento agotado | Válida | Stock = 0 | Evento marcado como agotado |

#### Tabla de Análisis de Valores Límite (AVL) - Stock

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| AVL-EVE-01 | Stock = 0 | Válido | Stock: 0 | Evento agotado |
| AVL-EVE-02 | Stock = 1 | Válido | Stock: 1 | Últimas entradas |
| AVL-EVE-03 | Stock > 1 | Válido | Stock: 10 | Disponible normalmente |

---

### 3.4. Validación de Búsqueda de Eventos (RF-04)

#### Tabla de Partición de Equivalencia (PE) - Búsqueda de Eventos

| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| PE-BUS-01 | Búsqueda por título existente | Válida | "Rock" | Retorna eventos coincidentes |
| PE-BUS-02 | Búsqueda por ubicación existente | Válida | "Lima" | Retorna eventos coincidentes |
| PE-BUS-03 | Búsqueda sin coincidencias | Válida | "EventoXYZ" | Sin resultados |
| PE-BUS-04 | Campo vacío | Válida | "" | Muestra todos los eventos |

#### Tabla de Análisis de Valores Límite (AVL) - Campo de Búsqueda

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| AVL-BUS-01 | Longitud 0 | Válido | "" | Mostrar todos los eventos |
| AVL-BUS-02 | Longitud 1 | Válido | "R" | Buscar coincidencias |
| AVL-BUS-03 | Longitud normal | Válido | "Rock" | Buscar coincidencias |

---

### 3.6. Validación de Control de Transacciones (RF-06)

#### Tabla de Partición de Equivalencia (PE) - Control de Transacciones

| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| PE-TRA-01 | Compra válida | Válida | Stock: 10, Compra: 2 | Compra registrada y stock actualizado |
| PE-TRA-02 | Error durante la transacción | Inválida | Falla de inserción | ROLLBACK ejecutado |
| PE-TRA-03 | Compra consume todo el stock | Válida | Stock: 5, Compra: 5 | Stock final = 0 |
| PE-TRA-04 | Compra simultánea excede stock | Inválida | Dos compras concurrentes | Se evita sobreventa |

#### Tabla de Análisis de Valores Límite (AVL) - Stock Posterior

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| AVL-TRA-01 | Stock final = 0 | Válido | Stock: 1, Compra: 1 | Compra exitosa |
| AVL-TRA-02 | Stock negativo | Inválido | Stock: 1, Compra: 2 | Compra rechazada |
| AVL-TRA-03 | Stock positivo | Válido | Stock: 10, Compra: 4 | Stock final = 6 |

---

### 3.7. Validación de Historial de Entradas (RF-07)

#### Tabla de Partición de Equivalencia (PE) - Historial de Entradas

| ID Clase | Descripción de la Clase | Tipo | Datos de Prueba Representativos | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| PE-HIS-01 | Usuario con compras | Válida | Usuario con registros en purchases | Mostrar historial |
| PE-HIS-02 | Usuario sin compras | Válida | Usuario sin registros | Mostrar mensaje informativo |
| PE-HIS-03 | Usuario no autenticado | Inválida | Sin sesión activa | Redirección al login |
| PE-HIS-04 | Acceso a compras ajenas | Inválida | Intento de ver compras de otro usuario | Acceso denegado |

#### Tabla de Análisis de Valores Límite (AVL) - Cantidad de Compras

| ID Prueba | Valor Límite Evaluado | Tipo | Datos de Prueba | Resultado Esperado |
| :--- | :--- | :--- | :--- | :--- |
| AVL-HIS-01 | 0 compras | Válido | Sin compras registradas | Historial vacío |
| AVL-HIS-02 | 1 compra | Válido | Una compra registrada | Mostrar una entrada |
| AVL-HIS-03 | Varias compras | Válido | Cinco compras registradas | Mostrar todas las entradas |
