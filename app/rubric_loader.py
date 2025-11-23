# app/rubric_loader.py
import pandas as pd

def load_rubric(path):
    """
    Loads the rubric excel into a DataFrame.
    Expected columns: 'criterion', 'description', 'weight' (others optional).
    """
    df = pd.read_excel(path, engine="openpyxl")
    # normalize columns
    df.columns = [c.strip() for c in df.columns]
    return df
