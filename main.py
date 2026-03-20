import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. GLOBAL PREMIUM TASARIM (CSS) ---
st.set_page_config(page_title="Detayvalık Premium Asistan", layout="centered")

st.markdown("""
    <style>
    /* Global Arka Plan (Yumuşak Fildişi) */
    .stApp { background-color: #FEFEF7 !important; }
    
    /* Global Yazı Rengi ve Kalınlık (Koyu Füme) */
    h1, h2, h3, h4, h5, h6, label, p, span, div, td, th { 
        color: #2D3436 !important; 
        -webkit-text-fill-color: #2D3436 !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600 !important; 
    }
    
    /* SEKMELER TASARIMI (Deniz Turkuazı) */
    .stTabs [data-baseweb="tab"] { color: #008080 !important; font-weight: bold; border-bottom-color: transparent !important; }
    .stTabs [data-baseweb="tab"] p { color: #008080 !important; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #008080 !important; }

    /* MİSAFİR VE GİRİŞ KARTLARI (Deniz Turkuazı Şeritli) */
    .premium-card, .mode-card {
        background: #ffffff !important; 
        padding: 25px; 
        border-radius: 20px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); 
        border-left: 12px solid #008080; 
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .mode-card:hover { transform: translateY(-5px); cursor: pointer; }
    .premium-card h3 { color: #008080 !important; margin-bottom: 10px; }
    
    /* REZERVASYON VE FİNANS KARTLARI (Altın Şeritli) */
    .metric-card, .rez-card {
        background: #ffffff !important; padding: 20px; border-radius: 16px; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.08); border-left: 10px solid #DAA520; margin-bottom: 15px;
    }
    .metric-card .label { font-size: 0.9em; color: #666; }
    .metric-card .value { font-size: 1.8em; color: #DAA520; font-weight: bold; }

    /* BUTONLAR TASARIMI (Sıcak Altın) */
    .stButton button {
        background-color: #DAA520 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 100% !important;
    }
    .stButton button:hover { background-color: #B8860B !important; }
    
    /* WHATSAPP BUTONU (Doğal Yeşil) */
    .wa-button { 
        display: block; background-color: #25D366; color: white !important; 
        padding: 12px; border-radius: 12px; text-decoration: none; font-weight: bold; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 10px;
    }

    /* TAKVİM PREMIUM TASARIMI (Yuvarlak Köşeli Grid) */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 6px; }
    .modern-table th { background-color: #008080; color: white !important; padding: 10px; border-radius: 8px; text-align: center; }
    .day-link { display: block; text-decoration: none; padding: 14px 0; border-radius: 14px; font-weight: bold; color: white !important; text-align: center; font-size: 1.1em; }
    .bos { background: #2ECC71 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1); } 
    .dolu { background: #E74C3C !important; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ TABANI ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 3. MOD KONTROLÜ ---
if 'user_mode' not in st.session_state: st.session_state.user_mode = None
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

# --- ANA GİRİŞ EKRANI (PREMIUM KARTLAR) ---
if st.session_state.user_mode is None:
    st.markdown('<h1 style="text-align:center;color:#008080;">🌿 Detayvalık Villa Asistanı</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;margin-bottom:30px;">Hoş geldiniz! Kimliğinizi doğrulayın:</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="mode-card" style="text-align:center;"><h2>🛋️ MİSAFİR</h2><p>Giriş, Wi-Fi, Rehber</p></div>', unsafe_allow_html=True)
        if st.button("Misafir Olarak Devam Et", use_container_width=True, key="guest_btn"):
            st.session_state.user_mode = "misafir"
            st.rerun()
            
    with col2:
        st.markdown('<div class="mode-card" style="border-left-color:#DAA520;text-align:center;"><h2>🔑 YÖNETİCİ</h2><p>Takvim, Finans, Kayıtlar</p></div>', unsafe_allow_html=True)
        if st.button("Yönetici Girişi Yap", use_container_width=True, key="admin_btn"):
            st.session_state.user_mode = "yonetici"
            st.rerun()

# --- 🌟 MİSAFİR MODU (GÖRSEL KARTLAR) ---
elif st.session_state.user_mode == "misafir":
    if st.button("⬅️ Ana Menüye Dön"):
        st.session_state.user_mode = None
        st.rerun()
        
    st.markdown('<h1 style="color:#008080;">🌿 Keyifli Konaklamalar!</h1>', unsafe_allow_html=True)
    
    m_t1, m_t2, m_t3 = st.tabs(["🏠 EV BİLGİLERİ", "📍 GEZİLECEK YERLER", "📞 İLETİŞİM"])
    
    with m_t1:
        st.markdown("""
        <div class="premium-card">
            <h3>📶 Wi-Fi Bilgileri</h3>
            <b>Ağ:</b> Detayvalik_Villa<br>
            <b>Şifre:</b> ayvalik2026
        </div>
        <div class="premium-card" style="border-left-color: #2196F3;">
            <h3>⏰ Giriş / Çıkış</h3>
            <b>Giriş:</b> 14:00<br>
            <b>Çıkış:</b> 11:00
        </div>
        """, unsafe_allow_html=True)

    with m_t2:
        recoms = [
            {"yer": "Cunda Adası", "not": "Ara sokaklar, sakızlı dondurma, Taş Kahve."},
            {"yer": "Şeytan Sofrası", "not": "Muazzam gün batımı manzarası."}
        ]
        for r in recoms:
            st.markdown(f'<div class="rez-card">**📍 {r["yer"]}**: {r["not"]}</div>', unsafe_allow_html=True)

    with m_t3:
        st.subheader("🆘 Desteğe mi ihtiyacınız var?")
        st.markdown('<a href="https://wa.me/905330000000" class="wa-button">💬 WhatsApp Destek Hattı</a>', unsafe_allow_html=True)

# --- 🛠️ YÖNETİCİ MODU (DASHBOARD GÖRÜNÜMÜ) ---
elif st.session_state.user_mode == "yonetici":
    # Şifre Koruması
    if not st.session_state.admin_auth:
        st.subheader("🔑 Yönetici Doğrulaması")
        sifre = st.text_input("Şifre", type="password", placeholder="Şifreyi girin")
        if st.button("Doğrula"):
            if sifre == "1234": # ŞİFRE: 1234
                st.session_state.admin_auth = True
                st.rerun()
            else: st.error("Hatalı şifre!")
    else:
        # Yönetici Paneli Aktif
        if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.admin_auth = False
            st.session_state.user_mode = None
            st.rerun()

        st.markdown('<h1 style="color:#008080;">🛡️ Kontrol Paneli</h1>', unsafe_allow_html=True)
        t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

        with t1: # TAKVİM PREMIUM
            c1, c2 = st.columns(2)
            ins = df[df["Tarih"] == today_str]
            with c1:
                st.write("### ⬇️ Girişler")
                for _, r in ins.iterrows(): st.success(f"👤 {r['Ad Soyad']}")
            with c2:
                st.write("### ⬆️ Çıkışlar")
                df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
                df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
                for _, r in df[df["C_str"] == today_str].iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

            st.divider()
            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
            sec_ay = st.selectbox("Ay", aylar, index=datetime.now().month-1)
            ay_idx = aylar.index(sec_ay) + 1
            
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
            with st.expander("📝 Kayıt İşle", expanded=True if q_date else False):
                with st.form("r_form", clear_on_submit=True):
                    f_t, f_a, f_p = st.text_input("Tarih", value=q_date), st.text_input("İsim"), st.text_input("Tel")
                    f_f, f_g = st.number_input("Fiyat", min_value=0), st.number_input("Gece", min_value=1)
                    if st.form_submit_button("KAYDET"):
                        start = datetime.strptime(f_t, "%Y-%m-%d")
                        new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                        pd.concat([df[REZ_COLS], pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                        st.rerun()

        with t2: # KAYITLAR
            st.subheader("🔍 Müşteri Listesi")
            ara = st.text_input("Arama")
            if not df.empty:
                list_df = df.copy().fillna("").groupby(["Ad Soyad", "Toplam", "Tel", "Gece"]).agg(Baslangic=("Tarih", "min")).reset_index()
                if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
                for _, r in list_df.iterrows():
                    st.markdown(f'<div class="rez-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 {r["Baslangic"]} ({r["Gece"]} Gece)<br>💰 {r["Toplam"]:,} TL</div>', unsafe_allow_html=True)
                    if r['Tel']:
                        st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}" target="_blank" class="wa-button">💬 WhatsApp</a>', unsafe_allow_html=True)
                    st.divider()

        with t3: # GİDERLER
            st.subheader("💸 Gider İşlemleri")
            with st.form("g_form", clear_on_submit=True):
                gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Komisyon", "Diğer"]), st.text_input("Açıklama"), st.number_input("Tutar")
                if st.form_submit_button("Gideri Kaydet"):
                    pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                    st.success("Gider kaydedildi.")

        with t4: # FİNANS DASHBOARD
            m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
            ciro, m_gid_sum = m_rez["Toplam"].sum(), df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
            kdv = ciro * 0.20
            
            st.markdown(f"### 📊 {sec_ay} Mali Özeti")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><div class="label">Ciro</div><div class="value">{ciro:,.0f} TL</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card" style="border-left-color:#E74C3C;"><div class="label">KDV Payı</div><div class="value">-{kdv:,.0f} TL</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card" style="border-left-color:#E74C3C;"><div class="label">Giderler</div><div class="value">-{m_gid_sum:,.0f} TL</div></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="rez-card" style="border-left-color:#2ECC71;text-align:center;">💰 <b>NET KAZANÇ: {ciro - kdv - m_gid_sum:,.0f} TL</b></div>', unsafe_allow_html=True)

        with t5: # YÖNETİM
            st.subheader("⚙️ Veri Kontrolü")
            if not df.empty:
                csv = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Giris=("Tarih", "min"), Cikis=("Tarih", "max")).to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Excel Yedeği Al", csv, f"rapor.csv", "text/csv")
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
