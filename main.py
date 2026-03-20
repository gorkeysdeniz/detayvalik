import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. GÜVENLİK & YEREL VERİ BANKASI ---
ADMIN_PASSWORD = "123" # Burayı kendine göre güncelleyebilirsin

# MEKANLAR VE GOOGLE HARİTALAR LİNKLERİ
MEKANLAR = {
    "tost": {
        "cevap": "Ayvalık'ta tost bir sanattır! En iyi duraklar şunlar:",
        "liste": ["Tostuyevski", "Aşkın Tost Evi", "Tadım Tost Evi"],
        "konum": "https://www.google.com/maps/search/Ayvalık+Tostçular+Çarşısı"
    },
    "beach": {
        "cevap": "Denizin tadını çıkarabileceğiniz kaliteli beachler:",
        "liste": ["Ayvalık Sea Long", "Ajlan Beach", "Kesebir Beach", "Scala Beach"],
        "konum": "https://www.google.com/maps/search/Sarımsaklı+Beachler"
    },
    "plaj": {
        "cevap": "Ücretsiz ve doğal plaj önerilerim:",
        "liste": ["Badavut Plajı", "Sarımsaklı Plajı", "Ortunç Koyu"],
        "konum": "https://www.google.com/maps/search/Ayvalık+Halk+Plajları"
    },
    "pizza": {
        "cevap": "Ayvalık'ta İtalyan rüzgarı esen en iyi pizzacılar:",
        "liste": ["Cunda Uno", "Küçük İtalya Küçükköy", "Pizza Teos", "Tino Pizza"],
        "konum": "https://www.google.com/maps/search/Ayvalık+Pizzacılar"
    },
    "tarih": {
        "cevap": "Ayvalık'ın tarih kokan sokaklarında buraları görmelisiniz:",
        "liste": ["Ayazma", "Rahmi Koç Müzesi", "Taksiyarhis Kilisesi", "Şeytan Sofrası"],
        "konum": "https://www.google.com/maps/search/Ayvalık+Tarihi+Yerler"
    }
}

st.set_page_config(page_title="Detayvalık Operasyon v42.6", layout="wide")

# --- 2. GİRİŞ KONTROLÜ (GUEST VS ADMIN) ---
is_guest = st.query_params.get("guest", "false") == "true"

# --- MÜŞTERİ SAYFASI (DETAYVALIK AI) ---
if is_guest:
    st.markdown("# 🏡 Detayvalık Akıllı Asistan")
    st.info("🗝️ **Villa Kuralları:** Giriş 14:00 | Çıkış 11:00 | Wi-Fi: VillaDetay / Şifre: Ayvalik10")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Merhaba! Ben Detayvalık rehberiniz. Size yemek, plaj veya gezilecek yerler konusunda nasıl yardımcı olabilirim?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Nereyi keşfetmek istersiniz?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            found = False
            p_low = prompt.lower()
            for key, data in MEKANLAR.items():
                if key in p_low:
                    res = f"🤖 {data['cevap']}\n\n" + "\n".join([f"- {m}" for m in data['liste']])
                    res += f"\n\n📍 [Haritalarda Göster]({data['konum']})"
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    found = True
                    break
            if not found:
                res = "🤖 Bunu henüz bilmiyorum ama 'Tost', 'Pizza', 'Beach' veya 'Tarih' derseniz size harika öneriler sunabilirim!"
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})
    st.stop()

# --- YÖNETİCİ PANELİ (GÜVENLİ GİRİŞ) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("### 🔒 Yönetici Panel Girişi")
    pwd = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else: st.error("Hatalı şifre!")
    st.stop()

# --- 3. YÖNETİM PANELİ (TAKTAK ÇALIŞAN v42.4 İSKELETİ) ---
st.markdown('<h2 style="color:#1A3636;">🏡 Detayvalık Yönetim Merkezi</h2>', unsafe_allow_html=True)

# Veri Yükleme Fonksiyonları
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])

t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    now = datetime.now()
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1]); sec_ay = c1.selectbox("Ay Seçin", aylar, index=now.month-1); ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Çizimi
    cal_html = '<table style="width:100%; text-align:center; border-collapse:collapse;"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"; cl = "#A94438" if not df[df["Tarih"] == d_s].empty else "#4F6F52"
                cal_html += f'<td><div style="background:{cl}; color:white; padding:10px; border-radius:5px; margin:2px;">{day}</div></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

# --- TAB 2: REZERVASYONLAR ---
with t_rez:
    st.write("### Aktif Kayıtlar")
    if not df.empty:
        # İsim bazlı gruplayıp telefonları gösteriyoruz
        temp_df = df.groupby(["Ad Soyad", "Tel", "Toplam"]).agg(Giris=("Tarih", "min")).reset_index()
        for i, r in temp_df.iterrows():
            st.write(f"👤 {r['Ad Soyad']} | 📞 {r['Tel']} | 💰 {r['Toplam']:,} TL")
            st.divider()

# --- TAB 3: FİNANS (NET KÂR) ---
with t_fin:
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_fin["Toplam"].sum()
    st.metric("Aylık Brüt Ciro", f"{ciro:,.0f} TL")
    # Gider ekleme formu buraya eklenebilir

# --- TAB 4: AYARLAR ---
with t_set:
    if st.button("🔴 Tüm Verileri Sıfırla (Dikkat!)"):
        if os.path.exists("rez.csv"): os.remove("rez.csv")
        st.rerun()
