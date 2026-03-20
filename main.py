import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP", layout="centered")

# --- GELİŞMİŞ GÖRÜNÜRLÜK VE MODERN TASARIM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: white !important; color: #1a1a1a !important; }
    
    /* INPUT VE FORM ALANLARI (SAFARİ/IPHONE FIX) */
    input, select, textarea, [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    label { color: #333 !important; font-weight: bold !important; }

    /* YAKLAŞAN REZERVASYON KARTI */
    .alarm-card {
        background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%);
        color: white !important;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(255, 106, 136, 0.2);
        text-align: center;
    }

    /* TAKVİM VE DİĞER KARTLAR */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } 
    .dolu { background: #E74C3C !important; } 
    .opsiyon { background: #F1C40F !important; color: #1A1A1A !important; }
    
    .f-card {
        background: #ffffff !important; 
        padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 12px;
        border-left: 6px solid #007BFF; color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
init_db()
df = pd.read_csv("rez.csv")

# --- 🔔 YAKLAŞAN REZERVASYON SİSTEMİ ---
st.title("🏡 Detayvalık Yönetim")

today_str = datetime.now().strftime("%Y-%m-%d")
# Gelecekteki ilk rezervasyonu bul
future_rexs = df[df["Tarih"] >= today_str].sort_values(by="Tarih")

if not future_rexs.empty:
    next_rez = future_rexs.iloc[0]
    days_left = (datetime.strptime(next_rez["Tarih"], "%Y-%m-%d") - datetime.now()).days + 1
    
    if days_left == 0:
        uyari_metni = f"🚨 BUGÜN GİRİŞ VAR! \n {next_rez['Ad Soyad']}"
    else:
        uyari_metni = f"🔔 Yaklaşan Rezervasyon: {days_left} gün sonra \n {next_rez['Ad Soyad']} ({next_rez['Tarih']})"
    
    st.markdown(f'<div class="alarm-card"><h3>{uyari_metni}</h3></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alarm-card" style="background:#f0f2f6; color:#666 !important;">Şu an yakın bir rezervasyon görünmüyor.</div>', unsafe_allow_html=True)

# --- SEKMELER ---
selected_date = st.query_params.get("date", "")
t1, t2, t3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Dönem", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    # Takvim Çizimi (v12.5 ile aynı stabil yapı)
    cal_html = '<table class="modern-table"><thead><tr>'
    for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]: cal_html += f'<th>{g}</th>'
    cal_html += '</tr></thead><tbody>'
    cal = calendar.monthcalendar(2026, ay_no)
    for week in cal:
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                t_str = f"2026-{ay_no:02d}-{day:02d}"
                is_full = df[df["Tarih"] == t_str]
                cls = "bos"
                if not is_full.empty:
                    cls = "dolu" if is_full.iloc[0]["Durum"] == "Kesin" else "opsiyon"
                cal_html += f'<td><a href="?date={t_str}" target="_self" class="day-link {cls}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</tbody></table>', unsafe_allow_html=True)

    # Rezervasyon Formu
    with st.expander("📝 Kayıt Yap", expanded=True if selected_date else False):
        with st.form("r_form"):
            f_tar = st.text_input("Seçili Tarih", value=selected_date)
            f_ad = st.text_input("Müşteri Ad Soyad")
            f_tel = st.text_input("WhatsApp (90...)")
            f_ucret = st.number_input("Günlük Ücret", min_value=0)
            f_gece = st.number_input("Gece", min_value=1)
            if st.form_submit_button("KAYDET"):
                # Kayıt mantığı...
                start = datetime.strptime(f_tar, "%Y-%m-%d")
                rows = [[(start + timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_ucret, f_gece, "", "Kesin", f_ucret*f_gece] for i in range(int(f_gece))]
                pd.concat([df, pd.DataFrame(rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                st.rerun()

# Finans Sekmesi (v12.5 ile aynı)
with t3:
    # ... Finansal hesaplamalar ...
    st.write("Finansal özet burada görünecek.")
