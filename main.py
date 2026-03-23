import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse
# --- AYDINLIK MOD & SOFT TASARIM ---
st.markdown("""
    <style>
        /* 1. TARAYICIYA AYDINLIK MODU DAYAT */
        :root {
            color-scheme: light !important;
        }

        /* 2. TÜM SAYFAYI AYDINLIĞA ÇİVİLE */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #FDFCF9 !important;
        }

        /* 3. HAYALET YAZILARI (CİRO, DOLULUK VB.) SİMSİYAH YAP */
        /* opacity: 1 ve -webkit zorlaması iPhone için kritiktir */
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], 
        [data-testid="stMarkdownContainer"] p, label, span, h1, h2, h3 {
            color: #000000 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* 4. TÜM BUTONLARI OKUNUR YAP (MİNT + SİYAH YAZI) */
        .stButton button, div.stButton > button {
            background-color: #8FD9C8 !important;
            color: #000000 !important;
            font-weight: 800 !important;
            border: 2px solid #5FB39F !important;
            border-radius: 12px !important;
            height: 3.5em !important;
            width: 100% !important;
        }

        /* 5. METRİK KARTLARINI BELİRGİNLEŞTİR */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E0DDD7 !important;
            border-radius: 12px !important;
            padding: 15px !important;
        }

        /* 6. GİRİŞ KUTULARI */
        input, div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #DCD9D2 !important;
        }
    </style>
""", unsafe_allow_html=True)







# --- 1. AYARLAR & SABİT TASARIM ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="wide", page_icon="🏡")

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
st.markdown('<div class="main-header">🏡 Villa Yönetim Paneli (Beta 1.0)</div>', unsafe_allow_html=True)
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

