import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

st.set_page_config(
    layout='wide'
)

intro_markdown = read_markdown_file("README.md")
st.markdown(intro_markdown, unsafe_allow_html=True)

st.title("Lego-Baustein-Rüstungszeit-Optimierungs-Software-Dingsbums")
st.markdown("Diese Software dient der Optimierung der Rüstzeiten -und Vorgänge eines Produktionssystems. Es kann das Produktionssystem bestehend aus Maschinen, Mitarbeitern, Kosten, Skills usw. initiallisiert werden. Anschließend kann das System simuliert werden, um die Rüstzeiten zu optimieren.")
