import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="BHUB: Next Race", layout="wide")
st.title("Next Scheduled Race")

def get_next_race_from_web():
    # We scrape the UK Racing Tips page directly
    url = "https://www.betfair.com.au/hub/models/uk-racing-tips/"
    
    try:
        # Use a User-Agent to prevent being blocked
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return "⚠️ Hub Website is currently unreachable."

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # We look for the track name and race number headings on the page
        # These are usually in <h3> or <h4> tags on the Hub
        race_headings = soup.find_all(['h3', 'h4'])
        
        next_race = None
        for heading in race_headings:
            text = heading.get_text().strip()
            # Identifying a race heading like "R2. Bangor-On-Dee"
            if "R" in text and "." in text:
                next_race = text
                break # We found the first one in the list
                
        return next_race if next_race else "No active races found on page."

    except Exception as e:
        return f"Scrape Error: {e}"

# --- DISPLAY ---
if st.button("🔍 IDENTIFY NEXT RACE"):
    with st.spinner("Reading Betfair Hub..."):
        race_name = get_next_race_from_web()
        
        if race_name:
            st.header(f"🏇 {race_name}")
        else:
            st.warning("Could not find any scheduled races. Check site status.")

st.divider()
st.caption(f"Last Attempt: {datetime.now().strftime('%H:%M:%S')}")
