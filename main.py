import streamlit as st
import pandas as pd
import os
REZ_FILE = os.path.join(os.getcwd(), 'rez.csv')
from datetime import datetime, timedelta
import calendar
import urllib.parse
from github import Github


def finans_kart_olustur(baslik, deger, renk="#1E293B"):
    st.markdown(f"""
        <div style="background-color: {renk}; padding: 22px; border-radius: 18px; text-align: center; margin-bottom: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); border: 1px solid rgba(255,255,255,0.1);">
            <p style="margin: 0; font-size: 13px; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;">{baslik}</p>
            <h2 style="margin: 5px 0 0 0; font-size: 32px; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; font-weight: 900; letter-spacing: -1px;">{deger}</h2>
        </div>
    """, unsafe_allow_html=True)



# --- 1. AYARLAR & SABİT TASARIM ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="wide", page_icon="🏡")

# --- 2. GÖRSEL SORUNLARI BİTİREN KESİN STİL ---
st.markdown("""
    <style>
        /* TÜM SİSTEMİ SIFIRLA VE MODA GÖRE RENKLENDİR */
        
        /* 1. AYDINLIK MOD (BEMBEYAZ TEMA) */
        @media (prefers-color-scheme: light) {
            .stApp, [data-testid="stAppViewContainer"], .main {
                background-color: #FFFFFF !important;
            }
            /* Yazıları Siyah Yap */
            h1, h2, h3, p, span, label, div, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
                color: #1e293b !important;
                -webkit-text-fill-color: #1e293b !important;
            }
            /* Kartları Hafif Gri Yap */
            .stat-box { background: #F8FAFC !important; border: 1px solid #E2E8F0 !important; }
            .modern-table td { border: 1px solid #E2E8F0 !important; }
            /* Buton Yazısı Siyah */
            .stButton button { color: #000000 !important; font-weight: 700 !important; }
        }

        /* 2. KARANLIK MOD (SİYAH TEMA) */
        @media (prefers-color-scheme: dark) {
            .stApp, [data-testid="stAppViewContainer"], .main {
                background-color: #0E1117 !important;
            }
            /* Yazıları Beyaz Yap */
            h1, h2, h3, p, span, label, div, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
                color: #FFFFFF !important;
                -webkit-text-fill-color: #FFFFFF !important;
            }
            /* Kartları Koyu Yap */
            .stat-box { background: #1A1C24 !important; border: 1px solid #33363F !important; }
            .modern-table td { border: 1px solid #4D4D4D !important; }
            /* Buton Yazısı Beyaz */
            .stButton button { color: #FFFFFF !important; font-weight: 800 !important; border: 1px solid #FFFFFF !important; }
        }

        /* ORTAK TASARIM ELEMANLARI */
        .main-header { font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
        .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
        .day-link { 
            display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; 
            font-weight: 700; color: white !important; text-align: center; font-size: 16px;
        }
        .bos { background: #10b981 !important; } 
        .dolu { background: #ef4444 !important; } 
        .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
        .stat-box { flex: 1; min-width: 120px; padding: 15px; border-radius: 10px; text-align: center; }
        .stButton button { background-color: #8FD9C8 !important; border-radius: 12px !important; height: 3.5em !important; width: 100% !important; }
        
        /* Tablar (Sekmeler) İçin Düzeltme */
        button[data-baseweb="tab"] p { color: inherit !important; }
    </style>
""", unsafe_allow_html=True)





# --- 2. VERİ YÖNETİMİ (GÜNCELLENMİŞ VE GÜVENLİ) ---
REZ_FILE = "rez.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]

def load_data():
    if not os.path.exists(REZ_FILE):
        # Dosya yoksa başlıklarla yeni bir tane oluştur
        return pd.DataFrame(columns=['Tarih', 'Ad Soyad', 'Tel', 'Ucret', 'Gece', 'Not', 'Durum', 'Toplam', 'Kapora'])
    try:
        # Dosyayı oku
        return pd.read_csv(REZ_FILE, sep=',', encoding='utf-8-sig')
    except:
        # Hata varsa boş dön
        return pd.DataFrame(columns=['Tarih', 'Ad Soyad', 'Tel', 'Ucret', 'Gece', 'Not', 'Durum', 'Toplam', 'Kapora'])
        
