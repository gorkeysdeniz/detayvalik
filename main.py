import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP Pro", layout="centered")

# --- MOBİLDE ASLA KAYMAYAN TABLO CSS ---
st.markdown("""
    <style>
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th, td { 
        border: 1px solid #ddd; 
        padding: 8px 2px; 
        text-align: center; 
        font-size: 12px; 
        font-weight: bold;
    }
    th { background-color: #1f2d3d; color: white; }
    .day-link {
        display: block;
        text-decoration: none;
        padding: 10px 0;
        border-radius: 4px;
        color: white;
    }
    .bos { background-color: #28a745; }
    .dolu { background-color: #dc3545; }
    .opsiyon { background-color: #ffc107; color: black; }
    .empty { background-color: transparent; border: none; }
    
    /* Finans Kartları */
    .f-card {
        background: white;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 8px;
        font-size: 14px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
    if not os.path.exists("gider.csv"):
        pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"]).to_csv("gider.csv", index=False)

init_db()
df = pd.read_csv("rez.csv")
gdf = pd.read_csv("gider.csv")

st.title("🏡 Detayvalık VIP Pro")

# --- URL PARAMETRE KONTROLÜ (Tıklanan günü yakalar) ---
params = st.query_params
selected_date = params.get("date", "")

tab1, tab2, tab3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with tab1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.write(f"### {sec_ay} 2026")
    
    # HTML TABLO OLUŞTURMA
    html_table = "<table><thead><tr>"
    for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]:
        html_table += f"<th>{g}</th>"
    html_table += "</tr></thead><tbody>"

    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        html_table += "<tr>"
        for gun in hafta:
            if gun == 0:
                html_table += '<td class="empty"></td>'
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                kayit = df[df["Tarih"] == t_str]
                
                # Durum Belirleme
                cls = "bos"
                if not kayit.empty:
                    cls = "dolu" if kayit.iloc[0]["Durum"] == "Kesin" else "opsiyon"
                
                # Tıklanabilir Link (Kendi URL'sine parametre atar)
                link = f"?date={t_str}"
                html_table += f'<td><a href="{link}" target="_self" class="day-link {cls}">{gun}</a></td>'
        html_table += "</tr>"
    html_table += "</tbody></table>"
    
    st.markdown(html_table, unsafe_allow_html=True)
    st.caption("💡 Tarihe tıklayınca aşağıdaki formu doldurur.")

    # Tıklanan Günün Bilgisi
    if selected_date:
        kayit_detay = df[df["Tarih"] == selected_date]
        if not kayit_detay.empty:
            k = kayit_detay.iloc[0]
            st.warning(f"📍 {selected_date} | **{k['Ad Soyad']}**\n\n📞 {k['Tel']} | 💰 {k['Toplam']} TL")
        else:
            st.success(f"📍 {selected_date} seçildi. Kayıt yapabilirsiniz.")

    st.write("---")
    with st.expander("📝 Kayıt Formu", expanded=True if selected_date else False):
        with st.form("yeni_form"):
            f1, f2 = st.columns(2)
            t_in = f1.text_input("Giriş Tarihi", value=selected_date)
            ad_in = f2.text_input("Müşteri İsim")
            tel_in = f1.text_input("Telefon")
            u_in = f2.number_input("Günlük Ücret", min_value=0)
            g_in = f1.number_input("Gece", min_value=1)
            d_in = f2.selectbox("Durum", ["Kesin", "Opsiyonel"])
            not_in = st.text_area("Not")
            if st.form_submit_button("KAYDET"):
                start = datetime.strptime(t_in, "%Y-%m-%d")
                rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), ad_in, tel_in, u_in, g_in, not_in, d_in, u_in*g_in] for i in range(int(g_in))]
                pd.concat([df, pd.DataFrame(rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                st.query_params.clear() # Formu temizle
                st.rerun()

with tab3:
    st.subheader(f"📊 {sec_ay} Analizi")
    m_no = aylar.index(sec_ay) + 1
    bu_ay = df[pd.to_datetime(df["Tarih"]).dt.month == m_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut = bu_ay["Toplam"].sum()
    gider = gdf[pd.to_datetime(gdf["Tarih"]).dt.month == m_no]["Tutar"].sum()
    
    # KDV %20, Konaklama %2, Komisyon %15
    kdv = brut * 0.20
    konaklama = brut * 0.02
    komisyon = brut * 0.15
    net = brut - gider - kdv - konaklama - komisyon

    st.markdown(f"""
    <div class="f-card">💰 Brüt: {brut:,.0f} TL</div>
    <div class="f-card">🧾 KDV (%20): -{kdv:,.0f} TL</div>
    <div class="f-card">🏢 Konaklama Vergisi (%2): -{konaklama:,.0f} TL</div>
    <div class="f-card">💸 Gider: -{gider:,.0f} TL</div>
    <div class="f-card" style="border-left:5px solid #28a745">✅ <b>NET KAR: {net:,.0f} TL</b></div>
    """, unsafe_allow_html=True)
