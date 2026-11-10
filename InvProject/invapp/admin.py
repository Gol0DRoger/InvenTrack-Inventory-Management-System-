from django.contrib import admin
from .models import Product, AuditLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'sku', 'price', 'quantity', 'supplier')
    search_fields = ('name', 'sku', 'supplier')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'product_name', 'username')
    list_filter = ('action', 'timestamp')
    search_fields = ('product_name', 'username', 'product_id')
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
