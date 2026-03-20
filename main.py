import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP", layout="centered")

# --- MODERN VE SABİT TASARIM (DARK MODE ENGELLEYİCİ) ---
st.markdown("""
    <style>
    /* Arka Plan ve Genel Yazı Rengi */
    .stApp { background-color: #F8F9FA !important; color: #1A1A1A !important; }
    
    /* Tabloyu 7 Sütunda Sabitleyen CSS */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .modern-table th { color: #666; font-size: 11px; text-transform: uppercase; padding-bottom: 8px; text-align: center; }
    .modern-table td { text-align: center; padding: 2px; }
    
    /* Gün Butonları (Yuvarlak ve Modern) */
    .day-link {
        display: block; text-decoration: none; padding: 12px 0; border-radius: 12px;
        font-weight: bold; font-size: 14px; color: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: 0.2s;
    }
    .day-link:active { transform: scale(0.9); }
    
    /* Durum Renkleri (Pastel Modern) */
    .bos { background: #2ECC71; } 
    .dolu { background: #E74C3C; } 
    .opsiyon { background: #F1C40F; color: #1A1A1A !important; }
    .empty { background: transparent; }

    /* Finans Kartları */
    .f-card {
        background: white; padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 12px;
        border-left: 6px solid #007BFF; color: #1A1A1A !important;
    }
    
    /* Sekme Yazıları */
    button[data-baseweb="tab"] p { color: #1A1A1A !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
    if not os.path.exists("gider.csv"):
        pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"]).to_csv("gider.csv", index=False)

init_db()
df = pd.read_csv("rez.csv")
gdf = pd.read_csv("gider.csv")

st.title("🏡 Detayvalık VIP")
selected_date = st.query_params.get("date", "")

t1, t2, t3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.markdown(f"<h3 style='text-align:center;'>{sec_ay} 2026</h3>", unsafe_allow_html=True)
    
    # HTML TABLO (Asla dikey listeye dönmez)
    html = '<table class="modern-table"><thead><tr>'
    for g in ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"]: html += f'<th>{g}</th>'
    html += '</tr></thead><tbody>'

    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        html += '<tr>'
        for gun in hafta:
            if gun == 0: html += '<td><div class="empty"></div></td>'
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                kayit = df[df["Tarih"] == t_str]
                cls = "bos"
                if not kayit.empty:
                    cls = "dolu" if kayit.iloc[0]["Durum"] == "Kesin" else "opsiyon"
                html += f'<td><a href="?date={t_str}" target="_self" class="day-link {cls}">{gun}</a></td>'
        html += '</tr>'
    st.markdown(html + '</tbody></table>', unsafe_allow_html=True)

    if selected_date:
        k_detay = df[df["Tarih"] == selected_date]
        if not k_detay.empty:
            k = k_detay.iloc[0]
            st.info(f"👤 {k['Ad Soyad']} | 💰 {k['Toplam']} TL")
        else: st.success(f"📍 {selected_date} Boş.")

    with st.expander("📝 Yeni Kayıt Ekle", expanded=True if selected_date else False):
        with st.form("r_form"):
            f_tar = st.text_input("Tarih", value=selected_date)
            f_ad = st.text_input("Müşteri Ad Soyad")
            f_tel = st.text_input("WhatsApp (905...)")
            f_ucret = st.number_input("Günlük Ücret", min_value=0)
            f_gece = st.number_input("Gece", min_value=1)
            f_durum = st.selectbox("Durum", ["Kesin", "Opsiyonel"])
            
            if st.form_submit_button("SİSTEME İŞLE"):
                if f_tar and f_ad and f_tel:
                    start = datetime.strptime(f_tar, "%Y-%m-%d")
                    total = f_ucret * f_gece
                    rows = [[(start + timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_ucret, f_gece, "", f_durum, total] for i in range(int(f_gece))]
                    pd.concat([df, pd.DataFrame(rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                    
                    msg = f"Merhaba {f_ad}, Detayvalık Villa rezervasyonunuz {f_tar} tarihinde onaylanmıştır. 🏡"
                    wa_link = f"https://wa.me/{f_tel}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:8px; display:block; text-align:center; text-decoration:none; font-weight:bold;">WhatsApp Onayı Gönder</a>', unsafe_allow_html=True)
                    st.rerun()

with t3:
    m_no = aylar.index(sec_ay) + 1
    df_t = df.copy(); df_t["Tarih"] = pd.to_datetime(df_t["Tarih"])
    bu_ay = df_t[df_t["Tarih"].dt.month == m_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut = bu_ay["Toplam"].sum()
    kdv = brut * 0.20
    net = brut - kdv - (brut * 0.17) # Komisyon dahil tahmini
    
    st.markdown(f'<div class="f-card">💰 <b>Brüt:</b> {brut:,.0f} TL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card">🧾 <b>KDV (%20):</b> -{kdv:,.0f} TL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color:#2ECC71">✅ <b>Tahmini Net: {net:,.0f} TL</b></div>', unsafe_allow_html=True)
