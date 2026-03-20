import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. ZIRHLI GÖRÜNÜRLÜK AYARLARI ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    h1, h2, h3, h4, label, p, span, div, table, td, th { 
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important; 
    }
    input, select, textarea, [data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #f0f2f6 !important;
        -webkit-text-fill-color: #000000 !important;
    }
    .stButton button { background-color: #1a1a1a !important; color: #ffffff !important; border-radius: 12px !important; }
    .alarm-card {
        background: linear-gradient(135deg, #FF9A8B 0%, #FF6A88 55%, #FF99AC 100%);
        color: white !important; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;
    }
    .f-card {
        background: #ffffff !important; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 6px solid #007BFF; margin-bottom: 10px;
    }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 10px 0; border-radius: 10px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; } .opsiyon { background: #F1C40F !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI SÜTUN SABİTLEME ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    df = pd.read_csv(file)
    if list(df.columns) != cols: # Sütun hatası varsa düzelt
        df = df.reindex(columns=cols, fill_value="")
        df.to_csv(file, index=False)
    return df

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)

# --- 3. ÜST PANEL & BİLGİ SORGULAMA ---
st.title("🏡 Villa Yönetim Paneli")
today_str = datetime.now().strftime("%Y-%m-%d")

# Yaklaşan Rezervasyon
future = df[df["Tarih"] >= today_str].sort_values("Tarih")
if not future.empty:
    nxt = future.iloc[0]
    st.markdown(f'<div class="alarm-card">🔔 Sıradaki: {nxt["Ad Soyad"]} ({nxt["Tarih"]})</div>', unsafe_allow_html=True)

# --- 4. SEKMELER ---
q_date = st.query_params.get("date", "")
t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # GİRİŞ/ÇIKIŞ TAKİBİ (DÜZELTİLDİ)
    c_in, c_out = st.columns(2)
    with c_in:
        st.markdown("### ⬇️ Girişler")
        ins = df[df["Tarih"] == today_str]
        if not ins.empty:
            for _, r in ins.iterrows(): st.write(f"✅ {r['Ad Soyad']}")
        else: st.write("Yok")
    with c_out:
        st.markdown("### ⬆️ Çıkışlar")
        # Basit çıkış hesabı: Tarih + Gece
        df_tmp = df.copy()
        df_tmp['Tarih_dt'] = pd.to_datetime(df_tmp['Tarih'])
        df_tmp['Cikis'] = df_tmp.apply(lambda x: (x['Tarih_dt'] + timedelta(days=int(x['Gece']))).strftime("%Y-%m-%d"), axis=1)
        outs = df_tmp[df_tmp["Cikis"] == today_str]
        if not outs.empty:
            for _, r in outs.iterrows(): st.write(f"🔑 {r['Ad Soyad']}")
        else: st.write("Yok")

    # TAKVİM & TIKLAMA BİLGİSİ
    st.divider()
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_str = f"2026-{ay_idx:02d}-{day:02d}"
                r_found = df[df["Tarih"] == d_str]
                cl = "bos"
                if not r_found.empty: cl = "dolu"
                cal_html += f'<td><a href="?date={d_str}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    # Tıklanan Tarih Bilgisi (DÜZELTİLDİ)
    if q_date:
        info = df[df["Tarih"] == q_date]
        if not info.empty:
            st.info(f"📍 {q_date}: {info.iloc[0]['Ad Soyad']} burada.")
        else: st.success(f"📍 {q_date} Müsait.")

    with st.expander("📝 Yeni Kayıt", expanded=True if q_date else False):
        with st.form("new_r"):
            f_tar = st.text_input("Giriş Tarihi", value=q_date)
            f_ad = st.text_input("İsim")
            f_tel = st.text_input("WhatsApp (905...)")
            f_ucr = st.number_input("Fiyat", min_value=0)
            f_gc = st.number_input("Gece", min_value=1)
            f_not = st.text_area("Notlar")
            if st.form_submit_button("KAYDET"):
                s_dt = datetime.strptime(f_tar, "%Y-%m-%d")
                rows = [[(s_dt+timedelta(days=i)).strftime("%Y-%m-%d"), f_ad, f_tel, f_ucr, f_gc, f_not, "Kesin", f_ucr*f_gc] for i in range(int(f_gc))]
                pd.concat([df, pd.DataFrame(rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                st.rerun()

with t2:
    st.subheader("🔍 Rezervasyonlar & WhatsApp")
    search = st.text_input("İsimle Ara")
    # Gruplayarak göster (WhatsApp burada çıkacak)
    if not df.empty:
        g_df = df.groupby(["Ad Soyad", "Toplam", "Tel", "Not", "Gece"]).agg(Giris=("Tarih", "min")).reset_index()
        if search: g_df = g_df[g_df["Ad Soyad"].str.contains(search, case=False)]
        
        for _, r in g_df.iterrows():
            st.markdown(f'<div class="f-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 Başlangıç: {r["Giris"]} ({r["Gece"]} Gece)<br>💰 Tutar: {r["Toplam"]} TL<br>📝 {r["Not"]}</div>', unsafe_allow_html=True)
            if r["Tel"]:
                msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz onaylanmıştır.")
                st.markdown(f' <a href="https://wa.me/{r["Tel"]}?text={msg}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:8px; border-radius:5px; cursor:pointer;">💬 WhatsApp Mesajı Gönder</button></a>', unsafe_allow_html=True)
            st.divider()

with t3:
    st.subheader("💸 Gider Girişi")
    with st.form("g_form"):
        g_t = st.date_input("Tarih")
        g_k = st.selectbox("Tür", ["Temizlik", "Elektrik", "Su", "Airbnb Komisyon", "Diğer"])
        g_a = st.text_input("Açıklama")
        g_u = st.number_input("Tutar", min_value=0.0)
        if st.form_submit_button("GİDERİ İŞLE"):
            new_g = pd.DataFrame([[g_t.strftime("%Y-%m-%d"), g_k, g_a, g_u]], columns=GID_COLS)
            pd.concat([df_gider, new_g], ignore_index=True).to_csv("gider.csv", index=False)
            st.rerun()

with t4:
    # FİNANS & KDV (DÜZELTİLDİ)
    st.subheader(f"💰 {sec_ay} Mali Tablo")
    m_rez = df[pd.to_datetime(df["Tarih"]).dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"]).dt.month == ay_idx]
    
    gelir = m_rez["Toplam"].sum()
    gider = m_gid["Tutar"].sum()
    kdv = gelir * 0.20 # %20 KDV eklendi
    
    st.metric("Toplam Ciro", f"{gelir:,.0f} TL")
    st.metric("KDV Payı (%20)", f"-{kdv:,.0f} TL", delta_color="inverse")
    st.metric("Toplam Gider", f"-{gider:,.0f} TL")
    st.markdown(f'<div class="f-card" style="border-left-color:#2ECC71;">💰 <b>NET KAZANÇ: {gelir - kdv - gider:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    st.subheader("⚙️ Veri Yönetimi")
    if st.button("📥 Rezervasyonları İndir (CSV)"):
        st.download_button("Dosyayı Al", df.to_csv(index=False), "rez_yedek.csv")
    if st.button("🗑️ TÜM VERİLERİ SIFIRLA (DİKKAT)"):
        if st.checkbox("Eminim, her şeyi sil"):
            pd.DataFrame(columns=REZ_COLS).to_csv("rez.csv", index=False)
            st.rerun()
