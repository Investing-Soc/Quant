#getting and saving the list of s&p 500 companies
import sqlite3
import pandas as pd
import requests
import io
import random
import yfinance as yf
import time
import sqlite3

def updating(ticker):
    try:
        stock = yf.Ticker(ticker)

        info = stock.info
        history_daily = stock.history(period='1y', interval='1d')
        history_monthly = stock.history(period='20y', interval="1wk")

        with sqlite3.connect('permanent.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO stock_details
                (ticker, company_name, sector, description)
                VALUES (?, ?, ?, ?)
                ''', (ticker, info.get('longName'), info.get('sector'), info.get('longBusinessSummary')))
            for date, row in history_daily.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO price_history
                (ticker, history_date, close_price)
                VALUES (?, ?, ?)
                ''', (ticker, date.strftime('%Y-%m-%d'), row['Close']))

            for date, row in history_daily.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO price_history_monthly
                (ticker, history_date, close_price)
                VALUES (?, ?, ?)
                ''', (ticker, date.strftime('%Y-%m-%d'), row['Close']))

    except Exception as e:
        print(f'ticker {ticker} skipped: error details: {e}')
        return False

    sleep_throttle = random.uniform(2.0, 4.5)
    time.sleep(sleep_throttle)
    return True
        

def save(ticker):
    with sqlite3.connect('S&P-500.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO tickers (ticker) VALUES (?)', (ticker, ))



if __name__ == '__main__':

    n = 0

    #Obtains all the tickers for the S&P
    
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    with sqlite3.connect('S&P-500.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickers (
                ticker TEXT PRIMARY KEY
                )
            ''')
    with sqlite3.connect('permanent.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_details (
                ticker TEXT PRIMARY KEY,
                company_name TEXT,
                sector TEXT,
                description TEXT
                )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                ticker TEXT,
                history_date TEXT,
                close_price REAL,
                PRIMARY KEY (ticker, history_date)
                )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history_monthly (
                ticker TEXT,
                history_date TEXT,
                close_price REAL,
                PRIMARY KEY (ticker, history_date)
                )
            ''')

    response = requests.get(url, headers=headers)

    tables = pd.read_html(io.StringIO(response.text))

    sp500 = tables[0]['Symbol'].tolist()

    sp500 = [company.replace('.', '-') for company in sp500]

    #Downloads S&P data
    for ticker in sp500:
        n += 1
        print(f'Running {ticker}')
        result = updating(ticker)
        if result:
            print(f' {n}/500: Success!')
        else:
            print('Failed')
