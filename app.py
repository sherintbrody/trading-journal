import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Load Google Sheets credentials from Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["google_sheets"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Load Existing Sheet
try:
    sheet = client.open("Journal.xlsm").worksheet("Log")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error("❌ Could not load sheet. Check the sheet name and sharing permissions.")
    st.stop()

# 🧠 Streamlit App
st.set_page_config(page_title="📘 Trading Journal Viewer", layout="wide")
st.title("📘 Trading Journal Viewer")

st.dataframe(df, use_container_width=True)
