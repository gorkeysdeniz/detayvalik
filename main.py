import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      # %10 KDV
TURIZM_VERGISI = 0.02 # %2 Konaklama Vergisi

st.set_page_config(page_title="Villa Yönetim Sistemi v42.1", layout="wide")

# Tasarım Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 12px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .info-panel { background: #F8F4EC; border: 1px solid #D6BD98; padding: 20px; border-radius: 8px; margin-top: 15px; }
    .wa-link { background-color: #25D366; color: white !important; padding: 5px 12px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])

def get_clean_df(input_df):
    if input_df.empty: return input_df
    res = input_df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 3. ANALİTİK HESAPLAR ---
now = datetime.now()
curr_month, curr_year = now.month, now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]
df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]

booked_count = len(month_df)
empty_count = month_days - booked_count
occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0
days_left = month_days - now.day

clean_df = get_clean_df(df)
avg_stay = clean_df['Gece'].astype(float).mean() if not clean_df.empty else 0

# Finansal Özet (Bu Ay)
brut_ciro = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
kdv_kesinti = brut_ciro - (brut_ciro / (1 + KDV_ORANI))
konak_kesinti = brut_ciro - (brut_ciro / (1 + TURIZM_VERGISI))
gider_toplam = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == curr_month]["Tutar"].sum()
aylik_net_kar = brut_ciro - kdv_kesinti - konak_kesinti - gider_toplam

# --- 4. ANA EKRAN (TAKVİM) ---
st.title("🏡 Villa Rezervasyon & Takvim")

aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
c_ay, c_yil = st.columns([2, 1])
sec_ay = c_ay.selectbox("Ay Seçimi", aylar, index=curr_month-1)
ay_idx = aylar.index(sec_ay) + 1

# Takvim Çizimi
cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
for week in calendar.monthcalendar(2026, ay_idx):
    cal_html += '<tr>'
    for day in week:
        if day == 0: cal_html += '<td></td>'
        else:
            d_s = f"2026-{ay_idx:02d}-{day:02d}"
            cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
            cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
    cal_html += '</tr>'
st.markdown(cal_html + '</table>', unsafe_allow_html=True)

# Rezervasyon Ekleme/Görüntüleme (Sorgu Parametresi ile)
q_date = st.query_params.get("date", "")
if q_date:
    day_data = df[df["Tarih"] == q_date]
    if not day_data.empty:
        st.info(f"📍 {q_date} Tarihinde: {day_data.iloc[0]['Ad Soyad']} konaklıyor.")
    else:
        with st.form("yeni"):
            st.write(f"➕ **{q_date}** Tarihine Rezervasyon")
            f_ad = st.text_input("Ad Soyad")
            f_fiy = st.number_input("Gecelik Ücret", min_value=0)
            f_gece = st.number_input("Gece Sayısı", min_value=1)
            if st.form_submit_button("Kaydet"):
                start = datetime.strptime(q_date, "%Y-%m-%d")
                new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, "", f_fiy, f_gece, "", "Kesin", f_fiy*f_gece] for i in range(int(f_gece))]
                pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False)
                st.query_params.clear(); st.rerun()

st.divider()

# --- 5. İSTEDİĞİN DASHBOARD (TAKVİM ALTI) ---
st.subheader(f"📊 {sec_ay} Ayı Durum Özeti")

# Üst Satır: Sayısal Veriler
d1, d2, d3, d4 = st.columns(4)
d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b style="font-size:20px;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
d2.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b style="font-size:20px;">{avg_stay:.1f}</b></div>', unsafe_allow_html=True)
d3.markdown(f'<div class="stat-box"><small>Ayın Bitmesine</small><br><b style="font-size:20px;">{max(0, days_left)} Gün</b></div>', unsafe_allow_html=True)
d4.markdown(f'<div class="stat-box"><small>Net Kâr (Tahmini)</small><br><b style="font-size:20px; color:#2E7D32;">{aylik_net_kar:,.0f} TL</b></div>', unsafe_allow_html=True)

st.write("") # Boşluk

# Alt Satır: Gelecek Rezervasyonlar & Uyarılar
c_left, c_right = st.columns(2)

with c_left:
    st.write("**📅 Gelecek Rezervasyonlar**")
    future = clean_df[clean_df['Giris_DT'] >= now.replace(hour=0, minute=0)].sort_values('Giris_DT').head(2)
    if not future.empty:
        for _, r in future.iterrows():
            st.success(f"👤 {r['Ad Soyad']} - {r['Giris_Tarihi']} ({r['Gece']} Gece)")
    else:
        st.write("Yakın tarihte giriş yok.")

with c_right:
    st.write("**🚨 Akıllı Uyarılar**")
    if empty_count > 15:
        st.error(f"Dikkat! Bu ay hala {empty_count} gün boş. Kampanya yapılabilir.")
    elif empty_count == 0:
        st.balloons()
        st.success("Harika! Bu ay %100 doluluk oranına ulaştın.")
    else:
        st.warning(f"Bilgi: Bu ay için {empty_count} adet boş günün var.")

# --- 6. EKSTRA SEKMELER (Gider & Liste) ---
st.divider()
with st.expander("💸 Gider Ekle & Finansal Detaylar"):
    # Buraya v42.0'daki gider ve vergi tablonu ekleyebilirsin
    st.write(f"Brüt Ciro: {brut_ciro:,.0f} TL")
    st.write(f"Toplam Gider: {gider_toplam:,.0f} TL")
