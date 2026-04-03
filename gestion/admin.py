from django.contrib import admin
from .models import Cliente, Cuenta, Transferencia

# Register your models here.

admin.site.site_header = "DjangoWallet Admin"
admin.site.site_title = "DjangoWallet Admin Portal"
admin.site.index_title = "Welcome to DjangoWallet Admin Portal"


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('remitente', 'destinatario', 'monto', 'fecha') # Columnas que verás
    list_filter = ('fecha',) # Filtro lateral por fecha
    search_fields = ('remitente__usuario__username', 'destinatario__usuario__username')