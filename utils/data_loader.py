# utils/data_loader.py
import pandas as pd

def load_data(symbol):
    return pd.read_csv(f"data/{symbol}.csv")
