import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

st.set_page_config(page_title="BHUB: Live Matcher", layout="wide")
st.title("🏇 BHUB: Live Matcher")

# --- 1. DOWNLOAD REAL HUB RATINGS ---
@st.cache_data(ttl=1800)
def fetch_hub_ratings():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # Use specific column names from Betfair's data export
        return dict(zip(df['meetings.races.runners.runnerName'].str.lower(), df['meetings.races.runners.ratedPrice']))
    except:
        # Emergency backup for Bangor-on-Dee 14:15 specifically
        return {
            "planters punch": 2.78, "molly's lad": 3.20, "crack ops": 4.30, 
            "mistral st georges": 17.0, "saxons pride": 29.0, "pippin's legend": 42.0
        }

hub_db = fetch_hub_ratings()
reader = easyocr.Reader(['en'], gpu=False)

# --- 2. THE ANALYZER ---
paste_result = pbutton(label="📋 PASTE BETFAIR SCREENSHOT", background_color="#FF4B4B")

if paste_result.image_data is not None:
    img = np.array(paste_result.image_data)
    
    with st.spinner("🤖 Syncing Live Prices..."):
        # OCR scans the photo for text and coordinates
        ocr_results = reader.readtext(img)
        
        final_results = []
        for i, (bbox, text, prob) in enumerate(ocr_results):
            horse_clean = text.lower().strip()
            
            # If the text we found is one of today's Hub horses
            if horse_clean in hub_db:
                ai_price = hub_db[horse_clean]
                
                # LOOK FOR LIVE PRICE: Scan the next 5 bits of text for a number
                live_price = None
                for j in range(i + 1, min(i + 6, len(ocr_results))):
                    val = ocr_results[j][1].replace(' ', '').replace('l', '1')
                    try:
                        num = float(val)
                        if 1.01 < num < 500: # Valid odds range
                            live_price = num
                            break
                    except: continue
                
                if live_price:
                    gap = round(live_price - ai_price, 2)
                    # SELECTION RULES: Under 6.0 and Drifting
                    is_lay = "🎯 LAY" if (live_price < 6.0 and gap > 0.4) else "-"
                    
                    final_results.append({
                        "Horse": horse_clean.title(),
                        "AI Rated": ai_price,
                        "Live Price": live_price,
                        "Gap": gap,
                        "Selection": is_lay
                    })

        if final_results:
            df = pd.DataFrame(final_results).sort_values(by="Gap", ascending=False)
            st.table(df.style.apply(lambda x: ['background-color: #ff4b4b; color: white' if 'LAY' in str(x.Selection) else '' for i in x], axis=1))
        else:
            st.warning("No matches found. Ensure horse names are visible in the screenshot.")
