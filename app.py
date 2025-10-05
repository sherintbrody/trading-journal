import dash
from dash import dcc, html, dash_table
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Google Sheets Auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 📄 Load Existing Sheet
sheet = client.open("Journal October competition.XLSX").sheet1  # Replace with your actual sheet name
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 🧠 Dash App
app = dash.Dash(__name__)
server = app.server  # Required for deployment

app.layout = html.Div([
    html.H2("📋 Google Sheet Viewer"),
    dash_table.DataTable(
        id="sheet-table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        page_size=20
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
