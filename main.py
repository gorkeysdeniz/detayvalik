import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.7", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    .stat-box { flex: 1; min-width: 150px; background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; font-weight: 700; color: white !important; text-align: center; border-bottom: 3px solid rgba(0,0,0,0.1); }
    .bos { background: #10b981 !important; } .dolu { background: #ef4444 !important; } 
    .rez-card-detail { background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #D6BD98; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_FILE, GIDER_FILE = "rez.csv", "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): pd.DataFrame(columns=cols).to_csv(file, index=False, sep=';', encoding='utf-8-sig')
    try:
        df_temp = pd.read_csv(file, sep=';', encoding='utf-8-sig')
        # Boş satırları ve geçersiz kayıtları temizle
        df_temp = df_temp.dropna(how='all').dropna(subset=[cols[0]])
        return df_temp.reindex(columns=cols)
    except: return pd.DataFrame(columns=cols)

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.7</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim", "📋 Rezervasyonlar", "💰 Finansal Durum", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM ---
with t_cal:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Görünüm Ayı", aylar, index=datetime.now().month-1)
    ay_idx = aylar.index(sec_ay) + 1
    
    cal_html = '<table class="modern-table"><tr><th>Pt</th><th>Sa</th><th>Ça</th><th>Pe</th><th>Cu</th><th>Ct</th><th>Pz</th></tr>'
    for week in calendar.monthcalendar(2026, ay_idx):
        cal_html += '<tr>'
        for day in week:
            if day == 0: cal_html += '<td></td>'
            else:
                d_s = f"2026-{ay_idx:02d}-{day:02d}"
                is_dolu = not df[df["Tarih"] == d_s].empty
                cl = "dolu" if is_dolu else "bos"
                cal_html += f'<td><a href="?date={d_s}" target="_self" class="day-link {cl}">{day}</a></td>'
        cal_html += '</tr>'
    st.markdown(cal_html + '</table>', unsafe_allow_html=True)

    selected_date = st.query_params.get("date")
    if selected_date:
        rez_info = df[df["Tarih"] == selected_date]
        if rez_info.empty:
            with st.form("yeni_rez"):
                c1, c2, c3 = st.columns(3)
                f_ad = c1.text_input("Ad Soyad"); f_tel = c2.text_input("Tel", value="90"); f_giris = c3.date_input("Giriş", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                c4, c5, c6 = st.columns(3)
                f_gece = c4.number_input("Gece", 1); f_ucret = c5.number_input("Gecelik TL", 0); f_kap = c6.selectbox("Ödeme", ["Ödenmedi", "Alındı"])
                if st.form_submit_button("Kaydet"):
                    yeni = [{"Tarih":(f_giris+timedelta(days=i)).strftime("%Y-%m-%d"), "Ad Soyad":f_ad, "Tel":f_tel, "Ucret":f_ucret, "Gece":f_gece, "Durum":"Dolu", "Toplam":f_gece*f_ucret, "Kapora":f_kap} for i in range(int(f_gece))]
                    df = pd.concat([df, pd.DataFrame(yeni)], ignore_index=True)
                    df.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig'); st.rerun()

# --- TAB 2: REZERVASYON LİSTESİ ---
with t_rez:
    if not df.empty:
        df_group = df.copy(); df_group['Tarih_DT'] = pd.to_datetime(df_group['Tarih'], errors='coerce')
        summary = df_group.groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(Giris=('Tarih_DT', 'min'), Cikis=('Tarih_DT', 'max')).reset_index()
        summary['Cikis_S'] = summary['Cikis'] + timedelta(days=1)
        
        # Üst Metrikler (Kart Olarak)
        st.markdown('<div style="display:flex; gap:10px; margin-bottom:20px;">', unsafe_allow_html=True)
        st.columns(3)[0].metric("Toplam Rez", f"{len(summary)} Grup")
        st.columns(3)[1].metric("Bekleyen Kapora", f"{len(summary[summary['Kapora']=='Ödenmedi'])} Adet")
        st.columns(3)[2].metric("Toplam Ciro", f"{summary['Toplam'].sum():,.0f} TL")
        st.markdown('</div>', unsafe_allow_html=True)

        # Arama ve Detay Kartı
        search_term = st.text_input("🔍 Misafir Sorgula (İsim veya Tel)", "")
        if search_term:
            res = summary[summary['Ad Soyad'].astype(str).str.contains(search_term, case=False) | summary['Tel'].astype(str).str.contains(search_term)]
            for _, r in res.iterrows():
                st.markdown(f"""<div class="rez-card-detail"><h3>👤 {r['Ad Soyad']}</h3><div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <div><b>📞 Tel:</b> {r['Tel']}</div><div><b>🌙 Gece:</b> {r['Gece']}</div>
                    <div><b>📅 Giriş:</b> {r['Giris'].strftime('%d.%m.%Y')}</div><div><b>📅 Çıkış:</b> {r['Cikis_S'].strftime('%d.%m.%Y')}</div>
                    <div><b>💰 Toplam:</b> {r['Toplam']:,} TL</div><div><b>💳 Ödeme:</b> {r['Kapora']}</div></div></div>""", unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Özet Liste")
        final_table = summary[['Ad Soyad', 'Tel', 'Gece', 'Toplam', 'Kapora']].copy()
        st.dataframe(final_table, use_container_width=True, hide_index=True)
        
        # İndirme & Silme
        c_down, c_del = st.columns([2, 1])
        c_down.download_button("📥 Excel İndir (Kişi Bazlı)", data=final_table.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig'), file_name="Rezv_Ozet.csv")
        
        with c_del:
            secilen = st.selectbox("Kayıt Sil", ["Seçiniz..."] + summary['Ad Soyad'].tolist())
            if secilen != "Seçiniz..." and st.button(f"❌ {secilen} Sil"):
                df = df[df['Ad Soyad'] != secilen]
                df.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig'); st.rerun()

# --- TAB 3: FİNANS ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Ayı Finansal Durum")
    
    m_rez = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    gelir = m_rez.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    vergi = gelir * 0.12 # %10 KDV + %2 Konaklama
    
    df_gider['Tarih_DT'] = pd.to_datetime(df_gider['Tarih'], errors='coerce')
    m_gider = df_gider[df_gider['Tarih_DT'].dt.month == ay_idx]
    top_gider = m_gider["Tutar"].sum()
    net = gelir - vergi - top_gider

    # Finansal Kartlar
    f1, f2, f3 = st.columns(3)
    f1.metric("Brüt Gelir", f"{gelir:,.0f} TL")
    f2.metric("Vergi (%12)", f"-{vergi:,.0f} TL")
    f3.metric("Giderler", f"-{top_gider:,.0f} TL")
    
    st.success(f"### ✅ Net Kar: {net:,.0f} TL")
    
    st.divider()
    with st.form("gider_gir"):
        g1, g2, g3 = st.columns(3)
        gt = g1.date_input("Tarih"); ga = g2.text_input("Açıklama"); gu = g3.number_input("Tutar", 0)
        if st.form_submit_button("Gideri Kaydet"):
            new_g = pd.DataFrame([{"Tarih": gt.strftime("%Y-%m-%d"), "Kategori": "Genel", "Aciklama": ga, "Tutar": gu}])
            pd.concat([df_gider.drop(columns=['Tarih_DT']), new_g]).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.rerun()
    st.table(m_gider[['Tarih', 'Aciklama', 'Tutar']])

with t_set:
    if st.button("🔴 TÜM VERİLERİ SIFIRLA"):
        for f in [REZ_FILE, GIDER_FILE]: pd.DataFrame().to_csv(f, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
