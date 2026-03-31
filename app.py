import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="BHUB: Streamlined Radar", layout="wide")
st.title("🏇 BHUB: Streamlined Lay Radar")

# --- AUTO-SYNC HUB DATA ---
@st.cache_data(ttl=3600) # Refreshes every hour
def get_hub_data():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official Kash Model CSV URL
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # Rename complex Hub columns to simple ones
        df = df.rename(columns={
            "meetings.races.runners.runnerName": "horse",
            "meetings.races.runners.ratedPrice": "rating"
        })
        # Create a clean dictionary: {horse_name: rated_price}
        return dict(zip(df['horse'].str.lower(), df['rating']))
    except Exception as e:
        st.sidebar.error(f"Sync Error: {e}")
        return {}

# Load AI Brain & Hub Data
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()
hub_db = get_hub_data()

# Status Check
if hub_db:
    st.sidebar.success(f"✅ Synced {len(hub_db)} Hub Ratings")
else:
    st.sidebar.warning("⚠️ Hub Data not found for today yet.")

# --- THE INTERFACE ---
paste_result = pbutton(label="📋 PASTE SCREENSHOT HERE", background_color="#FF4B4B")

if paste_result.image_data is not None:
    img = paste_result.image_data
    with st.spinner("🤖 Analyzing Market..."):
        img_np = np.array(img)
        results = reader.readtext(img_np)
        
        # Build a list of all text found in the photo
        all_text = " ".join([res[1].lower() for res in results])

        summary_data = []
        for horse, ai_price in hub_db.items():
            # MATCH: Is the Hub horse name in your screenshot?
            if horse in all_text:
                # To get the LIVE price from the photo, we look for the number 
                # that appeared near that horse's name in the OCR results.
                # For this streamlined version, we'll use a placeholder until we 
                # refine the 'Number Grabber' logic for your specific phone screen.
                live_price = 5.00 # Placeholder
                gap = round(live_price - ai_price, 2)
                
                # APPLY YOUR RULES: Under 6.0 and Drifting
                if live_price < 6.0:
                    summary_data.append({
                        "Horse": horse.title(),
                        "AI Rated": ai_price,
                        "Current": live_price,
                        "Gap": gap,
                        "Selection": "🎯 LAY" if gap > 0.4 else "-"
                    })

        if summary_data:
            df_res = pd.DataFrame(summary_data).sort_values(by="Gap", ascending=False)
            
            def highlight(row):
                return ['background-color: #ff4b4b; color: white; font-weight: bold'] if "LAY" in str(row["Selection"]) else [''] * len(row)
            
            st.write("### 📊 Value Analysis")
            st.table(df_res.style.apply(highlight, axis=1).format({"Gap": "+{:.2f}"}))
        else:
            st.error("No matches found. Ensure the horse names are clear.")
