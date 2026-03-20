import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR VE CSS ---
st.set_page_config(page_title="Detayvalık Villa Yönetimi", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FEFEF7 !important; }
    h1, h2, h3, label, p, span, div, td, th { color: #2D3436 !important; font-family: 'Montserrat', sans-serif; font-weight: 600 !important; }
    .rez-card { background: #ffffff !important; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 10px solid #DAA520; margin-bottom: 15px; }
    .metric-card { background: #ffffff !important; padding: 20px; border-radius: 16px; box-shadow: 0 6px 15px rgba(0,0,0,0.08); border-left: 10px solid #008080; text-align: center; }
    .wa-button { display: block; background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; margin-top: 5px; }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { display: block; text-decoration: none; padding: 12px 0; border-radius: 12px; font-weight: bold; color: white !important; text-align: center; }
    .bos { background: #2ECC71 !important; } .dolu { background: #E74C3C !important; }
    .stButton button { background-color: #008080 !important; color: white !important; border-radius: 10px !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. OTURUM VE VERİ YÖNETİMİ ---
if 'user_mode' not in st.session_state: st.session_state.user_mode = None
if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False

REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 3. ANA AKIŞ ---
if st.session_state.user_mode is None:
    st.markdown('<h1 style="text-align:center;color:#008080;">🌿 Detayvalık Villa</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🛋️ MİSAFİR GİRİŞİ"): st.session_state.user_mode = "misafir"; st.rerun()
    if c2.button("🔑 YÖNETİCİ GİRİŞİ"): st.session_state.user_mode = "yonetici"; st.rerun()

elif st.session_state.user_mode == "misafir":
    if st.sidebar.button("⬅️ Çıkış"): st.session_state.user_mode = None; st.rerun()
    st.title("🌿 Hoş Geldiniz")
    st.info("Wi-Fi: detayvalik / Şifre: ayvalik2026")

elif st.session_state.user_mode == "yonetici":
    if not st.session_state.admin_auth:
        st.subheader("🔑 Güvenlik")
        pwd = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            if pwd == "1234": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Hatalı!")
    else:
        if st.sidebar.button("🚪 Çıkış"): st.session_state.admin_auth = False; st.session_state.user_mode = None; st.rerun()
        
        t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💸 GİDERLER", "💰 FİNANS", "⚙️ YÖNETİM"])

        with t1: # TAKVİM VE KAYIT
            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
            sec_ay = st.selectbox("Ay Seçimi", aylar, index=datetime.now().month-1)
            ay_idx = aylar.index(sec_ay) + 1
            
            # Bugün Giriş/Çıkış
            c1, c2 = st.columns(2)
            with c1:
                st.write("### ⬇️ Girişler")
                for _, r in df[df["Tarih"] == today_str].iterrows(): st.success(f"👤 {r['Ad Soyad']}")
            with c2:
                st.write("### ⬆️ Çıkışlar")
                df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
                df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
                for _, r in df[df["C_str"] == today_str].iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

            # Takvim Grid
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
            if q_date:
                with st.expander(f"📝 {q_date} Kayıt Ekle", expanded=True):
                    with st.form("new_r", clear_on_submit=True):
                        f_a, f_p = st.text_input("Ad Soyad"), st.text_input("Telefon")
                        f_f, f_g = st.number_input("Gecelik", min_value=0), st.number_input("Gece", min_value=1)
                        if st.form_submit_button("KAYDET"):
                            start = datetime.strptime(q_date, "%Y-%m-%d")
                            new = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                            pd.concat([df, pd.DataFrame(new, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                            st.query_params.clear(); st.rerun()

        with t2: # AKILLI REZERVASYON LİSTESİ & WHATSAPP
            st.subheader("🔍 Rezervasyonlar")
            ara = st.text_input("İsim Ara...")
            if not df.empty:
                # Müşteri bazlı gruplama (Tek satır gösterim)
                list_df = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Baslangic=("Tarih", "min")).reset_index()
                if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
                
                for _, r in list_df.iterrows():
                    st.markdown(f'''<div class="rez-card">
                        <b>👤 {r["Ad Soyad"]}</b><br>
                        📅 {r["Baslangic"]} | 🌙 {r["Gece"]} Gece<br>
                        💰 Toplam: {r["Toplam"]:,} TL</div>''', unsafe_allow_html=True)
                    if str(r['Tel']).strip():
                        msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, rezervasyonunuz onaylanmıştır.")
                        st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={msg}" target="_blank" class="wa-button">💬 WhatsApp Mesajı At</a>', unsafe_allow_html=True)

        with t3: # GİDERLER (FORM TEMİZLEME DAHİL)
            st.subheader("💸 Gider Girişi")
            with st.form("gider_f", clear_on_submit=True):
                gt, gk, ga, gu = st.date_input("Tarih"), st.selectbox("Tür", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.text_input("Açıklama"), st.number_input("Tutar", min_value=0.0)
                if st.form_submit_button("SİSTEME İŞLE"):
                    pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                    st.success("Gider başarıyla kaydedildi."); st.rerun()

        with t4: # FİNANS ANALİZİ (GÜNCEL)
            st.subheader(f"💰 {sec_ay} Mali Tablo")
            # Seçili ayın verilerini filtrele
            m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
            ciro = m_rez["Toplam"].sum()
            m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
            kdv = ciro * 0.20
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><small>Ciro</small><br><b>{ciro:,.0f} TL</b></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card" style="border-left-color:#E74C3C;"><small>Giderler</small><br><b>-{m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card" style="border-left-color:#2ECC71;"><small>Net Kar</small><br><b>{ciro - kdv - m_gid:,.0f} TL</b></div>', unsafe_allow_html=True)

        with t5: # YÖNETİM & RAPOR
            st.subheader("⚙️ Veri Yönetimi")
            if not df.empty:
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Excel Olarak İndir", csv, "villa_rapor.csv", "text/csv")
            
            st.divider()
            st.subheader("🗑️ Kayıt Sil")
            del_list = df.copy().fillna("").groupby(["Ad Soyad", "Toplam"]).agg(B=("Tarih", "min")).reset_index()
            for i, row in del_list.iterrows():
                col1, col2 = st.columns([4,1])
                col1.write(f"❌ {row['Ad Soyad']} ({row['Toplam']:,} TL)")
                if col2.button("SİL", key=f"del_{i}"):
                    df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                    df.to_csv("rez.csv", index=False); st.rerun()
