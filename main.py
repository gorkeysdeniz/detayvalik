import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. GÖRÜNÜRLÜK VE STİL (iOS FIX) ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
    input, select, textarea { color: #000000 !important; background-color: #f0f2f6 !important; }
    .rez-card { 
        background: #ffffff !important; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 10px solid #2ECC71; margin-bottom: 20px; 
    }
    .wa-button {
        display: inline-block; background-color: #25D366; color: white !important; 
        padding: 10px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; width: 100%;
    }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 10px 0; border-radius: 10px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÜKLEME ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    data = pd.read_csv(file)
    return data.reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 3. ANA PANEL ---
st.title("🏡 Villa Yönetim Paneli")

t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    # Giriş/Çıkış Takibi
    c1, c2 = st.columns(2)
    with c1:
        st.write("### ⬇️ Bugün Giriş")
        ins = df[df["Tarih"] == today_str]
        if not ins.empty:
            for _, r in ins.iterrows(): st.success(f"👤 {r['Ad Soyad']}")
        else: st.write("Giriş yok")
    with c2:
        st.write("### ⬆️ Bugün Çıkış")
        # Çıkış hesabı (Tarih + Gece)
        df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
        df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
        outs = df[df["C_str"] == today_str]
        if not outs.empty:
            for _, r in outs.iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")
        else: st.write("Çıkış yok")

    st.divider()
    # Takvim Grid
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

    # Yeni Kayıt Formu
    q_date = st.query_params.get("date", "")
    with st.expander("📝 Yeni Rezervasyon Ekle", expanded=True if q_date else False):
        with st.form("kayit_form"):
            f_t = st.text_input("Giriş Tarihi", value=q_date)
            f_a = st.text_input("Müşteri Ad Soyad")
            f_p = st.text_input("Telefon (905...)")
            f_f = st.number_input("Gecelik Fiyat", min_value=0)
            f_g = st.number_input("Gece Sayısı", min_value=1)
            f_n = st.text_area("Notlar")
            if st.form_submit_button("SİSTEME KAYDET"):
                start = datetime.strptime(f_t, "%Y-%m-%d")
                new_rows = [[(start + timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, f_n, "Kesin", f_f*f_g] for i in range(int(f_g))]
                pd.concat([df[REZ_COLS], pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                st.rerun()

with t2:
    # --- WHATSAPP VE KAYITLAR TAMİRİ ---
    st.subheader("🔍 Rezervasyon Kayıtları")
    ara = st.text_input("İsimle Filtrele (Boş bırakırsanız hepsi listelenir)")
    
    if not df.empty:
        # Veriyi grupla (Aynı rezervasyonu tek kartta göster)
        # Sütunları temizle (NaN hatası önleyici)
        temp = df.copy().fillna("")
        # Tekil rezervasyonları bul (Ad ve Toplam Tutar kombinasyonu ile)
        list_df = temp.groupby(["Ad Soyad", "Toplam", "Tel", "Not", "Gece"]).agg(Baslangic=("Tarih", "min")).reset_index()
        
        if ara:
            list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
        
        st.write(f"Toplam {len(list_df)} kayıt bulundu.")
        
        for _, r in list_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="rez-card">
                    <div style="font-size:1.2em; margin-bottom:5px;">👤 <b>{r['Ad Soyad']}</b></div>
                    📅 <b>Giriş:</b> {r['Baslangic']} | <b>Gece:</b> {r['Gece']}<br>
                    💰 <b>Toplam:</b> {r['Toplam']:,} TL<br>
                    📝 <b>Not:</b> {r['Not'] if r['Not'] else "-"}<br><br>
                </div>
                """, unsafe_allow_html=True)
                
                # WhatsApp Butonu
                if str(r['Tel']).strip():
                    tel_no = str(r['Tel']).replace(" ", "").replace("+", "")
                    mesaj = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz onaylanmıştır. Giriş tarihiniz: {r['Baslangic']}. Görüşmek üzere!")
                    wa_link = f"https://wa.me/{tel_no}?text={mesaj}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-button">💬 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Bu kayıt için telefon numarası girilmemiş.")
                st.divider()
    else:
        st.info("Henüz hiç kayıt yok.")

with t3:
    st.subheader("💸 Gider Girişi")
    with st.form("gider_f"):
        gt = st.date_input("Gider Tarihi")
        gk = st.selectbox("Kategori", ["Temizlik", "Elektrik", "Su", "Komisyon", "Diğer"])
        ga = st.text_input("Açıklama")
        gu = st.number_input("Tutar", min_value=0.0)
        if st.form_submit_button("Gideri Kaydet"):
            new_g = pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)
            pd.concat([df_gider, new_g], ignore_index=True).to_csv("gider.csv", index=False)
            st.rerun()

with t4:
    # FİNANS - KDV DAHİL
    st.subheader(f"💰 {sec_ay} Mali Durum")
    # Bu ayın gelirleri
    m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_rez["Toplam"].sum()
    # Bu ayın giderleri
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]
    top_gider = m_gid["Tutar"].sum()
    
    kdv = ciro * 0.20 # %20 KDV
    net = ciro - kdv - top_gider
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Ciro", f"{ciro:,.0f} TL")
    c2.metric("KDV (%20)", f"-{kdv:,.0f} TL")
    c3.metric("Giderler", f"-{top_gider:,.0f} TL")
    st.markdown(f'<div class="rez-card" style="border-left-color:#007BFF;">✅ <b>AYLIK NET KAZANÇ: {net:,.0f} TL</b></div>', unsafe_allow_html=True)

with t5:
    st.subheader("⚙️ Yönetim")
    if st.button("📥 Rezervasyon Yedeği İndir"):
        st.download_button("Dosyayı İndir", df.to_csv(index=False), "yedek.csv", "text/csv")
    if st.button("🗑️ TÜM KAYITLARI SİL"):
        if st.checkbox("Evet, her şeyi silmek istiyorum"):
            pd.DataFrame(columns=REZ_COLS).to_csv("rez.csv", index=False)
            st.rerun()
