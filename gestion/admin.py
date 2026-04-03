from django.contrib import admin
from .models import Cliente, Cuenta, Transaccion

# Register your models here.

admin.site.site_header = "DjangoWallet Admin"
admin.site.site_title = "DjangoWallet Admin Portal"
admin.site.index_title = "Welcome to DjangoWallet Admin Portal"

admin.site.register(Cliente)
admin.site.register(Cuenta)

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('cuenta_origen', 'cuenta_destino', 'monto', 'fecha') # Columnas que verás
    list_filter = ('fecha',) # Filtro lateral por fecha
    search_fields = ('cuenta_origen__numero', 'cuenta_destino__numero')