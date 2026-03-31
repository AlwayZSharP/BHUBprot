import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="BHUB: CSV Link Fixer", layout="wide")
st.title("🏇 Betfair Hub: Live CSV Finder")

# 1. DATE LOGIC: Find the UK "Today" (even if you are in AU)
# If it's late in AU, the UK races are often listed under 'tomorrow's' date
now = datetime.now()
date_today = now.strftime("%Y-%m-%d")
date_tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

st.info(f"System Date: {date_today}")

# 2. THE GENERATOR
def make_link(target_date):
    base = "https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets"
    params = f"?date={target_date}&presenter=RatingsPresenter&csv=true"
    return base + params

# 3. DISPLAY OPTIONS
st.write("### Select the race date shown on your Betfair Hub screen:")
col1, col2 = st.columns(2)

with col1:
    link_today = make_link(date_today)
    st.link_button(f"📅 Download: {date_today}", link_today, use_container_width=True)

with col2:
    link_tomorrow = make_link(date_tomorrow)
    st.link_button(f"📅 Download: {date_tomorrow}", link_tomorrow, use_container_width=True)

st.divider()
st.warning("⚠️ **If it says 'Invalid':** Open the Betfair Hub in a separate tab first, then come back here and click. This 'wakes up' the server for your phone.")
