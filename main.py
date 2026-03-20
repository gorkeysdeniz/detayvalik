import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP Pro", layout="wide")

# --- MOBİLDE ASLA BOZULMAYAN 7'Lİ SİSTEM (CSS FLEX) ---
st.markdown("""
    <style>
    .flex-container {
        display: flex;
        flex-wrap: nowrap;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 5px;
    }
    .flex-item {
        flex: 1;
        margin: 2px;
        text-align: center;
    }
    .stButton>button {
        width: 100% !important;
        height: 50px !important;
        padding: 0 !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
    /* Boş günler için görünmezlik */
    .hidden-btn { visibility: hidden; pointer-events: none; }
    
    /* Finans Kartları */
    .f-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 10px;
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

st.title("🏡 Detayvalık Yönetim")

tab1, tab2, tab3 = st.tabs(["📅 TAKVİM GİRİŞİ", "🔍 REZERVASYONLAR", "💰 FİNANS VE KDV"])

with tab1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.write(f"### {sec_ay} 2026")
    
    # Gün Başlıkları (Yan yana sabit)
    st.markdown('<div class="flex-container">' + 
        ''.join([f'<div class="flex-item"><b>{g}</b></div>' for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]]) + 
        '</div>', unsafe_allow_html=True)

    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        # Streamlit'in kendi sütun yapısı yerine Flexbox konteyneri simüle ediyoruz
        cols = st.columns(7) 
        for i, gun in enumerate(hafta):
            with cols[i]:
                if gun == 0:
                    st.markdown('<div class="hidden-btn">', unsafe_allow_html=True)
                    st.button("", key=f"empty_{hafta}_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    t_str = f"2026-{ay_no:02d}-{gun:02d}"
                    kayit = df[df["Tarih"] == t_str]
                    
                    # Renk Kodları
                    color = "#28a745" # Boş
                    if not kayit.empty:
                        color = "#dc3545" if kayit.iloc[0]["Durum"] == "Kesin" else "#ffc107"
                    
                    st.markdown(f'<style>button[key="btn_{t_str}"] {{ background-color: {color} !important; color: white !important; }}</style>', unsafe_allow_html=True)
                    
                    if st.button(f"{gun}", key=f"btn_{t_str}"):
                        if not kayit.empty:
                            st.session_state.detay = kayit.iloc[0].to_dict()
                        else:
                            st.session_state.t_sec = t_str
                            st.session_state.detay = None

    # Detay veya Kayıt Paneli
    if 'detay' in st.session_state and st.session_state.detay:
        d = st.session_state.detay
        st.warning(f"📍 {d['Tarih']} | **{d['Ad Soyad']}** ({d['Durum']})\n\n📞 {d['Tel']} | 💰 {d['Toplam']} TL\n\n📝 {d['Not']}")
        if st.button("Seçimi Kapat"): st.session_state.detay = None; st.rerun()

    st.write("---")
    with st.expander("📝 Kayıt Ekle", expanded=True if 't_sec' in st.session_state else False):
        with st.form("yeni_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            t_in = f1.text_input("Giriş Tarihi", value=st.session_state.get('t_sec', ''))
            ad_in = f2.text_input("Müşteri İsim")
            tel_in = f1.text_input("Telefon")
            u_in = f2.number_input("Günlük Ücret", min_value=0)
            g_in = f1.number_input("Gece", min_value=1)
            d_in = f2.selectbox("Durum", ["Kesin", "Opsiyonel"])
            not_in = st.text_area("Not")
            if st.form_submit_button("Sisteme Kaydet"):
                start = datetime.strptime(t_in, "%Y-%m-%d")
                rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), ad_in, tel_in, u_in, g_in, not_in, d_in, u_in*g_in] for i in range(int(g_in))]
                pd.concat([df, pd.DataFrame(rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                st.session_state.t_sec = ""; st.success("Kayıt Tamam!"); st.rerun()

with tab3:
    st.subheader("📊 Finansal Tablo")
    f_ay = st.selectbox("Ay", aylar, index=datetime.now().month-1, key="f_ay")
    m_no = aylar.index(f_ay) + 1
    
    # Hesaplama
    bu_ay = df[pd.to_datetime(df["Tarih"]).dt.month == m_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut = bu_ay["Toplam"].sum()
    gider = gdf[pd.to_datetime(gdf["Tarih"]).dt.month == m_no]["Tutar"].sum()
    
    kdv = brut * 0.20
    konaklama = brut * 0.02
    komisyon = brut * 0.15 # Tahmini Airbnb/Booking
    net = brut - gider - kdv - konaklama - komisyon

    st.markdown(f"""
    <div class="f-card">💰 <b>Brüt Ciro:</b> {brut:,.0f} TL</div>
    <div class="f-card">🧾 <b>KDV (%20):</b> -{kdv:,.0f} TL</div>
    <div class="f-card">🏨 <b>Konaklama Vergisi (%2):</b> -{konaklama:,.0f} TL</div>
    <div class="f-card">🌐 <b>Platform Komisyonu (%15):</b> -{komisyon:,.0f} TL</div>
    <div class="f-card">💸 <b>Toplam Gider:</b> -{gider:,.0f} TL</div>
    <div class="f-card" style="border-left:5px solid green">✅ <b>NET KAR: {net:,.0f} TL</b></div>
    """, unsafe_allow_html=True)
    
    # Gider Ekleme
    with st.expander("➕ Gider Ekle"):
        with st.form("g_f"):
            gt = st.date_input("Tarih"); ga = st.text_input("Açıklama"); gu = st.number_input("Tutar")
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([gdf, pd.DataFrame([[str(gt),"Genel",ga,gu]], columns=gdf.columns)]).to_csv("gider.csv", index=False)
                st.rerun()
