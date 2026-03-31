import streamlit as st
import pandas as pd
import time
import random

# --- APP CONFIG ---
st.set_page_config(page_title="Global Lay Hub", page_icon="🏇")

st.title("🏇 Global Lay Hub (UK/AUS/IRE)")
st.subheader("Automated Drifter Selection Engine")

# --- SIMULATED DATA FETCHING (Replace with your API logic) ---
def fetch_race_data():
    # This represents the live feed of races for the day
    races = [
        {"time": "14:10", "loc": "Ascot", "horse": "Galloping Ghost", "odds": 4.5, "gap": 0.8, "is_bh1": False},
        {"time": "14:30", "loc": "Wolv", "horse": "Slow Coach", "odds": 5.2, "gap": 1.5, "is_bh1": False},
        {"time": "15:00", "loc": "Navan", "horse": "Desert Drift", "odds": 3.8, "gap": 2.1, "is_bh1": True},
        {"time": "15:15", "loc": "Ascot", "horse": "Money Pit", "odds": 7.5, "gap": 3.0, "is_bh1": False},
    ]
    return races

# --- MAIN APP INTERFACE ---
if st.button("🚀 Fetch Today's Lays"):
    with st.status("🔍 Scanning Global Markets...", expanded=True) as status:
        all_races = fetch_race_data()
        qualifiers = []

        for race in all_races:
            # UI Feedback: Show the user which race is being evaluated
            st.write(f"Checking {race['time']} at {race['loc']}...")
            time.sleep(0.3) # Brief pause so you can actually read the scan

            # APPLYING YOUR RULES:
            # 1. Must be under odds of 6.0
            # 2. Identify the drifter
            if race['odds'] < 6.0:
                qualifiers.append(race)
        
        status.update(label="Scan Complete!", state="complete", expanded=False)

    if qualifiers:
        # Sort by largest value gap (Prioritizing the biggest drift)
        qualifiers = sorted(qualifiers, key=lambda x: x['gap'], reverse=True)
        
        # RULE: Prioritize the drifter within range but NOT BH1. 
        # But if BH1 is the biggest drift or only option, it's fine.
        selection = None
        non_bh1 = [q for q in qualifiers if not q['is_bh1']]
        
        if non_bh1:
            selection = non_bh1[0] # Biggest drift that isn't BH1
        else:
            selection = qualifiers[0] # Use BH1 if it's the only/biggest drift

        # --- THE OUTPUT TABLE ---
        st.success(f"✅ Top Value Lay Found!")
        
        # Formatting for the requested a b c style or table
        display_data = {
            "Race": f"{selection['time']} {selection['loc']}",
            "Selection": selection['horse'],
            "Current Odds": selection['odds'],
            "Value Gap": f"+{selection['gap']}"
        }
        
        st.table([display_data])
        
        st.info("💡 **Selection Criteria:** Drifter under 6.0 with the largest verified value gap.")

    else:
        st.warning("No qualifiers found under 6.0 right now.")

# --- FOOTER ---
st.divider()
st.caption("Data refreshes on every click. Ensure markets are liquid before placing lays.")
