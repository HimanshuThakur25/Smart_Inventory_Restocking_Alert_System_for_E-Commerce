from prophet import Prophet
import pandas as pd
from inventory.models import Sales
import matplotlib.pyplot as plt


def prepare_sales_data():
    sales_data = Sales.objects.all().values('product__name', 'date', 'units_sold')

    df = pd.DataFrame(sales_data)
    df.rename(columns={'date': 'ds', 'units_sold': 'y'}, inplace=True)

    return df


def forecast_sales(df):
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(df, periods=30)

    forecast = model.predict(future)

    model.plot(forecast)
    plt.show()

    return forecast

def run_forecasting():
    df = prepare_sales_data()
    forecast = forecast_sales(df)

    return forecast

if __name__ == '__main__':
    forecast = run_forecasting()
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
