import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse
import plotly.express as px

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      # %10 KDV
TURIZM_VERGISI = 0.02 # %2 Konaklama Vergisi

st.set_page_config(page_title="Villa Yönetim Sistemi", layout="wide")

# Modern Stil Ayarları
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 24px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { background-color: #F1F1F1; border-radius: 4px; padding: 8px 16px; color: #4A4A4A !important; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #1A3636 !important; color: white !important; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 110px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; transition: 0.2s; }
    .bos { background: #4F6F52 !important; }
    .dolu { background: #A94438 !important; }
    .info-panel { background: #F8F4EC; border: 1px solid #D6BD98; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .stButton button { background-color: #1A3636 !important; color: white !important; border-radius: 4px !important; border: none !important; height: 45px; width: 100%; font-weight: 500; }
    .wa-link, .doc-link { display: inline-block; color: white !important; padding: 5px 12px; border-radius: 5px; text-decoration: none; font-size: 13px; font-weight: 600; margin-bottom: 5px; }
    .wa-link { background-color: #25D366; }
    .doc-link { background-color: #008080; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)

def get_clean_df(input_df):
    if input_df.empty: return input_df
    temp = input_df.copy().fillna("")
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 3. DASHBOARD HESAPLAMALARI ---
now = datetime.now()
curr_month = now.month
curr_year = now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]

df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]
booked_days_count = len(month_df)
empty_days_count = month_days - booked_days_count
occ_rate = (booked_days_count / month_days) * 100 if month_days > 0 else 0
days_left = month_days - now.day

clean_df = get_clean_df(df)
avg_stay = clean_df['Gece'].astype(float).mean() if not clean_df.empty else 0

# --- 4. ANA ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi</div>', unsafe_allow_html=True)
t_dash, t_cal, t_rez, t_gid, t_fin, t_set = st.tabs(["📊 Dashboard", "📅 Takvim", "📋 Rezervasyonlar", "💸 Giderler", "💰 Finans", "⚙️ Ayarlar"])

# TAB: DASHBOARD
with t_dash:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-box"><small>Aylık Doluluk</small><br><b style="font-size:22px; color:#1A3636;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box"><small>Ayın Bitmesine</small><br><b style="font-size:22px;">{max(0, days_left)} Gün</b></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box"><small>Kalan Boş Gün</small><br><b style="font-size:22px; color:#A94438;">{empty_days_count} Gün</b></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-box"><small>Ort. Geceleme</small><br><b style="font-size:22px;">{avg_stay:.1f} Gece</b></div>', unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.write("**Gelir Performansı (Aylık)**")
        if not df.empty:
            chart_data = df.drop_duplicates(["Ad Soyad", "Toplam"]).copy()
            chart_data['Ay_Yil'] = chart_data['DT'].dt.strftime('%m/%Y')
            fig = px.bar(chart_data.groupby('Ay_Yil')['Toplam'].sum().reset_index(), x='Ay_Yil', y='Toplam', color_discrete_sequence=['#1A3636'])
            st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.write("**Gelecek Rezervasyonlar**")
        future = clean_df[clean_df['Giris_DT'] >= now.replace(hour=0, minute=0, second=0, microsecond=0)].sort_values('Giris_DT').head(3)
        if not future.empty:
            for _, r in future.iterrows():
                st.info(f"👤 {r['Ad Soyad']}\n📅 {r['Giris_Tarihi']} ({r['Gece']} Gece)")
        else: st.write("Yakın tarihte giriş yok.")
        
        st.divider()
        st.write("**Akıllı Uyarılar**")
        if occ_rate < 40: st.error(f"🚨 Doluluk düşük (%{occ_rate:.1f}). Kampanya düşünebilirsin.")
        elif empty_days_count > 10: st.warning(f"⚠️ Bu ay hala {empty_days_count} gün boş.")
        else: st.success("✅ Operasyon stabil.")

# TAB: TAKVİM
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    cx, cy = st.columns([1, 3])
    with cx: sec_ay = st.selectbox("Dönem", aylar, index=curr_month-1)
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
        day_data = df[df["Tarih"] == q_date]
        if not day_data.empty:
            info = day_data.iloc[0]
            st.markdown(f'<div class="info-panel"><b>Kayıt Detayı ({q_date})</b><br>Müşteri: {info["Ad Soyad"]} | Tutar: {info["Toplam"]:,} TL</div>', unsafe_allow_html=True)
        else:
            with st.form("new_r"):
                st.write(f"**{q_date} Yeni Rezervasyon**")
                c_a, c_b = st.columns(2); f_a, f_p = c_a.text_input("Ad Soyad"), c_b.text_input("Tel")
                f_f, f_g = c_a.number_input("Gecelik Ücret", min_value=0), c_b.number_input("Gece", min_value=1)
                f_n = st.text_area("Özel Notlar")
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, f_n, "Kesin", f_f*f_g] for i in range(int(f_g))]
                    pd.concat([df, pd.DataFrame(new, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.query_params.clear(); st.rerun()

# TAB: REZERVASYONLAR (ARAMA)
with t_rez:
    st.markdown("### Kayıt Sorgulama")
    search = st.text_input("🔍 İsim veya Telefon ile Ara...")
    if not df.empty:
        c_df = get_clean_df(df)
        if search: c_df = c_df[c_df['Ad Soyad'].str.contains(search, case=False) | c_df['Tel'].astype(str).str.contains(search)]
        for i, r in c_df.iterrows():
            col1, col2 = st.columns([4, 2])
            col1.markdown(f"**{r['Ad Soyad']}** 📅 Giriş: `{r['Giris_Tarihi']}` | 🚪 Çıkış: `{r['Cikis_Tarihi']}`\n🌙 {r['Gece']} Gece | 💰 {r['Toplam']:,} TL")
            if r['Tel']:
                clean_tel = str(r['Tel']).replace(' ','').replace('+','')
                msg = urllib.parse.quote(f"📝 *VİLLA REZERVASYON ONAYI*\n\nMisafir: {r['Ad Soyad']}\nGiriş: {r['Giris_Tarihi']}\nÇıkış: {r['Cikis_Tarihi']}\nGece: {r['Gece']}\nToplam: {r['Toplam']:,} TL\n\n---------------------------\n🏡 *KURALLAR*\n🗝️ Giriş: 14:00 | Çıkış: 11:00\n❄️ Klimaları ayrılırken kapatınız.\n🚭 Sigara içilmez.\n🧹 Düzenli bırakılmalıdır.")
                col2.markdown(f'<a href="https://wa.me/{clean_tel}?text={msg}" target="_blank" class="doc-link">WhatsApp Belge</a>', unsafe_allow_html=True)
            st.divider()

# TAB: GİDERLER
with t_gid:
    st.markdown("### Gider İşleme")
    with st.form("gid_f", clear_on_submit=True):
        c1, c2, c3 = st.columns(3); gt, gk, gu = c1.date_input("Tarih"), c2.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), c3.number_input("Tutar")
        ga = st.text_input("Açıklama")
        if st.form_submit_button("Kaydet"):
            pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()
    st.dataframe(df_gider, use_container_width=True, hide_index=True)

# TAB: FİNANS (VERGİLER)
with t_fin:
    st.markdown(f"### {sec_ay} Finansal Rapor")
    m_rez_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    toplam_brut = m_rez_fin["Toplam"].sum()
    kdv_tutari = toplam_brut - (toplam_brut / (1 + KDV_ORANI))
    konaklama_vergisi = toplam_brut - (toplam_brut / (1 + TURIZM_VERGISI))
    vergisiz_gelir = toplam_brut - kdv_tutari - konaklama_vergisi
    toplam_gider = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
    gercek_kar = vergisiz_gelir - toplam_gider

    f1, f2, f3 = st.columns(3)
    f1.markdown(f'<div class="stat-box"><small>Brüt Ciro</small><br><b>{toplam_brut:,.0f} TL</b></div>', unsafe_allow_html=True)
    f2.markdown(f'<div class="stat-box"><small>KDV (%10)</small><br><b style="color:#A94438;">{kdv_tutari:,.0f} TL</b></div>', unsafe_allow_html=True)
    f3.markdown(f'<div class="stat-box"><small>Turizm Vergisi (%2)</small><br><b style="color:#A94438;">{konaklama_vergisi:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.write("")
    f4, f5, f6 = st.columns(3)
    f4.markdown(f'<div class="stat-box"><small>Vergisiz Net Gelir</small><br><b>{vergisiz_gelir:,.0f} TL</b></div>', unsafe_allow_html=True)
    f5.markdown(f'<div class="stat-box"><small>Toplam Gider</small><br><b style="color:#A94438;">-{toplam_gider:,.0f} TL</b></div>', unsafe_allow_html=True)
    f6.markdown(f'<div class="stat-box"><small>Gerçek Kâr</small><br><b style="color:#4F6F52; font-size:20px;">{gercek_kar:,.0f} TL</b></div>', unsafe_allow_html=True)

# TAB: AYARLAR
with t_set:
    st.markdown("### Veri Yönetimi")
    if not df.empty:
        st.download_button("📊 Rapor İndir", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "villa_rapor.csv")
        st.divider()
        del_df = get_clean_df(df)
        for i, r in del_df.iterrows():
            cx, cy = st.columns([5, 1]); cx.write(f"🗑️ {r['Giris_Tarihi']} | {r['Ad Soyad']}")
            if cy.button("SİL", key=f"del_{i}"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]; df.to_csv("rez.csv", index=False); st.rerun()
