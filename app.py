import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- APP CONFIG ---
st.set_page_config(page_title="Global Lay Hub", page_icon="🏇", layout="wide")

st.title("🏇 Global Lay Hub: Live Radar")
st.subheader("Next 5 Chronological Races & AI Value Analysis")

# --- SIMULATED LIVE FEED ---
def get_next_5_races():
    now = datetime.now()
    # Generating 5 chronological races starting from "Now"
    data = []
    locations = ["Ascot", "Wolv", "Navan", "Sandown", "York"]
    horses = ["Fast Lane", "Slow Burn", "Market Mover", "Desert Drift", "Silver Bullet"]
    
    for i in range(5):
        race_time = (now + timedelta(minutes=15 * (i + 1))).strftime("%H:%M")
        # Simulating odds and AI ratings
        current_price = round(random.uniform(2.5, 8.0), 2)
        ai_rated_price = round(random.uniform(2.5, 5.0), 2)
        gap = round(current_price - ai_rated_price, 2)
        
        data.append({
            "Time": race_time,
            "Location": locations[i],
            "Horse": horses[i],
            "AI Rated Price": ai_rated_price,
            "Current Price": current_price,
            "Value Gap": gap,
            "Is_BH1": True if i == 2 else False # Simulating one BH1
        })
    return pd.DataFrame(data)

# --- SEARCH TRIGGER ---
if st.button("🚀 Scan Next 5 Races"):
    df = get_next_5_races()
    
    # IDENTIFY THE LAY SELECTION (Rules: Under 6.0, Largest Gap)
    # Filter for those under 6.0 first
    qualifiers = df[df["Current Price"] < 6.0].copy()
    
    lay_index = None
    if not qualifiers.empty:
        # Sort by Gap
        qualifiers = qualifiers.sort_values(by="Value Gap", ascending=False)
        # Apply BH1 Logic (Prioritize non-BH1 unless BH1 is the only/best)
        non_bh1 = qualifiers[qualifiers["Is_BH1"] == False]
        if not non_bh1.empty:
            best_horse = non_bh1.iloc[0]["Horse"]
        else:
            best_horse = qualifiers.iloc[0]["Horse"]
        
        lay_index = df[df["Horse"] == best_horse].index[0]

    # --- DISPLAY LOGIC ---
    def highlight_lay(row):
        if lay_index is not None and row.name == lay_index:
            return ['background-color: #ff4b4b; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    st.write("### 📊 Market Summary Table")
    st.write("Note: The row highlighted in **Red** is your identified Lay Selection.")
    
    # Apply styling and display
    styled_df = df.style.apply(highlight_lay, axis=1).format({
        "AI Rated Price": "{:.2f}",
        "Current Price": "{:.2f}",
        "Value Gap": "+{:.2f}"
    })
    
    st.table(styled_df)

    if lay_index is None:
        st.info("No selection currently qualifies (Price > 6.0 or no drift).")
    else:
        st.success(f"**Primary Lay Recommendation:** {df.iloc[lay_index]['Horse']} at {df.iloc[lay_index]['Time']}")

# --- HELP SECTION ---
with st.expander("Criteria Legend"):
    st.write("""
    * **AI Rated Price:** What the horse *should* be priced at.
    * **Current Price:** The actual live market price.
    * **Value Gap:** The difference (Drift). A higher positive number means a bigger drift.
    * **Red Highlight:** Meets all criteria: Under 6.0, High Drift, Priority Selection.
    """)
