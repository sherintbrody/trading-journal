import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔐 Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Trading Journal").sheet1  # Make sure this matches your sheet name

# 🧠 Dash App
app = dash.Dash(__name__)
server = app.server  # Required for deployment

app.layout = html.Div([
    html.H2("📘 Trading Journal"),

    html.Div([
        html.Label("Instrument"), dcc.Input(id="instrument", type="text"),
        html.Label("Open Date (UTC)"), dcc.Input(id="open_date", type="text", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
        html.Label("Close Date"), dcc.Input(id="close_date", type="text"),
        html.Label("Lot"), dcc.Input(id="lot", type="number"),
        html.Label("Buy/Sell"), dcc.Dropdown(id="direction", options=[{"label": i, "value": i} for i in ["Buy", "Sell"]]),
        html.Label("LS%"), dcc.Input(id="ls_percent", type="number"),
        html.Label("Entry"), dcc.Input(id="entry", type="number"),
        html.Label("SL"), dcc.Input(id="sl", type="number"),
        html.Label("TP"), dcc.Input(id="tp", type="number"),
        html.Label("Exit Price"), dcc.Input(id="exit_price", type="number"),
        html.Label("Result"), dcc.Dropdown(id="result", options=[{"label": i, "value": i} for i in ["Win", "Loss", "BE"]]),
        html.Label("Remarks"), dcc.Input(id="remarks", type="text"),
        html.Button("Add Trade", id="submit", n_clicks=0)
    ], style={"columnCount": 2}),

    html.Div(id="confirmation", style={"marginTop": "20px"}),

    dash_table.DataTable(
        id="trade-table",
        columns=[{"name": i, "id": i} for i in [
            "Open Date", "Close Date", "Instrument", "Lot", "Direction", "LS%",
            "Entry", "SL", "TP", "Exit Price", "Result", "Remarks"
        ]],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
        page_size=10
    )
])

# 🔁 Callback: Save Trade + Update Table
@app.callback(
    Output("confirmation", "children"),
    Output("trade-table", "data"),
    Input("submit", "n_clicks"),
    State("open_date", "value"),
    State("close_date", "value"),
    State("instrument", "value"),
    State("lot", "value"),
    State("direction", "value"),
    State("ls_percent", "value"),
    State("entry", "value"),
    State("sl", "value"),
    State("tp", "value"),
    State("exit_price", "value"),
    State("result", "value"),
    State("remarks", "value")
)
def save_trade(n, open_date, close_date, instrument, lot, direction, ls_percent, entry, sl, tp, exit_price, result, remarks):
    if n == 0 or not all([open_date, instrument, entry, sl, tp, exit_price]):
        return "", []

    new_row = [
        open_date, close_date, instrument, lot, direction, ls_percent,
        entry, sl, tp, exit_price, result, remarks
    ]
    sheet.append_row(new_row)

    data = sheet.get_all_records()
    return "✅ Trade added successfully", data

if __name__ == "__main__":
    app.run_server(debug=True)
