import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import calendar
import urllib.parse

# --- 1. AYARLAR & SABİT TASARIM ---
st.set_page_config(page_title="Detayvalık Operasyon v42.6.3", layout="wide", page_icon="🏡")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    .main-header { color: #1e293b; font-size: 24px; font-weight: 800; border-bottom: 3px solid #D6BD98; padding-bottom: 10px; margin-bottom: 20px; }
    .stat-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
    .stat-box { 
        flex: 1; min-width: 120px; background: white; border: 1px solid #E2E8F0; 
        padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .modern-table { width: 100%; border-collapse: separate; border-spacing: 5px; table-layout: fixed; }
    .day-link { 
        display: block; text-decoration: none; padding: 15px 0; border-radius: 8px; 
        font-weight: 700; color: white !important; text-align: center; font-size: 16px;
        border-bottom: 3px solid rgba(0,0,0,0.1);
    }
    .bos { background: #10b981 !important; } 
    .dolu { background: #ef4444 !important; } 
    .info-card { 
        background: white; padding: 20px; border-radius: 12px; 
        border-left: 8px solid #ef4444; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data():
    if not os.path.exists(REZ_FILE): 
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
    try:
        return pd.read_csv(REZ_FILE, sep=';', encoding='utf-8-sig').reindex(columns=COL_REZ, fill_value="")
    except:
        return pd.DataFrame(columns=COL_REZ)

def load_gider():
    if not os.path.exists(GIDER_FILE):
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
    try:
        df_g = pd.read_csv(GIDER_FILE, sep=';', encoding='utf-8-sig')
        if df_g.empty or 'Tarih' not in df_g.columns: return pd.DataFrame(columns=COL_GIDER)
        return df_g
    except:
        return pd.DataFrame(columns=COL_GIDER)

def save_data(df_to_save):
    df_to_save.to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')

df = load_data()
df_gider = load_gider()

# --- 3. ANA PANEL ---
st.markdown('<div class="main-header">🏡 Detayvalık Villa Operasyon v42.6.3</div>', unsafe_allow_html=True)
t_cal, t_rez, t_fin, t_set = st.tabs(["📅 Takvim & İşlemler", "📋 Rezervasyon Listesi", "💰 Finansal Tablo", "⚙️ Ayarlar"])

# --- TAB 1: TAKVİM & İŞLEMLER ---
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
        st.divider()
        rez_info = df[df["Tarih"] == selected_date]
        if not rez_info.empty:
            r = rez_info.iloc[0]
            g_tarih = datetime.strptime(str(r['Tarih']), "%Y-%m-%d")
            c_tarih = g_tarih + timedelta(days=int(r['Gece']))
            st.markdown(f"""<div class="info-card"><h3 style='margin-top:0;'>👤 Misafir: {r['Ad Soyad']}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div><b>📞 Tel:</b> {r['Tel']}</div><div><b>🌙 Gece:</b> {r['Gece']}</div>
                <div><b>📅 Giriş:</b> {g_tarih.strftime('%d.%m.%Y')}</div><div><b>📅 Çıkış:</b> {c_tarih.strftime('%d.%m.%Y')}</div>
                <div><b>💰 Toplam:</b> {r['Toplam']:,} TL</div><div><b>💳 Ödeme:</b> {r['Kapora']}</div></div></div>""", unsafe_allow_html=True)
            wp_msg = urllib.parse.quote(f"Merhaba {r['Ad Soyad']}, Detayvalık rezervasyonunuz...")
            st.markdown(f'<a href="https://wa.me/{str(r["Tel"]).replace(" ","")}?text={wp_msg}" target="_blank" style="background-color:#25D366; color:white; padding:12px; border-radius:10px; text-decoration:none; display:block; text-align:center; font-weight:bold;">📱 WhatsApp Mesajı Gönder</a>', unsafe_allow_html=True)
        else:
            st.subheader(f"📝 {selected_date} Rezervasyon Kaydı")
            with st.form("yeni_rez_v3", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                f_ad = c1.text_input("Ad Soyad")
                f_tel = c2.text_input("Telefon", value="90")
                f_giris = c3.date_input("Giriş Tarihi", value=datetime.strptime(selected_date, "%Y-%m-%d"))
                c4, c5, c6 = st.columns(3)
                f_gece = c4.number_input("Gece", min_value=1, value=1)
                f_gunluk = c5.number_input("Günlük Ücret", min_value=0)
                f_kapora = c6.selectbox("Kapora", ["Ödenmedi", "Tamamı Ödendi"])
                if st.form_submit_button("✅ REZERVASYONU TAMAMLA"):
                    yeni_satirlar = [{"Tarih": (f_giris + timedelta(days=i)).strftime("%Y-%m-%d"), "Ad Soyad": f_ad, "Tel": f_tel, "Ucret": f_gunluk, "Gece": f_gece, "Durum": "Dolu", "Toplam": f_gece * f_gunluk, "Kapora": f_kapora} for i in range(int(f_gece))]
                    df = pd.concat([df, pd.DataFrame(yeni_satirlar)], ignore_index=True)
                    save_data(df); st.rerun()

# --- TAB 2: REZERVASYON LİSTESİ ---
with t_rez:
    if not df.empty:
        df_v = df.copy(); df_v['Tarih_DT'] = pd.to_datetime(df_v['Tarih'], errors='coerce')
        summary = df_v.dropna(subset=['Tarih_DT']).groupby(["Ad Soyad", "Tel", "Gece", "Toplam", "Kapora", "Ucret"]).agg(Giris=('Tarih_DT', 'min'), Cikis=('Tarih_DT', 'max')).reset_index()
        summary['Giris_T'] = summary['Giris'].dt.strftime('%d.%m.%Y')
        summary['Cikis_T'] = (summary['Cikis'] + timedelta(days=1)).dt.strftime('%d.%m.%Y')
        
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        st.columns(3)[0].metric("Toplam Rez", f"{len(summary)} Grup")
        st.columns(3)[1].metric("Bekleyen Kapora", f"{len(summary[summary['Kapora']=='Ödenmedi'])}")
        st.columns(3)[2].metric("Toplam Ciro", f"{summary['Toplam'].sum():,.0f} TL")
        st.markdown('</div>', unsafe_allow_html=True)

        s_term = st.text_input("🔍 Misafir Ara...", "")
        if s_term:
            res = summary[summary['Ad Soyad'].str.contains(s_term, case=False, na=False)]
            for _, r in res.iterrows():
                st.info(f"👤 {r['Ad Soyad']} | 📅 {r['Giris_T']} - {r['Cikis_T']} | 💰 {r['Toplam']:,} TL")
        
        st.divider()
        st.dataframe(summary[['Ad Soyad', 'Tel', 'Giris_T', 'Cikis_T', 'Gece', 'Toplam', 'Kapora']], use_container_width=True, hide_index=True)
        csv_data = summary.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 Excel İndir (Kişi Bazlı)", data=csv_data, file_name="Rez_Ozet.csv")

# --- TAB 3: FİNANSAL TABLO (HATA DÜZELTİLDİ) ---
with t_fin:
    st.subheader(f"💰 {sec_ay} Finansal Analizi")
    m_rez = df[pd.to_datetime(df['Tarih'], errors='coerce').dt.month == ay_idx]
    brut = m_rez.drop_duplicates(["Ad Soyad", "Toplam"])["Toplam"].sum()
    vergi = brut * 0.12
    
    df_gider['Tarih_DT'] = pd.to_datetime(df_gider['Tarih'], errors='coerce')
    m_gider = df_gider[df_gider['Tarih_DT'].dt.month == ay_idx] if not df_gider.empty else pd.DataFrame()
    top_gider = m_gider["Tutar"].sum() if not m_gider.empty else 0
    net = brut - vergi - top_gider

    c1, c2, c3 = st.columns(3)
    c1.metric("Brüt Ciro", f"{brut:,.0f} TL")
    c2.metric("Vergi (%12)", f"-{vergi:,.0f} TL")
    c3.metric("Giderler", f"-{top_gider:,.0f} TL")
    st.success(f"### ✅ NET KAR: {net:,.0f} TL")

    st.divider()
    with st.form("yeni_gider_formu_v3", clear_on_submit=True):
        gc1, gc2, gc3 = st.columns([1,2,1])
        gt = gc1.date_input("Tarih"); ga = gc2.text_input("Açıklama"); gu = gc3.number_input("Tutar", 0)
        if st.form_submit_button("💰 GİDERİ KAYDET"):
            new_g = pd.DataFrame([{"Tarih": gt.strftime("%Y-%m-%d"), "Kategori": "Genel", "Aciklama": ga, "Tutar": gu}])
            pd.concat([df_gider.drop(columns=['Tarih_DT'], errors='ignore'), new_g]).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
            st.rerun()
    if not m_gider.empty: st.table(m_gider[['Tarih', 'Aciklama', 'Tutar']])

# --- TAB 4: AYARLAR ---
with t_set:
    if st.button("🔴 SİSTEMİ SIFIRLA"):
        pd.DataFrame(columns=COL_REZ).to_csv(REZ_FILE, index=False, sep=';', encoding='utf-8-sig')
        pd.DataFrame(columns=COL_GIDER).to_csv(GIDER_FILE, index=False, sep=';', encoding='utf-8-sig')
        st.rerun()
