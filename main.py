import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 100px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .wa-link, .doc-link { display: inline-block; color: white !important; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; }
    .wa-link { background-color: #25D366; }
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

# --- 3. DASHBOARD HESAPLAR ---
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
this_month_rev = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()

# --- 4. ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi</div>', unsafe_allow_html=True)
t_dash, t_cal, t_rez, t_fin, t_set = st.tabs(["📊 Dashboard", "📅 Takvim", "📋 Rezervasyonlar", "💰 Finans & Giderler", "⚙️ Ayarlar"])

# TAB: DASHBOARD
with t_dash:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-box"><small>Aylık Doluluk</small><br><b style="font-size:22px;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><small>Kalan Boş Gün</small><br><b style="font-size:22px; color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b style="font-size:22px;">{avg_stay:.1f} Gece</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-box"><small>Bu Ay Ciro</small><br><b style="font-size:22px; color:#4F6F52;">{this_month_rev:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.divider()
    cl, cr = st.columns(2)
    with cl:
        st.write("**📅 Yaklaşan Girişler**")
        future = clean_df[clean_df['Giris_DT'] >= now.replace(hour=0, minute=0)].sort_values('Giris_DT').head(3)
        if not future.empty:
            for _, r in future.iterrows(): st.info(f"👤 {r['Ad Soyad']} | 📅 {r['Giris_Tarihi']}")
    with cr:
        st.write("**📢 Notlar**")
        if occ_rate < 40: st.warning("⚠️ Doluluk düşük, aksiyon gerekebilir.")
        else: st.success("✅ Doluluk oranları dengeli.")

# TAB: TAKVİM
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    cx, cy = st.columns([1, 3]); sec_ay = cx.selectbox("Ay Seç", aylar, index=curr_month-1); ay_idx = aylar.index(sec_ay) + 1
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
        day_data = df[df["Tarih"] == q_date]
        if not day_data.empty:
            st.info(f"Kayıt: {day_data.iloc[0]['Ad Soyad']} | {day_data.iloc[0]['Toplam']:,} TL")
        else:
            with st.form("new_r"):
                st.write(f"📝 **{q_date} Yeni Rezervasyon**")
                fa, fp = st.columns(2); f_ad, f_tel = fa.text_input("Ad Soyad"), fp.text_input("Telefon")
                ff, fg = st.columns(2); f_fiy, f_gece = ff.number_input("Gecelik", min_value=0), fg.number_input("Gece", min_value=1)
                f_not = st.text_area("Notlar")
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_fiy, f_gece, f_not, "Kesin", f_fiy*f_gece] for i in range(int(f_gece))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns[:8])], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear(); st.rerun()

# TAB: REZERVASYONLAR (ARAMA & WHATSAPP)
with t_rez:
    s_q = st.text_input("🔍 İsim veya Tel Ara...")
    if not df.empty:
        r_df = get_clean_df(df)
        if s_q: r_df = r_df[r_df['Ad Soyad'].str.contains(s_q, case=False)]
        for i, r in r_df.iterrows():
            c1, c2 = st.columns([4, 2])
            c1.markdown(f"**{r['Ad Soyad']}** | {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']}\n🌙 {r['Gece']} Gece | 💰 {r['Toplam']:,} TL")
            if r['Tel']:
                t_c = str(r['Tel']).replace(' ','').replace('+','')
                msg = urllib.parse.quote(f"📝 *VİLLA REZERVASYON ONAYI*\n\nMisafir: {r['Ad Soyad']}\nGiriş: {r['Giris_Tarihi']}\nÇıkış: {r['Cikis_Tarihi']}\nGece: {r['Gece']}\nToplam: {r['Toplam']:,} TL\n\n---------------------------\n🏡 *KURALLAR VE BİLGİ*\n🗝️ Giriş: 14:00 | Çıkış: 11:00\n❄️ Klimaları evden ayrılırken kapatınız.\n🚭 Ev içinde sigara içilmemesi rica olunur.\n🧹 Villa düzenli ve temiz teslim edilmelidir.")
                c2.markdown(f'<a href="https://wa.me/{t_c}?text={msg}" target="_blank" class="wa-link">WhatsApp Belge</a>', unsafe_allow_html=True)
            st.divider()

# TAB: FİNANS & GİDERLER (DETAYLI)
with t_fin:
    st.markdown(f"### {sec_ay} Finansal Detaylar")
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    v_kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    v_konak = b_ciro - (b_ciro / (1 + TURIZM_VERGISI))
    gid_t = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
    
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Ciro", f"{b_ciro:,.0f} TL")
    f2.metric("KDV (%10)", f"-{v_kdv:,.0f} TL", delta_color="inverse")
    f3.metric("Konaklama V. (%2)", f"-{v_konak:,.0f} TL", delta_color="inverse")
    f4.metric("Giderler", f"-{gid_t:,.0f} TL", delta_color="inverse")
    
    st.markdown(f'<div style="background:#E8F5E9; padding:20px; border-radius:10px; text-align:center;"><small>Net Kâr</small><br><b style="font-size:28px; color:#2E7D32;">{(b_ciro-v_kdv-v_konak-gid_t):,.0f} TL</b></div>', unsafe_allow_html=True)
    
    st.divider()
    st.write("**💸 Gider Kaydı ve Tablosu**")
    gx, gy = st.columns(2)
    with gx:
        with st.form("g_f", clear_on_submit=True):
            gt, gk, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.number_input("Tutar")
            ga = st.text_input("Açıklama")
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()
    with gy:
        st.dataframe(df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx], use_container_width=True, hide_index=True)

# TAB: AYARLAR
with t_set:
    if not df.empty:
        st.download_button("Excel Al", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "yedek.csv")
        st.divider()
        d_df = get_clean_df(df)
        for i, r in d_df.iterrows():
            cx, cy = st.columns([5, 1]); cx.write(f"🗑️ {r['Giris_Tarihi']} | {r['Ad Soyad']}")
            if cy.button("Sil", key=f"d_{i}"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]; df.to_csv("rez.csv", index=False); st.rerun()
