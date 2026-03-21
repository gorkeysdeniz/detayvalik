import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR & PARAMETRELER ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Villa Yönetim Sistemi v42.4", layout="wide", page_icon="🏡")

# Modern Arayüz İçin Özel CSS
st.markdown("""
    <style>
    .stApp { background-color: #FDFDFD !important; }
    .main-header { color: #1A3636; font-size: 26px; font-weight: 700; margin-bottom: 20px; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; }
    .stat-box { background: white; border: 1px solid #E5E7EB; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; margin-top: 10px; }
    .day-link { display: block; text-decoration: none; padding: 20px 0; border-radius: 8px; font-weight: 600; color: white !important; text-align: center; transition: 0.3s; }
    .day-link:hover { opacity: 0.8; transform: scale(1.02); }
    .bos { background: #4F6F52 !important; } /* Zeytin Yeşili */
    .dolu { background: #A94438 !important; } /* Kiremit Kırmızısı */
    .wa-link { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (Kalıcı Dosyalar) ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

def get_clean_df(input_df):
    if input_df.empty: return input_df
    temp = input_df.copy().fillna("")
    # Rezervasyonları gruplayıp giriş/çıkış tarihlerini hesaplar
    res = temp.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(Giris_Tarihi=("Tarih", "min")).reset_index()
    res['Giris_DT'] = pd.to_datetime(res['Giris_Tarihi'])
    res['Cikis_Tarihi'] = (res['Giris_DT'] + pd.to_timedelta(res['Gece'].astype(int), unit='D')).dt.strftime('%Y-%m-%d')
    return res.sort_values(by="Giris_DT", ascending=False)

# --- 3. ANA BAŞLIK ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.4</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Dashboard", "📋 Rezervasyon Listesi", "💰 Finans & Giderler", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Görüntülenecek Ay", aylar, index=datetime.now().month-1)
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

    # Gün Detayı / Yeni Kayıt
    q_date = st.query_params.get("date", "")
    if q_date:
        st.divider()
        target_day = df[df["Tarih"] == q_date]
        if not target_day.empty:
            info = target_day.iloc[0]
            st.success(f"📍 {q_date} - Misafir: {info['Ad Soyad']} | 💰 {info['Toplam']:,} TL")
            
            # WhatsApp Metni Oluşturma
            if info['Tel']:
                t_cl = str(info['Tel']).replace(' ','').replace('+','')
                cikis_t = (pd.to_datetime(q_date) + timedelta(days=int(info['Gece']))).strftime("%d.%m.%Y")
                wp_metni = (
                    f"Merhaba {info['Ad Soyad']}, \n\n"
                    f"Detayvalık rezervasyonunuz onaylanmıştır! ✅\n"
                    f"📅 Giriş: {pd.to_datetime(q_date).strftime('%d.%m.%Y')} (14:00)\n"
                    f"📅 Çıkış: {cikis_t} (11:00)\n\n"
                    f"📍 Rehberimiz: https://detayvalik.io\n"
                    f"Şimdiden iyi tatiller! 🏡"
                )
                encoded_msg = urllib.parse.quote(wp_metni)
                st.markdown(f'<a href="https://wa.me/{t_cl}?text={encoded_msg}" target="_blank" class="wa-link">📱 WhatsApp Onay Mesajı</a>', unsafe_allow_html=True)
        else:
            with st.form("yeni_rez_form"):
                st.write(f"📝 **{q_date}** Tarihine Yeni Rezervasyon")
                f_a, f_t = st.columns(2); f_ad = f_a.text_input("Misafir Ad Soyad"); f_tel = f_t.text_input("Telefon")
                f_f, f_g = st.columns(2); f_fiy = f_f.number_input("Gecelik Fiyat", min_value=0); f_gec = f_g.number_input("Gece Sayısı", min_value=1)
                if st.form_submit_button("Kaydet"):
                    start = datetime.strptime(q_date, "%Y-%m-%d")
                    new_rows = []
                    for i in range(int(f_gec)):
                        new_rows.append({
                            "Tarih": (start + timedelta(days=i)).strftime("%Y-%m-%d"),
                            "Ad Soyad": f_ad, "Tel": f_tel, "Ucret": f_fiy, 
                            "Gece": f_gec, "Not": "", "Durum": "Kesin", "Toplam": f_fiy * f_gec
                        })
                    pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True).to_csv(REZ_FILE, index=False)
                    st.rerun()

# --- TAB 2: REZERVASYON LİSTESİ ---
with t_rez:
    st.subheader("📋 Geçmiş ve Gelecek Tüm Rezervasyonlar")
    if not df.empty:
        r_list = get_clean_df(df)
        st.dataframe(r_list.drop(columns=["Giris_DT"]), use_container_width=True, hide_index=True)

# --- TAB 3: FİNANS & GİDERLER ---
with t_fin:
    m_df = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    brut = m_df["Toplam"].sum()
    kdv = brut - (brut / (1 + KDV_ORANI))
    
    st.subheader(f"💰 {sec_ay} Finansal Durum")
    f1, f2 = st.columns(2)
    f1.metric("Aylık Brüt Ciro", f"{brut:,.0f} TL")
    f2.metric("Tahmini Net (KDV Sonrası)", f"{(brut - kdv):,.0f} TL")
    
    st.divider()
    with st.form("gider_ekle"):
        st.write("**Yeni Gider Kaydı**")
        g_t, g_k, g_u = st.date_input("Tarih"), st.selectbox("Kategori", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.number_input("Tutar")
        if st.form_submit_button("Gideri Kaydet"):
            new_g = pd.DataFrame([{"Tarih": g_t.strftime("%Y-%m-%d"), "Kategori": g_k, "Aciklama": "", "Tutar": g_u}])
            pd.concat([df_gider, new_g], ignore_index=True).to_csv(GIDER_FILE, index=False)
            st.rerun()

# --- TAB 4: AYARLAR ---
with t_set:
    st.subheader("⚙️ Sistem Araçları")
    if st.button("🔴 Tüm Verileri Sıfırla (Geri Dönülemez)"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False)
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False)
        st.rerun()
