import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık Operasyon v42.5.1", layout="wide", page_icon="🏡")

# Modern Tasarım CSS (Mobil Uyumluluk & Dolgun Butonlar)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 26px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 12px; margin-bottom: 20px; }
    .stat-box { background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Mobil Dostu Takvim Ayarları */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 8px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 20px 0; border-radius: 12px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 18px;
        transition: transform 0.1s; border-bottom: 4px solid rgba(0,0,0,0.2);
    }
    .day-link:active { transform: translateY(2px); border-bottom: 2px solid rgba(0,0,0,0.2); }
    .bos { background: #10b981 !important; } /* Yeşil */
    .dolu { background: #ef4444 !important; } /* Kırmızı */
    
    .info-card { background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 6px solid #3B82F6; margin: 15px 0; }
    .stForm { background: white !important; border-radius: 15px !important; padding: 20px !important; border: 1px solid #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (UTF-8-SIG & HATA KONTROLÜ) ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ =
