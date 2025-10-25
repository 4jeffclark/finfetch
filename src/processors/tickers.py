import yfinance as yf
import pandas as pd
import numpy as np
from polygon import RESTClient
import warnings
warnings.filterwarnings("ignore")

# Function to get S&P 500 tickers using yfinance
def get_sp500_tickers():
    # Scrape S&P 500 tickers from Wikipedia
    sp500_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    tickers = sp500_table['Symbol'].tolist()
    # Replace '.' with '-' for Yahoo Finance compatibility (e.g., BRK.B -> BRK-B)
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    return tickers

