# atlasog_app.py
import os
import json
import time
from datetime import datetime, timedelta
from random import choice, randint

import streamlit as st
import pandas as pd
import requests
# -----------------------------
# Sidebar Navigation
# -----------------------------
tab = st.sidebar.radio("Navigate", [
    "📈 Markets",
    "🤖 AI Assistant",
    "💸 Revenue Tracker"
])# -----------------------------
# Tab 1: Markets (Live Data)
# -----------------------------
if tab == "📈 Markets":
    st.header("Live Market Data & Asset Tracker")
    
    # Input ticker
    ticker = st.text_input("Enter a stock/crypto ticker (e.g., AAPL, BTC-USD):", "AAPL")
    
    if ticker:
        try:
            import yfinance as yf
            from datetime import datetime

            data = yf.download(ticker, period="5d", interval="1h")
            if not data.empty:
                st.line_chart(data["Close"])
                st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.dataframe(data.tail())
            else:
                st.warning("No data found for this ticker.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            # -----------------------------
# Tab 2: AI Assistant
# -----------------------------
if tab == "🤖 AI Assistant":
    st.header("Atlas AI Assistant")
    
    # Make sure your OpenAI API key is set in Streamlit Secrets as OPENAI_API_KEY
    openai.api_key = st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    
    user_prompt = st.text_area("Ask Atlas something:", "")
    
    if st.button("Run AI"):
        if not openai.api_key:
            st.warning("No OpenAI API key found. Add it in Streamlit Secrets as OPENAI_API_KEY.")
        else:
            try:
                import openai
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": user_prompt}]
                )
                st.success(response["choices"][0]["message"]["content"])
            except Exception as e:
                st.error(f"Error running AI: {e}")
# =============== CONFIG ===============
st.set_page_config(page_title="AtlasOG – Monetization Hub", layout="wide")
st.title("🌍 AtlasOG – Real-World Monetization Hub")
st.caption("Paste, connect, and track real revenue. Runs fine with no credentials; adds live data when you provide them.")

# =============== STORAGE ===============
CLICK_LOG = "click_log.csv"
DATA_FILE = "corporate_web_real.csv"

if not os.path.exists(CLICK_LOG):
    pd.DataFrame(columns=["ts","source","label","url"]).to_csv(CLICK_LOG, index=False)

if not os.path.exists(DATA_FILE):
    # simple corporate-web ledger table
    pd.DataFrame(columns=[
        "asset_id","corp_id","asset_type","creation_time","monetized_value",
        "reinvested","transferable_value"
    ]).to_csv(DATA_FILE, index=False)

# =============== HELPERS ===============
def money(x):
    try:
        return f"${float(x):,.2f}"
    except:
        return "$0.00"

def log_click(source:str, label:str, url:str):
    df = pd.read_csv(CLICK_LOG)
    df.loc[len(df)] = [datetime.utcnow().isoformat(), source, label, url]
    df.to_csv(CLICK_LOG, index=False)

# =============== SECRETS (Streamlit Cloud recommended) ===============
SECRETS = st.secrets if hasattr(st, "secrets") else {}
AMAZON_PARTNER_TAG = SECRETS.get("AMAZON_PARTNER_TAG", "")
PRINTFUL_API_KEY = SECRETS.get("PRINTFUL_API_KEY", "")
GSHEET_CREDS_JSON = SECRETS.get("GSHEET_CREDS_JSON", "")
GSHEET_NAME = SECRETS.get("GSHEET_NAME", "AtlasOG_Revenue")

# =============== LOAD DATA ===============
df_clicks = pd.read_csv(CLICK_LOG)
df_assets = pd.read_csv(DATA_FILE)

# =============== UI LAYOUT ===============
tabs = st.tabs([
    "📈 Overview",
    "🛒 Amazon Associates",
    "🖥️ Google AdSense",
    "👕 Printful (POD)",
    "📒 Google Sheet Ledger",
    "🧩 Corporate Web"
])