# --- TAB 2: REZERVASYON LİSTESİ (GÜNCEL SÜRÜM) ---
with t_rez:
    if df.empty:
        st.info("Kayıtlı rezervasyon bulunmuyor.")
    else:
        # 1. VERİ HAZIRLAMA & GRUPLAMA (Kişi Bazlı)
        df_view = df.copy()
        df_view['Tarih_DT'] = pd.to_datetime(df_view['Tarih'], errors='coerce')
        df_view = df_view.dropna(subset=['Tarih_DT'])
        
        summary = df_view.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(
            Giris=('Tarih_DT', 'min'),
            Cikis=('Tarih_DT', 'max')
        ).reset_index()
        
        summary['Cikis_S'] = summary['Cikis'] + timedelta(days=1)
        summary['Giris_T'] = summary['Giris'].dt.strftime('%d.%m.%Y')
        summary['Cikis_T'] = summary['Cikis_S'].dt.strftime('%d.%m.%Y')

        # 2. GÖRSEL METRİK KARTLARI (Şık Tasarım)
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stat-box"><small>Toplam Rez</small><br><b style="font-size:20px;">{len(summary)} Grup</b></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stat-box"><small>Bekleyen Kapora</small><br><b style="color:#ef4444; font-size:20px;">{len(summary[summary["Kapora"]=="Ödenmedi"])} Adet</b></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stat-box"><small>Toplam Ciro</small><br><b style="color:#10b981; font-size:20px;">{summary["Toplam"].sum():,.0f} TL</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. ARAMA VE ÖZEL KART GÖSTERİMİ
        st.subheader("🔍 Misafir Sorgula")
        search_term = st.text_input("İsim veya telefon yazın, detaylı kartı görün...", "")
        
        if search_term:
            # Arama sonuçlarını filtrele
            results = summary[
                summary['Ad Soyad'].astype(str).str.contains(search_term, case=False, na=False) | 
                summary['Tel'].astype(str).str.contains(search_term, na=False)
            ]
            
            if not results.empty:
                for idx, r in results.iterrows():
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #D6BD98; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
                        <h3 style="margin:0; color:#1e293b;">👤 {r['Ad Soyad']}</h3>
                        <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 15px;">
                            <div><b>📞 Tel:</b> {r['Tel']}</div>
                            <div><b>🌙 Konaklama:</b> {r['Gece']} Gece</div>
                            <div><b>📅 Giriş:</b> {r['Giris_T']}</div>
                            <div><b>📅 Çıkış:</b> {r['Cikis_T']}</div>
                            <div><b>💵 Gecelik:</b> {r['Ucret']:,} TL</div>
                            <div><b>💰 Toplam:</b> {r['Toplam']:,} TL</div>
                            <div style="grid-column: span 2; padding: 10px; background: #f8fafc; border-radius: 8px; text-align: center;">
                                <b>💳 Ödeme Durumu:</b> <span style="color: {'#ef4444' if r['Kapora']=='Ödenmedi' else '#10b981'}">{r['Kapora']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Eşleşen kayıt bulunamadı.")

        st.divider()

        # 4. GENEL TABLO (Sadece Liste Olarak)
        st.subheader("📋 Tüm Kayıtlar (Özet)")
        final_table = summary[['Ad Soyad', 'Tel', 'Giris_T', 'Cikis_T', 'Gece', 'Toplam', 'Kapora']].copy()
        final_table.columns = ['Misafir', 'Telefon', 'Giriş', 'Çıkış', 'Gece', 'Toplam', 'Ödeme']
        st.dataframe(final_table, use_container_width=True, hide_index=True)

        # 5. İNDİRME & SİLME (İstediğin gibi kaldı)
        col_down, col_del = st.columns([2, 1])
        
        with col_down:
            csv_data = final_table.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 Excel Listesi (Kişi Bazlı)", data=csv_data, file_name="Detayvalik_Rezv.csv", mime='text/csv')
            
        with col_del:
            sil_liste = summary['Ad Soyad'].unique().tolist()
            secilen_sil = st.selectbox("Kayıt Sil", ["Seçiniz..."] + sil_liste)
            if secilen_sil != "Seçiniz...":
                if st.button(f"❌ {secilen_sil} Sil"):
                    df = df[df['Ad Soyad'] != secilen_sil]
                    save_data(df)
                    st.rerun()

# --- TAB 3: FİNANSAL TABLO (v42.6.3 İSKELET UYUMLU) ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Analizi")
    
    # 1. GİDER DOSYASI KONTROLÜ
    GIDER_FILE = "gider.csv"
    COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]
    if not os.path.exists(GIDER_FILE):
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
    
    try:
        df_gider_raw = pd.read_csv(GIDER_FILE, sep=';', encoding='utf-8-sig')
        # Sütunları zorla doğrula
        for col in COL_GIDER:
            if col not in df_gider_raw.columns: df_gider_raw[col] = 0 if col == "Tutar" else ""
    except:
        df_gider_raw = pd.DataFrame(columns=COL_GIDER)

    # 2. HESAPLAMALAR
    # Gelir: Takvimdeki o ayın toplam cirosu
    m_rez_fin = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    brut_gelir = m_rez_fin.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    vergi_yukü = brut_gelir * 0.12 # %10 KDV + %2 Konaklama
    
    # Gider: Gider dosyasındaki o ayın toplamı
    df_gider_raw['Tarih_DT'] = pd.to_datetime(df_gider_raw['Tarih'], errors='coerce')
    m_gider_fin = df_gider_raw[df_gider_raw['Tarih_DT'].dt.month == ay_idx]
    toplam_gider_tl = m_gider_fin["Tutar"].sum()
    
    net_kar_tl = brut_gelir - vergi_yukü - toplam_gider_tl

    # 3. GÖRSEL PANEL (İskelet Tasarımıyla Aynı)
    st.markdown('<div class="stat-container">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    f1.markdown(f'<div class="stat-box"><small>Brüt Gelir</small><br><b style="font-size:18px;">{brut_gelir:,.0f} TL</b></div>', unsafe_allow_html=True)
    f2.markdown(f'<div class="stat-box"><small>Vergi (%12)</small><br><b style="color:#ef4444; font-size:18px;">-{vergi_yukü:,.0f} TL</b></div>', unsafe_allow_html=True)
    f3.markdown(f'<div class="stat-box"><small>Gider Toplamı</small><br><b style="color:#ef4444; font-size:18px;">-{toplam_gider_tl:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background:#1e293b; color:white; padding:20px; border-radius:15px; text-align:center; margin-top:15px; border-bottom: 5px solid #10b981;">
            <small style="opacity:0.8;">BU AYIN NET KARI</small>
            <h2 style="margin:0; color:#10b981;">{net_kar_tl:,.0f} TL</h2>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 4. GİDER GİRİŞ FORMU (Duplicate ID Korunmuş)
    st.subheader("🧾 Gider Ekle")
    with st.form("finans_gider_formu_v1", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        g_tarih = c1.date_input("Tarih", key="g_tarih_input")
        g_aciklama = c2.text_input("Gider Açıklaması (Market, Elektrik vb.)", key="g_desc_input")
        g_tutar = c3.number_input("Tutar (TL)", min_value=0, key="g_tutar_input")
        
        if st.form_submit_button("💰 GİDERİ KAYDET"):
            yeni_gider_satiri = pd.DataFrame([{
                "Tarih": g_tarih.strftime("%Y-%m-%d"),
                "Kategori": "Genel",
                "Aciklama": g_aciklama,
                "Tutar": g_tutar
            }])
            # Kaydet
            df_save_g = pd.concat([df_gider_raw.drop(columns=['Tarih_DT'], errors='ignore'), yeni_gider_satiri], ignore_index=True)
            df_save_g.to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.success("Gider başarıyla işlendi!")
            st.rerun()

    # 5. LİSTELEME
    if not m_gider_fin.empty:
        st.write("### Gider Detayları")
        st.dataframe(m_gider_fin[['Tarih', 'Aciklama', 'Tutar']], use_container_width=True, hide_index=True)
# --- TAB 4: AYARLAR (GÜNCELLENMİŞ & GÜVENLİ) ---
with t_set:
    st.subheader("📂 Dosya & Yedekleme Yönetimi")
    
    # Gider Dosyasını İndir (Bulutta dosyayı görebilmen için)
    if os.path.exists("gider.csv"):
        with open("gider.csv", "rb") as f:
            st.download_button(
                label="📥 Gider Listesini (Excel/CSV) İndir",
                data=f,
                file_name=f"Detayvalik_Gider_Yedek_{datetime.now().strftime('%d_%m')}.csv",
                mime="text/csv",
                key="down_gider_btn"
            )
    
    st.divider()
    
    # Dosya Sıfırlama (Tam Kontrol)
    st.warning("⚠️ Dikkat: Aşağıdaki buton tüm verileri kalıcı olarak siler.")
    if st.button("🔴 TÜM SİSTEMİ SIFIRLA (REZ + GİDER)"):
        # Rezervasyonları Sıfırla
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        # Giderleri Sıfırla
        pd.DataFrame(columns=["Tarih", "Kategori", "Aciklama", "Tutar"]).to_csv("gider.csv", index=False, sep=';', encoding='utf-8-sig')
        st.success("Tüm veriler temizlendi!")
        st.rerun()
