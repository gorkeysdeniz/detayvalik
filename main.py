import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık Pro VIP", layout="wide")

# --- MOBİL UYUMLU CSS ---
st.markdown("""
    <style>
    [data-testid="column"] { width: 14% !important; flex: 1 1 14% !important; min-width: 14% !important; padding: 2px !important; }
    .stButton>button { width: 100% !important; height: 55px !important; padding: 0 !important; border-radius: 6px !important; font-weight: bold !important; font-size: 14px !important; }
    /* Boş günler için görünmez buton alanı */
    .empty-btn button { visibility: hidden; }
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

st.title("🏙️ Detayvalık Yönetim Paneli")

tab1, tab2, tab3 = st.tabs(["📅 TAKVİM & GİRİŞ", "🔍 KAYITLAR", "💸 FİNANSAL ANALİZ"])

with tab1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.subheader(f"{sec_ay} 2026")
    
    # Gün Başlıkları
    h_cols = st.columns(7)
    for i, g in enumerate(["Pt", "Sa", "Ça", "Pe", "Cu", "Ct", "Pz"]):
        h_cols[i].markdown(f"<center><small>{g}</small></center>", unsafe_allow_html=True)

    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        cols = st.columns(7)
        for i, gun in enumerate(hafta):
            if gun == 0:
                cols[i].markdown('<div class="empty-btn">', unsafe_allow_html=True)
                cols[i].button("", key=f"empty_{hafta}_{i}")
                cols[i].markdown('</div>', unsafe_allow_html=True)
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                kayit = df[df["Tarih"] == t_str]
                
                # Renk Mantığı
                bg_color = "#28a745" # Boş - Yeşil
                if not kayit.empty:
                    bg_color = "#dc3545" if kayit.iloc[0]["Durum"] == "Kesin" else "#ffc107"
                
                st.markdown(f'<style>button[key="btn_{t_str}"] {{ background-color: {bg_color} !important; color: white !important; }}</style>', unsafe_allow_html=True)
                
                if cols[i].button(f"{gun}", key=f"btn_{t_str}"):
                    if not kayit.empty:
                        st.session_state.detay = kayit.iloc[0].to_dict()
                    else:
                        st.session_state.t_sec = t_str
                        st.session_state.detay = None

    # Tıklanan Günün Detayı veya Kayıt Formu
    if 'detay' in st.session_state and st.session_state.detay:
        d = st.session_state.detay
        st.info(f"📍 **{d['Tarih']}** | Müşteri: **{d['Ad Soyad']}** | Durum: {d['Durum']}\n\n📞 {d['Tel']} | 💰 Toplam: {d['Toplam']} TL")
        if st.button("Seçimi Temizle"): 
            st.session_state.detay = None
            st.rerun()

    st.divider()
    st.markdown("### 📝 Rezervasyon Girişi")
    with st.form("rez_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        g_tar = f1.text_input("Giriş Tarihi (Takvimden seçin)", value=st.session_state.get('t_sec', ''))
        isim = f2.text_input("Müşteri Ad Soyad")
        tel = f3.text_input("Telefon")
        
        f4, f5, f6 = st.columns(3)
        gunluk = f4.number_input("Günlük Ücret (TL)", min_value=0)
        gece = f5.number_input("Gece Sayısı", min_value=1)
        durum = f6.selectbox("Rez. Durumu", ["Kesin", "Opsiyonel"])
        notlar = st.text_area("Notlar (Opsiyonel)")
        
        if st.form_submit_button("RESERVASYONU KAYDET"):
            if g_tar and isim:
                start_dt = datetime.strptime(g_tar, "%Y-%m-%d")
                yeni_veriler = []
                for j in range(int(gece)):
                    yeni_veriler.append([(start_dt + timedelta(days=j)).strftime("%Y-%m-%d"), isim, tel, gunluk, gece, notlar, durum, gunluk*gece])
                
                yeni_df = pd.DataFrame(yeni_veriler, columns=df.columns)
                pd.concat([df, yeni_df]).to_csv("rez.csv", index=False)
                st.success("Kayıt başarıyla eklendi!")
                st.session_state.t_sec = ""
                st.rerun()
            else:
                st.error("Lütfen tarih ve isim giriniz!")

with tab3:
    st.header("📊 Finansal Durum Raporu")
    sec_ay_fin = st.selectbox("Analiz Ayı", aylar, index=datetime.now().month-1, key="fin_ay")
    m_no = aylar.index(sec_ay_fin) + 1
    
    # Bu ayın verilerini filtrele
    bu_ay_rez = df[pd.to_datetime(df["Tarih"]).dt.month == m_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    toplam_brut = bu_ay_rez["Toplam"].sum()
    
    # Giderler
    bu_ay_gider = gdf[pd.to_datetime(gdf["Tarih"]).dt.month == m_no]["Tutar"].sum()
    
    # Vergi ve Komisyon Hesaplamaları
    kdv = toplam_brut * 0.20
    konaklama_vergisi = toplam_brut * 0.02
    ota_komisyon = toplam_brut * 0.15 # Airbnb/Booking ortalama
    
    net_kazanc = toplam_brut - kdv - konaklama_vergisi - ota_komisyon - bu_ay_gider

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Brüt Ciro", f"{toplam_brut:,.0f} TL")
    c2.metric("KDV (%20)", f"-{kdv:,.0f} TL", delta_color="inverse")
    c3.metric("Platform Kom. (%15)", f"-{ota_komisyon:,.0f} TL")
    c4.metric("Net Kar", f"{net_kazanc:,.0f} TL", delta=f"Gider: {bu_ay_gider}")

    st.write("---")
    st.subheader("💸 Gider Ekle")
    with st.form("gider_form"):
        g1, g2, g3 = st.columns(3)
        g_tarih = g1.date_input("Gider Tarihi")
        g_kat = g2.selectbox("Kategori", ["Temizlik", "Elektrik/Su", "Aidat", "Tamirat", "Pazarlama", "Diğer"])
        g_tutar = g3.number_input("Tutar (TL)", min_value=0)
        g_aciklama = st.text_input("Açıklama")
        if st.form_submit_button("GİDERİ İŞLE"):
            yeni_gider = pd.DataFrame([[g_tarih, g_kat, g_aciklama, g_tutar]], columns=gdf.columns)
            pd.concat([gdf, yeni_gider]).to_csv("gider.csv", index=False)
            st.rerun()