def save_data(df_to_save):
    # 1. ADIM: Önce yerel dosyaya kaydet (Garantici yöntem)
    try:
        df_to_save.to_csv(REZ_FILE, index=False, sep=',', encoding='utf-8-sig')
    except Exception as e:
        st.error(f"Yerel kayıt hatası: {e}")

    # 2. ADIM: GitHub Yedekleme (Sadece bir kere ve doğru hizada)
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"]
        
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)
        
        # İçeriği hazırla
        content = df_to_save.to_csv(index=False, sep=',', encoding='utf-8-sig')
        
        try:
            # Önce GitHub'da dosya var mı bak ve güncelle
            contents = repo.get_contents("rez.csv")
            repo.update_file(contents.path, "🔄 Rezervasyon Güncellendi", content, contents.sha)
            st.toast("☁️ GitHub yedeği başarılı!", icon="✅")
        except:
            # Eğer dosya GitHub'da yoksa (404), YENİDEN OLUŞTUR
            repo.create_file("rez.csv", "🆕 İlk Dosya Oluşturuldu", content)
            st.toast("🚀 Yeni dosya GitHub'da oluşturuldu!", icon="✨")
            
    except Exception as e:
        # Eğer internet yoksa veya Token hatalıysa sistemi durdurmaz, sadece uyarır
        st.warning(f"⚠️ Bulut yedeği başarısız: {e}")

