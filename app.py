import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="BHUB: Race Finder", layout="wide")
st.title("Next Scheduled Race")

# --- STEP 1: ROBUST SCRAPER ---
def get_next_race_name():
    # We target 'Tomorrow' (01/04/2026) because of the AU/UK timezone offset
    target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Primary Data Feed
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={target_date}&presenter=RatingsPresenter&csv=true"
    
    try:
        response = requests.get(url, timeout=10)
        
        # If the server is 500 (Broken), we catch it here
        if response.status_code == 500:
            return "⚠️ Hub Server Error (500). Betfair is currently updating the feed."
            
        df = pd.read_csv(url)
        
        # Identify columns for Time and Track
        time_col = [c for c in df.columns if 'startTime' in c][-1]
        track_col = [c for c in df.columns if 'meetingName' in c][-1]
        
        # Sort chronologically
        df[time_col] = pd.to_datetime(df[time_col])
        now_utc = datetime.utcnow()
        future = df[df[time_col] > now_utc].sort_values(by=time_col)
        
        if not future.empty:
            next_time = future.iloc[0][time_col].strftime('%H:%M')
            next_track = future.iloc[0][track_col]
            return f"{next_time} {next_track}"
        return "No upcoming races found for this date."

    except Exception as e:
        return f"Connection Issue: {e}"

# --- DISPLAY ---
if st.button("🔍 IDENTIFY NEXT RACE"):
    with st.spinner("Checking Betfair Hub..."):
        race = get_next_race_name()
        st.header(f"🏇 {race}")
        
st.divider()
st.caption(f"Current System Time: {datetime.now().strftime('%H:%M:%S')}")
