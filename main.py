import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(page_title="Detayvalık VIP", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white !important; color: #1a1a1a !important; }
    
    /* IPHONE/SAFARİ YAZI RENGİ FİX */
    input, select, textarea, [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    label { color: #333 !important; font-weight: bold !important; }

    /* MODERN ALARM KARTI */
    .alarm-card {
        background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%);
        color: white !important; padding: 20px; border-radius: 15px;
        margin-bottom: 20px; text-align: center;
        box-shadow: 0 10px 20px rgba(255, 106, 136, 0.2);
    }

    /* TAKVİM DÜZENİ */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } 
    .dolu { background: #E74C3C !important; } 
    .opsiyon { background: #F1C40F !important; color: #1A1A1A !important; }
    
    /* FİNANS KARTLARI (SİYAHA ZORLANMIŞ) */
    .f-card {
        background: white !important; padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 12px;
        border-left: 6px solid #007BFF; color: #000000 !important;
    }
    .f-card b, .f-card span { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)

init_db()
df = pd.read_csv("rez.csv")

# --- 3. YAKLAŞAN REZERVASYON (GÖRSELDEKİ BÖLÜM) ---
st.title("🏡 Detayvalık Yönetim")
today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
future = df[df["Tarih"] >= today_str].sort_values(by="Tarih")

if not future.empty:
    next_r = future.iloc[0]
    d_left = (datetime.strptime(next_r["Tarih"], "%Y-%m-%d") - today).days + 1
    txt = f"🚨 BUGÜN GİRİŞ: {next_r['Ad Soyad']}" if d_left <= 0 else f"🔔 {d_left} Gün Sonra: {next_r['Ad Soyad']}\n({next_r['Tarih']})"
    st.markdown(f'<div class="alarm-card"><h3>{txt}</h3></div>', unsafe_allow_html=True)

# --- 4. SEKMELER ---
s_date = st.query_params.get("date", "")
t1, t2, t3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    ay_ad = st.selectbox("Ay", aylar, index=today.month-1)
    ay_no = aylar.index(ay_ad) + 1
    
    # Takvim Tablosu
    html = '<table class="modern-table"><thead><tr>'
    for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]: html += f'<th>{g}</th>'
    html += '</tr></thead><tbody>'
    cal = calendar.monthcalendar(2026, ay_no)
    for week in cal:
        html += '<tr>'
        for day in week:
            if day == 0: html += '<td></td>'
            else:
                ts = f"2026-{ay_no:02d}-{day:02d}"
                check = df[df["Tarih"] == ts]
                cl = "bos"
                if not check.empty: cl = "dolu" if check.iloc[0]["Durum"]=="Kesin" else "opsiyon"
                html += f'<td><a href="?date={ts}" target="_self" class="day-link {cl}">{day}</a></td>'
        html += '</tr>'
    st.markdown(html + '</tbody></table>', unsafe_allow_html=True)

    with st.expander("📝 Yeni Kayıt", expanded=True if s_date else False):
        with st.form("r_form"):
            f_t = st.text_input("Tarih", value=s_date)
            f_a = st.text_input("Ad Soyad")
            f_p = st.text_input("WhatsApp (90...)")
            f_u = st.number_input("Günlük", min_value=0)
            f_g = st.number_input("Gece", min_value=1)
            if st.form_submit_button("KAYDET"):
                if f_t and f_a:
                    start = datetime.strptime(f_t, "%Y-%m-%d")
                    new = [[(start + timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_u, f_g, "", "Kesin", f_u*f_g] for i in range(int(f_g))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns)]).to_csv("rez.csv", index=False)
                    st.rerun()

with t3:
    st.subheader(f"📊 {ay_ad} Finansal Durum")
    # Filtreleme: Sadece seçili ayın eşsiz kayıtlarını al
    df_f = df.copy()
    df_f["Tarih"] = pd.to_datetime(df_f["Tarih"])
    aylik = df_f[df_f["Tarih"].dt.month == ay_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    
    brut = aylik["Toplam"].sum()
    kdv = brut * 0.20
    net = brut - kdv - (brut * 0.15) # Tahmini komisyon düşüşü
    
    st.markdown(f'<div class="f-card">💰 <b>Brüt Ciro:</b> <span>{brut:,.0f} TL</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card">🧾 <b>KDV Payı:</b> <span>-{kdv:,.0f} TL</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color:#2ECC71">✅ <b>Net Kâr (Tahmini):</b> <span>{net:,.0f} TL</span></div>', unsafe_allow_html=True)
