import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi v42.3", layout="wide")

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

# --- 3. DASHBOARD HESAPLARI (TAKVİM ALTI İÇİN) ---
now = datetime.now()
curr_month, curr_year = now.month, now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]
df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]
booked_count = len(month_df)
empty_count = month_days - booked_count
occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0

# --- 4. ANA ARAYÜZ (SEKMELER) ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi v42.3</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# TAB 1: TAKVİM & ÖZET (Boş kalmaması için özet paneli buraya ekledik)
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
        if not df[df["Tarih"] == q_date].empty:
            st.info(f"📍 {q_date}: {df[df['Tarih'] == q_date].iloc[0]['Ad Soyad']} konaklıyor.")
        else:
            with st.form("yeni_rez"):
                st.write(f"📝 **{q_date}** Tarihine Kayıt")
                f_a, f_t = st.columns(2); f_ad = f_a.text_input("Ad Soyad"); f_tel = f_t.text_input("Tel")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik", min_value=0); f_gec = f_g.number_input("Gece", min_value=1)
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_fiy, f_gec, "", "Kesin", f_fiy*f_gec] for i in range(int(f_gec))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False); st.rerun()

    st.divider()
    st.subheader("📊 Aylık Hızlı Bakış")
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Boş Gün Sayısı</small><br><b style="color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Ay Sonuna</small><br><b>{max(0, (month_days - now.day))} Gün</b></div>', unsafe_allow_html=True)

# TAB 2: REZERVASYONLAR
with t_rez:
    search = st.text_input("🔍 İsim Ara...")
    if not df.empty:
        r_list = get_clean_df(df)
        if search: r_list = r_list[r_list['Ad Soyad'].str.contains(search, case=False)]
        for i, r in r_list.iterrows():
            c_a, c_b = st.columns([4, 2])
            c_a.markdown(f"**{r['Ad Soyad']}** | {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']}\n💰 {r['Toplam']:,} TL")
            if r['Tel']:
                msg = urllib.parse.quote(f"Onay Metni: {r['Ad Soyad']}, {r['Giris_Tarihi']} girişli kaydınız yapılmıştır.")
                c_b.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={msg}" target="_blank" class="wa-link">WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

# TAB 3: MALİ TABLO (BÜTÜNCÜL GÖRÜNÜM)
with t_fin:
    st.subheader(f"💰 {sec_ay} Dönemi Net Hesap")
    
    # Hesaplamalar
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    v_kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    v_konak = b_ciro - (b_ciro / (1 + TURIZM_VERGISI))
    
    # Giderlerin özeti (Tablodan çekilen gerçek veriler)
    m_giderler = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]
    toplam_gider = m_giderler["Tutar"].sum()
    
    # NET KÂR HESABI
    net_kar = b_ciro - v_kdv - v_konak - toplam_gider

    # Üst Gösterge Paneli
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Toplam Brüt Gelir", f"{b_ciro:,.0f} TL")
    f2.metric("KDV + Konaklama V.", f"-{(v_kdv + v_konak):,.0f} TL", delta_color="inverse")
    f3.metric("Toplam Operasyonel Gider", f"-{toplam_gider:,.0f} TL", delta_color="inverse")
    f4.metric("CEBE KALAN (NET)", f"{net_kar:,.0f} TL")
    
    st.divider()
    
    # Gider Yönetimi Alanı
    gx, gy = st.columns([1, 2])
    with gx:
        st.write("**💸 Gider Ekle**")
        with st.form("gider_form", clear_on_submit=True):
            g_tar = st.date_input("Tarih")
            g_kat = st.selectbox("Kategori", ["Temizlik", "Elektrik/Su", "Bakım-Onarım", "Komisyon", "Diğer"])
            g_tut = st.number_input("Tutar (TL)", min_value=0)
            g_ack = st.text_input("Açıklama")
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([df_gider, pd.DataFrame([[g_tar.strftime("%Y-%m-%d"), g_kat, g_ack, g_tut]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()
    
    with gy:
        st.write("**📋 Gider Detayları**")
        if not m_giderler.empty:
            st.dataframe(m_giderler, use_container_width=True, hide_index=True)
            st.info(f"💡 Bu ay en çok harcama yapılan kategori: **{m_giderler.groupby('Kategori')['Tutar'].sum().idxmax()}**")
        else:
            st.write("Bu ay için henüz gider girilmemiş.")

# TAB 4: AYARLAR
with t_set:
    st.download_button("Excel Al", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "villa_data.csv")
    if not df.empty:
        d_l = get_clean_df(df)
        for i, r in d_l.iterrows():
            cx, cy = st.columns([5, 1])
            cx.write(f"{r['Giris_Tarihi']} | {r['Ad Soyad']}")
            if cy.button("Sil", key=f"d_{i}"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]; df.to_csv("rez.csv", index=False); st.rerun()
