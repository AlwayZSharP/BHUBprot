import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Global Lay Hub", page_icon="🏇", layout="wide")
st.title("🏇 Global Lay Hub (UK/AUS/IRE)")

# API Endpoints for Betfair Hub Models
ENDPOINTS = {
    "UK/IRE Horses": "https://betfair-data-supplier-prod.herokuapp.com/api/widgets/uk-racing-model/datasets",
    "AUS Horses": "https://betfair-data-supplier-prod.herokuapp.com/api/widgets/kash-ratings-model/datasets",
    "AUS Greyhounds": "https://betfair-data-supplier-prod.herokuapp.com/api/widgets/greyhound-model/datasets"
}

def get_data():
    all_data = []
    for region, url in ENDPOINTS.items():
        try:
            res = requests.get(url).json()
            races = res.get('datasets', [])
            for race in races:
                venue = race.get('venue', 'Unknown')
                time = race.get('race_time', '')
                for r in race.get('runners', []):
                    rated = float(r.get('rated_price', 999))
                    live = float(r.get('live_price', 0))
                    if 1.1 <= live <= 6.0 and live > rated:
                        all_data.append({
                            'Region': region,
                            'Race': f"{venue} {time}",
                            'Runner': r.get('name'),
                            'Live': live,
                            'Rated': rated,
                            'Gap': round(live - rated, 2),
                            'is_bh1': r.get('is_favorite', False)
                        })
        except: continue
    return pd.DataFrame(all_data)

# --- APP LOGIC ---
if st.button("🚀 Fetch Today's Lays"):
    df = get_data()
    if not df.empty:
        # Sort by largest gap as per your rules
        df = df.sort_values('Gap', ascending=False)
        
        st.subheader("Section A: Top Selection")
        # Rule: Prioritize largest drift, but if BH1 is biggest it's okay.
        top = df.iloc[0]
        st.success(f"**Selection:** {top['Runner']} | **Race:** {top['Race']} | **Odds:** {top['Live']}")
        
        st.subheader("Section B: Summary Table")
        st.table(df[['Region', 'Race', 'Runner', 'Live', 'Gap']].head(5))
        
        st.subheader("Section C: Compliance")
        st.write(f"✅ Odds {top['Live']} is under 6.0")
        st.write(f"✅ Value Gap of {top['Gap']} identified")
    else:
        st.warning("No qualifiers found under 6.0 right now.")
