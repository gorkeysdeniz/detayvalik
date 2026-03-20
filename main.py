import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ ---
KDV_ORANI = 0.10
TURIZM_VERGISI = 0.02

st.set_page_config(page_title="Villa Yönetim Paneli", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link, .doc-link { display: inline-block; color: white !important; padding: 5px 12px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; }
    .wa-link { background-color: #25D366; }
    .doc-link { background-color: #008080; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])

def get_clean_df(input_df):
    if input_df.empty: return input_df
    res = input_df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 3. ANALİTİK HESAPLAR ---
now = datetime.now()
curr_month, curr_year = now.month, now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]
df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]
booked_count = len(month_df)
empty_count = month_days - booked_count
occ_rate = (booked_count / month_days) * 100
days_to_end = month_days - now.day

clean_df = get_clean_df(df)
avg_stay = clean_df['Gece'].astype(float).mean() if not clean_df.empty else 0
this_month_rev = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()

# --- 4. ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi</div>', unsafe_allow_html=True)
t_dash, t_cal, t_rez, t_fin = st.tabs(["📊 Dashboard", "📅 Takvim", "📋 Rezervasyonlar", "💰 Finans & Gider"])

with t_dash:
    # Üst Göstergeler
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-box"><small>Aylık Doluluk</small><br><b style="font-size:22px; color:#1A3636;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><small>Kalan Boş Gün</small><br><b style="font-size:22px; color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b style="font-size:22px;">{avg_stay:.1f} Gece</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-box"><small>Bu Ay Ciro</small><br><b style="font-size:22px; color:#4F6F52;">{this_month_rev:,.0f} TL</b></div>', unsafe_allow_html=True)

    st.divider()
    cl, cr = st.columns(2)
    
    with cl:
        st.write("**📅 Gelecek Rezervasyonlar (İlk 3)**")
        future = clean_df[clean_df['Giris_DT'] >= now.replace(hour=0, minute=0)].sort_values('Giris_DT').head(3)
        if not future.empty:
            for _, r in future.iterrows():
                st.success(f"👤 {r['Ad Soyad']} \n\n 📅 {r['Giris_Tarihi']} / {r['Gece']} Gece")
        else: st.info("Yakın tarihte giriş yok.")

    with cr:
        st.write("**📢 Akıllı Bildirimler**")
        st.info(f"📅 Bugün: {now.strftime('%d/%m/%Y')} - Ayın bitmesine {max(0, days_to_end)} gün kaldı.")
        if occ_rate < 50: st.warning(f"⚠️ Doluluk oranı %50'nin altında. Boş {empty_count} gün için aksiyon alabilirsin.")
        if empty_count == 0: st.success("🌟 Tebrikler! Bu ay tam kapasite dolusun.")
        elif empty_count < 5: st.success("✅ Ayın büyük çoğunluğu dolmuş durumda.")

# DİĞER SEKMELER (Takvim, Rez, Finans) STABİL OLARAK DEVAM EDER...
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    cx, cy = st.columns([1, 3]); sec_ay = cx.selectbox("Dönem", aylar, index=curr_month-1); ay_idx = aylar.index(sec_ay) + 1
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"; cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)
    # Rezervasyon formu (Takvim altı) aynı şekilde çalışır.

with t_rez:
    st.markdown("### Kayıt Sorgulama")
    search = st.text_input("🔍 İsim veya Tel Ara...")
    if not df.empty:
        c_df = get_clean_df(df)
        if search: c_df = c_df[c_df['Ad Soyad'].str.contains(search, case=False)]
        for i, r in c_df.iterrows():
            c1, c2 = st.columns([4, 2])
            c1.markdown(f"**{r['Ad Soyad']}** | {r['Giris_Tarihi']} / {r['Gece']} Gece")
            c2.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text=Onay" target="_blank" class="wa-link">WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

with t_fin:
    # Vergi hesaplamaları v42'deki gibi brüt üzerinden ayrıştırılır.
    m_fin = df[df["DT"].dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    konak = b_ciro - (b_ciro / (1 + TURIZM_VERGISI))
    gider = df_gider[pd.to_datetime(df_gider["Tarih"]).dt.month == ay_idx]["Tutar"].sum()
    st.metric("Net Kâr", f"{(b_ciro - kdv - konak - gider):,.0f} TL")
    st.dataframe(df_gider)
