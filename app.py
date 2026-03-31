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

# Load the OCR engine
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
    # IMPORTANT: paste_result.image_data is already a PIL Image!
    # No need for Image.open()
    img = paste_result.image_data 
    st.image(img, caption="Market Detected", width=300)
    
    with st.spinner("🤖 AI is matching prices with Betfair Hub..."):
        # Convert image to a format the OCR can read
        img_np = np.array(img)
        results = reader.readtext(img_np)
        
        # This combines all the text found in the image into one string
        all_detected_text = " ".join([res[1].lower() for res in results])

        # --- SIMULATED DATA (This is where your Hub scraper lives) ---
        hub_data = [
            {"Horse": "Fast Lane", "AI Price": 3.40},
            {"Horse": "Slow Burn", "AI Price": 4.10},
            {"Horse": "Desert Drift", "AI Price": 5.50},
            {"Horse": "Silver Bullet", "AI Price": 4.20},
        ]

        summary_data = []
        for item in hub_data:
            # Check if the horse name from the Hub appears anywhere in your photo
            if item["Horse"].lower() in all_detected_text:
                # Simulated current price - in a real version we'd parse the numbers
                # located physically next to the horse's name in the image.
                current_price = 5.20 
                gap = round(current_price - item["AI Price"], 2)
                
                summary_data.append({
                    "Horse": item["Horse"],
                    "AI Rated": item["AI Price"],
                    "Current": current_price,
                    "Gap": gap,
                    "Selection": "🎯 LAY" if (current_price < 6.0 and gap > 0.5) else "-"
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
            st.warning("⚠️ No matches found. Make sure the horse names are visible in the screenshot.")
            st.write("Words detected in your photo:", all_detected_text)

st.divider()
st.caption("Instructions: Screenshot Betfair -> Tap 'Paste' button -> Get Lay.")
