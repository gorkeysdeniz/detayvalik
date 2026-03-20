import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- AYARLAR ---
st.set_page_config(page_title="Detayvalık Takvim", layout="wide")

# --- VERİ TABANI ---
def load_data():
    f1, f2 = "rezler.csv", "giderler.csv"
    if not os.path.exists(f1): pd.DataFrame(columns=["Tarih","Ad Soyad","İletişim","Günlük Ücret","Gece","Not","Toplam"]).to_csv(f1, index=False)
    if not os.path.exists(f2): pd.DataFrame(columns=["Tarih","Açıklama","Tutar"]).to_csv(f2, index=False)
    return pd.read_csv(f1), pd.read_csv(f2)

df, gider_df = load_data()

st.title("🏡 Detayvalık Takvim")

t1, t2, t3 = st.tabs(["📅 Takvim & Kayıt", "🔍 Sorgula", "📊 Finans"])

# --- TAB 1: TAKVİM ---
with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seç", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        cols = st.columns(7)
        for i, gun in enumerate(hafta):
            if gun != 0:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                dolu = t_str in df["Tarih"].astype(str).values
                label = f"🔴 {gun}" if dolu else f"🟢 {gun}"
                if cols[i].button(label, key=t_str):
                    if dolu:
                        d = df[df["Tarih"].astype(str)==t_str].iloc[0]
                        st.warning(f"👤 {d['Ad Soyad']} | 💰 Toplam: {d['Toplam']} TL\n\n🌙 {d['Gece']} Gece | 📝 {d['Not']}")
                    else: st.session_state.t = t_str

    with st.expander("➕ Yeni Kayıt", expanded=True):
        with st.form("f", clear_on_submit=True):
            f_t = st.text_input("Giriş Tarihi", value=st.session_state.get('t',''))
            f_n = st.text_input("Ad Soyad")
            f_c = st.text_input("İletişim")
            f_u = st.number_input("Günlük Ücret", min_value=0)
            f_g = st.number_input("Gece", min_value=1)
            f_nt = st.text_area("Not")
            if st.form_submit_button("Kaydet"):
                start = datetime.strptime(f_t, "%Y-%m-%d")
                rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"),f_n,f_c,f_u,f_g,f_nt,f_u*f_g] for i in range(int(f_g))]
                pd.concat([df, pd.DataFrame(rows, columns=df.columns)]).to_csv("rezler.csv", index=False)
                st.success("Kayıt Başarılı!"); st.rerun()

# --- TAB 2: SORGULA ---
with t2:
    ara = st.text_input("İsim Ara:").lower()
    if ara:
        res = df[df["Ad Soyad"].str.lower().str.contains(ara, na=False)].drop_duplicates(subset=["Ad Soyad","Toplam"])
        st.table(res[["Ad Soyad","İletişim","Gece","Toplam","Not"]])

# --- TAB 3: FİNANS ---
with t3:
    f_ay = st.selectbox("Dönem", aylar, key="fin")
    m_no = aylar.index(f_ay)+1
    temp_df = df.copy(); temp_df["Tarih"] = pd.to_datetime(temp_df["Tarih"])
    brut = temp_df[temp_df["Tarih"].dt.month==m_no].drop_duplicates(subset=["Ad Soyad","Toplam"])["Toplam"].sum()
    temp_g = gider_df.copy(); temp_g["Tarih"] = pd.to_datetime(temp_g["Tarih"])
    gider = temp_g[temp_g["Tarih"].dt.month==m_no]["Tutar"].sum()
    kdv = brut * 0.10
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Brüt", f"{brut} TL")
    c2.metric("Gider", f"-{gider} TL")
    c3.metric("KDV (%10)", f"-{kdv} TL")
    c4.metric("NET KAR", f"{brut-gider-kdv} TL")
    
    with st.expander("💸 Gider Ekle"):
        with st.form("g"):
            gt = st.date_input("Tarih"); ga = st.text_input("Açıklama"); gu = st.number_input("Tutar")
            if st.form_submit_button("Gideri Kaydet"):
                pd.concat([gider_df, pd.DataFrame([[str(gt),ga,gu]], columns=gider_df.columns)]).to_csv("giderler.csv", index=False)
                st.success("Gider Eklendi!"); st.rerun()
