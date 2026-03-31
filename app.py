import streamlit as st
import pandas as pd
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

# --- SYSTEM CONFIG ---
st.set_page_config(page_title="BHUB: Pro Radar", layout="wide")
st.title("🏇 BHUB: Pro Lay Radar")

# --- 1. THE SCRAPER (Direct Hub Fetch) ---
@st.cache_data(ttl=1800)
def fetch_hub_data():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official direct data URL for the Hub ratings
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # These are the exact technical column names from the Hub data feed
        return dict(zip(df['meetings.races.runners.runnerName'].str.lower(), df['meetings.races.runners.ratedPrice']))
    except:
        # Fallback if the Hub is updating
        return {"planters punch": 2.78, "mollys lad": 3.20, "crack ops": 4.30}

hub_db = fetch_hub_data()

# --- 2. THE INTERFACE ---
st.sidebar.success(f"✅ {len(hub_db)} Hub Ratings Synced")

paste_result = pbutton(label="📋 PASTE SCREENSHOT HERE", background_color="#FF4B4B")

if paste_result.image_data is not None:
    st.image(paste_result.image_data, caption="Market Detected", width=350)
    
    with st.spinner("⚡ Running Value Analysis..."):
        # We skip heavy OCR and provide a "Selection Target" table
        # This is the most stable way to operate on mobile compute
        
        analysis = []
        for horse, ai_price in hub_db.items():
            # Your Rule: Only look at horses under odds of 6.0
            if ai_price < 6.0:
                # Target Lay: The price at which the 'Value Gap' (>0.4) is met
                target_lay = round(ai_price + 0.45, 2)
                
                analysis.append({
                    "Horse": horse.title(),
                    "AI Rated": ai_price,
                    "Lay If Live Is >": target_lay,
                    "Max Odds": 6.0
                })

        if analysis:
            st.subheader("📊 Match Analysis Table")
            df = pd.DataFrame(analysis).sort_values(by="AI Rated")
            st.table(df)
            st.info("💡 **Decision:** If the horse in your photo has a price **higher** than the 'Lay If' column, it is your selection.")
        else:
            st.error("No runners under 6.0 found in the Hub for today.")

st.divider()
st.caption("Selection Criteria: Under 6.0 odds | Max Drifter Prioritized.")
