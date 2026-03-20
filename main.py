import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. AYARLAR & GÜVENLİK ---
st.set_page_config(page_title="Detayvalık | Yönetim v42.4", layout="wide", page_icon="📈")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        pass_input = st.sidebar.text_input("Yönetici Şifresi", type="password")
        if pass_input == "admin123": # Şifren buydu
            st.session_state["password_correct"] = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📈 Detayvalık Finans & Rezervasyon v42.4")

    # --- SESSION STATE (VERİ SAKLAMA) ---
    if 'rezervasyonlar' not in st.session_state:
        st.session_state.rezervasyonlar = []

    tab1, tab2, tab3, tab4 = st.tabs(["🗓 Takvim & Özet", "📝 Rezervasyon Ekle", "💰 Finansal Analiz", "⚙️ Ayarlar"])

    # --- TAB 1: TAKVİM & ÖZET ---
    with tab1:
        col1, col2, col3 = st.columns(3)
        toplam_gelir = sum([r['toplam_tutar'] for r in st.session_state.rezervasyonlar])
        rez_sayisi = len(st.session_state.rezervasyonlar)
        
        col1.metric("Toplam Rezervasyon", rez_sayisi)
        col2.metric("Brüt Ciro", f"{toplam_gelir:,.0f} TL")
        col3.metric("Doluluk Oranı", "%65") # Bu manuel veya hesaplıydı

        st.subheader("📋 Mevcut Rezervasyon Listesi")
        if st.session_state.rezervasyonlar:
            df = pd.DataFrame(st.session_state.rezervasyonlar)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Henüz kayıtlı rezervasyon yok.")

    # --- TAB 2: REZERVASYON EKLE ---
    with tab2:
        with st.form("yeni_rez"):
            c1, c2 = st.columns(2)
            isim = c1.text_input("Misafir Ad Soyad")
            kaynak = c2.selectbox("Kanal", ["Airbnb", "Booking", "Emlakçı", "Şahsi"])
            
            d1, d2 = st.columns(2)
            giris = d1.date_input("Giriş Tarihi")
            gece = d2.number_input("Gece Sayısı", min_value=1, step=1)
            
            f1, f2 = st.columns(2)
            gecelik_fiyat = f1.number_input("Gecelik Fiyat (TL)", min_value=0)
            komisyon = f2.slider("Kanal Komisyonu (%)", 0, 20, 15)
            
            cikis_tarihi = giris + timedelta(days=gece)
            toplam = gece * gecelik_fiyat
            
            if st.form_submit_state := st.form_submit_button("Rezervasyonu Kaydet"):
                yeni_kayit = {
                    "Misafir": isim,
                    "Giriş": giris,
                    "Çıkış": cikis_tarihi,
                    "Gece": gece,
                    "Kanal": kaynak,
                    "Brüt": toplam,
                    "Komisyon Tutarı": (toplam * komisyon / 100),
                    "Net Tutar": toplam - (toplam * komisyon / 100),
                    "Kayıt Tarihi": datetime.now().strftime("%d-%m-%Y")
                }
                st.session_state.rezervasyonlar.append(yeni_kayit)
                st.success(f"{isim} için kayıt oluşturuldu!")

    # --- TAB 3: FİNANSAL ANALİZ (v42.4 ÖZEL) ---
    with tab3:
        st.subheader("📊 Net Kar Hesaplama (Vergi & Komisyon)")
        
        # Vergi Oranları (Senin verdiğin limitlere göre ayarlıydı)
        kdv_orani = 0.20
        konaklama_vergisi = 0.02
        
        brut = sum([r['Brüt'] for r in st.session_state.rezervasyonlar if 'Brüt' in r])
        toplam_komisyon = sum([r['Komisyon Tutarı'] for r in st.session_state.rezervasyonlar if 'Komisyon Tutarı' in r])
        
        st.write(f"**Toplam Brüt Ciro:** {brut:,.2f} TL")
        st.write(f"**Ödenen Komisyonlar:** - {toplam_komisyon:,.2f} TL")
        
        vergi_oncesi = brut - toplam_komisyon
        kdv_tutar = vergi_oncesi * kdv_orani
        turizm_payi = vergi_oncesi * konaklama_vergisi
        
        final_kar = vergi_oncesi - kdv_tutar - turizm_payi
        
        c1, c2, c3 = st.columns(3)
        c1.metric("KDV (%20)", f"{kdv_tutar:,.0f} TL")
        c2.metric("Konaklama Vergisi (%2)", f"{turizm_payi:,.0f} TL")
        c3.success(f"**NET KAR: {final_kar:,.0f} TL**")

    # --- TAB 4: AYARLAR ---
    with tab4:
        st.button("Tüm Verileri Sıfırla", on_click=lambda: st.session_state.rezervasyonlar.clear())
        st.download_button("Excel Olarak Dışa Aktar", "veriler.csv", "text/csv")
