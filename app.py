import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(layout="wide")  # Use wide mode

st.title("Global Economic Monitor Dashboard")

# World Bank API base URL
BASE_URL = "https://api.worldbank.org/v2"

# Function to fetch World Bank data
@st.cache_data  # Add caching to speed up repeated queries
def fetch_wb_data(indicator, country, start_date=None, end_date=None):
    """
    Fetch data from World Bank API
    """
    if isinstance(country, list):
        country = ';'.join(country)
        
    url = f"{BASE_URL}/country/{country}/indicator/{indicator}"
    
    params = {
        'format': 'json',
        'per_page': 1000,
        'date': f"{start_date}:{end_date}"
    }
        
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            return data[1]
    return None

# Expanded indicators
wb_indicators = {
    'NY.GDP.MKTP.CD': 'GDP (current US$)',
    'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
    'FP.CPI.TOTL.ZG': 'Inflation, consumer prices (annual %)',
    'NE.TRD.GNFS.ZS': 'Trade (% of GDP)',
    'BN.CAB.XOKA.GD.ZS': 'Current Account Balance (% of GDP)',
    'FI.RES.TOTL.CD': 'Total reserves',
    'SL.UEM.TOTL.ZS': 'Unemployment rate',
    'NY.GDP.MKTP.KD.ZG': 'GDP growth (annual %)',
    'BX.KLT.DINV.WD.GD.ZS': 'Foreign direct investment (% of GDP)',
    'GC.DOD.TOTL.GD.ZS': 'Government debt to GDP (%)'
}

# Expanded country list
countries = {
    'USA': 'United States',
    'CHN': 'China',
    'JPN': 'Japan',
    'DEU': 'Germany',
    'GBR': 'United Kingdom',
    'FRA': 'France',
    'IND': 'India',
    'BRA': 'Brazil',
    'CAN': 'Canada',
    'AUS': 'Australia',
    'KOR': 'South Korea',
    'RUS': 'Russia',
    'ZAF': 'South Africa',
    'MEX': 'Mexico'
}

# Sidebar
with st.sidebar:
    st.header("Data Selection")
    
    # Multi-country selection
    selected_countries = st.multiselect(
        "Choose countries (max 5)",
        options=list(countries.keys()),
        default=['USA'],
        format_func=lambda x: countries[x],
        max_selections=5
    )

    selected_indicator = st.selectbox(
        "Choose an indicator",
        options=list(wb_indicators.keys()),
        format_func=lambda x: wb_indicators[x]
    )

    # Analysis options
    st.header("Analysis Options")
    show_trend = st.checkbox("Show Trend Line", value=True)
    
    # Date range
    st.header("Time Period")
    end_date = datetime.now().year
    start_date = st.slider(
        "Select Year Range",
        min_value=1960,
        max_value=end_date,
        value=end_date-20
    )

# Main content
try:
    if not selected_countries:
        st.warning("Please select at least one country.")
    else:
        # Fetch data for all selected countries
        data = fetch_wb_data(
            selected_indicator,
            selected_countries,
            start_date=start_date,
            end_date=end_date
        )
        
        if data:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_numeric(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remove columns layout and use full width for graph
            fig = px.line(
                df,
                x='date',
                y='value',
                color='countryiso3code',
                labels={'countryiso3code': 'Country', 'value': wb_indicators[selected_indicator]},
                title=f"{wb_indicators[selected_indicator]} Over Time"
            )
            
            if show_trend:
                for country in selected_countries:
                    country_data = df[df['countryiso3code'] == country]
                    if not country_data.empty:
                        z = np.polyfit(country_data['date'], country_data['value'].fillna(0), 1)
                        p = np.poly1d(z)
                        fig.add_trace(
                            go.Scatter(
                                x=country_data['date'],
                                y=p(country_data['date']),
                                name=f"{countries[country]} trend",
                                line=dict(dash='dash'),
                                opacity=0.5
                            )
                        )
            
            # Make the chart larger
            fig.update_layout(
                height=700,  # Increase height
                width=None,  # Allow width to be responsive
                margin=dict(l=40, r=40, t=40, b=40)  # Adjust margins
            )
            
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='display: flex; justify-content: space-between; align-items: center;'>
    <div>Data source: World Bank Open Data</div>
    <div>
        <a href='www.linkedin.com/in/tom-granit-b27947137' target='_blank'>
            <img src='https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Logo.svg.original.svg' 
                 width='80px' 
                 alt='LinkedIn'/>
        </a>
        &nbsp;&nbsp;
        <a href='YOUR_X_URL' target='_blank'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg' 
                 width='30px' 
                 alt='X'/>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
