import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. TASARIM VE IPHONE GÖRÜNÜRLÜK AYARLARI ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white !important; color: #1a1a1a !important; }
    
    /* FORM BAŞLIKLARI VE BUTON FONTU */
    label, .stMarkdown h3, .stMarkdown h2, .stMarkdown h1 { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    /* INPUT KUTULARI VE YAZI RENGİ SABİT */
    input, select, textarea, [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* GENEL BUTON STİLİ (KOYU) */
    .stButton button {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    
    /* WHATSAPP VE İNDİRME BUTONLARI (ÖZEL RENK) */
    .wa-btn button { background-color: #25D366 !important; border: none !important; }
    .dl-btn button { background-color: #007BFF !important; border: none !important; }
    .del-btn button { background-color: #E74C3C !important; border: none !important; }

    /* ALARM KARTI (YAKLAŞAN REZ) */
    .alarm-card {
        background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%);
        color: white !important; padding: 20px; border-radius: 15px;
        margin-bottom: 20px; text-align: center; font-weight: bold;
    }

    /* TAKVİM TASARIMI */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } 
    .dolu { background: #E74C3C !important; } 
    .opsiyon { background: #F1C40F !important; color: #1A1A1A !important; }
    
    /* FİNANS VE KAYIT KARTLARI */
    .f-card {
        background: #ffffff !important; padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 12px;
        border-left: 8px solid #007BFF; color: #000000 !important;
    }
    .f-card b { color: #000000 !important; }
    
    /* GİRİŞ/ÇIKIŞ LİSTESİ */
    .io-list { background: #f8f9fa; padding: 10px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #ddd; }
    .io-item { border-bottom: 1px solid #eee; padding: 5px 0; color: #333; }
    .io-item:last-child { border-bottom: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AKILLI VERİ TABANI YÖNETİMİ ---
# Rezervasyon Sütunları (ValueError'u engellemek için sabitledik)
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
# Gider Sütunları
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
    current_df = pd.read_csv(file)
    # Otomatik Tamir Mekanizması
    if list(current_df.columns) != cols:
        for col in cols:
            if col not in current_df.columns:
                current_df[col] = 0 if col in ["Toplam", "Tutar", "Ucret", "Gece"] else ""
        current_df = current_df[cols]
        current_df.to_csv(file, index=False)
    return current_df

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)

# --- 3. ÜST PANEL (YAKLAŞAN REZERVASYON) ---
st.title("🏡 Villa Yönetim Paneli")
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
future_rexs = df[df["Tarih"] >= today_str].sort_values(by="Tarih")

if not future_rexs.empty:
    nxt = future_rexs.iloc[0]
    st.markdown(f'<div class="alarm-card">🔔 Sıradaki Misafir: {nxt["Ad Soyad"]} <br> Giriş: {nxt["Tarih"]}</div>', unsafe_allow_html=True)

# --- 4. SEKMELER ---
q_date = st.query_params.get("date", "")
t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=today_dt.month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # --- GİRİŞ / ÇIKIŞ LİSTESİ (YENİ) ---
    st.subheader("📋 Bugünün Hareket Planı")
    
    # Giriş Yapacaklar
    st.markdown('<div class="io-list"><strong>⬇️ Bugün Giriş Yapacaklar:</strong>', unsafe_allow_html=True)
    in_today = df[df["Tarih"] == today_str]
    if not in_today.empty:
        for _, r in in_today.iterrows():
            st.markdown(f'<div class="io-item">👤 {r["Ad Soyad"]} ({r["Gece"]} Gece)</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="io-item"><em>Bugün giriş yok.</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Çıkış Yapacaklar (Hesaplama)
    st.markdown('<div class="io-list"><strong>⬆️ Bugün Çıkış Yapacaklar:</strong>', unsafe_allow_html=True)
    df_checkout = df.copy()
    df_checkout['Tarih'] = pd.to_datetime(df_checkout['Tarih'])
    # Çıkış tarihi = Giriş tarihi + Gece sayısı
    df_checkout['CikisTar'] = df_checkout['Tarih'] + pd.to_timedelta(df_checkout['Gece'], unit='D')
    out_today = df_checkout[df_checkout["CikisTar"].dt.strftime("%Y-%m-%d") == today_str]
    if not out_today.empty:
        for _, r in out_today.iterrows():
            st.markdown(f'<div class="io-item">👤 {r["Ad Soyad"]} (Anahtar Teslim)</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="io-item"><em>Bugün çıkış yok.</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # --- TAKVİM GRİD ---
    st.subheader(f"📅 {sec_ay} 2026")
    cal_html = '<table class="modern-table"><thead><tr>'
    for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]: cal_html += f'<th>{g}</th>'
    cal_html += '</tr></thead><tbody>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_str = f"2026-{ay_idx:02d}-{day:02d}"
                r_found = df[df["Tarih"] == d_str]
                cl = "bos"
                if not r_found.empty: cl = "dolu" if r_found.iloc[0]["Durum"]=="Kesin" else "opsiyon"
                cal_html += f'<td><a href="?date={d_str}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</tbody></table>', unsafe_allow_html=True)

    # Takvimden Tıklanan Tarih
    if q_date:
        detay = df[df["Tarih"] == q_date]
        if not detay.empty:
            d_row = detay.iloc[0]
            st.warning(f"📍 {q_date} : {d_row['Ad Soyad']} adına kayıtlı.")
        else:
            st.success(f"📍 {q_date} tarihi şu an müsait.")

    with st.expander("📝 Yeni Rezervasyon Ekle", expanded=True if q_date else False):
        with st.form("r_form"):
            f_tar = st.text_input("Giriş Tarihi (YYYY-AA-GG)", value=q_date)
            f_ad = st.text_input("Müşteri Ad Soyad")
            f_tel = st.text_input("WhatsApp (Örn: 90532...)")
            col1, col2 = st.columns(2)
            f_ucr = col1.number_input("Gecelik Fiyat", min_value=0)
            f_gc = col2.number_input("Gece Sayısı", min_value=1)
            f_not = st.text_area("Müşteri Notları (Alerji, Özel İstek vb.)") # YENİ
            if st.form_submit_button("RESERVASYONU SİSTEME İŞLE"):
                if f_tar and f_ad:
                    try:
                        start_dt = datetime.strptime(f_tar, "%Y-%m-%d")
                        new_data = []
                        for i in range(int(f_gc)):
                            tar = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
                            new_data.append([tar, f_ad, f_tel, f_ucr, f_gc, f_not, "Kesin", f_ucr*f_gc])
                        
                        new_df = pd.DataFrame(new_data, columns=REZ_COLS)
                        pd.concat([df, new_df], ignore_index=True).to_csv("rez.csv", index=False)
                        st.success("Kayıt başarılı! Sayfa yenileniyor...")
                        st.rerun()
                    except ValueError: st.error("Tarih formatı hatalı! (YYYY-AA-GG)")

with t2:
    st.subheader("🔍 Müşteri Kayıtları")
    search = st.text_input("İsim ile hızlı ara...", placeholder="Müşteri adı girin")
    
    if not df.empty:
        # Gruplama (Giriş-Çıkış Hesaplama)
        k_df = df.copy()
        k_df['Tarih'] = pd.to_datetime(k_df['Tarih'])
        grouped = k_df.groupby(['Ad Soyad', 'Toplam', 'Tel', 'Not']).agg(Giris=('Tarih', 'min'), Cikis=('Tarih', 'max'), Gece=('Gece', 'first')).reset_index()
        
        if search: grouped = grouped[grouped['Ad Soyad'].str.contains(search, case=False)]
        
        for _, r in grouped.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="f-card">
                    <b>👤 {r['Ad Soyad']}</b><br>
                    📅 {r['Giris'].strftime('%d %b')} - {r['Cikis'].strftime('%d %b')} ({int(r['Gece'])} Gece)<br>
                    💰 Toplam Tutar: {r['Toplam']:,.0f} TL<br>
                    📝 Not: <em>{r['Not'] if r['Not'] else 'Not yok.'}</em>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                # WHATSAPP ONAY BUTONU (YENİ)
                if r['Tel']:
                    msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, {r['Giris'].strftime('%d %B')} tarihindeki rezervasyonunuz onaylanmıştır. Görüşmek üzere!")
                    wa_url = f"https://wa.me/{r['Tel']}?text={msg}"
                    c1.markdown(f'<div class="wa-btn"><a href="{wa_url}" target="_blank"><button>💬 WhatsApp Onayı</button></a></div>', unsafe_allow_html=True)
                else: c1.warning("Tel Yok")

with t3:
    # --- GİDER TAKİBİ SEKME (YENİ) ---
    st.subheader("💸 Gider Ekleme Formu")
    with st.form("gider_form"):
        g_tar = st.date_input("Gider Tarihi", value=today_dt)
        g_kat = st.selectbox("Kategori", ["Temizlik", "Elektrik", "Su", "İnternet", "Bahçe Bakımı", "Airbnb Komisyon", "Vergi", "Diğer"])
        g_aci = st.text_input("Açıklama (Örn: Haziran faturası)")
        g_tut = st.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("GİDERİ KAYDET"):
            new_gid = pd.DataFrame([[g_tar.strftime("%Y-%m-%d"), g_kat, g_aci, g_tut]], columns=GID_COLS)
            pd.concat([df_gider, new_gid], ignore_index=True).to_csv("gider.csv", index=False)
            st.success("Gider kaydedildi!")
            st.rerun()
            
    st.divider()
    st.subheader("📋 Gider Listesi")
    if not df_gider.empty:
        df_gider_disp = df_gider.copy()
        df_gider_disp['Tarih'] = pd.to_datetime(df_gider_disp['Tarih'])
        st.dataframe(df_gider_disp.sort_values(by="Tarih", ascending=False), use_container_width=True)
    else: st.info("Henüz gider kaydı yok.")

with t4:
    # --- GELİŞMİŞ FİNANS (GİDERLİ) ---
    df_f = df.copy()
    df_f["Tarih"] = pd.to_datetime(df_f["Tarih"])
    
    # Seçili Ayın Geliri
    ay_data = df_f[df_f["Tarih"].dt.month == ay_idx].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut_ay = ay_data["Toplam"].sum()
    
    # Seçili Ayın Gideri
    df_g_f = df_gider.copy()
    df_g_f["Tarih"] = pd.to_datetime(df_g_f["Tarih"])
    ay_gider_data = df_g_f[df_g_f["Tarih"].dt.month == ay_idx]
    gider_ay = ay_gider_data["Tutar"].sum()
    
    # Genel Toplamlar
    all_data = df_f.drop_duplicates(subset=["Ad Soyad", "Toplam"])
    total_brut = all_data["Toplam"].sum()
    total_gider = df_gider["Tutar"].sum()
    # Gerçek Net: Brüt - Gerçek Giderler - (Ciro bazlı KDV vb. %22 tahmini kesinti)
    total_net = (total_brut * 0.78) - total_gider 
    
    st.subheader(f"📊 {sec_ay} Finansal Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Aylık Brüt", f"{brut_ay:,.0f} TL")
    c2.metric("Aylık Gider", f"-{gider_ay:,.0f} TL")
    c3.metric("Aylık Tahmini Net", f"{(brut_ay*0.78)-gider_ay:,.0f} TL")
    
    st.divider()
    
    st.subheader("🌍 Tüm Zamanlar Genel Toplam")
    st.markdown(f'<div class="f-card" style="border-left-color: #2ECC71;">💵 Toplam Brüt Ciro: <b>{total_brut:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #E74C3C;">💸 Toplam Gerçek Gider: <b>-{total_gider:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #F1C40F; font-size:1.2em">✅ GERÇEK NET KÂR: <b>{total_net:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    # --- GELİŞMİŞ YÖNETİM (YEDEKLEME VE GÜVENLİ SİLME) ---
    st.subheader("🌍 Veri Güvenliği (Can Simidi)")
    
    # EXCEL OLARAK İNDİR BUTONU (YENİ)
    col1, col2 = st.columns(2)
    if not df.empty:
        csv_rez = df.to_csv(index=False).encode('utf-8')
        col1.download_button(label="📥 Rezervasyonları Excel (CSV) İndir", data=csv_rez, file_name=f'rezervasyon_yedek_{today_str}.csv', mime='text/csv', key='dl_rez')
    if not df_gider.empty:
        csv_gid = df_gider.to_csv(index=False).encode('utf-8')
        col2.download_button(label="📥 Giderleri Excel (CSV) İndir", data=csv_gid, file_name=f'gider_yedek_{today_str}.csv', mime='text/csv', key='dl_gid')
        
    st.divider()
    st.subheader("🗑️ Kayıt Silme Paneli")
    st.warning("Dikkat: Buradan silinen veriler geri getirilemez.")
    
    if not df.empty:
        delete_list = df.drop_duplicates(subset=["Ad Soyad", "Toplam"]).copy()
        for idx, row in delete_list.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.write(f"🗑️ {row['Ad Soyad']} ({row['Toplam']} TL)")
            
            # SİLME ONAYI (YENİ)
            if c2.button("Sil", key=f"del_{idx}"): st.session_state[f'confirm_{idx}'] = True
            
            if st.session_state.get(f'confirm_{idx}', False):
                st.error("Emin misiniz?")
                if c3.button("EVET, SİL", key=f"conf_{idx}"):
                    # Kaydı sil
                    df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                    df.to_csv("rez.csv", index=False)
                    del st.session_state[f'confirm_{idx}'] # Onay durumunu sıfırla
                    st.success("Kayıt silindi!")
                    st.rerun()
