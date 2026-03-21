import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. AYARLAR ---
st.set_page_config(page_title="Villa Yönetim v42.3", layout="wide", page_icon="💰")

# Vergi Parametreleri
KDV_ORANI = 0.20
TURIZM_PAYI = 0.02

# --- 2. VERİ YÖNETİMİ ---
def load_data():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih", "Misafir", "Gelir", "Gece", "Kanal"]).to_csv("rez.csv", index=False)
    return pd.read_csv("rez.csv")

df = load_data()

# --- 3. ARAYÜZ ---
st.title("💰 Detayvalık Finansal Yönetim v42.3")

tab1, tab2, tab3 = st.tabs(["📊 Finansal Özet", "📝 Yeni Kayıt", "📋 Kayıt Listesi"])

# --- TAB 1: FİNANSAL ÖZET ---
with tab1:
    if not df.empty:
        brut_toplam = df["Gelir"].sum()
        kdv_tutar = brut_toplam * KDV_ORANI
        turizm_tutar = brut_toplam * TURIZM_PAYI
        net_kar = brut_toplam - kdv_tutar - turizm_tutar

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Toplam Brüt", f"{brut_toplam:,.0f} TL")
        c2.metric("KDV (%20)", f"-{kdv_tutar:,.0f} TL", delta_color="inverse")
        c3.metric("Turizm Vergisi (%2)", f"-{turizm_tutar:,.0f} TL", delta_color="inverse")
        c4.success(f"**NET KAR: {net_kar:,.0f} TL**")
        
        st.divider()
        st.subheader("Kanal Bazlı Dağılım")
        st.bar_chart(df.groupby("Kanal")["Gelir"].sum())
    else:
        st.info("Henüz veri girişi yapılmadı.")

# --- TAB 2: YENİ KAYIT ---
with tab2:
    with st.form("kayit_formu"):
        col1, col2 = st.columns(2)
        misafir = col1.text_input("Misafir Ad Soyad")
        kanal = col2.selectbox("Rezervasyon Kanalı", ["Airbnb", "Booking", "Emlakçı", "Şahsi"])
        
        col3, col4 = st.columns(2)
        tarih = col3.date_input("Giriş Tarihi")
        gece = col4.number_input("Gece Sayısı", min_value=1, step=1)
        
        gelir = st.number_input("Toplam Konaklama Bedeli (TL)", min_value=0)
        
        if st.form_submit_button("Kaydı Tamamla"):
            yeni_veri = pd.DataFrame([{
                "Tarih": tarih.strftime("%Y-%m-%d"),
                "Misafir": misafir,
                "Gelir": gelir,
                "Gece": gece,
                "Kanal": kanal
            }])
            yeni_veri.to_csv("rez.csv", mode='a', header=False, index=False)
            st.success(f"{misafir} için kayıt eklendi!")
            st.rerun()

# --- TAB 3: KAYIT LİSTESİ ---
with tab3:
    st.subheader("📋 Tüm Rezervasyonlar")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        if st.button("Verileri Sıfırla"):
            os.remove("rez.csv")
            st.rerun()

        
