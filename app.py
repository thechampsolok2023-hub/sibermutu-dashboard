import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="SIBERMUTU Dashboard", layout="wide")

SPREADSHEET_ID = "1vPEr3dMNrotI9AbY8h4LDIKp2L7-G1VIbRO5C3rKXCw"
SHEET_NAME = "Sheet1"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=300)
def load_data():
    response = requests.get(CSV_URL)
    data = pd.read_csv(StringIO(response.text))
    return data

df = load_data()

st.title("📊 SIBERMUTU Dashboard")
st.markdown("Monitoring Kepatuhan Faskes")

st.sidebar.header("Filter Data")

if "Bulan" in df.columns:
    bulan_filter = st.sidebar.selectbox("Pilih Bulan", ["Semua"] + sorted(df["Bulan"].dropna().unique().tolist()))
    if bulan_filter != "Semua":
        df = df[df["Bulan"] == bulan_filter]

if "Kabupaten" in df.columns:
    kab_filter = st.sidebar.selectbox("Pilih Kabupaten", ["Semua"] + sorted(df["Kabupaten"].dropna().unique().tolist()))
    if kab_filter != "Semua":
        df = df[df["Kabupaten"] == kab_filter]

st.subheader("Executive Summary")

col1, col2 = st.columns(2)

col1.metric("Total Data", len(df))
if "Nama FKTP" in df.columns:
    col2.metric("Total FKTP", df["Nama FKTP"].nunique())

numeric_cols = df.select_dtypes(include='number').columns

if "Bulan" in df.columns and len(numeric_cols) > 0:
    trend_data = df.groupby("Bulan")[numeric_cols].mean()
    st.line_chart(trend_data)

if "Nama FKTP" in df.columns and len(numeric_cols) > 0:
    ranking = df.groupby("Nama FKTP")[numeric_cols].mean().mean(axis=1).sort_values(ascending=False)
    st.bar_chart(ranking)

st.subheader("Data Detail")
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Data CSV", csv, "data_filtered.csv", "text/csv")