# Bu satır save_data fonksiyonunun dışında, en altta kalmalı
df = load_data()

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Villa Yönetim Paneli (Beta 1.0)</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & İŞLEMLER ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1

    # --- EN YAKIN TEMİZLİK GÜNÜ HATIRLATICI ---
    bugun = datetime.now()
    
    # Tüm rezervasyonların çıkış tarihlerini hesapla
    if not df.empty:
        df_clean = df.copy()
        df_clean['Cikis_DT'] = pd.to_datetime(df_clean['Tarih']) + pd.to_timedelta(df_clean['Gece'], unit='d')
        
        # Gelecekteki (bugünden sonraki) en yakın çıkışı bul
        gelecek_cikislar = df_clean[df_clean['Cikis_DT'] >= bugun]
        
        if not gelecek_cikislar.empty:
            en_yakin_cikis = gelecek_cikislar['Cikis_DT'].min()
            gun_farki = (en_yakin_cikis - bugun).days + 1
            
            # Kartın rengini aciliyet durumuna göre belirleyelim
            if gun_farki == 0:
                kart_renk = "#ef4444" # Kırmızı (Bugün!)
                mesaj = "BUGÜN TEMİZLİK VAR!"
            elif gun_farki == 1:
                kart_renk = "#f59e0b" # Turuncu (Yarın)
                mesaj = "YARIN TEMİZLİK VAR"
            else:
                kart_renk = "#10b981" # Yeşil (Vakit var)
                mesaj = "Sıradaki Temizlik"

            # Görsel Kart Tasarımı
            st.markdown(f"""
                <div style="background-color: {kart_renk}; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; color: white;">
                    <p style="margin: 0; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">{mesaj}</p>
                    <h2 style="margin: 5px 0; font-size: 32px; color: white !important;">{en_yakin_cikis.strftime('%d %B %Y')}</h2>
                    <p style="margin: 0; opacity: 0.9;">📅 {gun_farki} gün kaldı</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Yakın zamanda planlı bir çıkış/temizlik bulunmuyor.")
    else:
        st.info("Henüz rezervasyon kaydı yok.")
    
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
        c1.markdown(f'<div class="stat-box"><small>Toplam Rez</small><br><b style="font-size:20px;">{len(summary)} </b></div>', unsafe_allow_html=True)
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
            # Silme listesi için "İsim - Telefon" kombinasyonu oluşturuyoruz (Daha güvenli)
            sil_opsiyonlari = summary.apply(lambda x: f"{x['Ad Soyad']} ({x['Tel']})", axis=1).tolist()
            secilen_sil_metin = st.selectbox("Silinecek Rezervasyon", ["Seçiniz..."] + sil_opsiyonlari)
            
            if secilen_sil_metin != "Seçiniz...":
                # Parantez içindeki telefon numarasını geri ayıklıyoruz
                secilen_tel = secilen_sil_metin.split('(')[-1].replace(')', '').strip()
                
                if st.button(f"❌ Kaydı Sil"):
                    # Sadece o telefon numarasına ait tüm günleri (rezervasyonu) siler
                    df = df[df['Tel'].astype(str) != str(secilen_tel)]
                    save_data(df)
                    st.success(f"{secilen_tel} numaralı kayıt silindi!")
                    st.rerun()

# --- TAB 3: FİNANSAL TABLO (PROFESYONEL GÖRÜNÜM) ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Analizi")
    
    # 1. Gider Dosyası Kontrolü & Veri Yükleme
    GIDER_FILE = "gider.csv"
    if not os.path.exists(GIDER_FILE):
        pd.DataFrame(columns=["Tarih", "Kategori", "Aciklama", "Tutar"]).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
    
    try:
        df_gider = pd.read_csv(GIDER_FILE, sep=';', encoding='utf-8-sig')
    except:
        df_gider = pd.DataFrame(columns=["Tarih", "Kategori", "Aciklama", "Tutar"])

    # 2. Hesaplamalar
    # Gelir: Takvimdeki o ayın toplam cirosu
    m_rez_fin = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    brut_gelir = m_rez_fin.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    vergi_yukü = brut_gelir * 0.12 # %12 Vergi Tahmini
    
    # Gider: Gider dosyasındaki o ayın toplamı
    df_gider['Tarih_DT'] = pd.to_datetime(df_gider['Tarih'], errors='coerce')
    m_gider_fin = df_gider[df_gider['Tarih_DT'].dt.month == ay_idx]
    toplam_gider_tl = m_gider_fin["Tutar"].sum()
    
    net_kar_tl = brut_gelir - vergi_yukü - toplam_gider_tl

    # 3. KESKİN VE KALIN YAZILI FİNANS KARTLARI
    # Col1 ve Col2 içinde ayrı ayrı gösterim
    c1, c2 = st.columns(2)
    
    with c1:
        finans_kart_olustur("BRÜT GELİR", f"{brut_gelir:,.0f} TL", "#1E293B")
        finans_kart_olustur("GİDER TOPLAMI", f"-{toplam_gider_tl:,.0f} TL", "#EF4444")
        
    with c2:
        finans_kart_olustur("VERGİ TAHMİNİ (%12)", f"-{vergi_yukü:,.0f} TL", "#334155")
        # NET KAR KUTUSU - DAHA BÜYÜK VE YEŞİL
        finans_kart_olustur("BU AYIN NET KARI", f"{net_kar_tl:,.0f} TL", "#10B981")

    st.divider()

    # 4. GİDER GİRİŞ FORMU
    st.subheader("🧾 Gider Ekle")
    with st.form("finans_gider_yeni_v4", clear_on_submit=True):
        col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
        g_tarih = col_g1.date_input("Tarih", key="fin_g_date")
        g_aciklama = col_g2.text_input("Açıklama (Elektrik, Su, Market vb.)", key="fin_g_desc")
        g_tutar = col_g3.number_input("Tutar (TL)", min_value=0, key="fin_g_val")
        
        if st.form_submit_button("💰 GİDERİ KAYDET"):
            yeni_gider = pd.DataFrame([{
                "Tarih": g_tarih.strftime("%Y-%m-%d"),
                "Kategori": "Genel",
                "Aciklama": g_aciklama,
                "Tutar": g_tutar
            }])
            # Kaydet ve Yenile
            df_gider_save = pd.concat([df_gider.drop(columns=['Tarih_DT'], errors='ignore'), yeni_gider], ignore_index=True)
            df_gider_save.to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.success("Gider başarıyla kaydedildi!")
            st.rerun()

    # 5. AYIN GİDER LİSTESİ
    if not m_gider_fin.empty:
        st.write(f"### 📋 {sec_ay} Gider Detayları")
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
