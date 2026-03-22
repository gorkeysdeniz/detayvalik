import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.5", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .stat-box { flex: 1; min-width: 150px; background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; font-weight: 700; color: white !important; text-align: center; border-bottom: 3px solid rgba(0,0,0,0.1); }
    .bos { background: #10b981 !important; } .dolu { background: #ef4444 !important; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False, sep=';', encoding='utf-8-sig')
    try:
        return pd.read_csv(file, sep=';', encoding='utf-8-sig').reindex(columns=cols, fill_value="")
    except:
        return pd.DataFrame(columns=cols)

def save_data(df, file):
    df.to_csv(file, index=False, sep=';', encoding='utf-8-sig')

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.5</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM (Sabit İskelet) ---
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
            with st.form("hizli_kayit"):
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
                    save_data(df, REZ_FILE); st.rerun()

# --- TAB 2: REZERVASYON LİSTESİ (KİŞİ BAZLI EXCEL) ---
with t_rez:
    if not df.empty:
        df_group = df.copy()
        df_group['Tarih_DT'] = pd.to_datetime(df_group['Tarih'])
        summary = df_group.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(
            Giris=('Tarih_DT', 'min'), Cikis=('Tarih_DT', 'max')
        ).reset_index()
        summary['Cikis'] = summary['Cikis'] + timedelta(days=1)
        
        # EXCEL İNDİRME (Kişi Bazlı Özet)
        st.subheader("📋 Kişi Bazlı Rezervasyon Arşivi")
        excel_summary = summary.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 Kişi Bazlı Excel İndir", data=excel_summary, file_name="Detayvalik_Ozet_Liste.csv", mime='text/csv')
        
        st.dataframe(summary, use_container_width=True)
        
        # Hızlı Silme
        st.write("---")
        for i, r in summary.iterrows():
            if st.button(f"🗑️ Sil: {r['Ad Soyad']} ({r['Giris'].strftime('%d.%m')})", key=f"d_{i}"):
                df = df[~((df['Ad Soyad'] == r['Ad Soyad']) & (df['Tel'] == r['Tel']))]
                save_data(df, REZ_FILE); st.rerun()

# --- TAB 3: FİNANSAL TABLO (VERGİ VE GİDER SİSTEMİ) ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Analiz")
    
    # Verileri aya göre filtrele
    m_rez = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    m_gider = df_gider[pd.to_datetime(df_gider['Tarih'], errors='coerce').dt.month == ay_idx]
    
    # Hesaplamalar
    gelir = m_rez.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    vergi = gelir * 0.12 # %10 KDV + %2 Konaklama/Turizm vergisi (Toplam %12)
    toplam_gider = m_gider["Tutar"].sum()
    net_kar = gelir - vergi - toplam_gider

    # Görsel Kartlar
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Gelir", f"{gelir:,.0f} TL")
    f2.metric("Vergiler (%12)", f"-{vergi:,.0f} TL", delta_color="inverse")
    f3.metric("Toplam Gider", f"-{toplam_gider:,.0f} TL", delta_color="inverse")
    f4.subheader(f"✅ Net: {net_kar:,.0f} TL")

    st.divider()
    
    # Gider Girme Sistemi
    st.write("🧾 **Yeni Gider Ekle**")
    with st.form("gider_form"):
        g1, g2, g3, g4 = st.columns(4)
        g_tar = g1.date_input("Gider Tarihi")
        g_kat = g2.selectbox("Kategori", ["Faturalar", "Temizlik", "Mutfak/Market", "Tamirat", "Pazarlama", "Diğer"])
        g_ack = g3.text_input("Açıklama")
        g_tut = g4.number_input("Tutar (TL)", min_value=0)
        
        if st.form_submit_button("Gideri Kaydet"):
            yeni_gider = pd.DataFrame([{"Tarih": g_tar.strftime("%Y-%m-%d"), "Kategori": g_kat, "Aciklama": g_ack, "Tutar": g_tut}])
            df_gider = pd.concat([df_gider, yeni_gider], ignore_index=True)
            save_data(df_gider, GIDER_FILE)
            st.success("Gider eklendi!"); st.rerun()

    if not m_gider.empty:
        st.write(f"📂 **{sec_ay} Ayı Gider Detayları**")
        st.table(m_gider)

# --- TAB 4: AYARLAR ---
with t_set:
    if st.button("🔴 Tüm Verileri Sıfırla"):
        save_data(pd.DataFrame(columns=COL_REZ), REZ_FILE)
        save_data(pd.DataFrame(columns=COL_GIDER), GIDER_FILE)
        st.rerun()
