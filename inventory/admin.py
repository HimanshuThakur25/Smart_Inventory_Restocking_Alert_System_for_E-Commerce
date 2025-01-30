from django.contrib import admin
from .models import Product, Inventory, Sales
from django.core.mail import send_mail
from django.conf import settings

# Customizing the Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_id', 'category', 'price', 'competitor_pricing')
    search_fields = ('name', 'product_id')
    list_filter = ('category',)

# Customizing the Inventory Admin
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'inventory_level', 'restock_threshold', 'needs_restocking', 'predict_restocking_time')
    search_fields = ('product__name',)
    list_filter = ('inventory_level',)

    # Show restocking status as a boolean field
    def needs_restocking(self, obj):
        return obj.needs_restocking()

    needs_restocking.boolean = True
    needs_restocking.short_description = 'Restocking Required'

    # Show the predicted restocking time
    def predict_restocking_time(self, obj):
        restock_time = obj.predict_restocking_time()
        return restock_time if restock_time else "No Prediction"

    predict_restocking_time.short_description = 'Predicted Restock Time'

    # Custom action to send restocking alert via email
    def send_restocking_alert(self, request, queryset):
        for inventory in queryset:
            restock_time = inventory.predict_restocking_time()
            if restock_time:
                send_mail(
                    subject=f'Restock Alert: {inventory.product.name}',
                    message=f'The product {inventory.product.name} will run out of stock by {restock_time}. Please restock it.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['admin_email@example.com'],  # Replace with admin email
                )
                self.message_user(request, f'Restocking alert sent for {inventory.product.name}')
            else:
                self.message_user(request, f'No restocking needed for {inventory.product.name}')
    
    send_restocking_alert.short_description = 'Send Restocking Alert via Email'
    
    actions = [send_restocking_alert]

# Customizing the Sales Admin
class SalesAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'units_sold', 'discount')
    search_fields = ('product__name',)
    list_filter = ('date',)

# Registering the models with their custom admin views
admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Sales, SalesAdmin)
