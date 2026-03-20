import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- 1. SAYFA AYARLARI VE TASARIM (CSS) ---
st.set_page_config(page_title="Detayvalık VIP v3.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 45px;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #ddd;
    }
    /* Takvim Hücresi Tasarımı */
    div.stButton > button:first-child { background-color: white; color: #333; }
    /* Durum Renkleri */
    .dolu { background-color: #ff4b4b !important; color: white !important; }
    .opsiyon { background-color: #ffc107 !important; color: black !important; }
    .bos { background-color: #28a745 !important; color: white !important; }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
    if not os.path.exists("gider.csv"):
        pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"]).to_csv("gider.csv", index=False)

init_db()
df = pd.read_csv("rez.csv")
gdf = pd.read_csv("gider.csv")

# --- 3. ANA BAŞLIK ---
st.title("🏙️ Detayvalık VIP Yönetim")
st.caption("Profesyonel Villa İşletme Paneli")

tab1, tab2, tab3 = st.tabs(["📅 TAKVİM", "🔍 REZERVASYON REHBERİ", "📊 FİNANSAL ANALİZ"])

# --- TAB 1: GERÇEK TAKVİM GÖRÜNÜMÜ ---
with tab1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    c1, c2 = st.columns([1, 4])
    sec_ay = c1.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.write(f"### {sec_ay} 2026")
    
    # Hafta Başlıkları (Sabit 7 Sütun)
    h_cols = st.columns(7)
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    for i, g in enumerate(gunler):
        h_cols[i].markdown(f"<center><b>{g}</b></center>", unsafe_allow_html=True)

    # Takvim Mantığı
    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        cols = st.columns(7)
        for i, gun in enumerate(hafta):
            if gun == 0:
                cols[i].write("") # Ay dışı günler boş kalsın
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                
                # Doluluk Kontrolü
                kayit = df[df["Tarih"] == t_str]
                css_class = "bos"
                if not kayit.empty:
                    durum = kayit.iloc[0]["Durum"]
                    css_class = "dolu" if durum == "Kesin" else "opsiyon"
                
                # Buton Oluşturma
                if cols[i].button(f"{gun}", key=t_str, help=f"{t_str} Detayı"):
                    if not kayit.empty:
                        d = kayit.iloc[0]
                        st.info(f"👤 **{d['Ad Soyad']}** ({d['Durum']})\n\n📞 {d['Tel']} | 💰 {d['Toplam']} TL\n\n📝 {d['Not']}")
                    else:
                        st.session_state.t_sec = t_str

    st.divider()
    
    # YENİ KAYIT FORMU
    with st.expander("➕ Yeni Rezervasyon Ekle", expanded=False):
        with st.form("rez_form"):
            f1, f2, f3 = st.columns(3)
            t_input = f1.text_input("Giriş Tarihi", value=st.session_state.get('t_sec',''))
            ad_input = f2.text_input("Müşteri Ad Soyad")
            tel_input = f3.text_input("Telefon")
            
            u_input = f1.number_input("Günlük Ücret", min_value=0)
            g_input = f2.number_input("Gece Sayısı", min_value=1)
            d_input = f3.selectbox("Durum", ["Kesin", "Opsiyonel"])
            not_input = st.text_area("Notlar")
            
            if st.form_submit_button("Sisteme İşle"):
                try:
                    start = datetime.strptime(t_input, "%Y-%m-%d")
                    new_rows = []
                    for d in range(int(g_input)):
                        target_t = (start + timedelta(days=d)).strftime("%Y-%m-%d")
                        new_rows.append([target_t, ad_input, tel_input, u_input, g_input, not_input, d_input, u_input*g_input])
                    
                    new_df = pd.DataFrame(new_rows, columns=df.columns)
                    pd.concat([df, new_df]).to_csv("rez.csv", index=False)
                    st.success("Kayıt Başarılı!"); st.rerun()
                except: st.error("Tarih formatı hatalı!")

# --- TAB 2: AKILLI SORGULAMA ---
with tab2:
    st.subheader("🔍 Rezervasyon Rehberi")
    ara = st.text_input("İsim ile Filtrele (Tüm listeyi görmek için boş bırakın):").lower()
    
    # Arama Boşsa Hepsi, Doluysa Filtreli
    display_df = df.drop_duplicates(subset=["Ad Soyad", "Toplam", "Gece"]).copy()
    if ara:
        display_df = display_df[display_df["Ad Soyad"].str.lower().str.contains(ara, na=False)]
    
    st.dataframe(display_df[["Tarih", "Ad Soyad", "Tel", "Gece", "Durum", "Toplam", "Not"]], use_container_width=True)
    
    # WhatsApp Fiş Özelliği
    if not display_df.empty and ara:
        st.write("### 📱 WhatsApp Bilgi Notu")
        m = display_df.iloc[0]
        fis_metni = f"*Detayvalık Rezervasyon Bilgisi*\n\nSayın {m['Ad Soyad']},\n{m['Tarih']} girişli, {m['Gece']} gecelik kaydınız *{m['Durum']}* olarak alınmıştır.\nToplam Tutar: {m['Toplam']} TL\nİyi tatiller dileriz."
        st.code(fis_metni)
        st.caption("Yukarıdaki metni kopyalayıp müşteriye gönderebilirsiniz.")

# --- TAB 3: FİNANSAL ANALİZ ---
with tab3:
    st.subheader("📊 Gelir / Gider Analizi")
    f_ay = st.selectbox("Dönem", aylar, key="fin_ay", index=datetime.now().month-1)
    f_no = aylar.index(f_ay) + 1
    
    # Hesaplamalar
    temp_rez = df.copy(); temp_rez["Tarih"] = pd.to_datetime(temp_rez["Tarih"])
    aylik_brut = temp_rez[temp_rez["Tarih"].dt.month == f_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])["Toplam"].sum()
    
    temp_gid = gdf.copy(); temp_gid["Tarih"] = pd.to_datetime(temp_gid["Tarih"])
    aylik_gider = temp_gid[temp_gid["Tarih"].dt.month == f_no]["Tutar"].sum()
    
    kdv = aylik_brut * 0.10
    net = aylik_brut - aylik_gider - kdv
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Brüt Gelir", f"{aylik_brut:,.0f} TL")
    c2.metric("Toplam Gider", f"-{aylik_gider:,.0f} TL")
    c3.metric("KDV (%10)", f"-{kdv:,.0f} TL")
    c4.metric("NET KAR", f"{net:,.0f} TL")
    
    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.write("### 💸 Gider Ekle")
        with st.form("gider_form"):
            gt = st.date_input("Tarih")
            gk = st.selectbox("Kategori", ["Temizlik", "Faturalar", "Bahçe/Havuz", "Tamirat", "Diğer"])
            ga = st.text_input("Açıklama")
            gu = st.number_input("Tutar (TL)", min_value=0)
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([gdf, pd.DataFrame([[str(gt),gk,ga,gu]], columns=gdf.columns)]).to_csv("gider.csv", index=False)
                st.success("Gider işlendi!"); st.rerun()
    with col_r:
        st.write("### 📂 Kategori Bazlı Giderler")
        if not temp_gid[temp_gid["Tarih"].dt.month == f_no].empty:
            pasta = temp_gid[temp_gid["Tarih"].dt.month == f_no].groupby("Kategori")["Tutar"].sum()
            st.bar_chart(pasta)
        else: st.info("Bu ay için gider kaydı bulunamadı.")
