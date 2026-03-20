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
    .wa-link { background-color: #25D366; color: white !important; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block; margin-top: 5px; }
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

# WhatsApp Mesaj Fonksiyonu (Tek merkezden yönetmek için)
def get_wa_link(ad, tel, giris, gece, toplam):
    t_cl = str(tel).replace(' ','').replace('+','')
    cikis_t = (pd.to_datetime(giris) + timedelta(days=int(gece))).strftime("%d.%m.%Y")
    giris_t_format = pd.to_datetime(giris).strftime("%d.%m.%Y")
    
    metin = (
        f"Merhaba {ad}, \n\n"
        f"Detayvalık konaklama rezervasyonunuz onaylanmıştır! ✅\n\n"
        f"📋 *REZERVASYON DETAYLARI*\n"
        f"📅 Giriş Tarihi: {giris_t_format} (Saat 14:00)\n"
        f"📅 Çıkış Tarihi: {cikis_t} (Saat 11:00)\n"
        f"🌙 Konaklama Süresi: {gece} Gece\n"
        f"💰 Toplam Konaklama Bedeli: {toplam:,} TL\n\n"
        f"📝 *EV KURALLARIMIZ*\n"
        f"• Ev içerisinde sigara içilmemesini rica ederiz.🚭\n"
        f"• Evcil hayvan kabul edilmemektedir.🐾\n"
        f"• Gece 24:00'den sonra çevre rahatsızlığı adına yüksek ses yasağı mevcuttur.🤫\n\n"
        f"📍 Konum ve Dijital Rehberimiz: https://detayvalik.io\n\n"
        f"Şimdiden keyifli tatiller dileriz! 🏡✨"
    )
    return f"https://wa.me/{t_cl}?text={urllib.parse.quote(metin)}"

# --- 4. ARAYÜZ ---
st.markdown('<div class="main-header">Villa Operasyon Merkezi v42.5</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyonlar", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# TAB 1: TAKVİM & DİNAMİK DASHBOARD
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # --- KRİTİK DÜZELTME: Dashboard Hesaplamaları Seçilen Aya Bağlandı ---
    month_days = calendar.monthrange(2026, ay_idx)[1]
    df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
    target_month_df = df[(df['DT'].dt.month == ay_idx) & (df['DT'].dt.year == 2026)]
    
    booked_count = target_month_df['Tarih'].nunique()
    empty_count = month_days - booked_count
    occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0
    # ------------------------------------------------------------------

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
                link = get_wa_link(info['Ad Soyad'], info['Tel'], q_date, info['Gece'], info['Toplam'])
                st.markdown(f'<a href="{link}" target="_blank" class="wa-link">📱 WhatsApp Kiralama Metni Gönder</a>', unsafe_allow_html=True)
        else:
            with st.form("yeni_rez"):
                st.write(f"📝 **{q_date}** Yeni Kayıt")
                f_a, f_t = st.columns(2); f_ad = f_a.text_input("Ad Soyad"); f_tel = f_t.text_input("Telefon")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik", min_value=0); f_gec = f_g.number_input("Gece", min_value=1)
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_fiy, f_gec, "", "Kesin", f_fiy*f_gec] for i in range(int(f_gec))]
                    pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False); st.rerun()

    st.divider()
    st.subheader(f"📊 {sec_ay} Ayı Durum Özeti")
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b>%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Boş Gün Sayısı</small><br><b style="color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Dolu Gün Sayısı</small><br><b>{booked_count} Gün</b></div>', unsafe_allow_html=True)
    d4.markdown(f'<div class="stat-box"><small>Toplam Gün</small><br><b>{month_days} Gün</b></div>', unsafe_allow_html=True)

# TAB 2: REZERVASYONLAR
with t_rez:
    search = st.text_input("🔍 İsim veya Tel Ara...")
    if not df.empty:
        r_list = get_clean_df(df)
        if search: r_list = r_list[r_list['Ad Soyad'].str.contains(search, case=False) | r_list['Tel'].astype(str).str.contains(search)]
        for i, r in r_list.iterrows():
            c_a, c_b = st.columns([4, 2])
            c_a.markdown(f"**{r['Ad Soyad']}** | 📞 {r['Tel']}\n📅 {r['Giris_Tarihi']} ➔ {r['Cikis_Tarihi']} | 💰 {r['Toplam']:,} TL")
            if r['Tel']:
                # Burada da aynı zengin metni çağırıyoruz
                link = get_wa_link(r['Ad Soyad'], r['Tel'], r['Giris_Tarihi'], r['Gece'], r['Toplam'])
                c_b.markdown(f'<a href="{link}" target="_blank" class="wa-link">Kiralama Metni</a>', unsafe_allow_html=True)
            st.divider()

# TAB 3: FİNANSAL TABLO (Burada da sec_ay kullanılıyor)
with t_fin:
    m_fin = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    b_ciro = m_fin["Toplam"].sum()
    v_kdv = b_ciro - (b_ciro / (1 + KDV_ORANI))
    v_konak = b_ciro - (b_ciro / (1 + TURIZM_VERGISI))
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]
    t_gider = m_gid["Tutar"].sum()
    
    st.subheader(f"💰 {sec_ay} Finansal Özeti")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Gelir", f"{b_ciro:,.0f} TL")
    f2.metric("Vergiler", f"-{(v_kdv + v_konak):,.0f} TL", delta_color="inverse")
    f3.metric("Giderler", f"-{t_gider:,.0f} TL", delta_color="inverse")
    f4.metric("NET KÂR", f"{(b_ciro - v_kdv - v_konak - t_gider):,.0f} TL")
    
    st.divider()
    gx, gy = st.columns([1, 2])
    with gx:
        with st.form("g_add", clear_on_submit=True):
            st.write("**Gider Ekle**")
            gt, gk, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.number_input("Tutar")
            ga = st.text_input("Açıklama")
            if st.form_submit_button("Kaydet"):
                pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False); st.rerun()
    with gy:
        st.write("**Gider Detayları**")
        st.dataframe(m_gid, use_container_width=True, hide_index=True)

# TAB 4: AYARLAR (Yedek ve Silme)
with t_set:
    st.download_button("Excel Yedek Al", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "yedek.csv")
    if not df.empty:
        for i, r in get_clean_df(df).iterrows():
            cx, cy = st.columns([5, 1]); cx.write(f"{r['Giris_Tarihi']} | {r['Ad Soyad']}")
            if cy.button("Sil", key=f"del_{i}"):
                df = df[~((df["Ad Soyad"] == r["Ad Soyad"]) & (df["Toplam"] == r["Toplam"]))]; df.to_csv("rez.csv", index=False); st.rerun()
