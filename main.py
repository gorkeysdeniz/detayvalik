import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. TASARIM VE KESİN GÖRÜNÜRLÜK AYARLARI (ZIRHLI CSS) ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="centered")

# Bu CSS, iOS Safari'nin aydınlık/karanlık mod ayarlarını ezer ve yazıları SİMSİYAH yapar.
st.markdown("""
    <style>
    /* Global Ayarlar */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    /* TÜM YAZI TİPLERİ VE BAŞLIKLAR (KESİN SİYAH) */
    h1, h2, h3, h4, h5, h6, p, span, label, li, div, table, thead, tbody, tr, th, td { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important; 
    }
    
    /* INPUT KUTULARI (ARKA PLAN GRİ, YAZI SİYAH) */
    input, select, textarea, [data-baseweb="input"] input, [data-baseweb="select"] div {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 10px !important;
    }
    /* Placeholder (Soluk Yazı) Fix */
    input::placeholder, textarea::placeholder { color: #666666 !important; -webkit-text-fill-color: #666666 !important; }

    /* GENEL BUTON STİLİ (KOYU) */
    .stButton button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    
    /* ÖZEL RENKLİ BUTONLAR */
    .wa-btn button { background-color: #25D366 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; border: none !important; }
    .dl-btn button { background-color: #007BFF !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; border: none !important; }
    .del-btn button { background-color: #E74C3C !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; border: none !important; }

    /* ALARM KARTI VE TAKVİM */
    .alarm-card {
        background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%);
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
        padding: 20px; border-radius: 15px; margin-bottom: 20px; text-align: center; font-weight: bold;
    }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; -webkit-text-fill-color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } 
    .dolu { background: #E74C3C !important; } 
    .opsiyon { background: #F1C40F !important; color: #1A1A1A !important; -webkit-text-fill-color: #1A1A1A !important; }
    
    /* KART TASARIMLARI (SİYAH YAZILI) */
    .f-card, .rez-card {
        background: #ffffff !important; padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 12px;
        border-left: 8px solid #007BFF; color: #000000 !important; -webkit-text-fill-color: #000000 !important;
    }
    .rez-card { border-left-color: #2ECC71; } /* Rezervasyon kartı yeşil şerit */
    
    /* GİRİŞ/ÇIKIŞ LİSTESİ SİYAH FONT */
    .io-list { background: #f8f9fa; padding: 15px; border-radius: 12px; margin-bottom: 15px; border: 1px solid #ddd; color: #000000 !important; }
    .io-item { border-bottom: 1px solid #eee; padding: 8px 0; color: #000000 !important; font-weight: 500 !important; }
    .io-item strong { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ VE TAMİR ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_and_fix_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    try: current_df = pd.read_csv(file)
    except: current_df = pd.DataFrame(columns=cols)
    if list(current_df.columns) != cols:
        for col in cols:
            if col not in current_df.columns: current_df[col] = 0 if col in ["Toplam", "Tutar", "Ucret", "Gece"] else ""
        current_df = current_df[cols].to_csv(file, index=False)
    return pd.read_csv(file)

df = load_and_fix_data("rez.csv", REZ_COLS)
df_gider = load_and_fix_data("gider.csv", GID_COLS)

# --- 3. ÜST PANEL ---
st.title("🏡 Villa Yönetim Paneli")
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
# "Ad Soyad" sütunundaki NaN değerleri boş string ile değiştir (Arama hatası fix 1)
df['Ad Soyad'] = df['Ad Soyad'].fillna('')
future_rexs = df[df["Tarih"] >= today_str].sort_values(by="Tarih")

if not future_rexs.empty:
    nxt = future_rexs.iloc[0]
    st.markdown(f'<div class="alarm-card">🔔 Sıradaki: {nxt["Ad Soyad"]} ({nxt["Tarih"]})</div>', unsafe_allow_html=True)

# --- 4. SEKMELER ---
q_date = st.query_params.get("date", "")
t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Dönem", aylar, index=today_dt.month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    st.subheader("📋 Bugünün Hareketleri")
    
    # Girişler
    st.markdown('<div class="io-list"><strong>⬇️ Bugün Girişler:</strong>', unsafe_allow_html=True)
    in_today = df[df["Tarih"] == today_str]
    if not in_today.empty:
        for _, r in in_today.iterrows(): st.markdown(f'<div class="io-item">👤 {r["Ad Soyad"]} ({r["Gece"]} Gece)</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="io-item"><em>Bugün giriş yok.</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Çıkışlar
    st.markdown('<div class="io-list"><strong>⬆️ Bugün Çıkışlar:</strong>', unsafe_allow_html=True)
    out_list = []
    if not df.empty:
        temp_df = df.copy()
        temp_df['Tarih'] = pd.to_datetime(temp_df['Tarih'])
        # NaN Gece değerlerini 0 yap (Hata fix 2)
        temp_df['Gece'] = pd.to_numeric(temp_df['Gece'], errors='coerce').fillna(0).astype(int)
        temp_df['Cikis'] = temp_df['Tarih'] + pd.to_timedelta(temp_df['Gece'], unit='D')
        out_today = temp_df[temp_df["Cikis"].dt.strftime("%Y-%m-%d") == today_str]
        out_list = out_today['Ad Soyad'].unique()

    if len(out_list) > 0:
        for name in out_list: st.markdown(f'<div class="io-item">👤 {name} (Anahtar Teslim)</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="io-item"><em>Bugün çıkış yok.</em></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    # Takvim
    st.subheader(f"📅 {sec_ay} 2026")
    cal_html = '<table class="modern-table"><thead><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr></thead><tbody>'
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

    with st.expander("📝 Rezervasyon İşle", expanded=True if q_date else False):
        with st.form("r_form"):
            f_tar = st.text_input("Giriş (YYYY-AA-GG)", value=q_date)
            f_ad = st.text_input("Müşteri Ad Soyad")
            f_tel = st.text_input("WhatsApp (90...)")
            c1, c2 = st.columns(2)
            f_ucr = c1.number_input("Gecelik Fiyat", min_value=0)
            f_gc = c2.number_input("Gece", min_value=1)
            f_not = st.text_area("Notlar")
            if st.form_submit_button("KAYDET"):
                if f_tar and f_ad:
                    start_dt = datetime.strptime(f_tar, "%Y-%m-%d")
                    new_data = [[(start_dt + timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_ucr, f_gc, f_not, "Kesin", f_ucr*f_gc] for i in range(int(f_gc))]
                    pd.concat([df, pd.DataFrame(new_data, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                    st.rerun()

with t2:
    # --- KESİN ÇÖZÜM: KAYITLAR VE ARAMA SEKME ---
    st.subheader("🔍 Rezervasyon Kayıtları")
    # Placeholder yazı rengini de siyaha çektik (Zırhlı CSS sayesinde okunur)
    search = st.text_input("İsim ile ara...", placeholder="Müşteri adı girin")
    
    if not df.empty:
        # Arama ve Gruplama Mantığı (Otomatik Liste Fix 3)
        k_df = df.copy()
        k_df['Ad Soyad'] = k_df['Ad Soyad'].fillna('') # NaN Temizliği
        
        # 1. Müşteri bazlı grupla ve Giriş/Çıkış hesapla
        k_df['Tarih_dt'] = pd.to_datetime(k_df['Tarih'])
        k_df['Gece_int'] = pd.to_numeric(k_df['Gece'], errors='coerce').fillna(0).astype(int)
        
        # Müşteri adı, Toplam ve Not'a göre grupla (Aynı rezervasyonu birleştir)
        grouped = k_df.groupby(['Ad Soyad', 'Toplam', 'Tel', 'Not']).agg(
            Giris=('Tarih_dt', 'min'),
            Cikis=('Tarih_dt', 'max')
        ).reset_index()
        
        # Çıkış tarihini doğru hesapla (Son giriş günü + Gece Sayısı yerine, grubun max tarihi daha güvenli)
        
        # 2. Arama Filtresi (Boşsa tüm listeyi gösterir - SENİN İSTEDİĞİN)
        if search:
            # İsmin içinde arama yap (case-insensitive)
            grouped = grouped[grouped['Ad Soyad'].str.contains(search, case=False)]
        
        # 3. Listeleme (Arama yapılmasa da otomatik gelir)
        st.write(f"Toplam {len(grouped)} rezervasyon bulundu.")
        for _, r in grouped.iterrows():
            st.markdown(f"""
            <div class="rez-card">
                <b>👤 {r['Ad Soyad']}</b><br>
                📅 {r['Giris'].strftime('%d %b')} - {r['Cikis'].strftime('%d %b %Y')}<br>
                Gece Sayısı: {int(r['Cikis'].day - r['Giris'].day)} <br> 💰 Toplam Tutar: {r['Toplam']:,.0f} TL<br>
                📝 Not: <em>{r['Not'] if r['Not'] else 'Not yok.'}</em>
            </div>
            """, unsafe_allow_html=True)
            
            # WhatsApp Onay Butonu
            if r['Tel']:
                msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, Detayvalık'taki rezervasyonunuz onaylanmıştır. Giriş: {r['Giris'].strftime('%d %B')}. Görüşmek üzere!")
                wa_url = f"https://wa.me/{r['Tel']}?text={msg}"
                st.markdown(f'<div class="wa-btn"><a href="{wa_url}" target="_blank"><button>💬 WhatsApp Onayı</button></a></div>', unsafe_allow_html=True)
            st.divider()
    else:
        st.info("Henüz rezervasyon kaydı bulunmuyor.")

with t3:
    # --- GİDERLER (SİYAH YAZILI) ---
    st.subheader("💸 Gider Girişi")
    with st.form("gider_form"):
        g_tar = st.date_input("Tarih", value=today_dt)
        g_kat = st.selectbox("Kategori", ["Temizlik", "Elektrik", "Su", "Airbnb Komisyon", "Bahçe Bakımı", "Vergi", "Diğer"])
        g_aci = st.text_input("Açıklama")
        g_tut = st.number_input("Tutar (TL)", min_value=0.0)
        if st.form_submit_button("KAYDET"):
            new_g = pd.DataFrame([[g_tar.strftime("%Y-%m-%d"), g_kat, g_aci, g_tut]], columns=GID_COLS)
            pd.concat([df_gider, new_g], ignore_index=True).to_csv("gider.csv", index=False)
            st.rerun()
            
    st.divider()
    if not df_gider.empty:
        st.dataframe(df_gider.sort_values(by="Tarih", ascending=False), use_container_width=True)

with t4:
    # --- FİNANS (KESİN SİYAH) ---
    df_f = df.copy()
    df_f["Tarih"] = pd.to_datetime(df_f["Tarih"])
    # Ay verisi
    ay_data = df_f[df_f["Tarih"].dt.month == ay_idx].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut_ay = ay_data["Toplam"].sum()
    
    # Gider verisi
    df_g_f = df_gider.copy()
    df_g_f["Tarih"] = pd.to_datetime(df_g_f["Tarih"])
    ay_gider_data = df_g_f[df_g_f["Tarih"].dt.month == ay_idx]
    gider_ay = ay_gider_data["Tutar"].sum()
    
    # Genel
    all_data = df_f.drop_duplicates(subset=["Ad Soyad", "Toplam"])
    total_brut = all_data["Toplam"].sum()
    total_gider = df_gider["Tutar"].sum()
    total_net = (total_brut * 0.78) - total_gider 
    
    st.subheader(f"📊 {sec_ay} Özeti")
    c1, c2, c3 = st.columns(3)
    # Metric yazıları da CSS sayesinde siyah
    c1.metric("Brüt Gelir", f"{brut_ay:,.0f} TL")
    c2.metric("Toplam Gider", f"-{gider_ay:,.0f} TL")
    c3.metric("Tahmini Net", f"{(brut_ay*0.78)-gider_ay:,.0f} TL")
    
    st.divider()
    st.subheader("🌍 Genel Toplam")
    st.markdown(f'<div class="f-card">💰 Toplam Brüt: <b>{total_brut:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #E74C3C;">💸 Toplam Gider: <b>-{total_gider:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #F1C40F;">✅ GERÇEK NET: <b>{total_net:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    # --- YÖNETİM ---
    st.subheader("Yedekleme ve Silme")
    
    # Yedekleme
    c1, c2 = st.columns(2)
    if not df.empty:
        col1_csv = df.to_csv(index=False).encode('utf-8')
        c1.download_button("📥 Rezervasyon Yedek (CSV)", data=col1_csv, file_name=f'rez_yedek_{today_str}.csv', mime='text/csv')
    if not df_gider.empty:
        col2_csv = df_gider.to_csv(index=False).encode('utf-8')
        c2.download_button("📥 Gider Yedek (CSV)", data=col2_csv, file_name=f'gider_yedek_{today_str}.csv', mime='text/csv')
        
    st.divider()
    st.subheader("🗑️ Kayıt Sil")
    if not df.empty:
        # Tekilleştirilmiş liste (Müşteri bazlı silme)
        del_df = df.drop_duplicates(subset=["Ad Soyad", "Toplam"]).copy()
        for idx, row in del_df.iterrows():
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.write(f"🗑️ {row['Ad Soyad']} ({row['Toplam']} TL)")
            if c2.button("Sil", key=f"del_{idx}"): st.session_state[f'c_{idx}'] = True
            if st.session_state.get(f'c_{idx}', False):
                st.error("Emin misiniz?")
                if c3.button("EVET", key=f"y_{idx}"):
                    df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                    df.to_csv("rez.csv", index=False)
                    del st.session_state[f'c_{idx}']
                    st.rerun()