# =============== OVERVIEW ===============
with tabs[0]:
    st.subheader("Revenue Snapshot")
    # Amazon projected from clicks (conservative)
    last7 = datetime.utcnow() - timedelta(days=7)
    clicks_7d = df_clicks[(pd.to_datetime(df_clicks["ts"])>=last7) & (df_clicks["source"]=="amazon")]
    EPC = 0.08  # conservative estimated revenue per click
    amazon_proj = round(len(clicks_7d) * EPC, 2)

    adsense_total = st.session_state.get("adsense_total_usd", 0.0)
    printful_total = st.session_state.get("printful_total_usd", 0.0)
    ledger_total = st.session_state.get("ledger_total_usd", 0.0)

    colA, colB, colC, colD = st.columns(4)
    colA.metric("Amazon (7d proj.)", money(amazon_proj))
    colB.metric("AdSense", money(adsense_total))
    colC.metric("Printful", money(printful_total))
    colD.metric("Ledger", money(ledger_total))

    st.divider()
    WEEKLY_GOAL = 1000.0
    weekly_total = amazon_proj + adsense_total + printful_total + ledger_total
    st.metric("This Week (all sources)", money(weekly_total), delta=f"{round((weekly_total/WEEKLY_GOAL)*100,1)}% of goal")

    with st.expander("Click log (recent)"):
        st.dataframe(df_clicks.tail(200), use_container_width=True)

# =============== AMAZON ASSOCIATES ===============
with tabs[1]:
    st.subheader("Amazon Associates")
    st.caption("Add affiliate links. App tracks clicks; use Amazon reporting for payouts.")
    if "amazon_links" not in st.session_state:
        st.session_state["amazon_links"] = []

    with st.form("add_amazon_link"):
        label = st.text_input("Link label (e.g., 'Top Keyboard')")
        url = st.text_input("Amazon affiliate URL (must include your partner tag)")
        submitted = st.form_submit_button("Add Link")
        if submitted and label and url:
            st.session_state["amazon_links"].append({"label":label, "url":url})
            st.success("Link added.")

    if st.session_state["amazon_links"]:
        st.write("Your links")
        for i, item in enumerate(st.session_state["amazon_links"], start=1):
            c1, c2, c3 = st.columns([3,1,1])
            c1.markdown(f"**{i}. {item['label']}**  \n{item['url']}")
            if c2.button("Open", key=f"open_{i}"):
                log_click("amazon", item["label"], item["url"])
                st.markdown(f"[Opened link]({item['url']})")
            if c3.button("Track Click", key=f"track_{i}"):
                log_click("amazon", item["label"], item["url"])
                st.success("Click recorded.")

    st.info("When Amazon pays commissions, record them in the Google Sheet ledger (Monetization → Google Sheet).")

# =============== ADSENSE ===============
with tabs[2]:
    st.subheader("Google AdSense")
    st.caption("Optional: connect AdSense via service JSON in Streamlit Secrets to pull real earnings.")
    st.write("AdSense integration is optional. If you add service JSON to Streamlit Secrets as `ADSENSE_SERVICE_JSON`, we can fetch reports.")

