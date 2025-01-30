from django.db import models
from prophet import Prophet
import pandas as pd
from datetime import timedelta
import logging
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings

# Suppress logging
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)
# Create your models here.
class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    competitor_pricing = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory_level = models.PositiveIntegerField()
    restock_threshold = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.product.name} Inventory"

    # def needs_restocking(self):
    #     return self.inventory_level <= self.restock_threshold

    def needs_restocking(self):
        if self.inventory_level <= self.restock_threshold:
            self.send_restock_alert()
            return True
        return False

    def send_restock_alert(self):
        subject = f"Restock Alert: {self.product.name}"
        message = (
            f"Dear Admin,\n\n"
            f"The inventory level for the product '{self.product.name}' has fallen below the restock threshold.\n"
            f"Current Inventory Level: {self.inventory_level}\n"
            f"Restock Threshold: {self.restock_threshold}\n\n"
            f"Please restock this item as soon as possible.\n\n"
            f"Best regards,\n"
            f"Smart Inventory System"
        )
        recipient_list = ['himanshu25t@gmail.com']  # Replace with the admin's email
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

    # def predict_restocking_time(self):
    #     # Prepare sales data for the product
    #     sales_data = Sales.objects.filter(product=self.product).values('date', 'units_sold')
    #     df = pd.DataFrame(sales_data)
    #     df.rename(columns={'date': 'ds', 'units_sold': 'y'}, inplace=True)

    #     # Check if there is enough data to make a prediction
    #     if df.empty or len(df) < 2:
    #         return None  # Not enough data for prediction

    #     # Train the model
    #     model = Prophet()
    #     model.fit(df)

    #     # Predict future sales
    #     future = model.make_future_dataframe(periods=30)
    #     forecast = model.predict(future)

    #     # Predict when stock will run out
    #     current_stock = self.inventory_level
    #     for _, row in forecast.iterrows():
    #         current_stock -= row['yhat']
    #         if current_stock <= self.restock_threshold:
    #             return row['ds']  # Return the date when restocking is needed
    #     return None

    def predict_restocking_time(self):
        from datetime import timedelta
        from .models import RestockPrediction

        try:
            cached_prediction = RestockPrediction.objects.get(product=self.product)
            if cached_prediction.last_updated >= now() - timedelta(hours=24):
                return cached_prediction.predicted_restock_date
        except RestockPrediction.DoesNotExist:
            cached_prediction = RestockPrediction(product=self.product)

        sales_data = Sales.objects.filter(product=self.product).values('date', 'units_sold')
        df = pd.DataFrame(sales_data)
        if df.empty:
            return None

        df = df.sort_values(by='date').tail(500)
        df.rename(columns={'date': 'ds', 'units_sold': 'y'}, inplace=True)

        model = Prophet()
        model.fit(df)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        current_stock = self.inventory_level
        predicted_date = None
        for index, row in forecast.iterrows():
            current_stock -= row['yhat']
            if current_stock <= self.restock_threshold:
                predicted_date = row['ds']
                break

        cached_prediction.predicted_restock_date = predicted_date
        cached_prediction.save()

        return predicted_date






class Sales(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    units_sold = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Sales for {self.product.name} on {self.date}"
    

class RestockPrediction(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    predicted_restock_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Restock Prediction for {self.product.name}"

