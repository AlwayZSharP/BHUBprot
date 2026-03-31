import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="BHUB: Auto-Lay Radar", layout="wide")
st.title("🏇 BHUB: Auto-Lay Radar")

# --- DATA ENGINE: SCRAPE & FILTER ---
@st.cache_data(ttl=30) # 30-second refresh to catch market suspensions
def get_live_analysis():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official direct data URL for the Hub ratings
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    
    try:
        df = pd.read_csv(url)
        
        # Technical Column Names from the Hub Feed
        name_col = 'meetings.races.runners.runnerName'
        rated_col = 'meetings.races.runners.ratedPrice'
        live_col = 'meetings.races.runners.lastPriceTraded'
        status_col = 'meetings.races.status' # Used to detect suspended markets
        
        # 1. FILTER: Ignore suspended races or those not currently active
        # Common active status labels include 'OPEN' or 'ACTIVE'
        df = df[df[status_col].str.upper() != 'SUSPENDED'] 
        
        # 2. FILTER: Selections must be priced under odds of 6.0
        df_filtered = df[(df[live_col] > 1.0) & (df[live_col] < 6.0)].copy()
        
        # 3. ANALYSIS: Calculate Value Gap
        df_filtered['Gap'] = df_filtered[live_col] - df_filtered[rated_col]
        
        # Format the Output Table
        results = df_filtered[[name_col, rated_col, live_col, 'Gap']]
        results.columns = ['Horse', 'Rated Price', 'Live Price', 'Gap']
        
        # Sort by largest value gap (The biggest Drifter)
        return results.sort_values(by='Gap', ascending=False)
        
    except Exception as e:
        return pd.DataFrame({"Error": [f"Scrape Failed: {e}"]})

# --- DISPLAY INTERFACE ---
if st.button("🔄 ANALYZE NEXT ACTIVE RACE"):
    data = get_live_analysis()
    
    if not data.empty and 'Error' not in data.columns:
        # Highlight the top drifter as the primary selection
        st.subheader("🎯 Current Value Selections")
        
        def highlight_top(s):
            return ['background-color: #ff4b4b; color: white' if i == 0 else '' for i in range(len(s))]

        st.table(data.style.format({
            "Rated Price": "{:.2f}",
            "Live Price": "{:.2f}",
            "Gap": "+{:.2f}"
        }))
        
        st.success(f"**Selection:** {data.iloc[0]['Horse']} identified as the largest value gap under 6.0.")
    else:
        st.info("No active runners found under odds of 6.0. The race may be suspended or data is loading.")

st.divider()
st.caption(f"Last Scrape: {datetime.now().strftime('%H:%M:%S')}")
