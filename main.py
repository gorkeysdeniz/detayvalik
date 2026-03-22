import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR & SABİT TASARIM ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.3", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    
    /* Dashboard Kutuları - Esnek ve Kaymayan Yapı */
    .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
    .stat-box { 
        flex: 1; min-width: 120px; background: white; border: 1px solid #E2E8F0; 
        padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 16px;
        border-bottom: 3px solid rgba(0,0,0,0.1);
    }
    .bos { background: #10b981 !important; } 
    .dolu { background: #ef4444 !important; } 
    
    .info-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border-left: 8px solid #ef4444; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ (EXCEL UYUMLU ;) ---
REZ_FILE = "rez.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]

def load_data():
    if not os.path.exists(REZ_FILE): 
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
    try:
        return pd.read_csv(REZ_FILE, sep=';', encoding='utf-8-sig').reindex(columns=COL_REZ, fill_value="")
    except:
        return pd.DataFrame(columns=COL_REZ)

def save_data(df_to_save):
    df_to_save.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')

df = load_data()

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.3</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & İŞLEMLER ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # TAKVİM GÖRÜNÜMÜ
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

    # SEÇİLİ GÜN DETAYI
    selected_date = st.query_params.get("date")
    if selected_date:
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        
        if not rez_info.empty:
            # DOLU GÜN: Eksiksiz Müşteri Bilgileri
            r = rez_info.iloc[0]
            g_tarih = datetime.strptime(str(r['Tarih']), "%Y-%m-%d")
            c_tarih = g_tarih + timedelta(days=int(r['Gece']))
            
            st.markdown(f"""
            <div class="info-card">
                <h3 style='margin-top:0;'>👤 Misafir: {r['Ad Soyad']}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                    <div><b>📞 Telefon:</b> {r['Tel']}</div>
                    <div><b>🌙 Gün Sayısı:</b> {r['Gece']} Gece</div>
                    <div><b>📅 Giriş:</b> {g_tarih.strftime('%d.%m.%Y')}</div>
                    <div><b>📅 Çıkış:</b> {c_tarih.strftime('%d.%m.%Y')}</div>
                    <div><b>💵 Günlük Ücret:</b> {r['Ucret']:,} TL</div>
                    <div><b>💰 Toplam:</b> {r['Toplam']:,} TL</div>
                    <div style='grid-column: span 2; border-top: 1px solid #eee; padding-top:10px;'>
                        <b>💳 Ödeme Durumu:</b> {r['Kapora']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            wp_msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, Detayvalık rezervasyonunuzu teyit etmek için yazıyorum...")
            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_msg}" target="_blank" style="background-color:#25D366; color:white; padding:12px; border-radius:10px; text-decoration:none; display:block; text-align:center; font-weight:bold;">📱 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)
        else:
            # BOŞ GÜN: Kayıt Formu
            st.subheader(f"📝 {selected_date} Rezervasyon Kaydı")
            with st.form("yeni_rez_v3", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                f_ad = c1.text_input("Ad Soyad")
                f_tel = c2.text_input("Telefon", value="90")
                f_giris = c3.date_input("Giriş Tarihi", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                
                c4, c5, c6 = st.columns(3)
                f_gece = c4.number_input("Gece Sayısı", min_value=1, value=1)
                f_gunluk = c5.number_input("Günlük Ücret (TL)", min_value=0)
                f_kapora = c6.selectbox("Kapora Durumu", ["Ödenmedi", "Kısmi Ödendi", "Tamamı Ödendi"])
                
                if st.form_submit_button("✅ REZERVASYONU TAMAMLA"):
                    yeni_satirlar = []
                    for i in range(int(f_gece)):
                        t_str = (f_giris + timedelta(days=i)).strftime("%Y-%m-%d")
                        yeni_satirlar.append({
                            "Tarih": t_str, "Ad Soyad": f_ad, "Tel": f_tel, "Ucret": f_gunluk, 
                            "Gece": f_gece, "Durum": "Dolu", "Toplam": f_gece * f_gunluk, "Kapora": f_kapora
                        })
                    df = pd.concat([df, pd.DataFrame(yeni_satirlar)], ignore_index=True)
                    save_data(df)
                    st.success("Kayıt Başarılı!")
                    st.rerun()

    # --- DASHBOARD (HER ZAMAN GÖRÜNÜR) ---
    st.divider()
    st.subheader(f"📊 {sec_ay} Özeti")
    
    m_days = calendar.monthrange(2026, ay_idx)[1]
    m_df = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    
    ciro = m_df.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    dolu_g = m_df['Tarih'].nunique()
    bos_g = m_days - dolu_g
    oran = (dolu_g / m_days) * 100

    # Tavsiye Mantığı
    if oran > 80: tavsiye = "🚀 Doluluk yüksek! Fiyatları %15 artırabilirsin."
    elif oran > 40: tavsiye = "✅ Gayet iyi. Erken rezervasyon indirimi devam edebilir."
    else: tavsiye = "📉 Boş gün çok! Hafta içi %20 indirim tanımlayabilirsin."

    # Stat Kutuları (CSS Stat-Container kullanıyor)
    st.markdown(f"""
    <div class="stat-container">
        <div class="stat-box"><small>Aylık Ciro</small><br><b>{ciro:,.0f} TL</b></div>
        <div class="stat-box"><small>Doluluk</small><br><b>%{oran:.1f}</b></div>
        <div class="stat-box"><small>Dolu Gün</small><br><b style='color:#ef4444;'>{dolu_g} Gün</b></div>
        <div class="stat-box"><small>Boş Gün</small><br><b style='color:#10b981;'>{bos_g} Gün</b></div>
        <div class="stat-box" style='flex: 2; min-width: 200px;'><small>İndirim & Tavsiye</small><br><span style='font-size:14px; font-weight:600;'>{tavsiye}</span></div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: REZERVASYON LİSTESİ (SADECE BU BLOĞU DEĞİŞTİR) ---
with t_rez:
    if df.empty:
        st.info("Kayıtlı rezervasyon bulunmuyor.")
    else:
        # 1. VERİ HAZIRLAMA & GRUPLAMA
        df_view = df.copy()
        df_view['Tarih_DT'] = pd.to_datetime(df_view['Tarih'], errors='coerce')
        df_view = df_view.dropna(subset=['Tarih_DT'])
        
        # Kişi bazlı özet tabloyu oluştur (Giriş-Çıkış şeklinde)
        summary = df_view.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(
            Giris=('Tarih_DT', 'min'),
            Cikis=('Tarih_DT', 'max')
        ).reset_index()
        
        # Çıkış sabahını ve tarih formatlarını ayarla
        summary['Cikis'] = summary['Cikis'] + timedelta(days=1)
        summary['Giris_Tarihi'] = summary['Giris'].dt.strftime('%d.%m.%Y')
        summary['Cikis_Tarihi'] = summary['Cikis'].dt.strftime('%d.%m.%Y')

        # 2. ÜST METRİKLER (Sade Dashboard)
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Grup", f"{len(summary)}")
        m2.metric("Bekleyen Kapora", f"{len(summary[summary['Kapora']=='Ödenmedi'])}")
        m3.metric("Toplam Ciro", f"{summary['Toplam'].sum():,.0f} TL")

        st.divider()

        # 3. ARAMA MOTORU (Düzeltildi)
        search = st.text_input("🔍 Misafir Adı veya Telefon ile Ara...", "")
        
        # Arama mantığını hem isim hem telefona göre çalıştır
        if search:
            # Telefon numarasını ve ismi string'e çevirip öyle aratıyoruz (Hata almamak için)
            summary = summary[
                summary['Ad Soyad'].astype(str).str.contains(search, case=False, na=False) | 
                summary['Tel'].astype(str).str.contains(search, na=False)
            ]

        # 4. PROFESYONEL TABLO GÖRÜNÜMÜ
        # Tabloda görünmesini istediğin sütunları seç ve sırala
        final_table = summary[['Ad Soyad', 'Tel', 'Giris_Tarihi', 'Cikis_Tarihi', 'Gece', 'Ucret', 'Toplam', 'Kapora']].copy()
        final_table.columns = ['Misafir', 'Telefon', 'Giriş', 'Çıkış', 'Gece', 'Gecelik', 'Toplam', 'Ödeme']
        
        # Tabloyu göster
        st.dataframe(final_table, use_container_width=True, hide_index=True)

        # 5. KİŞİ BAZLI EXCEL İNDİRME (Sütunlu Format)
        csv_data = final_table.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Bu Listeyi Excel (Kişi Bazlı) İndir",
            data=csv_data,
            file_name=f"Detayvalik_Ozet_Liste.csv",
            mime='text/csv',
        )

        # 6. HIZLI SİLME (Tablo Altında Seçenek)
        st.divider()
        st.subheader("🗑️ Kayıt Sil")
        sil_liste = summary['Ad Soyad'].unique().tolist()
        secilen_sil = st.selectbox("Silmek istediğiniz misafiri seçin", ["Seçiniz..."] + sil_liste)
        
        if secilen_sil != "Seçiniz...":
            if st.button(f"❌ {secilen_sil} Kaydını Tamamen Sil"):
                # Ana veriden o ismi temizle
                df = df[df['Ad Soyad'] != secilen_sil]
                save_data(df)
                st.success(f"{secilen_sil} kaydı silindi. Güncelleniyor...")
                st.rerun()

with t_fin: st.write("Finansal veriler aktif.")
with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
