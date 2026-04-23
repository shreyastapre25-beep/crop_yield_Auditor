import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# ==============================================================================
# 1. CORE LOGIC CLASSES (Extracted from your CLI code)
# ==============================================================================
class AgriLogic:
    @staticmethod
    def calculate_yield(area, greenness):
        return area * (greenness / 100.0)

    @staticmethod
    def quick_sort(data, key="Yield"):
        if len(data) <= 1: return data
        pivot = data[len(data) // 2][key]
        higher = [x for x in data if x[key] > pivot]
        equal = [x for x in data if x[key] == pivot]
        lower = [x for x in data if x[key] < pivot]
        return AgriLogic.quick_sort(higher) + equal + AgriLogic.quick_sort(lower)

def get_farmer_feedback(p_yield, area):
    efficiency = p_yield / area
    if efficiency >= 0.85:
        return "🌟 Appreciation: Elite Performance! Your plot is a model for others.", "success"
    elif efficiency >= 0.50:
        return "👍 Motivation: Good Progress. Stable yield detected.", "info"
    else:
        return "🌱 Advice: Needs Attention. Increase irrigation and fertilizer.", "warning"

# ==============================================================================
# 2. STREAMLIT WEB UI CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="AgriGuard Web Portal", layout="wide")

st.title("🛰️ AgriGuard: Satellite Audit Dashboard")
st.markdown("---")

# Persistent Database File
DB_FILE = "persistent_audit_log.csv"

# Load Data
if os.path.exists(DB_FILE):
    master_df = pd.read_csv(DB_FILE)
else:
    master_df = pd.DataFrame(columns=['Date', 'Farmer', 'Area', 'Greenness', 'Yield'])

# ==============================================================================
# 3. SIDEBAR - DATA ENTRY (Replacing terminal input)
# ==============================================================================
with st.sidebar:
    st.header("📍 New Audit Entry")
    with st.form("audit_form", clear_on_submit=True):
        f_name = st.text_input("Farmer Name")
        p_area = st.number_input("Area (Acres)", min_value=0.1, value=10.0)
        # Strict 0-100 Constraint
        p_green = st.slider("Satellite Greenness Index (%)", 0, 100, 75)
        
        submit_btn = st.form_submit_button("Run Audit & Save")

if submit_btn:
    # Perform Calculations
    current_yield = AgriLogic.calculate_yield(p_area, p_green)
    msg, theme = get_farmer_feedback(current_yield, p_area)
    
    # PROGRESS TRACKING (Time-Series)
    history = master_df[master_df['Farmer'] == f_name]
    if not history.empty:
        prev_yield = history.iloc[-1]['Yield']
        diff = current_yield - prev_yield
        st.session_state.trend = f"Trend: {'📈 Gain' if diff > 0 else '📉 Loss'} of {abs(diff):.2f} Tons"
    else:
        st.session_state.trend = "🆕 First audit for this farmer."

    # Save to Database
    new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), f_name, p_area, p_green, current_yield]], 
                             columns=master_df.columns)
    master_df = pd.concat([master_df, new_entry], ignore_index=True)
    master_df.to_csv(DB_FILE, index=False)
    
    st.sidebar.success("Audit Recorded!")

# ==============================================================================
# 4. MAIN PANEL - DASHBOARD & VISUALS
# ==============================================================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Audit Summary")
    if submit_btn:
        st.metric("Predicted Yield", f"{current_yield:.2f} Tons")
        if theme == "success": st.success(msg)
        elif theme == "info": st.info(msg)
        else: st.warning(msg)
        st.write(f"**Status:** {st.session_state.trend}")

with col2:
    st.subheader("📈 Productivity Rankings")
    if not master_df.empty:
        # Convert to list for our Quick Sort
        records = master_df.to_dict('records')
        sorted_records = AgriLogic.quick_sort(records)
        st.table(pd.DataFrame(sorted_records).tail(5))

st.divider()

# GRAPHING SECTION
st.subheader("🗺️ Visual Analytics")
v_col1, v_col2 = st.columns(2)

with v_col1:
    if not master_df.empty:
        st.markdown("**Yield Comparison (Bar Chart)**")
        fig, ax = plt.subplots()
        sns.barplot(data=master_df.tail(10), x='Farmer', y='Yield', palette='viridis', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

with v_col2:
    if not master_df.empty:
        st.markdown("**Health Distribution (Histogram)**")
        fig2, ax2 = plt.subplots()
        sns.histplot(master_df['Greenness'], bins=5, kde=True, color='purple', ax=ax2)
        st.pyplot(fig2)

# ==============================================================================
# 5. FOOTER
# ==============================================================================
st.caption("Developed by FY B.Tech Student | AI & Data Science | Vishwakarma University")