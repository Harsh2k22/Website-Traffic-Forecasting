from io import StringIO
from flask import Flask, render_template, request, jsonify
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error

app = Flask(__name__)


def forecast_traffic(data):
    # Train ARIMA model
    model = ARIMA(data, order=(5, 1, 0))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=45)

    return forecast.tolist()


# def calculate_mape(actual, forecast):
#     return mean_absolute_percentage_error(actual, forecast)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/load', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        csv_content = file.stream.read().decode('utf-8')
        csv_file = StringIO(csv_content)
        csv_string = csv_file.getvalue()
        data = pd.read_csv(StringIO(csv_string))
        if 'Page.Loads' in data.columns:
            forecast = forecast_traffic(data['Page.Loads'])
            actual = data['Page.Loads'].values[-45:]  # Last 45 days for comparison
            last_date = pd.to_datetime(data['Date']).max()
            start_date = last_date + pd.Timedelta(days=1)
            forecast_dates = pd.date_range(start=start_date, periods=40)
            print("Forecast Dates:", forecast_dates)
            print("Forecast:", forecast)
            # mape = calculate_mape(actual, forecast)
            # print("MAPE:", mape)
            if forecast:
                forecast_data = [{'Date': str(date), 'Forecasted Traffic': int(forecast[i])} for i, date in
                                 enumerate(forecast_dates)]
                return jsonify({'forecast_data': forecast_data})
            else:
                return jsonify({'error': 'Failed to generate forecast.'}), 505
        else:
            return jsonify({'error': 'Column "Page.Loads" not found in the uploaded file.'}), 505
    else:
        return jsonify({'error': 'No file uploaded.'}), 505


if __name__ == '__main__':
    app.run(debug=True)
