import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="BHUB: Auto-Lay Radar", layout="wide")
st.title("🏇 BHUB: Auto-Lay Radar")

# --- DATA ENGINE: SCRAPE & ANALYZE ---
@st.cache_data(ttl=60) # Refreshes every 60 seconds for live prices
def get_analysis():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official Betfair Hub Data Feed
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    
    try:
        df = pd.read_csv(url)
        # Column names from the Hub data feed
        name_col = 'meetings.races.runners.runnerName'
        rated_col = 'meetings.races.runners.ratedPrice'
        live_col = 'meetings.races.runners.lastPriceTraded' # Or 'bestBackPrice'
        
        # Filter for your specific rule: Odds under 6.0
        # Note: We use the live price for the threshold
        df_filtered = df[df[live_col] < 6.0].copy()
        
        # Calculate Value Gap
        df_filtered['Gap'] = df_filtered[live_col] - df_filtered[rated_col]
        
        # Create final output table
        output = df_filtered[[name_col, rated_col, live_col, 'Gap']]
        output.columns = ['Horse', 'Rated Price', 'Live Price', 'Gap']
        
        # Sort by largest value gap (The biggest Drifter)
        return output.sort_values(by='Gap', ascending=False)
    except Exception as e:
        return pd.DataFrame({"Error": [f"Could not fetch data: {e}"]})

# --- DISPLAY ---
if st.button("🔄 ANALYZE NEXT RACE"):
    data = get_analysis()
    
    if not data.empty and 'Error' not in data.columns:
        # Prioritize the drifter with the largest value gap
        top_selection = data.iloc[0]
        
        st.subheader(f"🎯 Top Selection: {top_selection['Horse']}")
        
        # Your ABC Format Summary Table
        st.table(data.style.format({
            "Rated Price": "{:.2f}",
            "Live Price": "{:.2f}",
            "Gap": "+{:.2f}"
        }).apply(lambda x: ['background-color: #ff4b4b; color: white' if x.name == 0 else '' for i in x], axis=1))
        
        st.info(f"**Selection Criteria:** Odds < 6.0 | Status: {top_selection['Horse']} is the largest drifter (+{top_selection['Gap']:.2f}).")
    else:
        st.error("No runners found under odds of 6.0 for the current race.")

st.divider()
st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
