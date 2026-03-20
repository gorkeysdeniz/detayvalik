import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse
from io import BytesIO

# --- 1. GÖRÜNÜRLÜK (iOS & BROWSER) ---
st.set_page_config(page_title="Villa Yönetim Paneli", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
    .rez-card { 
        background: #ffffff !important; padding: 15px; border-radius: 12px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 8px solid #2ECC71; margin-bottom: 15px; 
    }
    .wa-button {
        display: block; background-color: #25D366; color: white !important; 
        padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; text-align: center;
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
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

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
    
    # Giriş/Çıkış
    c1, c2 = st.columns(2)
    with c1:
        st.write("### ⬇️ Giriş")
        ins = df[df["Tarih"] == today_str]
        for _, r in ins.iterrows(): st.success(f"👤 {r['Ad Soyad']}")
    with c2:
        st.write("### ⬆️ Çıkış")
        df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
        df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
        outs = df[df["C_str"] == today_str]
        for _, r in outs.iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

    st.divider()
    # Takvim
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

    # Yeni Kayıt
    q_date = st.query_params.get("date", "")
    with st.expander("📝 Rezervasyon Ekle", expanded=True if q_date else False):
        with st.form("kayit_form", clear_on_submit=True):
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
                st.success("Rezervasyon kaydedildi!")
                st.rerun()

with t2:
    st.subheader("🔍 Rezervasyonlar")
    ara = st.text_input("İsim Ara")
    if not df.empty:
        temp = df.copy().fillna("")
        list_df = temp.groupby(["Ad Soyad", "Toplam", "Tel", "Not", "Gece"]).agg(Baslangic=("Tarih", "min")).reset_index()
        if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
        
        for _, r in list_df.iterrows():
            st.markdown(f'<div class="rez-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 {r["Baslangic"]} ({r["Gece"]} Gece)<br>💰 {r["Toplam"]:,} TL</div>', unsafe_allow_html=True)
            if str(r['Tel']).strip():
                mesaj = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz onaylanmıştır.")
                st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={mesaj}" target="_blank" class="wa-button">💬 WhatsApp Mesajı</a>', unsafe_allow_html=True)
            st.divider()

with t3:
    st.subheader("💸 Gider Girişi")
    # clear_on_submit=True sayesinde kaydet deyince form sıfırlanır
    with st.form("gider_f", clear_on_submit=True):
        gt = st.date_input("Tarih", value=datetime.now())
        gk = st.selectbox("Kategori", ["Temizlik", "Elektrik", "Su", "Bahçe Bakımı", "Komisyon", "Diğer"])
        ga = st.text_input("Açıklama", placeholder="Örn: Haziran elektrik faturası")
        gu = st.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("GİDERİ SİSTEME İŞLE"):
            if gu > 0:
                new_g = pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)
                pd.concat([df_gider, new_g], ignore_index=True).to_csv("gider.csv", index=False)
                st.success(f"{ga} gideri başarıyla kaydedildi ve form sıfırlandı!")
                # Sayfayı yenilemeye gerek yok, form zaten temizleniyor.
            else:
                st.error("Lütfen geçerli bir tutar girin.")

with t4:
    st.subheader(f"💰 {sec_ay} Finans Analizi")
    m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
    ciro = m_rez["Toplam"].sum()
    m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]
    top_gider = m_gid["Tutar"].sum()
    kdv = ciro * 0.20
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ciro", f"{ciro:,.0f} TL")
    c2.metric("KDV Payı", f"-{kdv:,.0f} TL")
    c3.metric("Giderler", f"-{top_gider:,.0f} TL")
    st.success(f"AYLIK NET KAZANÇ: {ciro - kdv - top_gider:,.0f} TL")

with t5:
    st.subheader("⚙️ Yönetim ve Raporlama")
    
    # --- AKILLI EXCEL İNDİRME MANTIĞI ---
    if not df.empty:
        # Verileri grup bazlı birleştir (Excel için)
        report_df = df.copy().fillna("")
        report_df['T_dt'] = pd.to_datetime(report_df['Tarih'])
        
        excel_data = report_df.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Not"]).agg(
            Giris_Tarihi=("T_dt", "min"),
            Cikis_Tarihi=("T_dt", "max")
        ).reset_index()
        
        # Sütun sırasını güzelleştir
        excel_data = excel_data[["Ad Soyad", "Giris_Tarihi", "Cikis_Tarihi", "Gece", "Toplam", "Tel", "Not"]]
        
        # Excel'e çevir (CSV formatında ama düzenli)
        csv = excel_data.to_csv(index=False).encode('utf-8-sig') # Excel'de Türkçe karakter için utf-8-sig
        
        st.download_button(
            label="📥 Profesyonel Müşteri Listesini İndir (Excel/CSV)",
            data=csv,
            file_name=f'villa_rapor_{today_str}.csv',
            mime='text/csv'
        )
    
    st.divider()
    st.subheader("🗑️ Kayıt Sil")
    del_list = df.copy().fillna("").groupby(["Ad Soyad", "Toplam"]).agg(Baslangic=("Tarih", "min")).reset_index()
    for i, row in del_list.iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"❌ {row['Ad Soyad']} ({row['Toplam']:,} TL)")
        if c2.button("SİL", key=f"del_{i}"):
            df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
            df.to_csv("rez.csv", index=False)
            st.rerun()
