from django.contrib import admin
from api.models import Order, OrderItem, Product , User

# Inline for OrderItem inside Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # show one empty row by default

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("order_id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "order_id")


# Admin for Product (separate from Order)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "in_stock")
    search_fields = ("name",)
    list_filter = ("stock",)
    ordering = ("-price",)


# Register models
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(User)
