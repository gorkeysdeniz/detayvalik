import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- 1. AYARLAR VE KURUMSAL TEMA ---
st.set_page_config(page_title="Detayvalık Yönetim Paneli", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #F1F1F1; border-radius: 4px 4px 0 0; padding: 8px 16px; color: #4A4A4A !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #1A3636 !important; color: white !important; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 20px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; transition: 0.2s; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .info-panel { background: #F8F4EC; border: 1px solid #D6BD98; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .stButton button { background-color: #1A3636 !important; color: white !important; border-radius: 4px !important; border: none !important; height: 45px; width: 100%; font-weight: 500; }
    .del-btn button { background-color: #A94438 !important; height: 35px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)

# Müşteri bazlı özet tablo hazırlayan fonksiyon
def get_customer_based_df(input_df):
    if input_df.empty: return input_df
    return input_df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">Detayvalık Villa Yönetimi</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["Takvim", "Rezervasyonlar", "Giderler", "Finans", "Ayarlar"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([1, 3])
    with c1: sec_ay = st.selectbox("Dönem Seçimi", aylar, index=datetime.now().month-1)
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

    q_date = st.query_params.get("date", "")
    if q_date:
        st.divider()
        day_data = df[df["Tarih"] == q_date]
        if not day_data.empty:
            info = day_data.iloc[0]
            st.markdown(f"""
            <div class="info-panel">
                <b style="color:#A94438;">Seçili Tarih Bilgisi ({q_date}):</b><br>
                <b>Müşteri:</b> {info['Ad Soyad']} | <b>Tel:</b> {info['Tel']}<br>
                <b>Konaklama:</b> {info['Gece']} Gece | <b>Tutar:</b> {info['Toplam']:,} TL<br>
                <b>Notlar:</b> {info['Not'] if info['Not'] else '-'}
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.form("kayit_f", clear_on_submit=True):
                st.markdown(f"**{q_date} İçin Yeni Kayıt**")
                c_a, c_b = st.columns(2)
                f_a, f_p = c_a.text_input("Ad Soyad"), c_b.text_input("Telefon")
                f_f, f_g = c_a.number_input("Gecelik Ücret", min_value=0), c_b.number_input("Gece Sayısı", min_value=1)
                f_n = st.text_area("Notlar")
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, f_n, "Kesin", f_f*f_g] for i in range(int(f_g))]
                    pd.concat([df, pd.DataFrame(new, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear(); st.rerun()

with t2:
    st.markdown("### Kayıtlı Rezervasyonlar")
    ara = st.text_input("İsim Ara...")
    if not df.empty:
        cust_df = get_customer_based_df(df)
        if ara: cust_df = cust_df[cust_df["Ad Soyad"].str.contains(ara, case=False)]
        st.dataframe(cust_df[["Giris_Tarihi", "Ad Soyad", "Tel", "Gece", "Toplam", "Not"]], use_container_width=True, hide_index=True)

with t3:
    st.markdown("### Gider Yönetimi")
    with st.form("gid_f", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        gt, gk, gu = c1.date_input("Tarih"), c2.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), c3.number_input("Tutar")
        ga = st.text_input("Açıklama")
        if st.form_submit_button("Gideri Kaydet"):
            pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
            st.rerun()
    st.dataframe(df_gider, use_container_width=True, hide_index=True)

with t4:
    st.markdown(f"### {sec_ay} Finansal Özet")
    m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_rez["Toplam"].sum()
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stat-box"><small>Ciro</small><br><b>{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><small>Gider</small><br><b>-{m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><small>Net</small><br><b>{ciro - m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    st.markdown("### Veri ve Sistem Yönetimi")
    
    # Müşteri Bazlı Excel İndirme
    if not df.empty:
        report_df = get_customer_based_df(df)
        st.download_button("📊 Müşteri Bazlı Rapor İndir (Excel/CSV)", report_df.to_csv(index=False).encode('utf-8-sig'), "detayvalik_musteri_raporu.csv", "text/csv")
    
    st.divider()
    st.markdown("### Kayıt Silme İşlemi")
    if not df.empty:
        del_df = get_customer_based_df(df)
        for i, r in del_df.iterrows():
            col_x, col_y = st.columns([5, 1])
            col_x.write(f"🗑️ {r['Giris_Tarihi']} | {r['Ad Soyad']} ({r['Toplam']:,} TL)")
            if col_y.button("SİL", key=f"del_{i}", help="Bu rezervasyonu tamamen siler"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]
                df.to_csv("rez.csv", index=False); st.rerun()
