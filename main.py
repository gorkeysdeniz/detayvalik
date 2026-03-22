import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR & VERGİ PARAMETRELERİ ---
KDV_ORANI = 0.10      
TURIZM_VERGISI = 0.02 

st.set_page_config(page_title="Detayvalık Operasyon v42.5.5", layout="wide", page_icon="🏡")

# Modern Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 26px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 12px; margin-bottom: 20px; }
    .stat-box { background: white; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); min-height: 120px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 8px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 20px 0; border-radius: 12px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 18px;
        transition: transform 0.1s; border-bottom: 4px solid rgba(0,0,0,0.2);
    }
    .day-link:active { transform: translateY(2px); border-bottom: 2px solid rgba(0,0,0,0.2); }
    .bos { background: #10b981 !important; } 
    .dolu { background: #ef4444 !important; } 
    .info-card { background: white; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; border-top: 6px solid #ef4444; margin: 15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stForm { background: white !important; border-radius: 15px !important; padding: 20px !important; border: 1px solid #E2E8F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
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
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.5.5</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & İŞLEMLER ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    selected_date = st.query_params.get("date", None)

    # 1. TAKVİM
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

    # 2. ETKİLEŞİM PANELİ
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        
        if not rez_info.empty:
            r = rez_info.iloc[0]
            try:
                giris_dt = datetime.strptime(str(r['Tarih']), "%Y-%m-%d")
                cikis_dt = giris_dt + timedelta(days=int(r['Gece']))
                cikis_str = cikis_dt.strftime('%d.%m.%Y')
                giris_str = giris_dt.strftime('%d.%m.%Y')
            except:
                giris_str, cikis_str = selected_date, "Belirtilmedi"

            # Hata veren f-string bloğu burada düzeltildi:
            st.markdown(f"""
            <div class="info-card">
                <h3 style='margin-top:0;'>👤 Misafir: {r['Ad Soyad']}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size:16px;'>
                    <div>📅 <b>Giriş:</b> {giris_str}</div>
                    <div>📅 <b>Çıkış:</b> {cikis_str}</div>
                    <div>🌙 <b>Toplam:</b> {r['Gece']} Gece</div>
                    <div>📞 <b>Tel:</b> {r['Tel']}</div>
                    <div>💵 <b>Günlük:</b> {r['Ucret']:,} TL</div>
                    <div>💰 <b>Toplam:</b> {r['Toplam']:,} TL</div>
                    <div style='grid-column: span 2; padding:10px; background:#f8fafc; border-radius:8px; border:1px dashed #cbd5e1; margin-top:10px;'>
                        💳 <b>Ödeme Durumu:</b> {r['Kapora']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            wp_msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, Detayvalık Villa rezervasyonunuzu teyit etmek için yazıyorum...")
            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_msg}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 25px; border-radius: 12px; text-decoration: none; font-weight: 700; display: inline-block; text-align:center; width:100%;">📱 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)
        
        else:
            st.subheader(f"📝 {selected_date} İçin Hızlı Kayıt")
            with st.form("hizli_kayit_v5", clear_on_submit=True):
                f1, f2, f3 = st.columns(3)
                f_ad = f1.text_input("Misafir Ad Soyad")
                f_tel = f2.text_input("Telefon (90...)", value="90")
                f_tarih = f3.date_input("Giriş Tarihi", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                
                f4, f5, f6 = st.columns(3)
                f_gun = f4.number_input("Gece Sayısı", min_value=1, value=1)
                f_ucret = f5.number_input("Gecelik Ücret (TL)", min_value=0)
                f_kapora = f6.selectbox("Ödeme/Kapora Durumu", ["Kapora Bekleniyor", "Kapora Alındı", "Tamamı Ödendi"])
                
                toplam_hesap = f_gun * f_ucret
                st.info(f"💰 **Otomatik Hesaplanan Toplam: {toplam_hesap:,} TL**")
                
                if st.form_submit_button("✅ REZERVASYONU KAYDET"):
                    yeni_liste = []
                    for i in range(int(f_gun)):
                        t_str = (f_tarih + timedelta(days=i)).strftime("%Y-%m-%d")
                        yeni_liste.append({
                            "Tarih": t_str, "Ad Soyad": f_ad, "Tel": f_tel, 
                            "Ucret": f_ucret, "Gece": f_gun, "Durum": "Dolu", 
                            "Toplam": toplam_hesap, "Kapora": f_kapora
                        })
                    pd.concat([df, pd.DataFrame(yeni_liste)], ignore_index=True).to_csv(REZ_FILE, index=False, encoding='utf-8-sig')
                    st.success("Kayıt Başarıyla Eklendi!")
                    st.rerun()

    # 3. GELİŞMİŞ DASHBOARD (En Altta)
    st.divider()
    month_days = calendar.monthrange(2026, ay_idx)[1]
    month_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    
    ciro = month_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    dolu_gun = month_df['Tarih'].nunique()
    bos_gun = month_days - dolu_gun
    occ_rate = (dolu_gun / month_days) * 100

    if occ_rate > 85: tavsiye = "🚀 Harika! Fiyatları %15 artırabilirsin."
    elif occ_rate > 50: tavsiye = "✅ İyi Gidiyor. Son dakika indirimleri yapabilirsin."
    elif occ_rate > 0: tavsiye = "📉 Kampanya veya reklam çıkma zamanı."
    else: tavsiye = "💤 Henüz kayıt yok. İlanları kontrol et!"
