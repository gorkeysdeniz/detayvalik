import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi v42.4.4", layout="wide")

# Modern Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link { background-color: #25D366; color: white !important; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
COLUMNS_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
COLUMNS_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", COLUMNS_REZ)
df_gider = load_data("gider.csv", COLUMNS_GIDER)

def get_clean_df(input_df):
    if input_df.empty: return input_df
    temp = input_df.copy().fillna("")
    # Gruplama yaparak giriş-çıkış tarihlerini netleştiriyoruz
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 3. ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi v42.4.4</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# TAB 1: TAKVİM & DİNAMİK DASHBOARD
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    month_days = calendar.monthrange(2026, ay_idx)[1]
    df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
    month_df = df[(df['DT'].dt.month == ay_idx) & (df['DT'].dt.year == 2026)]
    booked_count = month_df['Tarih'].nunique()
    empty_count = month_days - booked_count
    occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0
    
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
            
            if info['Tel']:
                t_cl = str(info['Tel']).replace(' ','').replace('+','')
                cikis_t = (pd.to_datetime(q_date) + timedelta(days=int(info['Gece']))).strftime("%d.%m.%Y")
                wp_metni = (
                    f"Merhaba {info['Ad Soyad']}, \n\n"
                    f"Detayvalık konaklama rezervasyonunuz onaylanmıştır! ✅\n"
                    f"📅 Giriş: {pd.to_datetime(q_date).strftime('%d.%m.%Y')} (14:00)\n"
                    f"📅 Çıkış: {cikis_t} (11:00)\n"
                    f"💰 Toplam: {info['Toplam']:,} TL\n\n"
                    f"📍 Konum ve Rehber: https://detayvalik.io\n"
                    f"Şimdiden iyi tatiller dileriz! 🏡"
                )
                encoded_msg = urllib.parse.quote(wp_metni)
                st.markdown(f'<a href="https://wa.me/{t_cl}?text={encoded_msg}" target="_blank" class="wa-link">📱 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)
        else:
            with st.form("yeni_rez"):
                st.write(f"📝 **{q_date}** Yeni Kayıt")
                f_a, f_t = st.columns(2); f_ad = f_a.text_input("Ad Soyad"); f_tel = f_t.text_input("Telefon")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik", min_value=0); f_gec = f_g.number_input("Gece", min_value=1)
                
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new_data = []
                    for i in range(int(f_gec)):
                        new_data.append({
                            "Tarih": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
                            "Ad Soyad": f_ad, "Tel": f_tel, "Ucret": f_fiy, 
                            "Gece": f_gec, "Not": "", "Durum": "Kesin", "Toplam": f_fiy * f_gec
                        })
                    new_df = pd.DataFrame(new_data)
                    pd.concat([df, new_df], ignore_index=True).to_csv("rez.csv", index=False)
                    st.success("Kaydedildi!"); st.rerun()

    st.divider()
    st.subheader(f"📊 {sec_ay} Özeti")
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Boş Gün</small><br><b style="color:#A94438;">{empty_count}</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Toplam Gece</small><br><b>{booked_count}</b></div>', unsafe_allow_html=True)

# TAB 2: REZERVASYONLAR
with t_rez:
    search = st.text_input("🔍 İsim Ara...")
    if not df.empty:
        r_list = get_clean_df(df)
        if search: r_list = r_list[r_list['Ad Soyad'].str.contains(search, case=False)]
        for i, r in r_list.iterrows():
            st.write(f"**{r['Ad Soyad']}** | {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']} | 💰 {r['Toplam']:,} TL")
            st.divider()

# TAB 3: FİNANSAL TABLO
with t_fin:
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    v_kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    
    st.subheader(f"💰 {sec_ay} Finansı")
    f1, f2 = st.columns(2)
    f1.metric("Brüt Gelir", f"{b_ciro:,.0f} TL")
    f2.metric("Net Tahmin", f"{(b_ciro - v_kdv):,.0f} TL")
    
    with st.form("g_add"):
        st.write("**Gider Ekle**")
        gt, gk, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım"]), st.number_input("Tutar")
        if st.form_submit_button("Gideri Kaydet"):
            new_gider = pd.DataFrame([{"Tarih": gt.strftime("%Y-%m-%d"), "Kategori": gk, "Aciklama": "", "Tutar": gu}])
            pd.concat([df_gider, new_gider], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()

# TAB 4: AYARLAR
with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA (DİKKAT)"):
        pd.DataFrame(columns=COLUMNS_REZ).to_csv("rez.csv", index=False)
        pd.DataFrame(columns=COLUMNS_GIDER).to_csv("gider.csv", index=False)
        st.rerun()
