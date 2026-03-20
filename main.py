import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import urllib.parse

# --- 1. AYARLAR ---
st.set_page_config(page_title="Detayvalık VIP Yönetim", layout="wide")

# --- 2. OTURUM HAFIZASI ---
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- 3. PREMIUM CSS (Sadece Yöneticiye Özel Şık Tasarım) ---
st.markdown("""
    <style>
    .stApp { background-color: #FEFEF7 !important; }
    /* Takvim Tasarımı */
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 4px; }
    .day-link { 
        display: block; text-decoration: none; padding: 15px 0; border-radius: 12px; 
        font-weight: bold; color: white !important; text-align: center; font-size: 1.1em;
    }
    .bos { background: #2ECC71 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); } 
    .dolu { background: #E74C3C !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    /* Kartlar */
    .rez-card { 
        background: #ffffff !important; padding: 20px; border-radius: 15px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 10px solid #DAA520; margin-bottom: 15px; 
    }
    .wa-button { 
        display: block; background-color: #25D366; color: white !important; 
        padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; 
    }
    /* Butonlar */
    .stButton button { background-color: #008080 !important; color: white !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. VERİ YÜKLEME ---
REZ_COLS = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam"]
GID_COLS = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False)
    return pd.read_csv(file).reindex(columns=cols, fill_value="")

df = load_data("rez.csv", REZ_COLS)
df_gider = load_data("gider.csv", GID_COLS)
today_str = datetime.now().strftime("%Y-%m-%d")

# --- 5. GİRİŞ KONTROLÜ ---
if not st.session_state.admin_auth:
    st.markdown('<h2 style="text-align:center;color:#008080;margin-top:50px;">🔐 Detayvalık Yönetim Girişi</h2>', unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            pwd = st.text_input("Şifre", type="password", placeholder="Yönetici şifresini giriniz")
            if st.button("Sisteme Giriş Yap", use_container_width=True):
                if pwd == "1234":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Hatalı şifre!")
else:
    # --- YÖNETİCİ PANELİ (ANA GÖVDE) ---
    st.sidebar.title("🛡️ Admin")
    if st.sidebar.button("🚪 Güvenli Çıkış"):
        st.session_state.admin_auth = False
        st.query_params.clear()
        st.rerun()

    t1, t2, t3, t4, t5 = st.tabs(["📅 TAKVİM & KAYIT", "🔍 MÜŞTERİ LİSTESİ", "💸 GİDERLER", "💰 FİNANSAL ANALİZ", "⚙️ AYARLAR"])

    with t1: # TAKVİM VE HIZLI KAYIT
        aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
        sec_ay = st.selectbox("İşlem Yapılacak Ay", aylar, index=datetime.now().month-1)
        ay_idx = aylar.index(sec_ay) + 1
        
        # Bugünün Özeti
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### ⬇️ Bugün Gelecekler")
            for _, r in df[df["Tarih"] == today_str].iterrows(): st.success(f"👤 {r['Ad Soyad']}")
        with c2:
            st.markdown("### ⬆️ Bugün Gidecekler")
            df['T_dt'] = pd.to_datetime(df['Tarih'], errors='coerce')
            df['C_str'] = df.apply(lambda x: (x['T_dt'] + timedelta(days=int(x['Gece'] or 0))).strftime("%Y-%m-%d") if pd.notnull(x['T_dt']) else "", axis=1)
            for _, r in df[df["C_str"] == today_str].iterrows(): st.warning(f"🔑 {r['Ad Soyad']}")

        st.divider()
        
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

        # Tarih Seçildiğinde Açılan Form
        q_date = st.query_params.get("date", "")
        if q_date:
            with st.expander(f"📝 {q_date} Tarihine Rezervasyon Ekle", expanded=True):
                with st.form("new_reservation"):
                    f_a, f_p = st.text_input("Müşteri Ad Soyad"), st.text_input("Telefon No")
                    f_f, f_g = st.number_input("Gecelik Ücret (TL)", min_value=0), st.number_input("Gece Sayısı", min_value=1)
                    if st.form_submit_button("REZERVASYONU KAYDET"):
                        start = datetime.strptime(q_date, "%Y-%m-%d")
                        new_data = [[(start+timedelta(days=i)).strftime("%Y-%m-%d"), f_a, f_p, f_f, f_g, "", "Kesin", f_f*f_g] for i in range(int(f_g))]
                        pd.concat([df, pd.DataFrame(new_data, columns=REZ_COLS)], ignore_index=True).to_csv("rez.csv", index=False)
                        st.query_params.clear()
                        st.rerun()

    with t2: # WHATSAPP ENTEGRELİ LİSTE
        st.subheader("🔍 Kayıtlı Rezervasyonlar")
        ara = st.text_input("İsim ile süz...")
        if not df.empty:
            list_df = df.copy().fillna("").groupby(["Ad Soyad", "Tel", "Gece", "Toplam"]).agg(Baslangic=("Tarih", "min")).reset_index()
            if ara: list_df = list_df[list_df["Ad Soyad"].str.contains(ara, case=False)]
            
            for _, r in list_df.iterrows():
                st.markdown(f'''<div class="rez-card">
                    <b>👤 {r["Ad Soyad"]}</b><br>
                    📅 Giriş: {r["Baslangic"]} | 🌙 {r["Gece"]} Gece<br>
                    💰 Toplam Tutar: {r["Toplam"]:,} TL</div>''', unsafe_allow_html=True)
                if str(r['Tel']).strip():
                    msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, Detayvalık rezervasyonunuz onaylanmıştır.")
                    st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={msg}" target="_blank" class="wa-button">💬 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)

    with t3: # GİDER TAKİBİ
        st.subheader("💸 Gider Girişi")
        with st.form("gider_form", clear_on_submit=True):
            gt, gk, ga, gu = st.date_input("Gider Tarihi"), st.selectbox("Kategori", ["Temizlik", "Fatura", "Bakım", "Diğer"]), st.text_input("Detay / Açıklama"), st.number_input("Tutar (TL)", min_value=0.0)
            if st.form_submit_button("GİDERİ İŞLE"):
                pd.concat([df_gider, pd.DataFrame([[gt.strftime("%Y-%m-%d"), gk, ga, gu]], columns=GID_COLS)], ignore_index=True).to_csv("gider.csv", index=False)
                st.success("Gider kaydedildi."); st.rerun()

    with t4: # FİNANSAL ÖZET
        st.subheader(f"📊 {sec_ay} Dönemi Mali Tablosu")
        m_rez = df[pd.to_datetime(df["Tarih"], errors='coerce').dt.month == ay_idx].drop_duplicates(["Ad Soyad", "Toplam"])
        ciro = m_rez["Toplam"].sum()
        m_gid = df_gider[pd.to_datetime(df_gider["Tarih"], errors='coerce').dt.month == ay_idx]["Tutar"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Ciro", f"{ciro:,.0f} TL")
        col2.metric("Toplam Gider", f"-{m_gid:,.0f} TL")
        col3.metric("Net Kazanç", f"{ciro - m_gid:,.0f} TL", delta_color="normal")

    with t5: # VERİ YÖNETİMİ
        st.subheader("⚙️ Veri İşlemleri")
        if not df.empty:
            st.download_button("📥 Tüm Kayıtları Excel Olarak İndir", df.to_csv(index=False).encode('utf-8-sig'), "detayvalik_yedek.csv", "text/csv")
        st.divider()
        st.subheader("🗑️ Kayıt Silme")
        del_list = df.copy().fillna("").groupby(["Ad Soyad", "Toplam"]).agg(B=("Tarih", "min")).reset_index()
        for i, row in del_list.iterrows():
            c1, c2 = st.columns([4,1])
            c1.write(f"❌ {row['Ad Soyad']} - {row['Toplam']:,} TL")
            if c2.button("SİL", key=f"del_{i}"):
                df = df[~((df["Ad Soyad"] == row["Ad Soyad"]) & (df["Toplam"] == row["Toplam"]))]
                df.to_csv("rez.csv", index=False); st.rerun()
