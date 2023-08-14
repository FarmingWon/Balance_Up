import base64
from pathlib import Path
import streamlit as st

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


html = """
<h1>준비 중입니다.</h1>
"""

st.markdown(html, unsafe_allow_html=True)
with st.sidebar:
    htmlSide=f"""
        <br/>
        <p></p>
    """
    st.markdown(htmlSide, unsafe_allow_html=True)
    st.sidebar.markdown("---")

