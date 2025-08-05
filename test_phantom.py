# test_phantom.py
import sys
import os
sys.path.append(os.path.abspath("."))  # Adds current directory to the path

from phantom_connect.phantom_connect import connect_phantom
import streamlit as st

st.title("🔐 Phantom Wallet Connect Demo")

wallet = connect_phantom()

if wallet:
    st.success(f"Connected wallet: {wallet}")
else:
    st.info("Please connect your Phantom wallet.")
