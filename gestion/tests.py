from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction
from decimal import Decimal
from gestion.models import Cliente, Cuenta, Transaccion


class GestionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # El Cliente se crea automáticamente por el signal
        self.cliente = self.user.cliente
        self.cuenta = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000
        )

    def test_login_view_render(self):
        response = self.client.get(reverse('gestion:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/login.html')

    def test_login_view_post(self):
        response = self.client.post(reverse('gestion:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_view_render(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gestion:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/dashboard.html')
        self.assertContains(response, 'Saldo Total General')

    def test_agregar_cuenta_view_render(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gestion:agregar_cuenta'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/agregar_cuenta.html')

    def test_agregar_cuenta_view_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('gestion:agregar_cuenta'), {
            'tipo': 'SANT',
            'saldo': '500'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cuenta.objects.filter(tipo='SANT').exists())

    def test_administrar_cuentas_view_render(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gestion:administrar_cuentas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/administrar_cuentas.html')
        self.assertContains(response, 'BCI-123456789012')

    def test_transferencias_view_render(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gestion:transferencias'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/transferencias.html')

    def test_transferencias_view_post(self):
        self.client.login(username='testuser', password='testpass123')
        
        cuenta_destino = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='ESTD',
            numero='ESTD-987654321098',
            saldo_disponible=500
        )
        
        response = self.client.post(reverse('gestion:transferencias'), {
            'cuenta_origen': str(self.cuenta.id),
            'numero_destino': 'ESTD-987654321098',
            'monto': '100',
            'descripcion': 'Transferencia de prueba'
        })
        
        self.assertEqual(response.status_code, 302)
        self.cuenta.refresh_from_db()
        cuenta_destino.refresh_from_db()
        
        self.assertEqual(self.cuenta.saldo_disponible, 900)
        self.assertEqual(cuenta_destino.saldo_disponible, 600)
        self.assertTrue(Transaccion.objects.filter(tipo='transferencia').exists())

    def test_transacciones_view_render(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gestion:transacciones'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion/transacciones.html')


class GestionModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # El Cliente se crea automáticamente por el signal
        self.cliente = self.user.cliente

    def test_cliente_creation(self):
        user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        # El Cliente se crea automáticamente por el signal
        cliente = user.cliente
        
        # Actualizar los datos del cliente
        cliente.direccion = 'Calle Test 123'
        cliente.estado = 'activa'
        cliente.save()
        
        self.assertEqual(cliente.user.username, 'testuser2')
        self.assertEqual(cliente.direccion, 'Calle Test 123')
        self.assertEqual(cliente.estado, 'activa')
        self.assertTrue(cliente.fecha_creacion)

    def test_cuenta_creation(self):
        cuenta = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000,
            activa=True
        )
        
        self.assertEqual(cuenta.cliente, self.cliente)
        self.assertEqual(cuenta.tipo, 'BCI')
        self.assertEqual(cuenta.numero, 'BCI-123456789012')
        self.assertEqual(cuenta.saldo_disponible, 1000)
        self.assertTrue(cuenta.activa)
        self.assertTrue(cuenta.fecha_creacion)

    def test_transaccion_creation_deposito(self):
        cuenta = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000
        )
        
        transaccion = Transaccion.objects.create(
            cuenta_origen=cuenta,
            tipo='deposito',
            monto=Decimal('500.00'),
            descripcion='Depósito de prueba'
        )
        
        self.assertEqual(transaccion.cuenta_origen, cuenta)
        self.assertEqual(transaccion.tipo, 'deposito')
        self.assertEqual(transaccion.monto, Decimal('500.00'))
        self.assertEqual(transaccion.descripcion, 'Depósito de prueba')
        self.assertTrue(transaccion.fecha_transaccion)

    def test_transaccion_creation_transferencia(self):
        cuenta_origen = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000
        )
        
        cuenta_destino = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='SANT',
            numero='SANT-987654321098',
            saldo_disponible=500
        )
        
        transaccion = Transaccion.objects.create(
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            tipo='transferencia',
            monto=Decimal('200.00'),
            descripcion='Transferencia de prueba'
        )
        
        self.assertEqual(transaccion.cuenta_origen, cuenta_origen)
        self.assertEqual(transaccion.cuenta_destino, cuenta_destino)
        self.assertEqual(transaccion.tipo, 'transferencia')
        self.assertEqual(transaccion.monto, Decimal('200.00'))

    def test_transaccion_validation_misma_cuenta(self):
        cuenta = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000
        )
        
        transaccion = Transaccion(
            cuenta_origen=cuenta,
            cuenta_destino=cuenta,
            tipo='transferencia',
            monto=Decimal('100.00')
        )
        
        with self.assertRaises(Exception):
            transaccion.clean()

    def test_transaccion_validation_transferencia_sin_destino(self):
        cuenta = Cuenta.objects.create(
            cliente=self.cliente,
            tipo='BCI',
            numero='BCI-123456789012',
            saldo_disponible=1000
        )
        
        transaccion = Transaccion(
            cuenta_origen=cuenta,
            tipo='transferencia',
            monto=Decimal('100.00')
        )
        
        with self.assertRaises(Exception):
            transaccion.clean()


class GestionIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # El Cliente se crea automáticamente por el signal
        self.cliente = self.user.cliente

    def test_flujo_completo_crear_cuenta_y_transferir(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('gestion:agregar_cuenta'), {
            'tipo': 'BCI',
            'saldo': '1000'
        })
        self.assertEqual(response.status_code, 302)
        
        cuenta1 = Cuenta.objects.get(tipo='BCI')
        
        response = self.client.post(reverse('gestion:agregar_cuenta'), {
            'tipo': 'SANT',
            'saldo': '500'
        })
        self.assertEqual(response.status_code, 302)
        
        cuenta2 = Cuenta.objects.get(tipo='SANT')
        
        response = self.client.post(reverse('gestion:transferencias'), {
            'cuenta_origen': str(cuenta1.id),
            'numero_destino': cuenta2.numero,
            'monto': '200.00',
            'descripcion': 'Transferencia de prueba'
        })
        self.assertEqual(response.status_code, 302)
        
        cuenta1.refresh_from_db()
        cuenta2.refresh_from_db()
        
        self.assertEqual(cuenta1.saldo_disponible, 800)
        self.assertEqual(cuenta2.saldo_disponible, 700)
        
        transacciones = Transaccion.objects.filter(
            cuenta_origen=cuenta1,
            cuenta_destino=cuenta2
        )
        self.assertEqual(transacciones.count(), 1)
        self.assertEqual(transacciones.first().monto, Decimal('200.00'))
