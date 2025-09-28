from django.contrib import admin
from api.models import Order, OrderItem #registering the models in admin panel

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
class OrderAdmin(admin.ModelAdmin):
    #using inlines so admin use can add order items dynamically
    inlines=[
        OrderItemInline

    ]
admin.site.register(Order, OrderAdmin)