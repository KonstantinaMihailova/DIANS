import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

start_time = time.time()




url = "https://www.mse.mk/mk/stats/symbolhistory/MPT/?FromDate=01.01.2023"
response = requests.get(url)
raw_html = response.text
soup = BeautifulSoup(raw_html, "html.parser")
select = soup.find("select", {"id": "Code"})

if select:
    option_values = [
        option['value'] for option in select.find_all('option')
        if not re.search(r'\d', option['value'])
    ]
else:
    print("No <select> element found with id 'Code'")

data = {
    "Issuer": [],
    "Date": [],
    "Open": [],
    "High": [],
    "Low": [],
    "Close": [],
    "Change": [],
    "Volume": [],
    "Turnover": [],
    "Market Cap": []
}

def fetch_data_for_issuer_year(issuer, from_date, to_date):
    base_url = "https://www.mse.mk/mk/stats/symbolhistory/"
    url = f"{base_url}{issuer}/?FromDate={from_date}&ToDate={to_date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    tabela = soup.find("tbody")

    temp_data = {
        "Issuer": [],
        "Date": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": [],
        "Change": [],
        "Volume": [],
        "Turnover": [],
        "Market Cap": []
    }

    if tabela:
        rows = tabela.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 9:
                temp_data["Issuer"].append(issuer)
                temp_data["Date"].append(cells[0].get_text(strip=True))
                temp_data["Open"].append(cells[1].get_text(strip=True))
                temp_data["High"].append(cells[2].get_text(strip=True))
                temp_data["Low"].append(cells[3].get_text(strip=True))
                temp_data["Close"].append(cells[4].get_text(strip=True))
                temp_data["Change"].append(cells[5].get_text(strip=True))
                temp_data["Volume"].append(cells[6].get_text(strip=True))
                temp_data["Turnover"].append(cells[7].get_text(strip=True))
                temp_data["Market Cap"].append(cells[8].get_text(strip=True))

        for key in data.keys():
            data[key].extend(temp_data[key])

def fetch_all_data_parallel():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for option in option_values:
            for year in range(2014, 2025):
                from_date = f"01.01.{year}"
                to_date = f"31.12.{year}"
                if year == 2024:
                    to_date = f"01.11.{year}"
                futures.append(executor.submit(fetch_data_for_issuer_year, option, from_date, to_date))

        for future in as_completed(futures):
            future.result()

def save_data_to_csv():
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')

    columns_to_format = ["Open", "High", "Low", "Close", "Change", "Turnover", "Market Cap"]
    for column in columns_to_format:
        df[column] = df[column].apply(format_mk_price)

    df['Date'] = df['Date'].dt.strftime('%d.%m.%Y')
    df.to_csv('stock_data.csv', index=False, encoding='utf-8')
    print("Податоците се успешно запишани во 'stock_data.csv' со македонски формат на цените.")

def format_mk_price(value):
    try:
        if ',' in value:
            return value
        number = int(value.replace('.', '').replace(',', ''))
        return f"{number:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        return value

if __name__ == "__main__":
    fetch_all_data_parallel()
    save_data_to_csv()

    df = pd.read_csv('stock_data.csv', encoding='utf-8')
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    latest_dates = df.groupby('Issuer')['Date'].max().reset_index()
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%d.%m.%Y')

    new_data = {
        "Issuer": [],
        "Date": [],
        "Open": [],
        "High": [],
        "Low": [],
        "Close": [],
        "Change": [],
        "Volume": [],
        "Turnover": [],
        "Market Cap": []
    }

    def fetch_data_for_date_range(issuer, from_date, to_date):
        base_url = "https://www.mse.mk/mk/stats/symbolhistory/"
        url = f"{base_url}{issuer}/?FromDate={from_date}&ToDate={to_date}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        tabela = soup.find("tbody")

        if tabela:
            rows = tabela.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) == 9:
                    new_data["Issuer"].append(issuer)
                    new_data["Date"].append(cells[0].get_text(strip=True))
                    new_data["Open"].append(cells[1].get_text(strip=True))
                    new_data["High"].append(cells[2].get_text(strip=True))
                    new_data["Low"].append(cells[3].get_text(strip=True))
                    new_data["Close"].append(cells[4].get_text(strip=True))
                    new_data["Change"].append(cells[5].get_text(strip=True))
                    new_data["Volume"].append(cells[6].get_text(strip=True))
                    new_data["Turnover"].append(cells[7].get_text(strip=True))
                    new_data["Market Cap"].append(cells[8].get_text(strip=True))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _, row in latest_dates.iterrows():
            issuer = row['Issuer']
            last_date = row['Date']
            if last_date < yesterday:
                from_date_str = last_date.strftime('%d.%m.%Y')
                to_date_str = yesterday_str
                futures.append(executor.submit(fetch_data_for_date_range, issuer, from_date_str, to_date_str))

        for future in as_completed(futures):
            future.result()

    new_data_df = pd.DataFrame(new_data)
    new_data_df['Date'] = pd.to_datetime(new_data_df['Date'], format='%d.%m.%Y')

    df = pd.concat([df, new_data_df])
    df['Date'] = df['Date'].dt.strftime('%d.%m.%Y')
    df.to_csv('stock_data.csv', index=False, encoding='utf-8')

    print("Податоците се успешно ажурирани со нови вредности до вчерашниот ден.")

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Време на извршување: {execution_time} секунди")