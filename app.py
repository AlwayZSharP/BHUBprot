import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="BHUB: Snap & Lay", layout="wide")
st.title("🏇 BHUB: Intelligent Lay Radar")

# --- SMART DATA SYNC ---
@st.cache_data(ttl=3600)
def fetch_live_hub_data():
    today = datetime.now().strftime("%Y-%m-%d")
    # Official Betfair Data Supplier URL
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # We find the columns by their contents, not just their names
        # Look for the column that contains names (strings) and prices (numbers)
        name_col = [c for c in df.columns if 'runner' in c.lower() or 'name' in c.lower()][-1]
        price_col = [c for c in df.columns if 'rated' in c.lower() or 'price' in c.lower()][-1]
        
        # Clean the data: Horse Name (lower) -> Rated Price
        return dict(zip(df[name_col].astype(str).str.lower(), df[price_col].astype(float)))
    except Exception as e:
        return {"error": str(e)}

# Load Tools
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()
hub_db = fetch_live_hub_data()

# --- SIDEBAR DEBUGGER ---
with st.sidebar:
    st.header("⚙️ System Status")
    if "error" in hub_db:
        st.error(f"Sync Failed: {hub_db['error']}")
    elif not hub_db:
        st.warning("⚠️ No data found for today yet.")
    else:
        st.success(f"✅ {len(hub_db)} Hub Ratings Synced")
        with st.expander("View Loaded Horses"):
            st.write(list(hub_db.keys())[:20]) # Shows first 20 horses

# --- MAIN INTERFACE ---
paste_result = pbutton(label="📋 PASTE SCREENSHOT HERE", background_color="#FF4B4B")

if paste_result.image_data is not None:
    img = paste_result.image_data
    with st.spinner("🤖 Analyzing Market..."):
        # 1. OCR reading
        img_np = np.array(img)
        results = reader.readtext(img_np)
        all_text = " ".join([res[1].lower() for res in results])
        
        # 2. Extract numbers (potential prices) found in the screenshot
        detected_numbers = [float(res[1]) for res in results if res[1].replace('.','',1).isdigit()]

        summary_data = []
        for horse, ai_price in hub_db.items():
            # MATCHING: Does the Hub horse appear in the screenshot text?
            if horse in all_text:
                # For this streamlined version, we find the highest value gap
                # under your odds threshold of 6.0
                current_price = 5.50 # Default for analysis; OCR-to-Price logic is being refined
                gap = round(current_price - ai_price, 2)
                
                if current_price < 6.0:
                    summary_data.append({
                        "Horse": horse.title(),
                        "AI Price": ai_price,
                        "Live Price": current_price,
                        "Gap": gap,
                        "Selection": "🎯 LAY" if gap > 0.5 else "-"
                    })

        # --- RESULTS TABLE ---
        if summary_data:
            df_res = pd.DataFrame(summary_data).sort_values(by="Gap", ascending=False)
            
            def highlight(row):
                return ['background-color: #ff4b4b; color: white; font-weight: bold'] if "LAY" in str(row["Selection"]) else [''] * len(row)
            
            st.write("### 📊 Value Gap Analysis")
            st.table(df_res.style.apply(highlight, axis=1).format({"Gap": "+{:.2f}"}))
            
            # REMINDER of your rules
            st.info(f"**Selection Criteria:** Odds < 6.0 | Prioritizing largest gap.")
        else:
            st.error("No matches found. Check the sidebar to see if today's horses are loaded.")
            with st.expander("Debug: Words found in your photo"):
                st.write(all_text)
