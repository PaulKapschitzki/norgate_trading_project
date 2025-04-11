# webapp/app.py (Streamlit-Beispiel)
import streamlit as st
import pandas as pd

st.title("Tägliches Screening")
df = pd.read_csv("../data/daily_screen_results.csv")
st.dataframe(df)
