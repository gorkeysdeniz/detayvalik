import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi v42.4", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link { background-color: #25D366; color: white !important; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-size: 15px; font-weight: 600; display: inline-block; margin-top: 10px; }
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
    temp = input_df.copy().fillna("")
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
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

# --- 4. ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi v42.4.2</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# TAB 1: TAKVİM
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=curr_month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
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

    q_date = st.query_params.get("date", "")
    if q_date:
        st.divider()
        target_day = df[df["Tarih"] == q_date]
        if not target_day.empty:
            info = target_day.iloc[0]
            st.info(f"📍 {q_date} | Misafir: {info['Ad Soyad']} | 📞 Tel: {info['Tel']} | 💰 {info['Toplam']:,} TL")
            
            # BURASI YENİ: WhatsApp Onay Metni Hazırlama
            if info['Tel']:
                t_cl = str(info['Tel']).replace(' ','').replace('+','')
                cikis_t = (pd.to_datetime(q_date) + timedelta(days=int(info['Gece']))).strftime("%Y-%m-%d")
                wp_metni = (
                    f"Merhaba {info['Ad Soyad']}, \n\n"
                    f"Detayvalık rezervasyonunuz onaylanmıştır. ✅\n"
                    f"📅 Giriş: {q_date}\n"
                    f"📅 Çıkış: {cikis_t}\n"
                    f"🌙 Toplam: {info['Gece']} Gece\n"
                    f"💰 Tutar: {info['Toplam']:,} TL\n\n"
                    f"Konum ve detaylı asistan rehberimiz için: https://detayvalik.io\n"
                    f"Şimdiden iyi tatiller dileriz! 🏡"
                )
                encoded_msg = urllib.parse.quote(wp_metni)
                st.markdown(f'<a href="https://wa.me/{t_cl}?text={encoded_msg}" target="_blank" class="wa-link">📱 WhatsApp Onay Mesajı Gönder</a>', unsafe_allow_html=True)
        else:
            with st.form("yeni_rez"):
                st.write(f"📝 **{q_date}** Yeni Kayıt")
                f_a, f_t = st.columns(2); f_ad = f_a.text_input("Ad Soyad"); f_tel = f_t.text_input("Telefon")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik", min_value=0); f_gec = f_g.number_input("Gece", min_value=1)
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_fiy, f_gec, "", "Kesin", f_fiy*f_gec] for i in range(int(f_gec))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False); st.rerun()

# (Kodun geri kalanı Tab 2, Tab 3 ve Tab 4 senin orijinal kodunun aynısı kalsın)
