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
        if pass_input == "admin123": # Şifren
            st.session_state["password_correct"] = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📈 Detayvalık Finans & Rezervasyon v42.4")

    # --- SESSION STATE (VERİ SAKLAMA) ---
    if 'rezervasyonlar' not in st.session_state:
        st.session_state.rezervasyonlar = []

    tab1, tab2, tab3, tab4 = st.tabs(["🗓 Özet & Liste", "📝 Rezervasyon Ekle", "💰 Finansal Analiz", "⚙️ Ayarlar"])

    # --- TAB 1: ÖZET & LİSTE ---
    with tab1:
        if st.session_state.rezervasyonlar:
            toplam_brut = sum([r['Brüt'] for r in st.session_state.rezervasyonlar])
            rez_sayisi = len(st.session_state.rezervasyonlar)
        else:
            toplam_brut = 0
            rez_sayisi = 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Rezervasyon", rez_sayisi)
        col2.metric("Toplam Brüt Ciro", f"{toplam_brut:,.0f} TL")
        col3.metric("Durum", "Aktif", delta="Sistem Çevrimiçi")

        st.subheader("📋 Güncel Rezervasyon Listesi")
        if st.session_state.rezervasyonlar:
            df = pd.DataFrame(st.session_state.rezervasyonlar)
            # Sütun sıralamasını düzenleyelim
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Henüz kayıtlı rezervasyon bulunmuyor.")

    # --- TAB 2: REZERVASYON EKLE ---
    with tab2:
        with st.form("yeni_rez_formu"):
            c1, c2 = st.columns(2)
            isim = c1.text_input("Misafir Ad Soyad")
            kaynak = c2.selectbox("Kanal", ["Airbnb", "Booking", "Emlakçı", "Şahsi"])
            
            d1, d2 = st.columns(2)
            giris = d1.date_input("Giriş Tarihi")
            gece = d2.number_input("Gece Sayısı", min_value=1, step=1)
            
            f1, f2 = st.columns(2)
            gecelik_fiyat = f1.number_input("Gecelik Fiyat (TL)", min_value=0)
            komisyon_orani = f2.slider("Kanal Komisyonu (%)", 0, 25, 15)
            
            # Kaydet Butonu (Sabitlendi)
            submitted = st.form_submit_button("Rezervasyonu Kaydet")
            
            if submitted:
                if isim:
                    cikis = giris + timedelta(days=gece)
                    brut_tutar = gece * gecelik_fiyat
                    kom_tutar = (brut_tutar * komisyon_orani / 100)
                    
                    yeni_kayit = {
                        "Misafir": isim,
                        "Giriş": giris,
                        "Çıkış": cikis,
                        "Gece": gece,
                        "Kanal": kaynak,
                        "Brüt": brut_tutar,
                        "Komisyon Tutarı": kom_tutar,
                        "Net Tutar": brut_tutar - kom_tutar,
                        "Kayıt Tarihi": datetime.now().strftime("%d-%m-%Y")
                    }
                    st.session_state.rezervasyonlar.append(yeni_kayit)
                    st.success(f"✅ {isim} başarıyla kaydedildi!")
                    st.rerun()
                else:
                    st.error("Lütfen misafir ismini boş bırakmayın.")

    # --- TAB 3: FİNANSAL ANALİZ ---
    with tab3:
        st.subheader("📊 Net Kar & Vergi Detayları")
        
        if st.session_state.rezervasyonlar:
            toplam_brut_fin = sum([r['Brüt'] for r in st.session_state.rezervasyonlar])
            toplam_kom_fin = sum([r['Komisyon Tutarı'] for r in st.session_state.rezervasyonlar])
            net_gelir = toplam_brut_fin - toplam_kom_fin
            
            # Vergi Hesapları (%20 KDV + %2 Konaklama)
            kdv = net_gelir * 0.20
            turizm_payi = net_gelir * 0.02
            cebe_kalan = net_gelir - kdv - turizm_payi
            
            st.write(f"**Toplam Brüt:** {toplam_brut_fin:,.2f} TL")
            st.write(f"**Toplam Komisyon:** -{toplam_kom_fin:,.2f} TL")
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("KDV (%20)", f"{kdv:,.0f} TL")
            c2.metric("Konaklama Vergisi (%2)", f"{turizm_payi:,.0f} TL")
            c3.success(f"**NET KAR: {cebe_kalan:,.0f} TL**")
        else:
            st.warning("Hesaplama yapılacak veri henüz girilmedi.")

    # --- TAB 4: AYARLAR ---
    with tab4:
        st.subheader("⚙️ Sistem Yönetimi")
        if st.button("🔴 Tüm Verileri Temizle"):
            st.session_state.rezervasyonlar = []
            st.rerun()
            
        if st.session_state.rezervasyonlar:
            df_export = pd.DataFrame(st.session_state.rezervasyonlar)
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Verileri CSV Olarak İndir", data=csv, file_name="detayvalik_kayitlar.csv", mime="text/csv")
