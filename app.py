import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# --- APP CONFIG ---
st.set_page_config(page_title="Global Lay Hub", page_icon="🏇", layout="wide")

st.title("🏇 Global Lay Hub: Live Radar")
st.subheader("Next 5 Chronological Races & AI Value Analysis")

# --- DATA GENERATOR ---
def get_next_5_races():
    now = datetime.now()
    data = []
    locations = ["Ascot", "Wolv", "Navan", "Sandown", "York"]
    horses = ["Fast Lane", "Slow Burn", "Market Mover", "Desert Drift", "Silver Bullet"]
    
    for i in range(5):
        race_time = (now + timedelta(minutes=15 * (i + 1))).strftime("%H:%M")
        # Current Price (Market)
        current_price = round(random.uniform(2.5, 8.0), 2)
        # AI Rated Price (Value)
        ai_rated_price = round(random.uniform(2.5, 5.5), 2)
        gap = round(current_price - ai_rated_price, 2)
        
        data.append({
            "Time": race_time,
            "Location": locations[i],
            "Horse": horses[i],
            "AI Rated": ai_rated_price,
            "Current": current_price,
            "Gap": gap,
            "Is_BH1": True if i == 2 else False
        })
    return pd.DataFrame(data)

# --- APP LOGIC ---
if st.button("🚀 Scan Next 5 Races"):
    df = get_next_5_races()
    
    # 1. Qualify: Under 6.0 and Drifting (Gap > 0)
    qualifiers = df[(df["Current"] < 6.0) & (df["Gap"] > 0)].copy()
    
    lay_selection_horse = None
    if not qualifiers.empty:
        # Sort by Gap (Largest drift first)
        qualifiers = qualifiers.sort_values(by="Gap", ascending=False)
        # Rule: Priority to non-BH1
        non_bh1 = qualifiers[qualifiers["Is_BH1"] == False]
        if not non_bh1.empty:
            lay_selection_horse = non_bh1.iloc[0]["Horse"]
        else:
            lay_selection_horse = qualifiers.iloc[0]["Horse"]

    # --- THE SUMMARY TABLE ---
    st.write("### 📊 Market Summary")

    def make_pretty(row):
        # If this horse is our chosen Lay, highlight the whole row RED
        if lay_selection_horse and row["Horse"] == lay_selection_horse:
            return ['background-color: #ff4b4b; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    # Clean up the table for display
    styled_df = df.style.apply(make_pretty, axis=1).format({
        "AI Rated": "{:.2f}",
        "Current": "{:.2f}",
        "Gap": "+{:.2f}"
    })

    st.table(styled_df)

    # --- FINAL VERDICT ---
    if lay_selection_horse:
        st.success(f"🎯 **LAY SELECTION:** {lay_selection_horse} (Highlighted Red)")
    else:
        st.info("ℹ️ No horse currently meets the 'Under 6.0 + Drift' criteria.")

# --- FOOTER ---
st.divider()
st.caption("Evaluation includes the next 5 chronological races. Highlight indicates the optimal value drift.")
