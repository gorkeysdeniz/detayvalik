import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.4", layout="wide", page_icon="🏡")

# Modern Tasarım CSS (İskeleti korur, kartları güzelleştirir)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .stat-box { 
        flex: 1; min-width: 150px; background: white; border: 1px solid #E2E8F0; 
        padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; font-weight: 700; color: white !important; text-align: center; border-bottom: 3px solid rgba(0,0,0,0.1); }
    .bos { background: #10b981 !important; } .dolu { background: #ef4444 !important; } 
    .rez-card { background: white; padding: 15px; border-radius: 12px; border-left: 5px solid #ef4444; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (Kritik: Veri kaymasını önler) ---
REZ_FILE = "rez.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]

def load_data():
    if not os.path.exists(REZ_FILE): 
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
    try:
        # Boş satırları ve None değerleri temizleyerek oku
        read_df = pd.read_csv(REZ_FILE, sep=';', encoding='utf-8-sig').dropna(subset=["Tarih"])
        return read_df.reindex(columns=COL_REZ)
    except:
        return pd.DataFrame(columns=COL_REZ)

def save_data(df_to_save):
    # Kaydetmeden önce temizlik yapar
    df_to_save.dropna(subset=["Tarih"]).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')

df = load_data()

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.4</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM (Dokunulmadı, sadece stabilite eklendi) ---
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
        rez_info = df[df["Tarih"] == selected_date]
        if rez_info.empty:
            with st.form("yeni_rez"):
                c1, c2, c3 = st.columns(3)
                f_ad = c1.text_input("Ad Soyad")
                f_tel = c2.text_input("Tel", value="90")
                f_giris = c3.date_input("Giriş", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                c4, c5, c6 = st.columns(3)
                f_gece = c4.number_input("Gece", min_value=1)
                f_ucret = c5.number_input("Gecelik TL")
                f_kap = c6.selectbox("Kapora", ["Ödenmedi", "Alındı"])
                if st.form_submit_button("Kaydet"):
                    yeni = []
                    for i in range(int(f_gece)):
                        t = (f_giris + timedelta(days=i)).strftime("%Y-%m-%d")
                        yeni.append({"Tarih":t, "Ad Soyad":f_ad, "Tel":f_tel, "Ucret":f_ucret, "Gece":f_gece, "Durum":"Dolu", "Toplam":f_gece*f_ucret, "Kapora":f_kap})
                    df = pd.concat([df, pd.DataFrame(yeni)], ignore_index=True)
                    save_data(df)
                    st.rerun()

# --- TAB 2: REZERVASYON LİSTESİ (İstediğin Tüm Özellikler Burada) ---
with t_rez:
    if df.empty:
        st.info("Kayıtlı rezervasyon bulunmuyor.")
    else:
        # Veriyi Gruplama (Kişi bazlı Giriş-Çıkış)
        df_group = df.copy()
        df_group['Tarih_DT'] = pd.to_datetime(df_group['Tarih'])
        
        summary = df_group.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(
            Giris=('Tarih_DT', 'min'),
            Cikis=('Tarih_DT', 'max')
        ).reset_index()
        summary['Cikis'] = summary['Cikis'] + timedelta(days=1) # Çıkış sabahını göster

        # Üst Metrikler (Görsel Kartlar)
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="stat-box"><small>Toplam Rezervasyon</small><br><b>{len(summary)} Grup</b></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="stat-box"><small>Bekleyen Kaporalar</small><br><b>{len(summary[summary["Kapora"]=="Ödenmedi"])} Adet</b></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="stat-box"><small>Toplam Gelecek Gelir</small><br><b>{summary["Toplam"].sum():,.0f} TL</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Arama Barı
        search = st.text_input("🔍 Misafir Adı veya Telefon ile Ara", "")
        if search:
            summary = summary[summary['Ad Soyad'].str.contains(search, case=False) | summary['Tel'].astype(str).contains(search)]

        # Rezervasyon Kartları ve Silme
        for idx, row in summary.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="rez-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b>👤 {row['Ad Soyad']}</b>
                        <span style="color:#64748b; font-size:12px;">📞 {row['Tel']}</span>
                    </div>
                    <div style="font-size:14px; margin-top:5px;">
                        📅 {row['Giris'].strftime('%d.%m.%Y')} - {row['Cikis'].strftime('%d.%m.%Y')} ({row['Gece']} Gece) <br>
                        💰 {row['Toplam']:,} TL ({row['Kapora']})
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ Rezervasyonu Tamamen Sil", key=f"del_{idx}"):
                    # O kişiye ait tüm günleri CSV'den temizle
                    df = df[~((df['Ad Soyad'] == row['Ad Soyad']) & (df['Tel'] == row['Tel']))]
                    save_data(df)
                    st.success("Rezervasyon silindi!")
                    st.rerun()

        st.divider()
        # Excel İndirme (Hücreli Format)
        st.subheader("📊 Ham Veri Tablosu")
        st.dataframe(df, use_container_width=True)
        excel_data = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 Excel Formatında İndir", data=excel_data, file_name="Detayvalik_Rezervasyonlar.csv", mime='text/csv')

# --- TAB 3 & 4 (İskelet Korundu) ---
with t_fin: st.write("Finansal veriler.")
with t_set:
    if st.button("🔴 Verileri Sıfırla"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
