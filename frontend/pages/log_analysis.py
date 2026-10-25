"""
CodeSecure AI — Log Analysis Page Entrypoint
"""
import streamlit as st

st.set_page_config(page_title="CodeSecure AI — Log Analysis", layout="wide")

try:
    st.switch_page("streamlit_app.py")
except Exception:
    st.info("CodeSecure AI runs on a unified interactive platform.")
    st.page_link("streamlit_app.py", label="Open CodeSecure AI Platform")
