import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYVALIK REHBER VERİSİ (BOTUN TEMELİ) ---
AYVALIK_REHBERI = {
    "tost": "🥪 Ayvalık'ta tost denince: Tostuyevski, Aşkın Tost Evi ve Tadım Tost Evi en iyileridir.",
    "beach": "🏖️ Ücretli & Kaliteli: Ayvalık Sea Long, Ajlan Beach, Kesebir veya Scala Beach.",
    "plaj": "🌊 Ücretsiz & Doğal: Badavut Plajı, Sarımsaklı Plajı veya Ortunç Koyu.",
    "kafe": "☕ Kahve Keyfi: Pinos Cafe Sarımsaklı, Nona Cunda, Crew Coffee.",
    "kokteyl": "🍹 Akşam Eğlencesi: Kaktüs Cunda, Ciello Cunda, Luna Cunda veya Rituel 1873.",
    "pizza": "🍕 En İyi Pizzacılar: Cunda Uno, Küçük İtalya (Küçükköy), Pizza Teos veya Tino Pizza Ristorante.",
    "tarih": "🏛️ Kültür Rotası: Ayvalık Ayazması, Rahmi Koç Müzesi, Taksiyarhis Kilisesi, Yel Değirmeni ve Şeytan Sofrası.",
    "ödül": "🏅 Gurme (Michelin/Gault): Ayna (Cunda), Bay Nihat ve L'Arancia (Michelin) mutlaka denenmeli."
}

# --- 2. GENEL AYARLAR ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık v42.5", layout="wide")

# --- 3. MÜŞTERİ MODU (GUEST MODE) ---
# URL sonuna ?guest=true eklenince devreye giren kısım
is_guest = st.query_params.get("guest", "false") == "true"

if is_guest:
    st.markdown("# 🏡 Detayvalık Misafir Asistanı")
    st.info("🗝️ **Villa Bilgileri:** Giriş: 14:00 | Çıkış: 11:00 | Wi-Fi: VillaDetay_2026 / Şifre: Ayvalik10")
    
    st.write("### 🤖 Ayvalık Rehberine Sor")
    user_q = st.text_input("Nereyi keşfetmek istersiniz?", placeholder="Örn: Beach, Tost, Pizza...")
    
    if user_q:
        found = False
        for anahtar, cevap in AYVALIK_REHBERI.items():
            if anahtar in user_q.lower():
                st.success(f"🤖 **Bot:** {cevap}")
                found = True
                break
        if not found:
            st.warning("🤖 **Bot:** Bunu henüz bilmiyorum ama 'Beach', 'Tost' veya 'Pizza' gibi kelimelerle sorarsan yardımcı olabilirim!")
    
    with st.expander("📍 Tüm Önerilerimizi Gör"):
        for k, v in AYVALIK_REHBERI.items():
            st.write(f"**{k.capitalize()}:** {v}")
    
    st.stop() # Misafir paneli burada biter, yönetim paneli yüklenmez.

# --- 4. YÖNETİM PANELİ (SENİN EKRANIN) ---
st.markdown("""<style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link { background-color: #25D366; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; }
    </style>""", unsafe_allow_html=True)

# Veri Yükleme
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])

def get_clean_df(input_df):
    if input_df.empty: return input_df
    temp = input_df.copy().fillna("")
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# Hesaplamalar
now = datetime.now()
curr_month, curr_year = now.month, now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]
df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]
booked_count = len(month_df)
empty_count = month_days - booked_count
occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0
clean_df = get_clean_df(df)
avg_stay = clean_df['Gece'].astype(float).mean() if not clean_df.empty else 0

st.markdown('<div class="main-header">Detayvalık Yönetim v42.5</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# TAB 1: TAKVİM & ÖZET (v42.4 İskeletiyle aynı)
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1]); sec_ay = c1.selectbox("Ay Seçin", aylar, index=curr_month-1); ay_idx = aylar.index(sec_ay) + 1
    
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"; cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    st.divider(); st.subheader("📊 Performans")
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f'<div class="stat-box"><small>Doluluk</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b>{avg_stay:.1f}</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Boş Gün</small><br><b style="color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    d4.markdown(f'<div class="stat-box"><small>Kalan Gün</small><br><b>{max(0, (month_days - now.day))} Gün</b></div>', unsafe_allow_html=True)

# TAB 2: REZERVASYONLAR & WHATSAPP
with t_rez:
    st.info("💡 Müşteri Linki: `https://senin-app-ismin.streamlit.app/?guest=true`")
    if not df.empty:
        r_list = get_clean_df(df)
        for i, r in r_list.iterrows():
            ca, cb = st.columns([4, 2])
            ca.markdown(f"**{r['Ad Soyad']}** | 📞 {r['Tel']}\n📅 {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']} | 💰 {r['Toplam']:,} TL")
            if r['Tel']:
                t_cl = str(r['Tel']).replace(' ','').replace('+','')
                msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz onaylanmıştır. Rehberimiz için: https://senin-app-ismin.streamlit.app/?guest=true")
                cb.markdown(f'<a href="https://wa.me/{t_cl}?text={msg}" target="_blank" class="wa-link">WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

# TAB 3: FİNANSAL TABLO (NET KÂR ODAKLI)
with t_fin:
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    v_kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    v_konak = b_ciro - (b_ciro / (1 + TURIZM_VERGISI))
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]; t_gider = m_gid["Tutar"].sum()
    
    st.subheader(f"💰 {sec_ay} Finansal Özeti")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Gelir", f"{b_ciro:,.0f} TL")
    f2.metric("Vergiler", f"-{(v_kdv + v_konak):,.0f} TL", delta_color="inverse")
    f3.metric("Giderler", f"-{t_gider:,.0f} TL", delta_color="inverse")
    f4.metric("NET KÂR", f"{(b_ciro - v_kdv - v_konak - t_gider):,.0f} TL")

# TAB 4: AYARLAR (SİLME & YEDEK)
with t_set:
    st.download_button("Excel Yedek Al", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "yedek.csv")
