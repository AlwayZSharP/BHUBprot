import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="BHUB: Auto-Lay Radar", layout="wide")
st.title("🏇 BHUB: Auto-Lay Radar")

# --- STEP 1: SCRAPE REAL HUB DATA ---
@st.cache_data(ttl=60) # Refreshes every minute for live prices
def get_hub_analysis():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official direct data URL for Betfair Hub ratings
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    
    try:
        df = pd.read_csv(url)
        # Use exact Betfair Hub technical column names
        name_col = 'meetings.races.runners.runnerName'
        rated_col = 'meetings.races.runners.ratedPrice'
        live_col = 'meetings.races.runners.lastPriceTraded'
        status_col = 'meetings.races.status'
        
        # FILTER 1: Only Active/Open markets (Ignore Suspended)
        df = df[df[status_col].str.upper().isin(['OPEN', 'ACTIVE'])]
        
        # FILTER 2: Rule - Selections priced under odds of 6.0
        df_filtered = df[(df[live_col] > 1.0) & (df[live_col] < 6.0)].copy()
        
        # CALCULATION: Value Gap (Live Price - Rated Price)
        df_filtered['Gap'] = df_filtered[live_col] - df_filtered[rated_col]
        
        # Formatting Output
        res = df_filtered[[name_col, rated_col, live_col, 'Gap']]
        res.columns = ['Horse', 'Rated Price', 'Live Price', 'Gap']
        
        # Sort by largest value gap (The biggest Drifter)
        return res.sort_values(by='Gap', ascending=False)
    except:
        return pd.DataFrame()

# --- STEP 2: DISPLAY RESULTS ---
if st.button("🔄 ANALYZE NEXT ACTIVE RACE"):
    data = get_hub_analysis()
    
    if not data.empty:
        # ABC Format Summary Table as requested
        st.subheader("🎯 Current Value Selections")
        
        # Highlight the top selection (Largest drifter under 6.0)
        st.table(data.style.format({
            "Rated Price": "{:.2f}",
            "Live Price": "{:.2f}",
            "Gap": "+{:.2f}"
        }).apply(lambda x: ['background-color: #ff4b4b; color: white' if i == 0 else '' for i in range(len(x))], axis=1))
        
        # Logic Check: Prioritize the drifter with the largest gap
        top_horse = data.iloc[0]['Horse']
        st.success(f"**Selection:** {top_horse} is currently the biggest drifter within the price range.")
    else:
        st.info("No active runners under 6.0 meet the criteria at this moment.")

st.divider()
st.caption(f"Last Scrape: {datetime.now().strftime('%H:%M:%S')}")
