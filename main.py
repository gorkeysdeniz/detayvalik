import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık Villa Yönetimi v42.4.5", layout="wide")

# Modern Tasarım CSS (Kareli Dashboard & Takvim)
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link { background-color: #25D366; color: white !important; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.4.5</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Dashboard", "📋 Rezervasyon & Belge", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Çizimi
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"
                cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    # Dashboard Hesaplamaları
    month_days = calendar.monthrange(2026, ay_idx)[1]
    month_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    booked_count = month_df['Tarih'].nunique()
    occ_rate = (booked_count / month_days) * 100
    kalan_gun = (month_days - datetime.now().day) if ay_idx == datetime.now().month else 0

    st.divider()
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f'<div class="stat-box"><small>Doluluk</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Dolu Gün</small><br><b>{booked_count} Gün</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Ay Sonuna Kalan</small><br><b>{max(0, kalan_gun)} Gün</b></div>', unsafe_allow_html=True)
    
    # --- AKILLI UYARI MESAJLARI ---
    if occ_rate < 40:
        d4.warning("📉 Doluluk düşük! Kampanya yapabilirsin.")
    elif occ_rate > 85:
        d4.success("🚀 Harika! Villa neredeyse full.")
    else:
        d4.info("📊 Sezon normal seyrediyor.")

# --- TAB 2: REZERVASYON & WHATSAPP BELGE ---
with t_rez:
    search = st.text_input("🔍 Misafir Ara (İsim veya Tel)")
    # Rezervasyonları gruplayıp liste yapma
    if not df.empty:
        df_clean = df.copy()
        df_clean['Giris'] = pd.to_datetime(df_clean['Tarih'])
        r_list = df_clean.groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Giris=("Giris", "min")).reset_index()
        
        if search:
            r_list = r_list[r_list['Ad Soyad'].str.contains(search, case=False)]

        for i, r in r_list.iterrows():
            c_inf, c_wa = st.columns([3, 1])
            cikis = r['Giris'] + timedelta(days=int(r['Gece']))
            c_inf.markdown(f"👤 **{r['Ad Soyad']}** | 📞 {r['Tel']}\n📅 {r['Giris'].strftime('%d.%m')} - {cikis.strftime('%d.%m')} | 🌙 {r['Gece']} Gece")
            
            # WhatsApp Belge Metni
            wp_text = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, \n\n*Rezervasyon Onay Belgesi* 🏡\n📅 Giriş: {r['Giris'].strftime('%d.%m.%Y')}\n📅 Çıkış: {cikis.strftime('%d.%m.%Y')}\n💰 Toplam: {r['Toplam']:,} TL\n\nKeyifli tatiller! ✨")
            c_wa.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_text}" target="_blank" class="wa-link">📱 Belge Gönder</a>', unsafe_allow_html=True)
            st.divider()

# --- TAB 3: FİNANS & GİDER ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Rapor")
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    brut = m_fin["Toplam"].sum()
    kdv = brut * KDV_ORANI
    turizm = brut * TURIZM_VERGISI
    toplam_gider = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Gelir", f"{brut:,.0f} TL")
    f2.metric("Vergi Yükü (KDV+Turizm)", f"{(kdv+turizm):,.0f} TL", delta_color="inverse")
    f3.metric("Toplam Gider", f"{toplam_gider:,.0f} TL", delta_color="inverse")
    f4.success(f"**NET KAR: {(brut - kdv - turizm - toplam_gider):,.0f} TL**")

    st.divider()
    with st.form("gider_form", clear_on_submit=True):
        st.write("➕ **Yeni Gider Ekle**")
        gt, gk, gu, ga = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.number_input("Tutar"), st.text_input("Açıklama")
        if st.form_submit_button("Gideri Kaydet"):
            new_g = pd.DataFrame([{"Tarih": gt.strftime("%Y-%m-%d"), "Kategori": gk, "Aciklama": ga, "Tutar": gu}])
            pd.concat([df_gider, new_g], ignore_index=True).to_csv(GIDER_FILE, index=False); st.rerun()

# --- TAB 4: AYARLAR ---
with t_set:
    if st.button("🔴 VERİLERİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False)
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False)
        st.rerun()
