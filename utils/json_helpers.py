"""Helper-Funktionen für JSON-Serialisierung"""
import numpy as np
from datetime import datetime, date
import pandas as pd

def convert_to_serializable(obj):
    """Konvertiert ein Objekt in ein JSON-serialisierbares Format"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    return obj

def prepare_df_for_json(df: pd.DataFrame) -> dict:
    """
    Bereitet einen DataFrame für die JSON-Serialisierung vor
    
    Args:
        df: Der zu konvertierende DataFrame
        
    Returns:
        Ein Dictionary mit serialisierbaren Werten
    """
    result = {}
    for column in df.columns:
        values = df[column].apply(convert_to_serializable).to_list()
        result[column] = values
    return result
