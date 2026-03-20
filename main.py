import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & PROFESYONEL TEMA ---
st.set_page_config(page_title="Detayvalık VIP Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Ana Arka Plan ve Font */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3, p, span, div { font-family: 'Inter', sans-serif !important; color: #1E293B !important; }
    
    /* Yan Menü (Sidebar) Tasarımı */
    [data-testid="stSidebar"] { background-color: #008080 !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Profesyonel Kartlar */
    .stat-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-top: 5px solid #008080;
        text-align: center; margin-bottom: 20px;
    }
    .rez-detail-card {
        background: #FFF9E6; padding: 15px; border-radius: 10px;
        border: 1px solid #DAA520; margin-bottom: 20px;
    }
    
    /* Takvim Hücreleri */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; }
    .day-link { 
        display: block; text-decoration: none; padding: 18px 0; border-radius: 10px; 
        font-weight: 700; color: white !important; text-align: center; transition: 0.3s;
    }
    .day-link:hover { transform: translateY(-3px); filter: brightness(1.1); }
    .bos { background: #10B981 !important; } /* Yeşil */
    .dolu { background: #EF4444 !important; } /* Kırmızı */
    
    /* Butonlar */
    .stButton button {
        background: #008080 !important; color: white !important;
        border-radius: 8px !important; border: none !important; font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 3. YAN MENÜ (NAVIGATION) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/619/619034.png", width=80) # Örnek ikon
    st.title("Detayvalık VIP")
    menu = st.radio("MENÜ", ["📅 Takvim & İşlemler", "🔍 Müşteri Kayıtları", "💸 Gider Yönetimi", "💰 Finansal Analiz", "⚙️ Veri Yönetimi"])
    st.divider()
    st.caption("v32.0 Premium Dashboard")

# --- 4. FONKSİYONLAR ---
def get_rez_info(date_str):
    return df[df["Tarih"] == date_str]

# --- 5. SAYFA İÇERİKLERİ ---

if menu == "📅 Takvim & İşlemler":
    st.header("📅 Rezervasyon Takvimi")
    
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([1, 2])
    with c1: sec_ay = st.selectbox("Görüntülenen Ay", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Grid
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

    # --- Tıklanan Günün Detayı ---
    q_date = st.query_params.get("date", "")
    if q_date:
        st.divider()
        rez_bilgi = get_rez_info(q_date)
        
        if not rez_bilgi.empty:
            # GÜN DOLUYSA: BİLGİLERİ GETİR
            info = rez_bilgi.iloc[0]
            st.markdown(f"""
            <div class="rez-detail-card">
                <h4>📌 {q_date} Tarihli Rezervasyon Detayı</h4>
                <b>👤 Müşteri:</b> {info['Ad Soyad']} <br>
                <b>📞 Telefon:</b> {info['Tel']} <br>
                <b>📝 Not:</b> {info['Not'] if info['Not'] else 'Not yok.'} <br>
                <b>💰 Toplam Tutar:</b> {info['Toplam']:,} TL
            </div>
            """, unsafe_allow_html=True)
        else:
            # GÜN BOŞSA: KAYIT FORMU AÇ
            st.markdown(f"### 📝 {q_date} İçin Yeni Kayıt")
            with st.form("pro_rez_form", clear_on_submit=True):
                f_a, f_p = st.text_input("Müşteri Ad Soyad"), st.text_input("Telefon")
                f_f, f_g = st.number_input("Gecelik Fiyat", min_value=0), st.number_input("Gece Sayısı", min_value=1)
                f_n = st.text_area("Özel Notlar (Örn: Kapora alındı, Ek yatak istendi)")
                if st.form_submit_button("RESERVASYONU ONAYLA"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, f_n, "Kesin", f_f*f_g] for i in range(int(f_g))]
                    pd.concat([df, pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear()
                    st.rerun()

elif menu == "🔍 Müşteri Kayıtları":
    st.header("🔍 Müşteri Veritabanı")
    ara = st.text_input("Müşteri ismi ile hızlı arama...")
    if not df.empty:
        list_df = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris=("Tarih", "min")).reset_index()
        if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
        
        for _, r in list_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="rez-card">
                    <b>👤 {r["Ad Soyad"]}</b> | 📅 {r["Giris"]} | 🌙 {r["Gece"]} Gece <br>
                    <small>📝 {r["Not"]}</small> <br>
                    <b>💰 {r["Toplam"]:,} TL</b>
                </div>
                """, unsafe_allow_html=True)
                if r['Tel']:
                    st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}" class="wa-button">💬 WhatsApp Mesajı</a>', unsafe_allow_html=True)
                st.divider()

elif menu == "💰 Finansal Analiz":
    st.header("💰 Finansal Dashboard")
    ay_list = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay_fin = st.selectbox("Analiz Dönemi", ay_list, index=datetime.now().month-1)
    f_idx = ay_list.index(sec_ay_fin) + 1
    
    m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == f_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_rez["Toplam"].sum()
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == f_idx]["Tutar"].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="stat-card"><h3>Ciro</h3><h2 style="color:#008080;">{ciro:,.0f} TL</h2></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="stat-card"><h3>Gider</h3><h2 style="color:#EF4444;">-{m_gid:,.0f} TL</h2></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="stat-card"><h3>Net</h3><h2 style="color:#10B981;">{ciro - m_gid:,.0f} TL</h2></div>', unsafe_allow_html=True)

# Giderler ve Ayarlar bölümleri de benzer şık yapıda devam eder...
