import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def get_next_chronological_race():
    # URL targeting the UK Racing Tips model on the AU Hub
    url = "https://www.betfair.com.au/hub/models/uk-racing-tips/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Error: Could not access Hub."

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Find all race blocks
        # The Hub nests race names in <h3> or <h4> and countdowns in <span> tags
        races = []
        
        # Finding the 'Meeting' context (e.g., Bangor-On-Dee)
        # In the Hub HTML, these are often grouped by track-filter-buttons
        active_meeting = "Unknown Location"
        track_elements = soup.find_all('button', class_=re.compile('track-filter'))
        for track in track_elements:
            if 'active' in track.get('class', []):
                active_meeting = track.get_text().strip()

        # 2. Extract Race Name and Countdown
        # We look for the countdown pattern (00:00:00)
        timers = soup.find_all(text=re.compile(r'\d{2}:\d{2}:\d{2}'))
        
        for timer in timers:
            # Find the nearest heading above this timer
            parent_section = timer.find_parent(['div', 'section'])
            race_title = parent_section.find(['h3', 'h4'])
            
            if race_title:
                races.append({
                    "name": race_title.get_text().strip(),
                    "location": active_meeting,
                    "countdown": timer.strip()
                })

        # 3. Sort by smallest non-negative countdown
        if races:
            # Sorting logic: Smallest string value (since 00:02:39 < 00:32:39)
            races.sort(key=lambda x: x['countdown'])
            return races[0]
            
        return None

    except Exception as e:
        return f"System Error: {e}"

# --- STREAMLIT UI ---
st.title("Next Scheduled Race")

if st.button("🔍 FIND NEXT RACE"):
    result = get_next_chronological_race()
    if isinstance(result, dict):
        st.header(f"🏇 {result['name']}")
        st.subheader(f"📍 Location: {result['location']}")
        st.write(f"⏳ Countdown: {result['countdown']}")
    else:
        st.error(result if result else "No races found.")
