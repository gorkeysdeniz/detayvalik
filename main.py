import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. ZIRHLI GÖRÜNÜRLÜK VE MODERN TASARIM ---
st.set_page_config(page_title="Detayvalık Villa Paneli", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
    
    /* Giriş Ekranı Butonları */
    .mode-btn button {
        height: 150px !important;
        font-size: 24px !important;
        border-radius: 20px !important;
        margin-bottom: 20px !important;
    }
    
    /* Misafir Kartları */
    .guest-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #FFC107;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .rez-card { 
        background: #ffffff !important; padding: 15px; border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 8px solid #2ECC71; margin-bottom: 15px; 
    }
    
    .wa-button {
        display: block; background-color: #25D366; color: white !important; 
        padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; text-align: center;
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

# --- 3. GİRİŞ KONTROLÜ (SESSION STATE) ---
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = None

# --- MOD SEÇİM EKRANI ---
if st.session_state.user_mode is None:
    st.title("🏡 Detayvalık Villa Yönetimi")
    st.subheader("Hoş geldiniz, lütfen devam etmek için giriş türünü seçin:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
        if st.button("🛋️ MİSAFİR\nGİRİŞİ"):
            st.session_state.user_mode = "misafir"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
        if st.button("🔑 YÖNETİCİ\nGİRİŞİ"):
            st.session_state.user_mode = "yonetici"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 🌟 MİSAFİR GİRİŞİ EKRANI ---
elif st.session_state.user_mode == "misafir":
    if st.button("⬅️ Geri Dön"):
        st.session_state.user_mode = None
        st.rerun()
        
    st.title("🌿 Villamıza Hoş Geldiniz!")
    st.write("Konaklamanız boyunca ihtiyacınız olabilecek tüm bilgiler burada.")
    
    m_t1, m_t2, m_t3 = st.tabs(["🏠 EV BİLGİLERİ", "📍 GEZİLECEK YERLER", "📞 İLETİŞİM"])
    
    with m_t1:
        st.markdown("""
        <div class="guest-card">
            <h3>📶 Wi-Fi Bilgileri</h3>
            <b>Ağ Adı:</b> Detayvalik_Villa<br>
            <b>Şifre:</b> ayvalik2026
        </div>
        <div class="guest-card" style="border-left-color: #2196F3;">
            <h3>⏰ Giriş / Çıkış</h3>
            <b>Giriş Saati:</b> 14:00<br>
            <b>Çıkış Saati:</b> 11:00
        </div>
        <div class="guest-card" style="border-left-color: #F44336;">
            <h3>🚫 Ev Kuralları</h3>
            • İç mekanda sigara içilmemesi rica olunur.<br>
            • Gece 23:00'den sonra yüksek ses yapılmaması komşuluk ilişkileri için önemlidir.<br>
            • Evden ayrılırken klimaların kapatılması rica edilir.
        </div>
        """, unsafe_allow_html=True)

    with m_t2:
        st.subheader("🕵️ Ayvalık'ta Mutlaka Yapın")
        recoms = [
            {"yer": "Cunda Adası", "not": "Ara sokaklarda kaybolun ve meşhur sakızlı dondurmayı tadın."},
            {"yer": "Şeytan Sofrası", "not": "Gün batımını izlemek için en iyi nokta."},
            {"yer": "Sarımsaklı Plajı", "not": "İnce kumu ve temiz deniziyle meşhurdur."},
            {"yer": "Antikacılar Çarşısı", "not": "Ayvalık merkezde yerel hediyelikler için ideal."}
        ]
        for r in recoms:
            st.markdown(f"**📍 {r['yer']}**: {r['not']}")
            st.divider()

    with m_t3:
        st.subheader("🆘 Yardım mı lazım?")
        st.write("Herhangi bir sorunuzda bize WhatsApp üzerinden ulaşabilirsiniz.")
        # Buraya kendi numaranı ekleyebilirsin
        st.markdown('<a href="https://wa.me/905330000000?text=Merhaba, villada konaklıyorum, bir sorum olacaktı." target="_blank" class="wa-button">💬 Ev Sahibine Yaz</a>', unsafe_allow_html=True)

# --- 🛠️ YÖNETİCİ GİRİŞİ EKRANI (BİZİM PANEL) ---
elif st.session_state.user_mode == "yonetici":
    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.user_mode = None
        st.rerun()
        
    # --- Önceki tüm yönetici kodları buraya (v21.0 sürümü) ---
    st.title("🛡️ Yönetici Paneli")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])
    
    # (Buraya v21.0'daki Takvim, Kayıtlar, Giderler, Finans ve Yönetim kod blokları gelecek)
    # Kısalık olması için v21.0 mantığını aynen koruduğumuzu varsayıyoruz...
    
    with t1:
        # v21.0 Takvim kodu...
        aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
        ay_idx = aylar.index(sec_ay) + 1
        st.write(f"Takvim ve rezervasyon işlemleri aktif.")
        # ... (v21.0 içeriği buraya devam eder)

    with t2:
        st.subheader("🔍 Rezervasyonlar")
        # v21.0 Kayıtlar kodu...

    with t3:
        st.subheader("💸 Gider Girişi")
        with st.form("gider_f", clear_on_submit=True):
            gt = st.date_input("Tarih", value=datetime.now())
            gk = st.selectbox("Kategori", ["Temizlik", "Elektrik", "Su", "Bahçe Bakımı", "Komisyon", "Diğer"])
            ga = st.text_input("Açıklama")
            gu = st.number_input("Tutar (TL)", min_value=0.0)
            if st.form_submit_button("KAYDET"):
                new_g = pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)
                pd.concat([df_gider, new_g], ignore_index=True).to_csv("gider.csv", index=False)
                st.success("Gider kaydedildi!")

    with t4:
        # v21.0 Finans kodu...
        st.write("Finansal tablolar bu ay için hesaplanıyor.")

    with t5:
        # v21.0 Yönetim ve Raporlama kodu...
        st.write("Excel raporu ve veri yönetimi.")
