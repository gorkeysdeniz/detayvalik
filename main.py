import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. PREMIUM CSS & MOBİL UYUMLULUK ---
st.set_page_config(page_title="Detayvalık Premium", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FEFEF7 !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #2D3436 !important; font-family: 'Montserrat', sans-serif; font-weight: 600 !important; }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f1f2f6; border-radius: 10px 10px 0 0; padding: 10px 20px; color: #008080 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #008080 !important; color: white !important; }
    .stTabs [data-baseweb="tab"] p { color: inherit !important; }

    /* Kartlar */
    .premium-card, .mode-card, .metric-card, .rez-card {
        background: #ffffff !important; padding: 20px; border-radius: 20px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-left: 12px solid #008080; margin-bottom: 20px;
    }
    .metric-card { border-left-color: #DAA520; text-align: center; }
    
    /* Takvim Tablosu */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { 
        display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; 
        font-weight: bold; color: white !important; text-align: center; font-size: 1.1em;
        transition: all 0.2s;
    }
    .day-link:hover { transform: scale(1.05); filter: brightness(1.1); }
    .bos { background: #2ECC71 !important; } 
    .dolu { background: #E74C3C !important; }
    
    /* Form & Buton */
    .stButton button { background-color: #DAA520 !important; color: white !important; border-radius: 12px !important; border: none !important; padding: 10px; }
    .wa-button { display: block; background-color: #25D366; color: white !important; padding: 12px; border-radius: 12px; text-decoration: none; font-weight: bold; text-align: center; }
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

# --- 3. MOD KONTROLÜ ---
if 'user_mode' not in st.session_state: st.session_state.user_mode = None
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

# --- ANA GİRİŞ ---
if st.session_state.user_mode is None:
    st.markdown('<h1 style="text-align:center;color:#008080;margin-top:50px;">🌿 Detayvalık Villa</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛋️ MİSAFİR GİRİŞİ", use_container_width=True):
            st.session_state.user_mode = "misafir"
            st.rerun()
    with c2:
        if st.button("🔑 YÖNETİCİ GİRİŞİ", use_container_width=True):
            st.session_state.user_mode = "yonetici"
            st.rerun()

# --- 🌟 MİSAFİR MODU ---
elif st.session_state.user_mode == "misafir":
    if st.sidebar.button("⬅️ Çıkış"): st.session_state.user_mode = None; st.rerun()
    st.title("🌿 Hoş Geldiniz")
    m_tabs = st.tabs(["🏠 BİLGİLER", "📍 REHBER", "📞 İLETİŞİM"])
    with m_tabs[0]:
        st.markdown('<div class="premium-card"><h3>📶 Wi-Fi</h3><b>Şifre:</b> ayvalik2026</div>', unsafe_allow_html=True)
    with m_tabs[1]:
        st.write("📍 **Cunda Adası** | 📍 **Şeytan Sofrası**")
    with m_tabs[2]:
        st.markdown('<a href="https://wa.me/905330000000" class="wa-button">💬 WhatsApp Destek</a>', unsafe_allow_html=True)

# --- 🛠️ YÖNETİCİ MODU ---
elif st.session_state.user_mode == "yonetici":
    if not st.session_state.admin_auth:
        st.markdown('<div style="max-width:400px;margin:auto;margin-top:100px;">', unsafe_allow_html=True)
        pwd = st.text_input("Yönetici Şifresi", type="password")
        if st.button("Giriş"):
            if pwd == "1234": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if st.sidebar.button("🚪 Güvenli Çıkış"): 
            st.session_state.admin_auth = False; st.session_state.user_mode = None; st.rerun()

        # URL'de tarih varsa Takvim sekmesini aktif tutmak için mantık
        q_date = st.query_params.get("date", "")
        
        st.markdown('<h2 style="color:#008080;">🛡️ Yönetim Paneli</h2>', unsafe_allow_html=True)
        t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

        with t1:
            c1, c2 = st.columns(2)
            with c1:
                st.write("### ⬇️ Bugün Gelecekler")
                for _, r in df[df["Tarih"] == today_str].iterrows(): st.success(f"👤 {r['Ad Soyad']}")
            with c2:
                st.write("### ⬆️ Bugün Gidecekler")
                df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
                df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
                for _, r in df[df["C_str"] == today_str].iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

            st.divider()
            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
            sec_ay = st.selectbox("Görüntülenen Ay", aylar, index=datetime.now().month-1)
            ay_idx = aylar.index(sec_ay) + 1
            
            cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
            for week in calendar.monthcalendar(2026, ay_idx):
                cal_html += '<tr>'
                for day in week:
                    if day == 0: cal_html += '<td></td>'
                    else:
                        d_s = f"2026-{ay_idx:02d}-{day:02d}"
                        cl = "dolu" if not df[df["Tarih"] == d_s].empty else "bos"
                        # target="_self" kullanarak aynı sayfada kalmasını sağlıyoruz
                        cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
                cal_html += '</tr>'
            st.markdown(cal_html + '</table>', unsafe_allow_html=True)

            if q_date:
                with st.expander(f"📝 {q_date} Tarihine Kayıt Ekle", expanded=True):
                    with st.form("quick_rez", clear_on_submit=True):
                        f_a, f_p = st.text_input("Müşteri Ad Soyad"), st.text_input("Telefon")
                        f_f, f_g = st.number_input("Gecelik Fiyat", min_value=0), st.number_input("Gece Sayısı", min_value=1)
                        if st.form_submit_button("SİSTEME İŞLE"):
                            start = datetime.strptime(q_date, "%Y-%m-%d")
                            new_rows = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                            pd.concat([df[REZ_COLS], pd.DataFrame(new_rows, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                            st.query_params.clear() # Tarihi temizle ki form kapansın
                            st.rerun()

        with t2:
            ara = st.text_input("İsim ile ara...")
            if not df.empty:
                list_df = df.copy().fillna("").groupby(["Ad Soyad", "Toplam", "Tel", "Gece"]).agg(Baslangic=("Tarih", "min")).reset_index()
                if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
                for _, r in list_df.iterrows():
                    st.markdown(f'<div class="rez-card">👤 <b>{r["Ad Soyad"]}</b><br>📅 {r["Baslangic"]} ({r["Gece"]} Gece) | 💰 {r["Toplam"]:,} TL</div>', unsafe_allow_html=True)

        with t3:
            st.subheader("💸 Gider Girişi")
            with st.form("gider_form", clear_on_submit=True):
                gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Tamirat", "Diğer"]), st.text_input("Açıklama"), st.number_input("Tutar")
                if st.form_submit_button("Gideri Kaydet"):
                    pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                    st.success("Gider kaydedildi.")

        with t4:
            m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
            ciro, m_gid_sum = m_rez["Toplam"].sum(), df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><small>Ciro</small><br><span class="value">{ciro:,.0f} TL</span></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card"><small>Gider</small><br><span class="value">-{m_gid_sum:,.0f} TL</span></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card" style="border-left-color:#2ECC71;"><small>Net</small><br><span class="value">{(ciro*0.8)-m_gid_sum:,.0f} TL</span></div>', unsafe_allow_html=True)

        with t5:
            st.subheader("⚙️ Veri & Yedekleme")
            if not df.empty:
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Tüm Veriyi İndir", csv, "villa_data.csv", "text/csv")
            st.divider()
            st.subheader("🗑️ Kayıt Sil")
            del_list = df.copy().fillna("").groupby(["Ad Soyad", "Toplam"]).agg(B=("Tarih", "min")).reset_index()
            for i, row in del_list.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"❌ {row['Ad Soyad']} ({row['Toplam']:,} TL)")
                if c2.button("SİL", key=f"del_{i}"):
                    df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                    df.to_csv("rez.csv", index=False); st.rerun()
