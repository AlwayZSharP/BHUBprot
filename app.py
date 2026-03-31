import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from streamlit_paste_button import paste_image_button as pbutton

# --- APP CONFIG ---
st.set_page_config(page_title="BHUB: Snap & Lay", layout="wide")

st.title("🏇 BHUB: Snap & Lay Radar")
st.write("Screenshot your Betfair market, then tap the button below.")

# Load the OCR engine (cached for speed)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

reader = load_reader()

# --- THE PASTE BOX ---
paste_result = pbutton(
    label="📋 PASTE SCREENSHOT HERE",
    background_color="#FF4B4B",
    hover_background_color="#D33636",
)

# --- PROCESSING LOGIC ---
if paste_result.image_data is not None:
    # 1. Display the pasted image
    st.image(paste_result.image_data, caption="Market Detected", width=300)
    
    with st.spinner("🤖 AI is matching prices with Betfair Hub..."):
        # Convert pasted image to a format the AI can read
        img = Image.open(paste_result.image_data)
        img_np = np.array(img)
        
        # OCR reads the horse names and odds
        results = reader.readtext(img_np)
        detected_text = " ".join([res[1] for res in results])

        # --- OPTION 2: AUTO-MATCHING DATA ---
        # This part simulates the 'Scraper' finding the Hub AI prices 
        # for whatever horses it just read in your screenshot.
        hub_data = [
            {"Horse": "Horse A", "AI Price": 3.40},
            {"Horse": "Horse B", "AI Price": 4.10},
            {"Horse": "Horse C", "AI Price": 5.50},
        ]

        summary_data = []
        for item in hub_data:
            # If the horse name from the Hub is found in your screenshot text:
            if item["Horse"].lower() in detected_text.lower():
                # We pull the live price (simulated for this example)
                live_price = 5.20 
                gap = round(live_price - item["AI Price"], 2)
                
                summary_data.append({
                    "Horse": item["Horse"],
                    "AI Rated": item["AI Price"],
                    "Current": live_price,
                    "Gap": gap,
                    "Selection": "🎯 LAY" if (live_price < 6.0 and gap > 0.8) else "-"
                })

        # --- THE RESULT TABLE ---
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            def highlight_row(row):
                if "LAY" in str(row["Selection"]):
                    return ['background-color: #ff4b4b; color: white; font-weight: bold'] * len(row)
                return [''] * len(row)

            st.write("### 📊 Live Value Analysis")
            st.table(df.style.apply(highlight_row, axis=1).format({"Gap": "+{:.2f}"}))
        else:
            st.warning("Could not match horses. Ensure names are clear in the screenshot.")

st.divider()
st.caption("Instructions: Screenshot Betfair -> Tap 'Paste' button -> Get Lay.")
