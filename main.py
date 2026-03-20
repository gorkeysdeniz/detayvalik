import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi v42.2", layout="wide")

# Tasarım Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .info-panel { background: #F8F4EC; border: 1px solid #D6BD98; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .wa-link { background-color: #25D366; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; }
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

# --- 3. ANALİTİK HESAPLAR (DASHBOARD İÇİN) ---
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
kdv_v = brut_ciro - (brut_ciro / (1 + KDV_ORANI))
konak_v = brut_ciro - (brut_ciro / (1 + TURIZM_VERGISI))
gid_toplam = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == curr_month]["Tutar"].sum()
net_kar = brut_ciro - kdv_v - konak_v - gid_toplam

# --- 4. ANA ARAYÜZ (SEKMELER) ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi v42.2</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finans & Giderler", "⚙️ Ayarlar"])

# TAB 1: TAKVİM & TAKVİM ALTI DASHBOARD
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Görüntülenen Ay", aylar, index=curr_month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Çizelgesi
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

    # Rezervasyon Formu (Tıklandığında Açılır)
    q_date = st.query_params.get("date", "")
    if q_date:
        st.divider()
        day_data = df[df["Tarih"] == q_date]
        if not day_data.empty:
            st.info(f"📍 {q_date}: {day_data.iloc[0]['Ad Soyad']} konaklıyor.")
        else:
            with st.form("yeni_rez"):
                st.write(f"📝 **{q_date}** Tarihine Kayıt")
                f_ad, f_tel = st.columns(2); f_a = f_ad.text_input("Ad Soyad"); f_t = f_tel.text_input("Telefon")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik", min_value=0); f_gece = f_g.number_input("Gece", min_value=1)
                f_not = st.text_area("Özel Notlar")
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_t, f_fiy, f_gece, f_not, "Kesin", f_fiy*f_gece] for i in range(int(f_gece))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear(); st.rerun()

    st.divider()
    # --- TAKVİM ALTI DASHBOARD ---
    st.subheader(f"📊 {sec_ay} Ayı Performans Özeti")
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b style="font-size:20px;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b style="font-size:20px;">{avg_stay:.1f}</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Kalan Boş Gün</small><br><b style="font-size:20px; color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    d4.markdown(f'<div class="stat-box"><small>Net Kâr (Vergi Hariç)</small><br><b style="font-size:20px; color:#2E7D32;">{net_kar:,.0f} TL</b></div>', unsafe_allow_html=True)
    
    st.write("")
    l_col, r_col = st.columns(2)
    with l_col:
        st.write("**📅 Yaklaşan Girişler**")
        future = clean_df[clean_df['Giris_DT'] >= now.replace(hour=0, minute=0)].sort_values('Giris_DT').head(2)
        if not future.empty:
            for _, r in future.iterrows(): st.info(f"👤 {r['Ad Soyad']} | {r['Giris_Tarihi']}")
        else: st.write("Yakın tarihte kayıt yok.")
    with r_col:
        st.write("**🚨 Akıllı Uyarılar**")
        st.write(f"Ay sonuna {max(0, days_left)} gün kaldı.")
        if occ_rate < 40: st.warning("⚠️ Doluluk düşük, kampanya düşünebilirsin.")
        else: st.success("✅ Doluluk oranları stabil.")

# TAB 2: REZERVASYONLAR (ARAMA & WHATSAPP)
with t_rez:
    search = st.text_input("🔍 İsim veya Tel ile Ara...")
    if not df.empty:
        r_list = get_clean_df(df)
        if search: r_list = r_list[r_list['Ad Soyad'].str.contains(search, case=False) | r_list['Tel'].astype(str).str.contains(search)]
        for i, r in r_list.iterrows():
            c_a, c_b = st.columns([4, 2])
            c_a.markdown(f"**{r['Ad Soyad']}** | {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']}\n🌙 {r['Gece']} Gece | 💰 {r['Toplam']:,} TL")
            if r['Tel']:
                t_cl = str(r['Tel']).replace(' ','').replace('+','')
                msg = urllib.parse.quote(f"📝 *VİLLA REZERVASYON ONAYI*\n\nMisafir: {r['Ad Soyad']}\nGiriş: {r['Giris_Tarihi']}\nÇıkış: {r['Cikis_Tarihi']}\nGece: {r['Gece']}\nToplam: {r['Toplam']:,} TL\n\n---------------------------\n🏡 *BİLGİLENDİRME*\n🗝️ Giriş: 14:00 | Çıkış: 11:00\n❄️ Klimaları ayrılırken kapatınız.\n🚭 Sigara içilmez.")
                c_b.markdown(f'<a href="https://wa.me/{t_cl}?text={msg}" target="_blank" class="wa-link">WhatsApp Belge</a>', unsafe_allow_html=True)
            st.divider()

# TAB 3: FİNANS & GİDERLER
with t_fin:
    st.subheader(f"{sec_ay} Mali Tablo")
    f1, f2, f3 = st.columns(3)
    f1.metric("Brüt Ciro", f"{brut_ciro:,.0f} TL")
    f2.metric("KDV (%10)", f"-{kdv_v:,.0f} TL", delta_color="inverse")
    f3.metric("Turizm V. (%2)", f"-{konak_v:,.0f} TL", delta_color="inverse")
    
    st.divider()
    gx, gy = st.columns(2)
    with gx:
        st.write("**💸 Gider Ekle**")
        with st.form("g_add", clear_on_submit=True):
            gt, gk, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.number_input("Tutar")
            ga = st.text_input("Açıklama")
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()
    with gy:
        st.write("**📋 Gider Listesi**")
        st.dataframe(df_gider, use_container_width=True, hide_index=True)

# TAB 4: AYARLAR (SİLME & YEDEK)
with t_set:
    st.download_button("📊 Excel Olarak İndir", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "villa_yedek.csv")
    st.divider()
    if not df.empty:
        d_list = get_clean_df(df)
        for i, r in d_list.iterrows():
            ca, cb = st.columns([5, 1]); ca.write(f"🗑️ {r['Giris_Tarihi']} | {r['Ad Soyad']}")
            if cb.button("Sil", key=f"del_{i}"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]; df.to_csv("rez.csv", index=False); st.rerun()
