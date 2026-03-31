import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# --- STEP 1: CONTEXT ---
# Because you are using the AU Hub for UK races, we look at 'tomorrow' 
# to capture the UK afternoon/evening sessions.
target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

def get_next_race():
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={target_date}&presenter=RatingsPresenter&csv=true"
    
    try:
        df = pd.read_csv(url)
        
        # 1. Identify the 'Race Time' and 'Meeting Name' columns
        # The Hub uses 'meetings.races.startTime' and 'meetings.meetingName'
        time_col = [c for c in df.columns if 'startTime' in c][-1]
        meeting_col = [c for c in df.columns if 'meetingName' in c][-1]
        
        # 2. Convert string time to actual datetime objects for sorting
        df[time_col] = pd.to_datetime(df[time_col])
        
        # 3. Filter for races that haven't started yet (Current Time < Start Time)
        # We use UTC comparison as the Hub data is usually in UTC
        now_utc = datetime.utcnow()
        future_races = df[df[time_col] > now_utc].sort_values(by=time_col)
        
        if not future_races.empty:
            next_race_time = future_races.iloc[0][time_col].strftime('%H:%M')
            next_meeting = future_races.iloc[0][meeting_col]
            return f"{next_race_time} {next_meeting}"
        else:
            return "No upcoming races found for the selected date."
            
    except Exception as e:
        return f"Error connecting to Hub: {e}"

# --- STEP 2: DISPLAY ---
st.title("Next Scheduled Race")

if st.button("🔍 IDENTIFY NEXT RACE"):
    race_name = get_next_race()
    st.header(f"🏇 {race_name}")
