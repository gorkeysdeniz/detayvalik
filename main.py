import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# --- 1. AYARLAR & GÜVENLİK ---
st.set_page_config(page_title="Detayvalık | Yönetim v42.5", layout="wide", page_icon="📅")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        pass_input = st.sidebar.text_input("Yönetici Şifresi", type="password")
        if pass_input == "admin123":
            st.session_state["password_correct"] = True
            st.rerun()
        return False
    return True

if check_password():
    st.title("📅 Detayvalık Akıllı Yönetim v42.5")

    if 'rezervasyonlar' not in st.session_state:
        st.session_state.rezervasyonlar = []

    tab1, tab2, tab3, tab4 = st.tabs(["🗓 Görsel Takvim", "📝 Rezervasyon Kaydı", "💰 Finansal Analiz", "⚙️ Ayarlar"])

    # --- TAB 1: GÖRSEL TAKVİM ---
    with tab1:
        st.subheader("🏠 Villanın Doluluk Durumu")
        
        # Ay seçimi
        bugun = datetime.now()
        secilen_ay = st.selectbox("Görüntülenecek Ay", [bugun.month, (bugun.month % 12) + 1], format_func=lambda x: calendar.month_name[x])
        yil = bugun.year
        
        # Takvim matrisi oluşturma
        cal = calendar.monthcalendar(yil, secilen_ay)
        ay_ismi = calendar.month_name[secilen_ay]
        
        # Kanal Renkleri
        renkler = {"Airbnb": "🔴", "Booking": "🔵", "Emlakçı": "🟠", "Şahsi": "🟢", "Boş": "⚪"}
        st.write(f"**Rehber:** {' | '.join([f'{v} {k}' for k,v in renkler.items()])}")

        # Takvimi Çizme
        cols = st.columns(7)
        gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for i, gun in enumerate(gunler):
            cols[i].write(f"**{gun}**")

        for hafta in cal:
            for i, gun_no in enumerate(hafta):
                if gun_no == 0:
                    cols[i].write(" ")
                else:
                    su_an_tarih = datetime(yil, secilen_ay, gun_no).date()
                    durum = "⚪"
                    detay = ""
                    
                    # Rezervasyon kontrolü
                    for rez in st.session_state.rezervasyonlar:
                        if rez['Giriş'] <= su_an_tarih < rez['Çıkış']:
                            durum = renkler.get(rez['Kanal'], "🔴")
                            detay = rez['Misafir']
                            break
                    
                    cols[i].info(f"{gun_no}\n{durum}")
                    if detay:
                        cols[i].caption(f"👤{detay}")

        st.divider()
        st.subheader("📋 Liste Görünümü")
        if st.session_state.rezervasyonlar:
            st.dataframe(pd.DataFrame(st.session_state.rezervasyonlar), use_container_width=True)

    # --- TAB 2: REZERVASYON EKLE ---
    with tab2:
        with st.form("yeni_rez_v42"):
            c1, c2 = st.columns(2)
            isim = c1.text_input("Misafir Ad Soyad")
            kaynak = c2.selectbox("Kanal", ["Airbnb", "Booking", "Emlakçı", "Şahsi"])
            
            d1, d2 = st.columns(2)
            giris = d1.date_input("Giriş Tarihi")
            gece = d2.number_input("Gece Sayısı", min_value=1, step=1)
            
            f1, f2 = st.columns(2)
            gecelik_fiyat = f1.number_input("Gecelik Fiyat (TL)", min_value=0)
            komisyon_orani = f2.slider("Komisyon (%)", 0, 25, 15)
            
            if st.form_submit_button("Rezervasyonu Kaydet"):
                if isim:
                    cikis = giris + timedelta(days=gece)
                    brut = gece * gecelik_fiyat
                    kom_tutar = (brut * komisyon_orani / 100)
                    
                    st.session_state.rezervasyonlar.append({
                        "Misafir": isim, "Giriş": giris, "Çıkış": cikis,
                        "Gece": gece, "Kanal": kaynak, "Brüt": brut,
                        "Komisyon Tutarı": kom_tutar, "Net Tutar": brut - kom_tutar
                    })
                    st.success("Kaydedildi!")
                    st.rerun()

    # --- TAB 3: FİNANSAL ANALİZ ---
    with tab3:
        if st.session_state.rezervasyonlar:
            brut_toplam = sum([r['Brüt'] for r in st.session_state.rezervasyonlar])
            net_toplam = sum([r['Net Tutar'] for r in st.session_state.rezervasyonlar])
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Brüt Ciro", f"{brut_toplam:,.0f} TL")
            c2.metric("Net (Komisyon Sonrası)", f"{net_toplam:,.0f} TL")
            
            vergi = net_toplam * 0.22 # KDV %20 + Turizm %2
            c3.metric("Tahmini Vergi Yükü", f"{vergi:,.0f} TL", delta_color="inverse")
            
            st.success(f"### 💰 CEBE KALAN NET: {net_toplam - vergi:,.2f} TL")
        else:
            st.info("Henüz finansal veri yok.")

    # --- TAB 4: AYARLAR ---
    with tab4:
        if st.button("🔴 TÜM VERİLERİ SIFIRLA"):
            st.session_state.rezervasyonlar = []
            st.rerun()
