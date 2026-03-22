import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.1", layout="wide", page_icon="🏡")

# Modern Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 26px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 12px; margin-bottom: 20px; }
    .stat-box { background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 110px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 8px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 20px 0; border-radius: 12px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 18px;
        transition: transform 0.1s; border-bottom: 4px solid rgba(0,0,0,0.2);
    }
    .day-link:active { transform: translateY(2px); }
    .bos { background: #10b981 !important; } 
    .dolu { background: #ef4444 !important; } 
    .info-card { background: white; padding: 20px; border-radius: 15px; border-top: 6px solid #ef4444; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (EXCEL UYUMLU AYIRICI) ---
REZ_FILE = "rez.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]

def load_data(file, cols):
    if not os.path.exists(file): 
        # Excel'in Türkçe versiyonları için sep=';' kullanıyoruz
        pd.DataFrame(columns=cols).to_csv(file, index=False, sep=';', encoding='utf-8-sig')
    try:
        temp_df = pd.read_csv(file, sep=';', encoding='utf-8-sig')
        return temp_df.reindex(columns=cols, fill_value="")
    except:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False, sep=';', encoding='utf-8-sig')

df = load_data(REZ_FILE, COL_REZ)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.1</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- SEKME 1: TAKVİM ---
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
            st.markdown(f'<div class="info-card"><h3>👤 {r["Ad Soyad"]}</h3><p>{r["Gece"]} Gece | {r["Toplam"]:,} TL | {r["Kapora"]}</p></div>', unsafe_allow_html=True)
        else:
            with st.form("hizli_kayit_v7"):
                f1, f2, f3 = st.columns(3); f_ad = f1.text_input("Ad Soyad"); f_tel = f2.text_input("Tel", value="90"); f_tarih = f3.date_input("Giriş", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                f4, f5, f6 = st.columns(3); f_gun = f4.number_input("Gece", min_value=1); f_ucret = f5.number_input("Gecelik TL"); f_kapora = f6.selectbox("Ödeme", ["Bekleniyor", "Kapora Alındı", "Ödendi"])
                if st.form_submit_button("✅ KAYDET"):
                    yeni = []
                    for i in range(int(f_gun)):
                        t = (f_tarih + timedelta(days=i)).strftime("%Y-%m-%d")
                        yeni.append({"Tarih": t, "Ad Soyad": f_ad, "Tel": f_tel, "Ucret": f_ucret, "Gece": f_gun, "Durum": "Dolu", "Toplam": f_gun*f_ucret, "Kapora": f_kapora})
                    df = pd.concat([df, pd.DataFrame(yeni)], ignore_index=True)
                    save_data(df, REZ_FILE)
                    st.rerun()

    st.divider()
    m_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    ciro = m_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    dolu = m_df['Tarih'].nunique(); bos = calendar.monthrange(2026, ay_idx)[1] - dolu
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-box"><small>Ciro</small><br><b>{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><small>Doluluk</small><br><b>%{ (dolu/30)*100 if dolu>0 else 0:.1f}</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><small>Dolu/Boş</small><br><b>{dolu}D / {bos}B</b></div>', unsafe_allow_html=True)

# --- SEKME 2: REZERVASYON LİSTESİ (EXCEL İNDİRME) ---
with t_rez:
    st.subheader("📋 Rezervasyon Yönetimi")
    
    if not df.empty:
        # İndirme Seçeneği (Excel Dostu CSV)
        csv_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Excel Olarak İndir (Sütunlu Format)",
            data=csv_data,
            file_name=f"Detayvalik_Rezervasyonlar_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime='text/csv',
        )
        
        # Arama ve Liste Görünümü
        search = st.text_input("🔍 Misafir Ara (İsim veya Tel)", "")
        filtered_df = df[df['Ad Soyad'].str.contains(search, case=False)] if search else df
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Silme İşlemi (Hızlı Liste)
        st.write("---")
        st.write("🗑️ **Kayıt Silme Paneli**")
        rez_groups = df.groupby(["Ad Soyad", "Tel"]).size().reset_index(name='Gün')
        for i, row in rez_groups.iterrows():
            if st.button(f"Sil: {row['Ad Soyad']} ({row['Gün']} Gün)", key=f"btn_{i}"):
                df = df[~(df['Ad Soyad'] == row['Ad Soyad'])]
                save_data(df, REZ_FILE)
                st.rerun()

# --- DİĞER SEKMELER ---
with t_fin: st.info("💰 Finansal tablo detayları yüklenecektir.")
with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
