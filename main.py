import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP", layout="wide")

# --- MOBİL UYUMLU TAKVİM TASARIMI (CSS) ---
st.markdown("""
    <style>
    .calendar-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .calendar-header {
        font-weight: bold;
        padding: 10px 0;
        background-color: #1f2d3d;
        color: white;
        font-size: 12px;
        border-radius: 5px;
    }
    .day-box {
        padding: 15px 0;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #ddd;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .bos { background-color: #28a745; color: white; }
    .dolu { background-color: #dc3545; color: white; }
    .opsiyon { background-color: #ffc107; color: black; }
    .empty { background-color: transparent; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YÖNETİMİ ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
    if not os.path.exists("gider.csv"):
        pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"]).to_csv("gider.csv", index=False)

init_db()
df = pd.read_csv("rez.csv")
gdf = pd.read_csv("gider.csv")

st.title("🏙️ Detayvalık VIP")

tab1, tab2, tab3 = st.tabs(["📅 TAKVİM", "🔍 SORGULA", "📊 FİNANS"])

with tab1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seç", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    # GERÇEK TAKVİM GÖRÜNÜMÜ (HTML İLE)
    st.write(f"### {sec_ay} 2026")
    
    # Gün Başlıkları
    h_html = '<div class="calendar-container">'
    for g in ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]:
        h_html += f'<div class="calendar-header">{g}</div>'
    
    # Takvim Günleri
    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        for gun in hafta:
            if gun == 0:
                h_html += '<div class="day-box empty"></div>'
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                kayit = df[df["Tarih"] == t_str]
                
                status_class = "bos"
                if not kayit.empty:
                    durum = kayit.iloc[0]["Durum"]
                    status_class = "dolu" if durum == "Kesin" else "opsiyon"
                
                h_html += f'<div class="day-box {status_class}">{gun}</div>'
    
    h_html += '</div>'
    st.markdown(h_html, unsafe_allow_html=True)

    st.info("💡 Not: Kayıt eklemek veya detay görmek için aşağıdaki formu/sorgu panelini kullanın. (HTML takvimde tıklama yerine güvenli kayıt formuna odaklandık.)")

    st.divider()
    with st.expander("➕ Yeni Rezervasyon Ekle"):
        with st.form("rez_form"):
            t_input = st.text_input("Giriş Tarihi (YYYY-AA-GG)", placeholder="2026-07-15")
            ad_input = st.text_input("Müşteri Ad Soyad")
            tel_input = st.text_input("Telefon")
            u_input = st.number_input("Günlük Ücret", min_value=0)
            g_input = st.number_input("Gece Sayısı", min_value=1)
            d_input = st.selectbox("Durum", ["Kesin", "Opsiyonel"])
            not_input = st.text_area("Notlar")
            
            if st.form_submit_button("Kaydet"):
                try:
                    start = datetime.strptime(t_input, "%Y-%m-%d")
                    new_rows = []
                    for d in range(int(g_input)):
                        target_t = (start + timedelta(days=d)).strftime("%Y-%m-%d")
                        new_rows.append([target_t, ad_input, tel_input, u_input, g_input, not_input, d_input, u_input*g_input])
                    pd.concat([df, pd.DataFrame(new_rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                    st.success("Kayıt Başarılı!"); st.rerun()
                except: st.error("Hata! Tarih formatı: YYYY-AA-GG")

with tab2:
    st.subheader("🔍 Kayıt Listesi")
    ara = st.text_input("İsim Ara...").lower()
    temp_df = df.drop_duplicates(subset=["Ad Soyad", "Toplam"]).copy()
    if ara:
        temp_df = temp_df[temp_df["Ad Soyad"].str.lower().str.contains(ara, na=False)]
    st.dataframe(temp_df, use_container_width=True)

with tab3:
    st.subheader("💰 Finansal Özet")
    f_ay = st.selectbox("Dönem", aylar, key="fin", index=datetime.now().month-1)
    f_no = aylar.index(f_ay) + 1
    
    brut = df[pd.to_datetime(df["Tarih"]).dt.month == f_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])["Toplam"].sum()
    gider = gdf[pd.to_datetime(gdf["Tarih"]).dt.month == f_no]["Tutar"].sum()
    kdv = brut * 0.10
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Brüt", f"{brut} TL")
    c2.metric("Gider", f"-{gider} TL")
    c3.metric("Net", f"{brut-gider-kdv} TL")
    
    with st.expander("💸 Gider Ekle"):
        with st.form("g_form"):
            gt = st.date_input("Tarih"); gk = st.selectbox("Tür", ["Temizlik", "Fatura", "Tamirat", "Diğer"]); gu = st.number_input("Tutar")
            if st.form_submit_button("Gider Kaydet"):
                pd.concat([gdf, pd.DataFrame([[str(gt),gk,"Gider",gu]], columns=gdf.columns)]).to_csv("gider.csv", index=False)
                st.rerun()
