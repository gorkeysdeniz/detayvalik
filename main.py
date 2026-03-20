import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR VE KURUMSAL TEMA ---
st.set_page_config(page_title="Detayvalık Yönetim Paneli", layout="wide")

st.markdown("""
    <style>
    /* Genel Arayüz */
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #F1F1F1; border-radius: 4px 4px 0 0; padding: 8px 16px; color: #4A4A4A !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #1A3636 !important; color: white !important; }

    /* Takvim Hücreleri */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { 
        display: block; text-decoration: none; padding: 20px 0; border-radius: 6px; 
        font-weight: 600; color: white !important; text-align: center; transition: 0.2s;
    }
    .bos { background: #4F6F52 !important; } /* Soft Yeşil */
    .dolu { background: #A94438 !important; } /* Soft Kırmızı */
    .day-link:hover { opacity: 0.8; transform: scale(1.02); }

    /* Bilgi Kartları */
    .info-panel {
        background: #F8F4EC; border: 1px solid #D6BD98; padding: 20px; border-radius: 8px; margin-bottom: 25px;
    }
    .stat-box {
        background: white; border: 1px solid #E5E7EB; padding: 20px; border-radius: 8px; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Butonlar */
    .stButton button {
        background-color: #1A3636 !important; color: white !important; border-radius: 4px !important;
        border: none !important; height: 45px; width: 100%; font-weight: 500;
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

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">Detayvalık Villa Yönetimi</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["Takvim", "Rezervasyonlar", "Giderler", "Finans", "Ayarlar"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([1, 3])
    with c1:
        sec_ay = st.selectbox("Dönem Seçimi", aylar, index=datetime.now().month-1)
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

    # --- AKILLI ETKİLEŞİM PANELİ ---
    q_date = st.query_params.get("date", "")
    if q_date:
        st.markdown(f"### Seçili Tarih: {q_date}")
        day_data = df[df["Tarih"] == q_date]
        
        if not day_data.empty:
            # GÜN DOLUYSA BİLGİ PANELİ
            info = day_data.iloc[0]
            st.markdown(f"""
            <div class="info-panel">
                <b style="color:#A94438;">Dolu Tarih Bilgisi:</b><br>
                <b>Müşteri:</b> {info['Ad Soyad']} | <b>Telefon:</b> {info['Tel']}<br>
                <b>Konaklama:</b> {info['Gece']} Gece | <b>Ücret:</b> {info['Toplam']:,} TL<br>
                <b>Notlar:</b> {info['Not'] if info['Not'] else '-'}
            </div>
            """, unsafe_allow_html=True)
        else:
            # GÜN BOŞSA KAYIT FORMU
            with st.form("kayit_formu", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                f_a = col_a.text_input("Müşteri Ad Soyad")
                f_p = col_b.text_input("Telefon Numarası")
                f_f = col_a.number_input("Gecelik Ücret", min_value=0)
                f_g = col_b.number_input("Gece Sayısı", min_value=1)
                f_n = st.text_area("Rezervasyon Notu")
                if st.form_submit_button("Rezervasyonu Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, f_n, "Kesin", f_f*f_g] for i in range(int(f_g))]
                    pd.concat([df, pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear()
                    st.rerun()

with t2:
    st.markdown("### Kayıtlı Rezervasyon Listesi")
    ara = st.text_input("İsim ile filtrele...")
    if not df.empty:
        list_df = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris=("Tarih", "min")).reset_index()
        if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
        st.table(list_df[["Giris", "Ad Soyad", "Gece", "Toplam", "Not"]])

with t3:
    st.markdown("### Gider Yönetimi")
    with st.form("gider_giris", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        gt = c1.date_input("Tarih")
        gk = c2.selectbox("Kategori", ["Temizlik", "Fatura", "Bakım", "Mutfak", "Diğer"])
        gu = c3.number_input("Tutar")
        ga = st.text_input("Açıklama")
        if st.form_submit_button("Gideri İşle"):
            pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
            st.rerun()
    st.divider()
    st.dataframe(df_gider, use_container_width=True)

with t4:
    st.markdown(f"### {sec_ay} Dönemi Finansal Durum")
    m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_rez["Toplam"].sum()
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="stat-box"><small>Ciro</small><br><b>{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-box"><small>Gider</small><br><b>-{m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-box"><small>Net Kar</small><br><b>{ciro - m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    st.markdown("### Veri Yönetimi")
    if st.button("Tüm Verileri CSV Olarak İndir"):
        st.download_button("İndirmeyi Başlat", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")
