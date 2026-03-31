from django.db import models
from django.core.exceptions import ValidationError

class Cliente(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('bloqueada', 'Bloqueada'),
        ('cerrada', 'Cerrada'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"


class Cuenta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='cuentas'
    )
    numero = models.CharField(max_length=20, unique=True)    
    saldo_disponible = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cuenta {self.numero} - {self.cliente.nombre}"


class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('deposito', 'Depósito'),
        ('retiro', 'Retiro'),
        ('transferencia', 'Transferencia'),
    ]

    
    cuenta_origen = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name='transacciones_realizadas'
    )    
    
    cuenta_destino = models.ForeignKey(
        Cuenta,
        on_delete=models.PROTECT,
        related_name='transacciones_recibidas',
        null=True,
        blank=True
    )

    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    def clean(self):
        """Validaciones de lógica de negocio a nivel de modelo."""
        if self.tipo == 'transferencia' and not self.cuenta_destino:
            raise ValidationError("Una transferencia requiere una cuenta de destino.")
        
        if self.tipo == 'transferencia' and self.cuenta_origen == self.cuenta_destino:
            raise ValidationError("No puedes transferir a la misma cuenta de origen.")

        if self.tipo in ['retiro', 'transferencia'] and self.cuenta_origen.saldo < self.monto:
            raise ValidationError("Saldo insuficiente para realizar esta operación.")

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.monto} ({self.fecha_transaccion.strftime('%d/%m/%Y')})"