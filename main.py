import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık Villa", layout="centered")

# --- 2. OTURUM HAFIZASI (EN ÜSTTE OLMALI) ---
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = None
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- 3. PREMIUM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FEFEF7 !important; }
    .rez-card { background: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 10px solid #DAA520; margin-bottom: 15px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; }
    .wa-button { display: block; background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ TABANI ---
def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file)

df = load_data("rez.csv", ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"])
df_gider = load_data("gider.csv", ["Tarih", "Kategori", "Aciklama", "Tutar"])
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 5. ANA GÖVDE (GİRİŞ KONTROLÜ) ---

# Eğer giriş yapılmamışsa SADECE giriş ekranını göster
if st.session_state.user_mode is None:
    st.markdown('<h1 style="text-align:center;color:#008080;">🌿 Detayvalık Villa</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🛋️ MİSAFİR GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "misafir"
        st.rerun()
    if c2.button("🔑 YÖNETİCİ GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "yonetici"
        st.rerun()

# Giriş yapılmışsa içeriğe geç
else:
    # Çıkış Butonu (Sidebar'da sabit)
    if st.sidebar.button("🚪 Sistemden Çık"):
        st.session_state.user_mode = None
        st.session_state.admin_auth = False
        st.query_params.clear()
        st.rerun()

    # --- MİSAFİR MODU ---
    if st.session_state.user_mode == "misafir":
        st.title("🌿 Hoş Geldiniz")
        st.info("Wi-Fi: detayvalik / Şifre: ayvalik2026")
        # Buraya diğer misafir fikirlerini ekleyebiliriz

    # --- YÖNETİCİ MODU ---
    elif st.session_state.user_mode == "yonetici":
        if not st.session_state.admin_auth:
            st.subheader("🔑 Yönetici Şifresi")
            pwd = st.text_input("Şifre", type="password")
            if st.button("Doğrula"):
                if pwd == "1234":
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Hatalı!")
        else:
            # --- YÖNETİCİ PANELİ AKTİF ---
            t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

            with t1:
                aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
                sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
                ay_idx = aylar.index(sec_ay) + 1
                
                # Takvim Grid
                cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
                for week in calendar.monthcalendar(2026, ay_idx):
                    cal_html += '<tr>'
                    for day in week:
                        if day == 0: cal_html += '<td></td>'
                        else:
                            d_s = f"2026-{ay_idx:02d}-{day:02d}"
                            cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                            # URL'ye parametre eklerken ana oturumu bozmaması için target="_self" kritik
                            cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
                    cal_html += '</tr>'
                st.markdown(cal_html + '</table>', unsafe_allow_html=True)

                # Kayıt Formu (Tarih seçilmişse)
                q_date = st.query_params.get("date", "")
                if q_date:
                    with st.expander(f"📝 {q_date} Kayıt Ekle", expanded=True):
                        with st.form("new_rez_form"):
                            f_a, f_p = st.text_input("Ad Soyad"), st.text_input("Telefon")
                            f_f, f_g = st.number_input("Gecelik Fiyat", min_value=0), st.number_input("Gece", min_value=1)
                            if st.form_submit_button("KAYDET"):
                                start = datetime.strptime(q_date, "%Y-%m-%d")
                                new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                                pd.concat([df, pd.DataFrame(new, columns=df.columns)], ignore_index=True).to_csv("rez.csv", index=False)
                                st.query_params.clear()
                                st.rerun()

            with t2: # KAYITLAR VE WHATSAPP
                st.subheader("🔍 Rezervasyonlar")
                ara = st.text_input("İsim ile ara...")
                if not df.empty:
                    list_df = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Baslangic=("Tarih", "min")).reset_index()
                    if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
                    for _, r in list_df.iterrows():
                        st.markdown(f'<div class="rez-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 {r["Baslangic"]} | {r["Gece"]} Gece | {r["Toplam"]:,} TL</div>', unsafe_allow_html=True)
                        if str(r['Tel']).strip():
                            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}" target="_blank" class="wa-button">💬 WhatsApp</a>', unsafe_allow_html=True)

            with t3: # GİDERLER
                with st.form("gider_form", clear_on_submit=True):
                    gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.text_input("Açıklama"), st.number_input("Tutar")
                    if st.form_submit_button("Gideri Kaydet"):
                        pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=df_gider.columns)], ignore_index=True).to_csv("gider.csv", index=False)
                        st.success("Kaydedildi."); st.rerun()

            with t4: # FİNANS
                m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
                ciro = m_rez["Toplam"].sum()
                m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
                c1, c2 = st.columns(2)
                c1.metric("Ciro", f"{ciro:,.0f} TL")
                c2.metric("Net (Gider Sonrası)", f"{ciro - m_gid:,.0f} TL")

            with t5: # YÖNETİM
                st.subheader("⚙️ Veri")
                if not df.empty:
                    st.download_button("📥 Excel İndir", df.to_csv(index=False).encode('utf-8-sig'), "rapor.csv")
