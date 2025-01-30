from django.shortcuts import render
from inventory.models import Inventory

def test_inventory(request):
    inventory_data = []
    inventories = Inventory.objects.all()

    for inventory_item in inventories:
        needs_restocking = inventory_item.needs_restocking()
        predicted_date = inventory_item.predict_restocking_time()
        inventory_data.append({
            'product': inventory_item.product.name,
            'needs_restocking': needs_restocking,
            'predicted_date': predicted_date,
        })

    return render(request, 'inventory/test_inventory.html', {'inventory_data': inventory_data})
