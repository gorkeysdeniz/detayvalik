import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık Operasyon v42.5.0", layout="wide", page_icon="🏡")

# Modern Tasarım CSS (Mobil Uyumluluk Rötuşu)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 26px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 12px; margin-bottom: 20px; }
    .stat-box { background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Mobil Dostu Takvim */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 6px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 22px 0; border-radius: 10px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 18px;
        transition: transform 0.2s;
    }
    .day-link:active { transform: scale(0.95); }
    .bos { background: #10b981 !important; border-bottom: 4px solid #059669; } /* Yeşil */
    .dolu { background: #ef4444 !important; border-bottom: 4px solid #b91c1c; } /* Kırmızı */
    
    /* Form ve Bilgi Kutusu Tasarımı */
    .info-card { background: #F1F5F9; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; margin-top: 10px; }
    .wa-link { background-color: #25D366; color: white !important; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: 600; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (UTF-8-SIG DESTEĞİ) ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False, encoding='utf-8-sig')
    return pd.read_csv(file, encoding='utf-8-sig').reindex(columns=cols, fill_value="")

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.5.0</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Dashboard", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Tıklanan Tarihi Yakala
    selected_date = st.query_params.get("date", None)

    # Takvim Çizimi
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"
                is_dolu = not df[df["Tarih"] == d_s].empty
                cl = "dolu" if is_dolu else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    # Dashboard Metrikleri
    month_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    ciro = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    occ_rate = (month_df['Tarih'].nunique() / calendar.monthrange(2026, ay_idx)[1]) * 100

    st.divider()
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="stat-box"><small>{sec_ay} Cirosu</small><br><b style="color:#10b981">{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Sezon Durumu</small><br><b>{"🔥 Yoğun" if occ_rate > 70 else "✅ Normal"}</b></div>', unsafe_allow_html=True)

    # --- ETKİLEŞİM PANELİ (TIKLAMA SONRASI) ---
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        
        if not rez_info.empty:
            # DOLU GÜN: Bilgi Kutucuğu
            r = rez_info.iloc[0]
            st.markdown(f"""
            <div class="info-card">
                <h4>📌 Rezervasyon Bilgisi ({selected_date})</h4>
                <p>👤 <b>Misafir:</b> {r['Ad Soyad']}<br>
                📞 <b>Tel:</b> {r['Tel']}<br>
                🌙 <b>Süre:</b> {r['Gece']} Gece<br>
                💰 <b>Toplam:</b> {r['Toplam']:,} TL | <b>Durum:</b> {r['Kapora']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # BOŞ GÜN: Hızlı Kayıt Formu
            st.subheader(f"📝 {selected_date} İçin Yeni Kayıt")
            with st.form("hizli_kayit", clear_on_submit=True):
                f1, f2, f3 = st.columns(3)
                f_ad = f1.text_input("Müşteri Ad Soyad")
                f_tel = f2.text_input("Telefon Numarası", value="90")
                f_tarih = f3.date_input("Giriş Tarihi", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                
                f4, f5, f6 = st.columns(3)
                f_gun = f4.number_input("Kalınacak Gün Sayısı", min_value=1, value=1)
                f_ucret = f5.number_input("Günlük Ücret (TL)", min_value=0)
                f_kapora = f6.selectbox("Kapora Durumu", ["Alınmadı", "Kısmi Alındı", "Tamamı Ödendi"])
                
                toplam_ucret = f_gun * f_ucret
                st.info(f"💰 **Hesaplanan Toplam Ücret: {toplam_ucret:,} TL**")
                
                if st.form_submit_button("💾 REZERVASYONU TAMAMLA"):
                    yeni_rezler = []
                    for i in range(f_gun):
                        t = (f_tarih + timedelta(days=i)).strftime("%Y-%m-%d")
                        yeni_rezler.append({
                            "Tarih": t, "Ad Soyad": f_ad, "Tel": f_tel, 
                            "Ucret": f_ucret, "Gece": f_gun, "Durum": "Dolu", 
                            "Toplam": toplam_ucret, "Kapora": f
