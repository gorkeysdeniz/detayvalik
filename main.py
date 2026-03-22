import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık Operasyon v42.5.2", layout="wide", page_icon="🏡")

# Modern Tasarım CSS (Mobil Uyumluluk & Dolgun Butonlar)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 26px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 12px; margin-bottom: 20px; }
    .stat-box { background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    
    /* Mobil Dostu Takvim Ayarları */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 8px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 20px 0; border-radius: 12px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 18px;
        transition: transform 0.1s; border-bottom: 4px solid rgba(0,0,0,0.2);
    }
    .day-link:active { transform: translateY(2px); border-bottom: 2px solid rgba(0,0,0,0.2); }
    .bos { background: #10b981 !important; } /* Yeşil */
    .dolu { background: #ef4444 !important; } /* Kırmızı */
    
    .info-card { background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 6px solid #3B82F6; margin: 15px 0; }
    .stForm { background: white !important; border-radius: 15px !important; padding: 20px !important; border: 1px solid #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (UTF-8-SIG & GÜVENLİ YÜKLEME) ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        pd.DataFrame(columns=cols).to_csv(file, index=False, encoding='utf-8-sig')
    try:
        temp_df = pd.read_csv(file, encoding='utf-8-sig')
        return temp_df.reindex(columns=cols, fill_value="")
    except:
        return pd.DataFrame(columns=cols)

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.5.2</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & Dashboard", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & DASHBOARD ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([2, 1])
    sec_ay = c1.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # URL'den gelen seçili tarihi yakala
    selected_date = st.query_params.get("date", None)

    # Takvim Çizimi
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"
                is_dolu = not df[df["Tarih"] == d_s].empty
                cl = "dolu" if is_dolu else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    # Dashboard Metrikleri
    month_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    ciro = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    occ_rate = (month_df['Tarih'].nunique() / calendar.monthrange(2026, ay_idx)[1]) * 100

    st.divider()
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="stat-box"><small>{sec_ay} Cirosu</small><br><b style="color:#10b981; font-size:20px;">{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="stat-box"><small>Doluluk</small><br><b style="font-size:20px;">%{occ_rate:.1f}</b></div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="stat-box"><small>Sezon Durumu</small><br><b style="font-size:20px;">{"🔥 Yoğun" if occ_rate > 70 else "✅ Normal"}</b></div>', unsafe_allow_html=True)

    # --- ETKİLEŞİM PANELİ ---
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        
        if not rez_info.empty:
            # DOLU GÜN: Bilgi Gösterimi
            r = rez_info.iloc[0]
            st.markdown(f"""
            <div class="info-card">
                <h3>📌 Misafir Bilgisi ({selected_date})</h3>
                <p style='font-size:18px;'>👤 <b>İsim:</b> {r['Ad Soyad']}<br>
                📞 <b>Telefon:</b> {r['Tel']}<br>
                🌙 <b>Konaklama:</b> {r['Gece']} Gece<br>
                💰 <b>Toplam Ücret:</b> {r['Toplam']:,} TL<br>
                💳 <b>Kapora:</b> {r['Kapora']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # WhatsApp Hızlı Buton
            wp_msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuzu teyit etmek için yazıyorum...")
            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_msg}" target="_blank" class="wa-link">📱 WhatsApp\'tan Yaz</a>', unsafe_allow_html=True)
        
        else:
            # BOŞ GÜN: Kayıt Formu
            st.subheader(f"📝 {selected_date} İçin Hızlı Kayıt")
            with st.form("hizli_kayit_final", clear_on_submit=True):
                f1, f2, f3 = st.columns(3)
                f_ad = f1.text_input("Misafir Ad Soyad")
                f_tel = f2.text_input("Telefon (90...)", value="90")
                f_tarih = f3.date_input("Giriş Tarihi", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                
                f4, f5, f6 = st.columns(3)
                f_gun = f4.number_input("Gece Sayısı", min_value=1, value=1)
                f_ucret = f5.number_input("Gecelik Ücret (TL)", min_value=0)
                f_kapora = f6.selectbox("Ödeme/Kapora Durumu", ["Bekleniyor", "Kapora Alındı", "Tamamı Ödendi"])
                
                toplam_hesap = f_gun * f_ucret
                st.info(f"💰 **Hesaplanacak Toplam: {toplam_hesap:,} TL**")
                
                if st.form_submit_button("✅ REZERVASYONU KAYDET"):
                    try:
                        yeni_liste = []
                        for i in range(int(f_gun)):
                            t_str = (f_tarih + timedelta(days=i)).strftime("%Y-%m-%d")
                            yeni_liste.append({
                                "Tarih": t_str, "Ad Soyad": f_ad, "Tel": f_tel, 
                                "Ucret": f_ucret, "Gece": f_gun, "Durum": "Dolu", 
                                "Toplam": toplam_hesap, "Kapora": f_kapora
                            })
                        
                        yeni_data = pd.DataFrame(yeni_liste)
                        pd.concat([df, yeni_data], ignore_index=True).to_csv(REZ_FILE, index=False, encoding='utf-8-sig')
                        st.success("İşlem Başarılı!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Hata oluştu: {e}")

# --- DİĞER SEKMELER (v42.4.5 İskeleti) ---
with t_rez:
    st.info("Rezervasyonlarınızı takvime tıklayarak yönetebilirsiniz. İşte kayıtlı misafirler:")
    if not df.empty:
        df_list = df.copy()
        df_list['Giris'] = pd.to_datetime(df_list['Tarih'])
        r_list = df_list.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora"]).agg(Giris=("Giris", "min")).reset_index()
        st.dataframe(r_list, use_container_width=True)

with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Özeti")
    m_gider = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
    st.metric("Aylık Brüt Gelir", f"{ciro:,.0f} TL")
    st.metric("Aylık Toplam Gider", f"{m_gider:,.0f} TL")
    st.success(f"Net Kar: {ciro - m_gider:,.0f} TL")

with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, encoding='utf-8-sig')
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False, encoding='utf-8-sig')
        st.rerun()
