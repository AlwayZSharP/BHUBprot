import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

st.set_page_config(page_title="BHUB: Intelligent Radar", layout="wide")
st.title("🏇 BHUB: Intelligent Lay Radar")

# --- 1. PRECISE DATA SYNC ---
@st.cache_data(ttl=3600)
def fetch_hub_data():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # Force column mapping to the specific Betfair Hub CSV structure
        name_col = 'meetings.races.runners.runnerName'
        price_col = 'meetings.races.runners.ratedPrice'
        
        # If the direct names fail, hunt for keywords
        if name_col not in df.columns:
            name_col = [c for c in df.columns if 'runner' in c.lower()][-1]
            price_col = [c for c in df.columns if 'rated' in c.lower()][-1]
            
        return dict(zip(df[name_col].astype(str).str.lower(), df[price_col].astype(float)))
    except:
        return {}

hub_db = fetch_hub_data()
reader = easyocr.Reader(['en'], gpu=False)

# --- 2. THE INTERFACE ---
paste_result = pbutton(label="📋 PASTE SCREENSHOT HERE", background_color="#FF4B4B")

if paste_result.image_data is not None:
    img = paste_result.image_data
    img_np = np.array(img)
    
    with st.spinner("🔍 Reading Market & Matching AI Prices..."):
        # OCR reads everything: names and numbers
        results = reader.readtext(img_np)
        
        final_table = []
        # We group the OCR results into "Lines" to keep horses with their prices
        for i, res in enumerate(results):
            text = res[1].lower().strip()
            
            # Check if this text is a Horse in our Hub Database
            if text in hub_db:
                ai_price = hub_db[text]
                
                # PRICE FINDER: Look at the next few OCR detections for the 'Back' price
                # In your screenshot, the live price usually follows the horse name
                live_price = None
                for j in range(i+1, min(i+5, len(results))):
                    val = results[j][1].replace(' ', '')
                    try:
                        potential_price = float(val)
                        if 1.01 <= potential_price <= 1000:
                            live_price = potential_price
                            break
                    except: continue
                
                if live_price:
                    gap = round(live_price - ai_price, 2)
                    # APPLY RULES: Selection must be < 6.0
                    status = "🎯 LAY" if (live_price < 6.0 and gap > 0.4) else "-"
                    
                    final_table.append({
                        "Horse": text.title(),
                        "AI Rated": ai_price,
                        "Live Price": live_price,
                        "Gap": gap,
                        "Selection": status
                    })

        # --- 3. DISPLAY RESULTS ---
        if final_table:
            df_res = pd.DataFrame(final_table).sort_values(by="Gap", ascending=False)
            
            def highlight(row):
                return ['background-color: #ff4b4b; color: white'] if "LAY" in str(row["Selection"]) else [''] * len(row)
            
            st.write("### 📊 Value Gap Analysis")
            st.table(df_res.style.apply(highlight, axis=1).format({"Gap": "+{:.2f}"}))
        else:
            st.error("No horses from today's Hub were found in your screenshot.")
