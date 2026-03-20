import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      # %10 KDV
TURIZM_VERGISI = 0.02 # %2 Turizm Konaklama Vergisi

st.set_page_config(page_title="Detayvalık Operasyon v42.4", layout="wide")

# --- 2. GÖRSEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 26px; font-weight: 700; margin-bottom: 20px; border-bottom: 2px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 18px 0; border-radius: 6px; font-weight: 600; color: white !important; text-align: center; transition: 0.3s; }
    .day-link:hover { opacity: 0.8; transform: scale(1.02); }
    .bos { background-color: #4F6F52 !important; } /* Yeşil - Müsait */
    .dolu { background-color: #A94438 !important; } /* Kırmızı - Dolu */
    </style>
    """, unsafe_allow_html=True)

# --- 3. VERİ YÖNETİMİ ---
def load_data(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])

# Rezervasyonları temiz bir liste haline getiren fonksiyon
def get_clean_df(input_df):
    if input_df.empty: return input_df
    temp = input_df.copy().fillna("")
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 4. DASHBOARD HESAPLAMALARI ---
now = datetime.now()
curr_month, curr_year = now.month, now.year
month_days = calendar.monthrange(curr_year, curr_month)[1]

# Aylık Doluluk Analizi
df['DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
month_df = df[(df['DT'].dt.month == curr_month) & (df['DT'].dt.year == curr_year)]
booked_count = len(month_df)
empty_count = month_days - booked_count
occ_rate = (booked_count / month_days) * 100 if month_days > 0 else 0

st.markdown('<div class="main-header">Detayvalık Yönetim Paneli v42.4</div>', unsafe_allow_html=True)

# SEKME YAPISI
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Özet", "📋 Rezervasyon Listesi", "💰 Finansal Analiz", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Görüntülenen Ay", aylar, index=curr_month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Çizimi
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0:
                cal_html += '<td></td>'
            else:
                d_str = f"2026-{ay_idx:02d}-{day:02d}"
                is_full = not df[df["Tarih"] == d_str].empty
                status_class = "dolu" if is_full else "bos"
                cal_html += f'<td><a href="?date={d_str}" target="_self" class="day-link {status_class}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    # Seçili Gün Detayı / Kayıt Ekleme
    q_params = st.query_params
    selected_date = q_params.get("date", "")
    
    if selected_date:
        st.divider()
        day_info = df[df["Tarih"] == selected_date]
        if not day_info.empty:
            st.warning(f"📍 {selected_date} Tarihinde Rezervasyon Var: **{day_info.iloc[0]['Ad Soyad']}**")
        else:
            with st.form("yeni_kayit"):
                st.subheader(f"📝 {selected_date} İçin Yeni Kayıt")
                f1, f2 = st.columns(2); f_ad = f1.text_input("Ad Soyad"); f_tel = f2.text_input("Telefon")
                f3, f4 = st.columns(2); f_ucret = f3.number_input("Gecelik Ücret (TL)", min_value=0); f_gece = f4.number_input("Gece Sayısı", min_value=1)
                if st.form_submit_button("Kaydı Tamamla"):
                    start_dt = datetime.strptime(selected_date, "%Y-%m-%d")
                    new_rows = []
                    for i in range(int(f_gece)):
                        current_d = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
                        new_rows.append([current_d, f_ad, f_tel, f_ucret, f_gece, "", "Kesin", f_ucret * f_gece])
                    new_df = pd.DataFrame(new_rows, columns=df.columns)
                    pd.concat([df, new_df], ignore_index=True).to_csv("rez.csv", index=False)
                    st.success("Kayıt başarıyla eklendi!"); st.rerun()

    st.divider()
    st.subheader("📊 Aylık Performans Verileri")
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(f'<div class="stat-box"><small>Doluluk Oranı</small><br><b style="font-size:20px;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Boş Gün Sayısı</small><br><b style="font-size:20px; color:#A94438;">{empty_count} Gün</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Ay Sonu Beklentisi</small><br><b style="font-size:20px;">{month_df["Tarih"].nunique()} Rez.</b></div>', unsafe_allow_html=True)
    d4.markdown(f'<div class="stat-box"><small>Yıl</small><br><b style="font-size:20px;">2026</b></div>', unsafe_allow_html=True)

# --- TAB 2: REZERVASYON LİSTESİ ---
with t_rez:
    st.subheader("📋 Tüm Rezervasyonlar")
    if not df.empty:
        clean_list = get_clean_df(df)
        st.dataframe(clean_list[["Giris_Tarihi", "Cikis_Tarihi", "Ad Soyad", "Tel", "Gece", "Toplam", "Not"]], use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kayıtlı rezervasyon bulunmuyor.")

# --- TAB 3: FİNANSAL ANALİZ ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Özeti")
    # Aylık ciro (Aynı kişiye ait mükerrer günleri toplamdan düşmek için groupby yapıyoruz)
    monthly_data = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    brut_ciro = monthly_data["Toplam"].sum()
    
    # Vergi hesapları
    kdv_tutari = brut_ciro - (brut_ciro / (1 + KDV_ORANI))
    konaklama_vergisi = brut_ciro - (brut_ciro / (1 + TURIZM_VERGISI))
    
    # Giderler
    monthly_gider = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]
    toplam_gider = monthly_gider["Tutar"].sum()
    
    net_kar = brut_ciro - kdv_tutari - konaklama_vergisi - toplam_gider
    
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Brüt Ciro", f"{brut_ciro:,.0f} TL")
    f2.metric("Toplam Vergi", f"-{(kdv_tutari + konaklama_vergisi):,.0f} TL", delta_color="inverse")
    f3.metric("Giderler", f"-{toplam_gider:,.0f} TL", delta_color="inverse")
    f4.metric("NET KÂR", f"{net_kar:,.0f} TL")
    
    st.divider()
    gx, gy = st.columns([1, 2])
    with gx:
        st.write("💸 **Gider Ekle**")
        with st.form("gider_ekle", clear_on_submit=True):
            gt = st.date_input("Tarih"); gk = st.selectbox("Kategori", ["Temizlik", "Elektrik/Su", "Bakım", "Diğer"])
            ga = st.text_input("Açıklama"); gu = st.number_input("Tutar", min_value=0)
            if st.form_submit_button("Kaydet"):
                pd.concat([df_gider, pd.DataFrame([[gt, gk, ga, gu]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False)
                st.rerun()
    with gy:
        st.write("📊 **Aylık Gider Detayı**")
        st.dataframe(monthly_gider, use_container_width=True, hide_index=True)

# --- TAB 4: AYARLAR ---
with t_set:
    st.subheader("⚙️ Sistem Yönetimi")
    st.download_button("📥 Verileri Excel Olarak İndir (Yedek)", get_clean_df(df).to_csv(index=False).encode('utf-8-sig'), "detayvalik_yedek.csv")
    
    if st.button("🗑️ Tüm Verileri Sıfırla"):
        if os.path.exists("rez.csv"): os.remove("rez.csv")
        if os.path.exists("gider.csv"): os.remove("gider.csv")
        st.success("Tüm veriler temizlendi, sayfa yenileniyor..."); st.rerun()
