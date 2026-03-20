import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR VE STİL ---
st.set_page_config(page_title="Detayvalık Villa Paneli", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 600 !important; }
    .rez-card { background: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 8px solid #2ECC71; margin-bottom: 15px; }
    .guest-card { background: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 10px solid #FFC107; margin-bottom: 15px; }
    .wa-button { display: block; background-color: #25D366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; text-align: center; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 10px 0; border-radius: 10px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI YÖNETİMİ ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 3. GİRİŞ VE MOD KONTROLÜ ---
if 'user_mode' not in st.session_state: st.session_state.user_mode = None
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

# --- ANA GİRİŞ EKRANI ---
if st.session_state.user_mode is None:
    st.title("🏡 Detayvalık Villa Asistanı")
    st.subheader("Hoş geldiniz! Devam etmek için seçim yapın:")
    c1, c2 = st.columns(2)
    if c1.button("🛋️ MİSAFİR GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "misafir"
        st.rerun()
    if c2.button("🔑 YÖNETİCİ GİRİŞİ", use_container_width=True):
        st.session_state.user_mode = "yonetici"
        st.rerun()

# --- 🌟 MİSAFİR MODU ---
elif st.session_state.user_mode == "misafir":
    if st.button("⬅️ Ana Menü"):
        st.session_state.user_mode = None
        st.rerun()
    st.title("🌿 Keyifli Konaklamalar!")
    m_t1, m_t2, m_t3 = st.tabs(["🏠 EV BİLGİLERİ", "📍 GEZİLECEK YERLER", "📞 İLETİŞİM"])
    with m_t1:
        st.markdown('<div class="guest-card"><h3>📶 Wi-Fi</h3><b>Ağ:</b> Detayvalik_Villa<br><b>Şifre:</b> ayvalik2026</div>', unsafe_allow_html=True)
        st.markdown('<div class="guest-card" style="border-left-color: #2196F3;"><h3>⏰ Giriş/Çıkış</h3><b>Giriş:</b> 14:00 | <b>Çıkış:</b> 11:00</div>', unsafe_allow_html=True)
    with m_t2:
        st.write("📍 **Cunda Adası:** Sakızlı dondurma ve ara sokaklar.")
        st.write("📍 **Şeytan Sofrası:** Muhteşem gün batımı.")
    with m_t3:
        st.markdown('<a href="https://wa.me/905330000000" class="wa-button">💬 WhatsApp Destek</a>', unsafe_allow_html=True)

# --- 🛠️ YÖNETİCİ MODU ---
elif st.session_state.user_mode == "yonetici":
    # Basit Şifre Koruması
    if not st.session_state.admin_auth:
        st.subheader("🔑 Yönetici Şifresi")
        sifre = st.text_input("Şifreyi girin", type="password")
        if st.button("Giriş Yap"):
            if sifre == "1234": # ŞİFRE BURADAN DEĞİŞİR
                st.session_state.admin_auth = True
                st.rerun()
            else: st.error("Hatalı şifre!")
    else:
        if st.sidebar.button("🚪 Çıkış Yap"):
            st.session_state.admin_auth = False
            st.session_state.user_mode = None
            st.rerun()

        st.title("🛡️ Yönetici Paneli")
        t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

        with t1: # TAKVİM VE KAYIT
            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
            sec_ay = st.selectbox("Ay", aylar, index=datetime.now().month-1)
            ay_idx = aylar.index(sec_ay) + 1
            
            c1, c2 = st.columns(2)
            with c1:
                st.write("### ⬇️ Giriş")
                ins = df[df["Tarih"] == today_str]
                for _, r in ins.iterrows(): st.success(f"👤 {r['Ad Soyad']}")
            with c2:
                st.write("### ⬆️ Çıkış")
                df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
                df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
                for _, r in df[df["C_str"] == today_str].iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

            st.divider()
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

            q_date = st.query_params.get("date", "")
            with st.expander("📝 Kayıt Ekle", expanded=True if q_date else False):
                with st.form("r_form", clear_on_submit=True):
                    f_t, f_a, f_p = st.text_input("Tarih", value=q_date), st.text_input("İsim"), st.text_input("Tel")
                    f_f, f_g = st.number_input("Fiyat", min_value=0), st.number_input("Gece", min_value=1)
                    if st.form_submit_button("KAYDET"):
                        start = datetime.strptime(f_t, "%Y-%m-%d")
                        new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                        pd.concat([df[REZ_COLS], pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                        st.rerun()

        with t2: # KAYITLAR VE WHATSAPP
            ara = st.text_input("İsim Ara")
            if not df.empty:
                list_df = df.copy().fillna("").groupby(["Ad Soyad", "Toplam", "Tel", "Gece"]).agg(Baslangic=("Tarih", "min")).reset_index()
                if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
                for _, r in list_df.iterrows():
                    st.markdown(f'<div class="rez-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 {r["Baslangic"]} ({r["Gece"]} Gece)<br>💰 {r["Toplam"]:,} TL</div>', unsafe_allow_html=True)
                    if r['Tel']:
                        st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}" target="_blank" class="wa-button">💬 WhatsApp</a>', unsafe_allow_html=True)
                    st.divider()

        with t3: # GİDERLER
            st.subheader("💸 Gider Girişi")
            with st.form("g_form", clear_on_submit=True):
                gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Komisyon", "Diğer"]), st.text_input("Açıklama"), st.number_input("Tutar")
                if st.form_submit_button("Gideri Kaydet"):
                    pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                    st.success("Gider işlendi.")

        with t4: # FİNANS
            m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
            ciro, m_gid_sum = m_rez["Toplam"].sum(), df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
            kdv = ciro * 0.20
            st.metric("Ciro", f"{ciro:,.0f} TL")
            st.metric("KDV", f"-{kdv:,.0f} TL")
            st.metric("Gider", f"-{m_gid_sum:,.0f} TL")
            st.success(f"NET: {ciro - kdv - m_gid_sum:,.0f} TL")

        with t5: # YÖNETİM & SİLME
            st.subheader("⚙️ Veri Yönetimi")
            if not df.empty:
                csv = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Giris=("Tarih", "min"), Cikis=("Tarih", "max")).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Müşteri Listesini İndir", csv, f"rapor_{today_str}.csv", "text/csv")
            st.divider()
            st.subheader("🗑️ Kayıt Sil")
            del_list = df.copy().fillna("").groupby(["Ad Soyad", "Toplam"]).agg(B=("Tarih", "min")).reset_index()
            for i, row in del_list.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"❌ {row['Ad Soyad']} ({row['Toplam']:,} TL)")
                if c2.button("SİL", key=f"del_{i}"):
                    df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                    df.to_csv("rez.csv", index=False)
                    st.rerun()
