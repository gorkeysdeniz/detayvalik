# --- 2. VERİ YÖNETİMİ (KESİN ÇÖZÜM) ---
REZ_FILE = "rez.csv"
GIDER_FILE = "gider.csv"
COL_REZ = ["Tarih", "Ad Soyad", "Tel", "Ucret", "Gece", "Not", "Durum", "Toplam", "Kapora"]
COL_GIDER = ["Tarih", "Kategori", "Aciklama", "Tutar"]

def load_data(file, cols):
    if not os.path.exists(file): 
        # Dosya yoksa sütunlarla birlikte oluştur
        pd.DataFrame(columns=cols).to_csv(file, index=False, encoding='utf-8-sig')
    try:
        # Dosyayı oku ve eksik sütun varsa tamamla
        temp_df = pd.read_csv(file, encoding='utf-8-sig')
        return temp_df.reindex(columns=cols, fill_value="")
    except:
        # Okuma hatası olursa boş dataframe dön
        return pd.DataFrame(columns=cols)

df = load_data(REZ_FILE, COL_REZ)
df_gider = load_data(GIDER_FILE, COL_GIDER)
