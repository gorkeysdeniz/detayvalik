import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Detayvalık VIP", layout="centered")

# --- ASLA BOZULMAYAN MOBİL TASARIM (CSS) ---
st.markdown("""
    <style>
    /* Tabloyu yan yana tutmaya zorlar */
    .calendar-table { width: 100%; border-collapse: collapse; table-layout: fixed; margin-bottom: 20px; }
    .calendar-table th, .calendar-table td { 
        border: 1px solid #eee; padding: 12px 2px; text-align: center; font-size: 14px; font-weight: bold;
    }
    .calendar-table th { background-color: #f8f9fa; color: #333; font-size: 12px; }
    .day-link {
        display: block; text-decoration: none; padding: 10px 0; border-radius: 6px; color: white !important;
    }
    .bos { background-color: #28a745; } /* Yeşil */
    .dolu { background-color: #dc3545; } /* Kırmızı */
    .opsiyon { background-color: #ffc107; color: black !important; } /* Sarı */
    .empty { background-color: transparent; border: none; }
    
    /* Finans Kartları */
    .f-card {
        background: #ffffff; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ TABANI KONTROLÜ ---
# Eğer dosyalar yoksa, örnek birer sütunla oluşturuyoruz
def init_db():
    if not os.path.exists("rez.csv"):
        pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"]).to_csv("rez.csv", index=False)
    if not os.path.exists("gider.csv"):
        pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"]).to_csv("gider.csv", index=False)

init_db()
# Verileri oku, yoksa boş dataframe yarat
try:
    df = pd.read_csv("rez.csv")
except:
    df = pd.DataFrame(columns=["Tarih","Ad Soyad","Tel","Ucret","Gece","Not","Durum","Toplam"])

try:
    gdf = pd.read_csv("gider.csv")
except:
    gdf = pd.DataFrame(columns=["Tarih","Kategori","Aciklama","Tutar"])

st.title("🏡 Detayvalık Yönetim")

# URL'den tıklanan tarihi al
params = st.query_params
selected_date = params.get("date", "")

t1, t2, t3 = st.tabs(["📅 TAKVİM", "🔍 KAYITLAR", "💰 FİNANS"])

with t1:
    aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
    sec_ay = st.selectbox("Ay Seçin", aylar, index=datetime.now().month-1)
    ay_no = aylar.index(sec_ay) + 1
    
    st.subheader(f"{sec_ay} 2026")
    
    # HTML TAKVİM ÇİZİMİ
    html = '<table class="calendar-table"><thead><tr>'
    for g in ["Pt","Sa","Ça","Pe","Cu","Ct","Pz"]: html += f'<th>{g}</th>'
    html += '</tr></thead><tbody>'

    cal = calendar.monthcalendar(2026, ay_no)
    for hafta in cal:
        html += '<tr>'
        for gun in hafta:
            if gun == 0:
                html += '<td class="empty"></td>'
            else:
                t_str = f"2026-{ay_no:02d}-{gun:02d}"
                # Rezervasyon kontrolü
                kayit = df[df["Tarih"] == t_str]
                cls = "bos"
                if not kayit.empty:
                    cls = "dolu" if kayit.iloc[0]["Durum"] == "Kesin" else "opsiyon"
                
                # Link oluştur
                link = f"?date={t_str}"
                html += f'<td><a href="{link}" target="_self" class="day-link {cls}">{gun}</a></td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

    # SEÇİLİ GÜN BİLGİSİ VE FORM
    st.write("---")
    if selected_date:
        k_detay = df[df["Tarih"] == selected_date]
        if not k_detay.empty:
            k = k_detay.iloc[0]
            st.info(f"📅 **{selected_date}**\n\n👤 {k['Ad Soyad']} | 📞 {k['Tel']}\n\n💰 Toplam: {k['Toplam']} TL")
        else:
            st.success(f"📍 {selected_date} Boş. Kayıt yapabilirsiniz.")

    with st.expander("📝 Yeni Rezervasyon Ekle", expanded=True if selected_date else False):
        with st.form("r_form"):
            c1, c2 = st.columns(2)
            f_tar = c1.text_input("Giriş Tarihi", value=selected_date)
            f_ad = c2.text_input("Müşteri Adı")
            f_tel = c1.text_input("Telefon")
            f_ucret = c2.number_input("Günlük Ücret", min_value=0)
            f_gece = c1.number_input("Gece Sayısı", min_value=1)
            f_durum = c2.selectbox("Durum", ["Kesin", "Opsiyonel"])
            f_not = st.text_area("Notlar")
            
            if st.form_submit_button("KAYDET"):
                if f_tar and f_ad:
                    start = datetime.strptime(f_tar, "%Y-%m-%d")
                    new_data = []
                    for i in range(int(f_gece)):
                        d_str = (start + timedelta(days=i)).strftime("%Y-%m-%d")
                        new_data.append([d_str, f_ad, f_tel, f_ucret, f_gece, f_not, f_durum, f_ucret*f_gece])
                    
                    pd.concat([df, pd.DataFrame(new_data, columns=df.columns)]).to_csv("rez.csv", index=False)
                    st.query_params.clear()
                    st.rerun()

with t2:
    st.subheader("📋 Tüm Rezervasyonlar")
    # Eğer veri varsa göster, yoksa uyarı ver
    if not df.empty:
        # Tekrar eden isimleri temizleyip ana listeyi göster
        liste_df = df.drop_duplicates(subset=["Ad Soyad", "Toplam"]).sort_values(by="Tarih", ascending=False)
        st.dataframe(liste_df[["Tarih", "Ad Soyad", "Tel", "Durum", "Toplam"]], use_container_width=True)
    else:
        st.warning("Henüz hiç rezervasyon kaydı bulunmuyor.")

with t3:
    st.subheader(f"📊 {sec_ay} Finansal Özet")
    # Bu ayın verileri
    m_no = aylar.index(sec_ay) + 1
    # Tarih sütununu datetime'a çevirip filtrele
    df_temp = df.copy()
    df_temp["Tarih"] = pd.to_datetime(df_temp["Tarih"])
    bu_ay_rez = df_temp[df_temp["Tarih"].dt.month == m_no].drop_duplicates(subset=["Ad Soyad", "Toplam"])
    
    brut = bu_ay_rez["Toplam"].sum()
    
    # Giderleri filtrele
    gdf_temp = gdf.copy()
    if not gdf_temp.empty:
        gdf_temp["Tarih"] = pd.to_datetime(gdf_temp["Tarih"])
        bu_ay_gider = gdf_temp[gdf_temp["Tarih"].dt.month == m_no]["Tutar"].sum()
    else:
        bu_ay_gider = 0

    # Hesaplama: KDV %20, Vergi %2, Komisyon %15
    kdv = brut * 0.20
    vergi = brut * 0.02
    komisyon = brut * 0.15
    net = brut - bu_ay_gider - kdv - vergi - komisyon

    st.markdown(f'<div class="f-card">💰 <b>Brüt Toplam:</b> {brut:,.0f} TL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card">🧾 <b>KDV (%20):</b> -{kdv:,.0f} TL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card">💸 <b>Giderler:</b> -{bu_ay_gider:,.0f} TL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-card" style="border-left-color:green">✅ <b>NET KAR: {net:,.0f} TL</b></div>', unsafe_allow_html=True)

    st.divider()
    with st.expander("💸 Yeni Gider Ekle"):
        with st.form("g_form"):
            g_tar = st.date_input("Gider Tarihi")
            g_acik = st.text_input("Açıklama (Örn: Elektrik)")
            g_tut = st.number_input("Tutar", min_value=0)
            if st.form_submit_button("GİDERİ KAYDET"):
                yeni_g = pd.DataFrame([[str(g_tar), "Genel", g_acik, g_tut]], columns=gdf.columns)
                pd.concat([gdf, yeni_g]).to_csv("gider.csv", index=False)
                st.rerun()
