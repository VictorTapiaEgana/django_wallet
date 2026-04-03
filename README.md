# DjangoWallet 💳

Sistema de gestión de billetera digital y transacciones bancarias desarrollado con **Django**. Permite a los usuarios administrar múltiples tipos de cuentas (bancarias, digitales y criptomonedas) y realizar transferencias entre ellas.

Version: 1.0.0

**En producción:** 
   https://django-wallet-r64y.onrender.com

**Usuario:** victor
**Contraseña:** 12345

## 🚀 Requisitos e Instalación

### Pre-requisitos
* Python 3.10+
* Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/VictorTapiaEgana/django_wallet
   cd DjangoWallet
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Realizar migraciones:**
   ```bash
   python manage.py migrate
   ```

5. **Crear un superusuario (Administrador):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación:**
   ```bash
   http://127.0.0.1:8000/
   ```
8. **Acceder con las credenciales:**
   ```
   usuario: victor
   contraseña: 12345
   ```


---



## 📦 Dependencias Principales
El proyecto utiliza las siguientes librerías principales:
* **Django**: Framework web principal.
* **SQLite3**: Base de datos predeterminada para desarrollo.
* (Otras dependencias detalladas en `requirements.txt`)

---

## 🏛️ Estructura de Clases (Modelos)

El sistema se basa en tres modelos principales definidos en `gestion/models.py`:

### 1. Cliente
Extiende la funcionalidad del usuario de Django.
* **Campos:** `user` (OneToOne), `direccion`, `estado` (Activa, Bloqueada, Cerrada), `fecha_creacion`.
* **Relación:** Cada usuario del sistema tiene un perfil de cliente asociado automáticamente.

### 2. Cuenta
Representa una cuenta financiera del cliente.
* **Tipos soportados:** BCI, Santander, Banco Estado, Chile, Mercado Pago, MACH, Tenpo, BTC, ETH, USDT.
* **Campos:** `cliente`, `tipo`, `numero` (único), `saldo_disponible`, `activa` (booleano).

### 3. Transaccion
Registra los movimientos de dinero.
* **Tipos:** Depósito, Retiro, Transferencia.
* **Campos:** `cuenta_origen`, `cuenta_destino`, `tipo`, `monto`, `descripcion`, `fecha_transaccion`.
* **Lógica:** Incluye validaciones para evitar transferencias sin destino, saldos insuficientes y transferencias a la misma cuenta.

---

## 🛠️ Uso General

### Dashboard
Al iniciar sesión, el usuario accede a un resumen de:
* Saldo total consolidado de todas sus cuentas.
* Listado de cuentas activas.
* Historial de la última transacción realizada o recibida.

### Gestión de Cuentas
* **Agregar Cuenta:** Permite crear nuevas cuentas seleccionando el tipo y un saldo inicial.
* **Administrar:** El usuario puede ver el detalle de sus cuentas, editarlas (cambiar estado o saldo) o eliminarlas.

### Transferencias
* Permite enviar dinero indicando la cuenta de origen (del usuario) y el número de cuenta de destino.
* El sistema valida automáticamente si el número de cuenta existe y si hay saldo suficiente.
* Se utiliza `transaction.atomic()` para asegurar la integridad de los datos durante el movimiento de fondos.

### Historial de Transacciones
* Vista detallada de todos los movimientos (enviados y recibidos) asociados al usuario actual.

---

## 🧪 Tests Automatizados

### Ejecutar Tests
```bash
python manage.py test
```

### Estructura de Tests
El proyecto incluye tests completos en `gestion/tests.py`:

#### GestionViewsTest
Tests de renderizado y funcionalidad de vistas:
* **test_login_view_render**: Verifica que la vista de login carga correctamente
* **test_login_view_post**: Valida autenticación exitosa
* **test_dashboard_view_render**: Comprueba renderizado del dashboard con datos del usuario
* **test_agregar_cuenta_view_render/post**: Test de creación de cuentas
* **test_transferencias_view_render/post**: Validación de transferencias entre cuentas
* **test_transacciones_view_render**: Historial de movimientos

#### GestionModelsTest
Tests de creación y validación de modelos:
* **test_cliente_creation**: Creación automática de cliente vía signals
* **test_cuenta_creation**: Creación de cuentas con campos validados
* **test_transaccion_creation_deposito/transferencia**: Registro de transacciones
* **test_transaccion_validation_misma_cuenta**: Evita transferencias a la misma cuenta
* **test_transaccion_validation_transferencia_sin_destino**: Requiere cuenta destino

#### GestionIntegrationTest
Tests de flujos completos:
* **test_flujo_completo_crear_cuenta_y_transferir**: Crear cuentas → Transferir → Validar saldos

### Implementación Técnica
* **Signals Django**: Cliente se crea automáticamente al crear User (`post_save`)
* **Transacciones atómicas**: `transaction.atomic()` garantiza integridad en transferencias
* **Validaciones modelo**: Métodos `clean()` validan reglas de negocio
* **Tipos de datos**: 
  * `DecimalField` para montos de transacciones (precisión decimal)
  * `IntegerField` para saldos de cuentas (valores enteros)

### Cobertura de Tests
| Módulo | Tests | Descripción |
|--------|-------|-------------|
| Views | 9 | Renderizado, autenticación, CRUD, transferencias |
| Models | 7 | Creación, validaciones, relaciones |
| Integration | 1 | Flujo completo de usuario |

### Comandos útiles
```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests específicos
python manage.py test gestion.tests.GestionViewsTest
python manage.py test gestion.tests.GestionModelsTest

# Ejecutar un test individual
python manage.py test gestion.tests.GestionViewsTest.test_dashboard_view_render
```
