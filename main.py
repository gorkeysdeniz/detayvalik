import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="wide", page_icon="🏡")

# Görsel çakışmaları bitiren ana stil
st.markdown("""
    <style>
        @media (prefers-color-scheme: light) {
            .stApp { background-color: #FFFFFF !important; }
            h1, h2, h3, p, label, span { color: #1e293b !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-color: #0E1117 !important; }
            h1, h2, h3, p, label, span { color: #FFFFFF !important; }
        }
        /* Butonları her iki modda da görünür yap */
        .stButton button { 
            background-color: #8FD9C8 !important; 
            color: #000000 !important; 
            font-weight: 700 !important; 
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Finans Kartı Fonksiyonu (Yazı tipi 900 Extra Bold)
def finans_kart_olustur(baslik, deger, renk="#1E293B"):
    st.markdown(f"""
        <div style="background-color: {renk}; padding: 22px; border-radius: 18px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
            <p style="margin: 0; font-size: 13px; color: #FFFFFF !important; font-weight: 700; text-transform: uppercase;">{baslik}</p>
            <h2 style="margin: 5px 0 0 0; font-size: 32px; color: #FFFFFF !important; font-weight: 900;">{deger}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- 2. SEKMELER (TABS) ---
tab1, tab2 = st.tabs(["📅 Takvim", "💰 Finansal Analiz"])

with tab1:
    st.header("Villa Müsaitlik Takvimi")
    st.write("Burada takvim kodların yer alacak.")

with tab2:
    st.header("💰 Mart Finansal Analizi")
    
    # Rakamları buraya bağla
    gelir = 50000
    gider = 5000
    vergi = gelir * 0.12
    net = gelir - gider - vergi

    c1, c2 = st.columns(2)
    with c1:
        finans_kart_olustur("BRÜT GELİR", f"{gelir:,} TL", "#1E293B")
        finans_kart_olustur("GİDER TOPLAMI", f"-{gider:,} TL", "#EF4444")
    with c2:
        finans_kart_olustur("VERGİ TAHMİNİ", f"-{vergi:,.0f} TL", "#334155")
        finans_kart_olustur("BU AYIN NET KARI", f"{net:,.0f} TL", "#10B981")
