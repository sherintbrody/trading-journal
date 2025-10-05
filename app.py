import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import sqlite3
from datetime import datetime

# 📦 SQLite Setup
conn = sqlite3.connect("journal.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    open_date TEXT,
    close_date TEXT,
    instrument TEXT,
    lot REAL,
    direction TEXT,
    ls_percent REAL,
    entry REAL,
    sl REAL,
    tp REAL,
    exit_price REAL,
    rr REAL,
    result TEXT,
    remarks TEXT
)
""")
conn.commit()

# 🧠 Dash App
app = dash.Dash(__name__)
server = app.server  # Required for Render

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
            "open_date", "close_date", "instrument", "lot", "direction", "ls_percent",
            "entry", "sl", "tp", "exit_price", "rr", "result", "remarks"
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

    rr = round(abs(tp - entry) / abs(entry - sl), 2)
    cursor.execute("""
        INSERT INTO trades (open_date, close_date, instrument, lot, direction, ls_percent, entry, sl, tp, exit_price, rr, result, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (open_date, close_date, instrument, lot, direction, ls_percent, entry, sl, tp, exit_price, rr, result, remarks))
    conn.commit()

    df = pd.read_sql("SELECT * FROM trades", conn)
    return f"✅ Trade added with RR: {rr}", df.to_dict("records")

if __name__ == "__main__":
    app.run_server(debug=True)
