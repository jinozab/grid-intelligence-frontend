import os
import requests
import pandas as pd
import streamlit as st

# API URL
if 'API_URI' in os.environ:
    BASE_URI = st.secrets[os.environ.get('API_URI')]
else:
    BASE_URI = st.secrets['cloud_api_uri']
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
url = BASE_URI + 'predict'

# Page config
st.set_page_config(page_title="Grid Intelligence", page_icon="⚡", layout="wide")

# Title
st.title("⚡ Grid Intelligence")
st.subheader("Day-Ahead Electricity Price Prediction — DE-LU Market")

# User Input
date = st.date_input("Select a date to predict")


st.markdown("""
    <style>
    div.stButton > button {
        background-color: #2ecc71;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #27ae60;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Call API
if st.button("Predict"):
    with st.spinner("Fetching prediction..."):
        response = requests.get(url, params={"date": str(date)})

    if response.status_code == 200:
        data = response.json()
        predictions = data["predictions_24h"]

        # Build dataframe
        df = pd.DataFrame({
            "hour": list(range(24)),
            "price (EUR/MWh)": predictions
        })

        # Chart
        st.line_chart(df.set_index("hour"))

        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Min Price", f"{min(predictions):.2f} EUR/MWh")
        col2.metric("Max Price", f"{max(predictions):.2f} EUR/MWh")
        col3.metric("Avg Price", f"{sum(predictions)/len(predictions):.2f} EUR/MWh")

    else:
        st.error(f"API Error: {response.status_code}")