# =============== PRINTFUL ===============
with tabs[3]:
    st.subheader("Printful (Print-on-Demand)")
    st.caption("Paste Printful API key in Streamlit Secrets (PRINTFUL_API_KEY) or enter below to fetch orders.")
    key_input = st.text_input("Printful API Key (starts 'PF-')", type="password", value=PRINTFUL_API_KEY or "")
    if st.button("Fetch Printful Orders"):
        if not key_input:
            st.warning("No API key provided.")
        else:
            try:
                headers = {"Authorization": f"Bearer {key_input}"}
                resp = requests.get("https://api.printful.com/orders", headers=headers, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                orders = data.get("result", [])
                total = 0.0
                rows = []
                for o in orders:
                    amount = 0.0
                    try:
                        amount = float(o.get("costs", {}).get("total", 0))
                    except:
                        pass
                    created = o.get("created", "")
                    rows.append({"id": o.get("id"), "status": o.get("status"), "created": created, "amount": amount})
                    total += max(0.0, amount)
                st.session_state["printful_total_usd"] = round(total, 2)
                st.success(f"Printful total: {money(total)}")
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            except Exception as e:
                st.error(f"Printful API error: {e}")

# =============== GOOGLE SHEET LEDGER ===============
with tabs[4]:
    st.subheader("Google Sheet Ledger (Free, Real Money Input)")
    st.caption("Create a Google Sheet named 'AtlasOG_Revenue' with columns: date, source, amount_usd, note.\n"
               "Put your service account JSON in Streamlit Secrets as GSHEET_CREDS_JSON (entire JSON).")

    if st.button("Fetch Ledger Totals"):
        if not GSHEET_CREDS_JSON:
            st.warning("No Google Sheets credentials in secrets yet.")
        else:
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
                creds_dict = json.loads(GSHEET_CREDS_JSON)
                scope = ["https://spreadsheets.google.com/feeds",
                         "https://www.googleapis.com/auth/spreadsheets",
                         "https://www.googleapis.com/auth/drive.file",
                         "https://www.googleapis.com/auth/drive"]
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                client = gspread.authorize(creds)
                sh = client.open(GSHEET_NAME).sheet1
                rows = sh.get_all_records()
                df_sheet = pd.DataFrame(rows)
                if not df_sheet.empty and "amount_usd" in df_sheet.columns:
                    total = float(df_sheet["amount_usd"].astype(float).sum())
                else:
                    total = 0.0
                st.session_state["ledger_total_usd"] = round(total, 2)
                st.success(f"Ledger total: {money(total)}")
                if not df_sheet.empty:
                    st.dataframe(df_sheet.tail(200), use_container_width=True)
            except Exception as e:
                st.error(f"Google Sheet error: {e}")

# =============== CORPORATE WEB (Real revenue integration) ===============
with tabs[5]:
    st.subheader("Corporate Web – Assets & Revenue")
    st.caption("Autonomous asset generation + reinvestment. Real revenue comes from Ledger/Printful/AdSense/Amazon (via clicks + later payouts).")
    st.write("NOTE: This module runs automatically on the server. Data is stored in the CSV in the app directory.")

    # load corporate assets CSV
    df_assets = pd.read_csv(DATA_FILE)

    # simple asset creation routine (only runs if assets are empty)
    CORP_IDS = ["AtlasCorp-A","AtlasCorp-B","AtlasCorp-C"]
    def create_asset(corp_id, monetized_value=0):
        asset_types = ["text_content","image_design","script","template","tool"]
        asset_type = choice(asset_types)
        asset_id = f"{asset_type[:2]}-{randint(1000,9999)}"
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "asset_id": asset_id, "corp_id": corp_id, "asset_type": asset_type,
            "creation_time": creation_time, "monetized_value": monetized_value,
            "reinvested": 0, "transferable_value": 0
        }

    # fetch ledger for monetized values if available
    ledger_df = pd.DataFrame()
    if GSHEET_CREDS_JSON:
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            creds_dict = json.loads(GSHEET_CREDS_JSON)
            scope = ["https://spreadsheets.google.com/feeds",
                     "https://www.googleapis.com/auth/spreadsheets",
                     "https://www.googleapis.com/auth/drive.file",
                     "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sh = client.open(GSHEET_NAME).sheet1
            rows = sh.get_all_records()
            ledger_df = pd.DataFrame(rows)
        except Exception:
            ledger_df = pd.DataFrame()

    # initialize
    if df_assets.empty:
        init_rows = []
        for corp in CORP_IDS:
            for _ in range(3):
                init_rows.append(create_asset(corp))
        df_assets = pd.concat([df_assets, pd.DataFrame(init_rows)], ignore_index=True)

    # run a few realistic cycles
    def corporate_cycle(df, ledger_df):
        new_assets = []
        for idx, row in df.iterrows():
            # update monetized values from ledger by asset_id if present
            if not ledger_df.empty and "asset_id" in ledger_df.columns:
                match = ledger_df[ledger_df["asset_id"]==row["asset_id"]]
                if not match.empty:
                    try:
                        val = float(match["amount_usd"].values[0])
                        df.at[idx,"monetized_value"] = val
                        df.at[idx,"transferable_value"] = val
                    except:
                        pass
            # reinvest using real monetized_value
            try:
                num_new = max(1, int(df.at[idx,"monetized_value"]*0.5))
            except:
                num_new = 1
            for _ in range(num_new):
                new_assets.append(create_asset(row["corp_id"]))
            df.at[idx,"reinvested"] += num_new
        return pd.concat([df, pd.DataFrame(new_assets)], ignore_index=True)

    # cycles and save
    CYCLES = 3
    for _ in range(CYCLES):
        df_assets = corporate_cycle(df_assets, ledger_df)

    df_assets.to_csv(DATA_FILE, index=False)

    # metrics
    total_assets = len(df_assets)
    total_reinvested = int(df_assets["reinvested"].sum())
    total_transferable = float(df_assets["transferable_value"].sum())
    st.metric("Total Assets", total_assets)
    st.metric("Total Reinvested", total_reinvested)
    st.metric("Total Transferable Revenue ($)", money(total_transferable))

    st.subheader("Recent Assets")
    st.dataframe(df_assets.tail(20), use_container_width=True)

st.success("AtlasOG is live — link your accounts in the Monetization tabs to show real money.")
