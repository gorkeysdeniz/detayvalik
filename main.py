# --- MODERN TASARIM DOKUNUŞLARI (CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #F7F9FC !important; }

    /* Modern Takvim Hücreleri */
    .calendar-table td { 
        border: none !important; 
        padding: 8px !important;
    }
    .day-link {
        border-radius: 12px !important; /* Tam yuvarlak köşeler */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Hafif gölge */
        transition: 0.3s; /* Geçiş efekti */
    }
    .day-link:hover { transform: scale(1.05); } /* Üstüne gelince büyüme */

    /* Yumuşak Renk Paleti */
    .bos { background: linear-gradient(135deg, #2ecc71, #27ae60) !important; }
    .dolu { background: linear-gradient(135deg, #e74c3c, #c0392b) !important; }
    .opsiyon { background: linear-gradient(135deg, #f1c40f, #f39c12) !important; color: white !important; }

    /* Finans Kartları (Premium Look) */
    .f-card {
        background: white !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
        margin-bottom: 15px;
    }
    
    /* Sekmeler (Tabs) */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
