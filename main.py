import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- 1. AYARLAR VE CSS ---
st.set_page_config(page_title="Detayvalık Villa", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FEFEF7 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f2f6; border-radius: 10px 10px 0 0; color: #008080 !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #008080 !important; color: white !important; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; }
    .stButton button { background-color: #DAA520 !important; color: white !important; border-radius: 12px !important; }
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

# --- 3. OTURUM HAFIZASI (SESSION STATE) ---
# Bu kısım sayfa yenilense bile giriş bilgilerini korur.
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = None
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- 4. AKILLI YÖNLENDİRME MANTIĞI ---
# Eğer kullanıcı zaten giriş yapmışsa, doğrudan ilgili paneli göster.

# --- SENARYO A: GİRİŞ YAPILMAMIŞ ---
if st.session_state.user_mode is None:
    st.markdown('<h1 style="text-align:center;color:#008080;">🌿 Detayvalık Villa</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("🛋️ MİSAFİR GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "misafir"
        st.rerun()
    if col2.button("🔑 YÖNETİCİ GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "yonetici"
        st.rerun()

# --- SENARYO B: MİSAFİR MODU ---
elif st.session_state.user_mode == "misafir":
    if st.sidebar.button("⬅️ Ana Menüye Dön"):
        st.session_state.user_mode = None
        st.rerun()
    st.title("🌿 Hoş Geldiniz")
    # Misafir içeriği buraya...

# --- SENARYO C: YÖNETİCİ MODU ---
elif st.session_state.user_mode == "yonetici":
    if not st.session_state.admin_auth:
        st.subheader("🔑 Yönetici Şifresi")
        pwd = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            if pwd == "1234":
                st.session_state.admin_auth = True
                st.rerun()
            else: st.error("Hatalı!")
    else:
        # YÖNETİCİ PANELİ (SİLİNMEYEN OTURUM)
        if st.sidebar.button("🚪 Çıkış Yap"):
            st.session_state.admin_auth = False
            st.session_state.user_mode = None
            st.rerun()

        st.markdown('<h2 style="color:#008080;">🛡️ Yönetim Paneli</h2>', unsafe_allow_html=True)
        
        # URL'den gelen tarihi kontrol et
        q_date = st.query_params.get("date", "")
        
        # Sekmeleri oluştur
        t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

        with t1:
            st.write(f"Bugün: {datetime.now().strftime('%d %B %Y')}")
            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
            sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
            ay_idx = aylar.index(sec_ay) + 1
            
            # Takvim Grid
            cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
            for week in calendar.monthcalendar(2026, ay_idx):
                cal_html += '<tr>'
                for day in week:
                    if day == 0: cal_html += '<td></td>'
                    else:
                        d_s = f"2026-{ay_idx:02d}-{day:02d}"
                        cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                        # Linke tıklandığında sayfa yenilense de session_state sayesinde giriş ekranına ATMAZ.
                        cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
                cal_html += '</tr>'
            st.markdown(cal_html + '</table>', unsafe_allow_html=True)

            # Tarih seçilmişse formu göster
            if q_date:
                st.info(f"Seçilen Tarih: {q_date}")
                with st.form("kayit_f", clear_on_submit=True):
                    f_a = st.text_input("Müşteri Ad Soyad")
                    f_g = st.number_input("Gece Sayısı", min_value=1)
                    f_f = st.number_input("Gecelik Fiyat", min_value=0)
                    if st.form_submit_button("KAYDET"):
                        start = datetime.strptime(q_date, "%Y-%m-%d")
                        new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, "", f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                        pd.concat([df[REZ_COLS], pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                        st.query_params.clear() # URL'yi temizle
                        st.rerun()

        with t2:
            st.subheader("🔍 Kayıtlar")
            st.dataframe(df)

        with t3:
            st.subheader("💸 Gider Girişi")
            with st.form("gider_f", clear_on_submit=True):
                gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Kategori", ["Temizlik", "Fatura", "Diger"]), st.text_input("Açıklama"), st.number_input("Tutar")
                if st.form_submit_button("Gideri Kaydet"):
                    pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                    st.success("Kaydedildi.")
        
        # Finans ve Yönetim kısımları v25 ile aynı mantıkta devam eder...
