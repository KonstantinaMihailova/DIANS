import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


sequence_length = 60
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


def forecast_next_n_days(model, data, n, scaler):
    last_sequence = data[-sequence_length:]
    forecasts = []
    for _ in range(n):
        reshaped_sequence = last_sequence.reshape(1, -1)
        prediction = model.predict(reshaped_sequence)
        forecasts.append(prediction[0])

        prediction_reshaped = np.array([prediction[0]])
        last_sequence = np.vstack((last_sequence[1:], prediction_reshaped))
    return scaler.inverse_transform(np.array(forecasts).reshape(-1, 1))


csv_path = sys.argv[1]
output_path = sys.argv[2]
issuer = sys.argv[3]


data = pd.read_csv(csv_path, encoding='utf-8')
data['Date'] = pd.to_datetime(data['Date'], format='%d.%m.%Y')


issuer_data = data[data['Issuer'] == issuer]
issuer_data = issuer_data.sort_values(by='Date')
issuer_data['Close'] = issuer_data['Close'].str.replace(',', '').astype(float)


scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(issuer_data[['Close']])


X, y = create_sequences(scaled_data, sequence_length)
X = X.reshape(X.shape[0], X.shape[1])


model = LinearRegression()
model.fit(X, y)


predictions = model.predict(X)
predicted_prices = scaler.inverse_transform(predictions.reshape(-1, 1))


forecasted_prices = forecast_next_n_days(model, scaled_data, 30, scaler)


future_dates = pd.date_range(issuer_data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=30)


plt.figure(figsize=(14, 5))
plt.plot(issuer_data['Date'][-len(predicted_prices):], issuer_data['Close'][-len(predicted_prices):], color='blue', label='Actual Prices')
plt.plot(issuer_data['Date'][-len(predicted_prices):], predicted_prices, color='red', label='Predicted Prices')


plt.plot(future_dates, forecasted_prices, color='green', label='Forecasted Prices')

plt.title(f'Actual vs Predicted and Forecasted Stock Prices for {issuer}')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()

issuer_directory = f"{output_path}/{issuer}_lstm"
if not os.path.exists(issuer_directory):
    os.makedirs(issuer_directory)


graph_path = f"{issuer_directory}/predicted_vs_actual.png"
plt.savefig(graph_path)


web_graph_path = f"/{issuer}_lstm/predicted_vs_actual.png"
print(web_graph_path)


forecast_csv_path = f"{issuer}_lstm/forecasted_prices.csv"


print(forecast_csv_path)

sys.stdout.flush()


