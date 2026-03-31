import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="BHUB: UK Time-Sync", layout="wide")
st.title("🏇 BHUB: UK Auto-Lay Radar")

# --- TIMEZONE OVERRIDE ---
# AU is ahead of UK. We need to check both dates.
date_choice = st.sidebar.radio("Select Data Date:", ["Auto (UK Today)", "UK Tomorrow"])

if date_choice == "Auto (UK Today)":
    target_date = datetime.now().strftime("%Y-%m-%d")
else:
    target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

# --- DATA ENGINE: DIRECT SCRAPE ---
@st.cache_data(ttl=60)
def get_uk_data(date_str):
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={date_str}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # Use keywords to find columns because names change by region
        name_col = [c for c in df.columns if 'runnerName' in c][-1]
        rated_col = [c for c in df.columns if 'ratedPrice' in c][-1]
        
        # In AU feeds for UK, Live Price is often 'lastPriceTraded' 
        # or it falls back to the AI price if the market isn't 'In-Play'
        price_cols = [c for c in df.columns if 'Price' in c and c != rated_col]
        live_col = price_cols[0] if price_cols else rated_col
        
        # RULE: Odds < 6.0
        df_filtered = df[df[rated_col] < 6.0].copy()
        
        # ANALYSIS: Value Gap
        df_filtered['Gap'] = df_filtered[live_col] - df_filtered[rated_col]
        
        res = df_filtered[[name_col, rated_col, live_col, 'Gap']]
        res.columns = ['Horse', 'Rated Price', 'Live Price', 'Gap']
        return res.sort_values(by='Gap', ascending=False)
    except:
        return pd.DataFrame()

# --- DISPLAY ---
st.info(f"Checking UK Races for: **{target_date}**")

if st.button("🔄 REFRESH UK SELECTIONS"):
    data = get_uk_data(target_date)
    
    if not data.empty:
        st.subheader("🎯 Active UK Value Lays")
        
        # Summary Table
        st.table(data.style.format({
            "Rated Price": "{:.2f}",
            "Live Price": "{:.2f}",
            "Gap": "+{:.2f}"
        }).apply(lambda x: ['background-color: #ff4b4b; color: white' if i == 0 else '' for i in range(len(x))], axis=1))
        
        st.success(f"**Top Drifter:** {data.iloc[0]['Horse']} (+{data.iloc[0]['Gap']:.2f} gap)")
    else:
        st.error(f"No data found for {target_date}. Try switching the date in the sidebar.")
