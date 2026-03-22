import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.6", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .stat-box { flex: 1; min-width: 140px; background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; font-weight: 700; color: white !important; text-align: center; border-bottom: 3px solid rgba(0,0,0,0.1); }
    .bos { background: #10b981 !important; } .dolu { background: #ef4444 !important; } 
    .info-card { background: white; padding: 15px; border-radius: 12px; border-left: 6px solid #ef4444; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_FILE, GIDER_FILE = "rez.csv", "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False, sep=';', encoding='utf-8-sig')
    try:
        temp = pd.read_csv(file, sep=';', encoding='utf-8-sig')
        return temp.reindex(columns=cols, fill_value="")
    except: return pd.DataFrame(columns=cols)

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.6</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
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

    selected_date = st.query_params.get("date")
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        if not rez_info.empty:
            r = rez_info.iloc[0]
            g_dt = datetime.strptime(str(r['Tarih']), "%Y-%m-%d")
            c_dt = g_dt + timedelta(days=int(r['Gece']))
            st.markdown(f'<div class="info-card"><h3>👤 {r["Ad Soyad"]}</h3><p>📞 {r["Tel"]} | 🌙 {r["Gece"]} Gece<br>📅 {g_dt.strftime("%d.%m")} - {c_dt.strftime("%d.%m")} | 💰 {r["Toplam"]:,} TL ({r["Kapora"]})</p></div>', unsafe_allow_html=True)
        else:
            with st.form("yeni_kayit"):
                c1, c2, c3 = st.columns(3)
                f_ad = c1.text_input("Ad Soyad"); f_tel = c2.text_input("Tel", value="90"); f_giris = c3.date_input("Giriş", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                c4, c5, c6 = st.columns(3)
                f_gece = c4.number_input("Gece", 1); f_ucret = c5.number_input("Gecelik TL", 0); f_kap = c6.selectbox("Ödeme", ["Ödenmedi", "Alındı"])
                if st.form_submit_button("Kaydet"):
                    yeni = [{"Tarih":(f_giris+timedelta(days=i)).strftime("%Y-%m-%d"), "Ad Soyad":f_ad, "Tel":f_tel, "Ucret":f_ucret, "Gece":f_gece, "Durum":"Dolu", "Toplam":f_gece*f_ucret, "Kapora":f_kap} for i in range(int(f_gece))]
                    df = pd.concat([df, pd.DataFrame(yeni)], ignore_index=True)
                    df.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig'); st.rerun()

    st.divider()
    m_days = calendar.monthrange(2026, ay_idx)[1]
    m_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    ciro = m_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    dolu = m_df['Tarih'].nunique(); bos = m_days - dolu; oran = (dolu/m_days)*100
    tavsiye = "🚀 Fiyat Artır" if oran > 80 else "📉 İndirim Yap" if oran < 30 else "✅ Dengeli"
    st.markdown(f'<div class="stat-container"><div class="stat-box"><small>Ciro</small><br><b>{ciro:,.0f} TL</b></div><div class="stat-box"><small>Doluluk</small><br><b>%{oran:.1f}</b></div><div class="stat-box"><small>Dolu/Boş</small><br><b>{dolu}D / {bos}B</b></div><div class="stat-box"><small>Tavsiye</small><br><b>{tavsiye}</b></div></div>', unsafe_allow_html=True)

# --- TAB 2: REZERVASYON LİSTESİ ---
with t_rez:
    if not df.empty:
        df_group = df.copy(); df_group['Tarih_DT'] = pd.to_datetime(df_group['Tarih'])
        summary = df_group.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora"]).agg(Giris=('Tarih_DT', 'min'), Cikis=('Tarih_DT', 'max')).reset_index()
        summary['Cikis'] = summary['Cikis'] + timedelta(days=1)
        
        # Arama ve İndirme
        search = st.text_input("🔍 Misafir Ara", "")
        if search: summary = summary[summary['Ad Soyad'].str.contains(search, case=False)]
        st.download_button("📥 Kişi Bazlı Excel İndir", data=summary.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig'), file_name="Detayvalik_Ozet.csv")
        
        for i, r in summary.iterrows():
            with st.expander(f"👤 {r['Ad Soyad']} ({r['Giris'].strftime('%d.%m')} - {r['Cikis'].strftime('%d.%m
