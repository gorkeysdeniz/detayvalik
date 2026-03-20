import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. TASARIM VE IPHONE GÖRÜNÜRLÜK AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: white !important; color: #1a1a1a !important; }
    
    /* FORM BAŞLIKLARI (LABEL) VE BUTON FONTU */
    label, .stMarkdown h3, .stMarkdown h2 { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }
    
    /* INPUT KUTULARI VE YAZI RENGİ SİBİT */
    input, select, textarea, [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* KAYDET BUTONU: KOYU VE NET */
    .stButton button {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        height: 3em !important;
        width: 100% !important;
    }

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
    
    /* FİNANS KARTLARI (KDV GÖRÜNÜR) */
    .f-card {
        background: #ffffff !important; padding: 18px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 12px;
        border-left: 8px solid #007BFF; color: #000000 !important;
    }
    .f-card b { color: #000000 !important; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
init_db()
df = pd.read_csv("rez.csv")

# --- 3. ÜST PANEL (YAKLAŞAN REZERVASYON) ---
st.title("🏡 Detayvalık Yönetim")
today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d")
future_rexs = df[df["Tarih"] >= today_str].sort_values(by="Tarih")

if not future_rexs.empty:
    nxt = future_rexs.iloc[0]
    st.markdown(f'<div class="alarm-card">🔔 Sıradaki Misafir: {nxt["Ad Soyad"]} <br> Tarih: {nxt["Tarih"]}</div>', unsafe_allow_html=True)

# --- 4. SEKMELER ---
q_date = st.query_params.get("date", "")
t1, t2, t3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=today_dt.month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Takvim Çizimi
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

    # TAKVİMDEN TIKLANAN TARİH DETAYI
    if q_date:
        detay = df[df["Tarih"] == q_date]
        if not detay.empty:
            d_row = detay.iloc[0]
            st.warning(f"📍 {q_date} : {d_row['Ad Soyad']} adına kayıtlı.")
        else:
            st.success(f"📍 {q_date} tarihi şu an müsait.")

    with st.expander("📝 Yeni Rezervasyon Yap", expanded=True if q_date else False):
        with st.form("r_form"):
            f_tar = st.text_input("Giriş Tarihi", value=q_date)
            f_ad = st.text_input("Müşteri Ad Soyad")
            f_tel = st.text_input("WhatsApp No")
            f_ucr = st.number_input("Gecelik Fiyat", min_value=0)
            f_gc = st.number_input("Kaç Gece?", min_value=1)
            if st.form_submit_button("RESERVASYONU KAYDET"):
                if f_tar and f_ad:
                    start_dt = datetime.strptime(f_tar, "%Y-%m-%d")
                    new_rows = [[(start_dt + timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_ucr, f_gc, "", "Kesin", f_ucr*f_gc] for i in range(int(f_gc))]
                    pd.concat([df, pd.DataFrame(new_rows, columns=df.columns)]).to_csv("rez.csv", index=False)
                    st.rerun()

with t2:
    st.subheader("🔍 Kayıt Sorgulama")
    search = st.text_input("İsim ile ara...", placeholder="Müşteri adı girin")
    
    if not df.empty:
        # Müşteri bazlı gruplama: Giriş-Çıkış hesaplama
        k_df = df.copy()
        k_df['Tarih'] = pd.to_datetime(k_df['Tarih'])
        grouped = k_df.groupby(['Ad Soyad', 'Toplam']).agg(
            Giris=('Tarih', 'min'),
            Cikis=('Tarih', 'max'),
            Gece=('Gece', 'first')
        ).reset_index()
        
        # Filtreleme
        if search:
            grouped = grouped[grouped['Ad Soyad'].str.contains(search, case=False)]
        
        for _, r in grouped.iterrows():
            st.markdown(f"""
            <div class="f-card">
                <b>👤 {r['Ad Soyad']}</b><br>
                📅 {r['Giris'].strftime('%d %b')} - {r['Cikis'].strftime('%d %b')} ({int(r['Gece'])} Gece)<br>
                💰 Toplam Ödeme: {r['Toplam']:,.0f} TL
            </div>
            """, unsafe_allow_html=True)

with t3:
    # --- FİNANSAL ZEKÂ ---
    df_f = df.copy()
    df_f["Tarih"] = pd.to_datetime(df_f["Tarih"])
    
    # Mevcut Ay
    ay_data = df_f[df_f["Tarih"].dt.month == ay_idx].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    brut_ay = ay_data["Toplam"].sum()
    kdv_ay = brut_ay * 0.20
    
    # Genel Toplam
    all_data = df_f.drop_duplicates(subset=["Ad Soyad", "Toplam"])
    total_brut = all_data["Toplam"].sum()
    # Net: %20 KDV, %2 Konaklama, %15 Komisyon/Giderler = Yaklaşık %37 kesinti
    total_net = total_brut * 0.63 
    
    st.subheader(f"📊 {sec_ay} Tablosu")
    st.markdown(f'<div class="f-card">💰 Aylık Brüt: <b>{brut_ay:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #E74C3C;">🧾 Tahmini KDV Payı: <b>-{kdv_ay:,.0f} TL</b></div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🌍 Tüm Zamanlar Genel Toplam")
    st.markdown(f'<div class="f-card" style="border-left-color: #2ECC71;">💵 Toplam Brüt Ciro: <b>{total_brut:,.0f} TL</b></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color: #F1C40F;">✨ TOPLAM NET GELİR: <b>{total_net:,.0f} TL</b></div>', unsafe_allow_html=True)
