import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. FONKSİYONLAR ---
def finans_kart_olustur(baslik, deger, renk="#1E293B"):
    """Finans ve Dashboard için 900 weight keskin tasarımlı kartlar"""
    st.markdown(f"""
        <div style="background-color: {renk}; padding: 22px; border-radius: 18px; text-align: center; margin-bottom: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); border: 1px solid rgba(255,255,255,0.1);">
            <p style="margin: 0; font-size: 13px; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;">{baslik}</p>
            <h2 style="margin: 5px 0 0 0; font-size: 32px; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; font-weight: 900; letter-spacing: -1px;">{deger}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- 2. AYARLAR & TASARIM ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
        @media (prefers-color-scheme: light) {
            .stApp { background-color: #FFFFFF !important; }
            h1, h2, h3, p, span, label, div { color: #1e293b !important; }
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-color: #0E1117 !important; }
            h1, h2, h3, p, span, label, div { color: #FFFFFF !important; }
        }
        .main-header { font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
        .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
        .day-link { display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; font-weight: 700; color: white !important; text-align: center; font-size: 16px; }
        .bos { background: #10b981 !important; } 
        .dolu { background: #ef4444 !important; } 
        .stat-box { padding: 15px; border-radius: 10px; text-align: center; background: #1A1C24; border: 1px solid #33363F; }
        .stButton button { background-color: #8FD9C8 !important; border-radius: 12px !important; height: 3.5em !important; width: 100% !important; color: black !important; font-weight: 700 !important;}
    </style>
""", unsafe_allow_html=True)

# --- 3. VERİ YÖNETİMİ ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]

def load_data():
    if not os.path.exists(REZ_FILE): 
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
    try:
        return pd.read_csv(REZ_FILE, sep=';', encoding='utf-8-sig').reindex(columns=COL_REZ, fill_value="")
    except:
        return pd.DataFrame(columns=COL_REZ)

def save_data(df_to_save):
    df_to_save.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')

df = load_data()

# --- 4. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Villa Yönetim Paneli (Beta 1.0)</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
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

    # Seçili Gün Detayı & Formu (Geri Getirildi)
    selected_date = st.query_params.get("date")
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        if not rez_info.empty:
            r = rez_info.iloc[0]
            st.success(f"👤 Misafir: {r['Ad Soyad']} | 📞 {r['Tel']} | 🌙 {r['Gece']} Gece | 💰 Toplam: {r['Toplam']:,} TL")
            wp_msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz teyit edilmiştir.")
            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_msg}" target="_blank" style="background-color:#25D366; color:white; padding:10px; border-radius:10px; text-decoration:none; display:block; text-align:center;">📱 WhatsApp Mesajı</a>', unsafe_allow_html=True)
        else:
            with st.form("yeni_rez_form"):
                f_ad = st.text_input("Ad Soyad")
                f_tel = st.text_input("Telefon", value="90")
                f_gece = st.number_input("Gece", min_value=1)
                f_gunluk = st.number_input("Günlük Ücret", min_value=0)
                f_kapora = st.selectbox("Kapora", ["Ödenmedi", "Kısmi", "Tamamı"])
                if st.form_submit_button("✅ KAYDET"):
                    yeni = [{"Tarih": (datetime.strptime(selected_date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d"), "Ad Soyad": f_ad, "Tel": f_tel, "Toplam": f_gece*f_gunluk, "Gece": f_gece, "Ucret": f_gunluk, "Kapora": f_kapora, "Durum": "Dolu"} for i in range(int(f_gece))]
                    df = pd.concat([df, pd.DataFrame(yeni)], ignore_index=True)
                    save_data(df)
                    st.rerun()

    # DASHBOARD ÖZETİ (Geri Getirildi)
    st.divider()
    m_days = calendar.monthrange(2026, ay_idx)[1]
    m_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    ciro = m_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    dolu_g = m_df['Tarih'].nunique()
    oran = (dolu_g / m_days) * 100
    
    st.subheader(f"📊 {sec_ay} Özeti")
    c1, c2, c3, c4 = st.columns(4)
    with c1: finans_kart_olustur("CİRO", f"{ciro:,.0f} TL", "#1E293B")
    with c2: finans_kart_olustur("DOLULUK", f"%{oran:.0f}", "#334155")
    with c3: finans_kart_olustur("DOLU GÜN", f"{dolu_g}", "#EF4444")
    with c4: finans_kart_olustur("BOŞ GÜN", f"{m_days-dolu_g}", "#10B981")

# --- TAB 2: REZERVASYON LİSTESİ & ARAMA (Geri Getirildi) ---
with t_rez:
    if not df.empty:
        df_v = df.copy()
        df_v['Tarih_DT'] = pd.to_datetime(df_v['Tarih'], errors='coerce')
        summary = df_v.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(Giris=('Tarih_DT', 'min')).reset_index()
        
        search = st.text_input("🔍 Misafir Ara (İsim veya Tel)")
        if search:
            summary = summary[summary['Ad Soyad'].str.contains(search, case=False) | summary['Tel'].str.contains(search)]
        
        st.dataframe(summary[['Ad Soyad', 'Tel', 'Gece', 'Toplam', 'Kapora']], use_container_width=True, hide_index=True)
        
        # Silme İşlemi
        sec_sil = st.selectbox("Silinecek Kayıt", ["Seçiniz..."] + summary['Ad Soyad'].tolist())
        if sec_sil != "Seçiniz..." and st.button("❌ KAYDI SİL"):
            df = df[df['Ad Soyad'] != sec_sil]
            save_data(df)
            st.rerun()

# --- TAB 3: FİNANSAL TABLO ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Analizi")
    if not os.path.exists(GIDER_FILE): pd.DataFrame(columns=["Tarih", "Aciklama", "Tutar"]).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
    df_g = pd.read_csv(GIDER_FILE, sep=';', encoding='utf-8-sig')
    df_g['Tarih_DT'] = pd.to_datetime(df_g['Tarih'], errors='coerce')
    toplam_gider = df_g[df_g['Tarih_DT'].dt.month == ay_idx]["Tutar"].sum()
    vergi = ciro * 0.12
    
    c1, c2 = st.columns(2)
    with c1:
        finans_kart_olustur("BRÜT GELİR", f"{ciro:,.0f} TL", "#1E293B")
        finans_kart_olustur("GİDER TOPLAMI", f"-{toplam_gider:,.0f} TL", "#EF4444")
    with c2:
        finans_kart_olustur("VERGİ (%12)", f"-{vergi:,.0f} TL", "#334155")
        finans_kart_olustur("NET KAR", f"{ciro-vergi-toplam_gider:,.0f} TL", "#10B981")

    with st.form("gider_form"):
        gt, ga, gv = st.columns(3)
        g_t = gt.date_input("Tarih")
        g_a = ga.text_input("Açıklama")
        g_v = gv.number_input("Tutar", min_value=0)
        if st.form_submit_button("💰 GİDER KAYDET"):
            new_g = pd.DataFrame([{"Tarih": g_t.strftime("%Y-%m-%d"), "Aciklama": g_a, "Tutar": g_v}])
            pd.concat([df_g.drop(columns=['Tarih_DT']), new_g]).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.rerun()

# --- TAB 4: AYARLAR ---
with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
