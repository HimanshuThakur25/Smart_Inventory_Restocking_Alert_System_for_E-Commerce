import csv
from django.core.management.base import BaseCommand
from inventory.models import Product, Inventory, Sales
from datetime import datetime
from django.db import transaction

class Command(BaseCommand):
    help = 'Load data from retail_store_inventory.csv into the database'

    def handle(self, *args, **kwargs):
        # file_path = r'C:\Users\hp\OneDrive\Desktop\VS_Code\smart_inventory\retail_store_inventory.csv'
        file_path = r'C:\Users\hp\OneDrive\Desktop\VS_Code\smart_inventory\retail_store_inventory.csv'

        products_to_create = []
        inventories_to_create = []
        sales_to_create = []

        self.stdout.write("Reading and processing CSV file...")
        
        row_count = 0
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row_count += 1

                product, created = Product.objects.get_or_create(
                    product_id=row['Product ID'],
                    defaults={
                        'name': row['Category'],
                        'category': row['Category'],
                        'price': row['Price'],
                        'competitor_pricing': row['Competitor Pricing']
                    }
                )
                if created:
                    products_to_create.append(product)

                inventories_to_create.append(Inventory(
                    product=product,
                    inventory_level=row['Inventory Level'],
                    restock_threshold=10
                ))

                sales_to_create.append(Sales(
                    product=product,
                    date=datetime.strptime(row['Date'], '%d-%m-%Y'),
                    units_sold=row['Units Sold'],
                    discount=row['Discount']
                ))

                if row_count % 1000 == 0:
                    self.stdout.write(f"Processed {row_count} rows...")

        self.stdout.write("Bulk inserting into the database...")

        with transaction.atomic():
            Inventory.objects.bulk_create(inventories_to_create, ignore_conflicts=True)
            Sales.objects.bulk_create(sales_to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Data loaded successfully! Total rows processed: {row_count}"))
