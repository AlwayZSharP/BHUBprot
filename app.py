import streamlit as st
import pandas as pd
import numpy as np
import easyocr
from streamlit_paste_button import paste_image_button as pbutton
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="BHUB: Snap & Lay", layout="wide")
st.title("🏇 BHUB: Streamlined Lay Radar")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

# --- AUTO-FETCH RATINGS ---
@st.cache_data(ttl=3600) # Refresh data every hour
def fetch_hub_ratings():
    today = datetime.now().strftime("%Y-%m-%d")
    # This is the direct data link for the Betfair Hub models (e.g., 'Kash' or 'Iggy')
    url = f"https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets?date={today}&presenter=RatingsPresenter&csv=true"
    try:
        df = pd.read_csv(url)
        # Simplify the data to just: Horse Name -> Rated Price
        # (Column names adjusted to match Betfair Hub's standard CSV export)
        df.columns = [c.lower() for c in df.columns]
        # We look for common name/rating columns
        name_col = [c for c in df.columns if 'runner' in c or 'name' in c][0]
        price_col = [c for c in df.columns if 'rated' in c or 'price' in c][0]
        return dict(zip(df[name_col].str.lower(), df[price_col]))
    except:
        return {}

# Load tools
reader = load_reader()
hub_db = fetch_hub_ratings()

if not hub_db:
    st.warning("⚠️ Could not auto-sync Betfair Hub ratings. Check internet or site status.")

# --- THE FAST-PASTE INTERFACE ---
paste_result = pbutton(label="📋 PASTE SCREENSHOT HERE", background_color="#FF4B4B")

if paste_result.image_data is not None:
    img = paste_result.image_data
    with st.spinner("🤖 Analyzing Market..."):
        img_np = np.array(img)
        results = reader.readtext(img_np)
        all_text = " ".join([res[1].lower() for res in results])

        summary_data = []
        for horse_name, ai_price in hub_db.items():
            if horse_name in all_text:
                # We found a match!
                # In a real run, you'd want to parse the current price from OCR too.
                # Here we assume a placeholder current price to show the logic.
                current_price = 5.20 
                gap = round(current_price - ai_price, 2)
                
                # YOUR RULES: Under 6.0 and Drifting
                if current_price < 6.0:
                    summary_data.append({
                        "Horse": horse_name.title(),
                        "AI Rated": ai_price,
                        "Current": current_price,
                        "Gap": gap,
                        "Selection": "🎯 LAY" if gap > 0.4 else "-"
                    })

        if summary_data:
            df_res = pd.DataFrame(summary_data)
            # Prioritize the drifter with the largest gap
            df_res = df_res.sort_values(by="Gap", ascending=False)
            
            def highlight_row(row):
                return ['background-color: #ff4b4b; color: white; font-weight: bold'] if "LAY" in str(row["Selection"]) else [''] * len(row)
            
            st.write("### 📊 Value Analysis")
            st.table(df_res.style.apply(highlight_row, axis=1).format({"Gap": "+{:.2f}"}))
        else:
            st.error("Could not find any horses from the screenshot in today's Hub Ratings.")
