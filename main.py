import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import random

# --- 1. AI YAPILANDIRMASI ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=API_KEY)
    else:
        st.error("Secrets kısmında API anahtarı bulunamadı!")
except Exception as e:
    st.error(f"Yapılandırma Hatası: {e}")

st.set_page_config(page_title="Detayvalık Asistanı", layout="centered", page_icon="🏡")

if "ai_model" not in st.session_state:
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_models = ['models/gemini-1.5-flash', 'models/gemini-pro']
        chosen_model = next((m for m in target_models if m in models), models[0])
        st.session_state.ai_model = genai.GenerativeModel(chosen_model)
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")

# --- 2. VERİ TABANI (ETKİNLİKLER VE ÖNERİLER) ---
ETKINLIKLER = [
    {"tarih": "2026-03-24", "sanatci": "Teoman"},
    {"tarih": "2026-03-27", "sanatci": "Pinhani"},
    {"tarih": "2026-04-05", "sanatci": "Duman"} # Test için uzak tarih ekledim
]

REHBER_ONERILERI = [
    "🥪 Bugün Tostuyevski'de bir Ayvalık tostu patlatmaya ne dersin?",
    "☕️ Cunda sokaklarında yürürken Kaktüs'te bir kahve molası verilir!",
    "🍕 Akşam yemeği için Cunda Uno'nun pizzaları efsanedir, benden söylemesi.",
    "🌊 Badavut plajında gün batımı izlemek tatilin olmazsa olmazıdır.",
    "🍦 Sakızlı dondurma yemeden Ayvalık'tan dönmek yasak dostum!"
]

# --- 3. ÖZEL TASARIM (MENÜ BÜYÜTME) ---
st.markdown("""
    <style>
    /* Ana Başlık */
    .main-header { background: linear-gradient(135deg, #1A3636 0%, #4F6F52 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; }
    
    /* Sekme (Tab) Menülerini Büyütme */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        font-size: 18px; /* Yazı boyutu büyütüldü */
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #4F6F52 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🏡 Detayvalık Asistanı</h1></div>', unsafe_allow_html=True)

# Sekmeleri Tanımla
t_rehber, t_ai, t_etkinlik, t_eczane = st.tabs(["📍 Rehber", "🤖 Asistan", "🎉 Etkinlikler", "💊 Eczane"])

# --- SEKME 1: REHBER ---
with t_rehber:
    st.subheader("💡 Günün Önerisi")
    st.info(random.choice(REHBER_ONERILERI))
    st.write("---")
    st.caption("✨ Daha fazla gizli mekan ve detaylı tarifler için **Asistan** sekmesine sormayı unutma dostum!")

# --- SEKME 2: ASİSTAN ---
with t_ai:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Selam dostum! Ayvalık hakkında merak ettiğin ne varsa sorabilirsin."}]
    
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Nereye gidelim dostum?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_box.chat_message("user"): st.markdown(prompt)
        
        try:
            with chat_box.chat_message("assistant"):
                response = st.session_state.ai_model.generate_content(f"Sen samimi bir Ayvalıklı rehbersin. Soru: {prompt}")
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("Ufak bir takılma oldu, kotayı zorlamadan tekrar dene dostum.")

# --- SEKME 3: ETKİNLİKLER (AKILLI FİLTRE) ---
with t_etkinlik:
    st.subheader("📅 Yaklaşan Etkinlikler")
    bugun = datetime.now()
    on_gun_sonra = bugun + timedelta(days=10)
    
    bulunan_etkinlik = False
    for konser in ETKINLIKLER:
        konser_tarihi = datetime.strptime(konser["tarih"], "%Y-%m-%d")
        
        # Sadece bugünden itibaren sonraki 10 günü kontrol et
        if bugun <= konser_tarihi <= on_gun_sonra:
            st.success(f"🎤 **{konser['sanatci']}** \n\n 🗓 {konser_tarihi.strftime('%d.%m.%Y')}")
            bulunan_etkinlik = True
            
    if not bulunan_etkinlik:
        st.write("Önümüzdeki 10 gün için planlanmış bir konser görünmüyor dostum.")
    
    st.caption("⚠️ Etkinlik tarihleri değişiklik gösterebilir.")

# --- SEKME 4: ECZANE ---
with t_eczane:
    st.link_button("💊 Güncel Nöbetçi Eczaneler", "https://www.balikesireczaciodasi.org.tr/nobetci-eczaneler")
