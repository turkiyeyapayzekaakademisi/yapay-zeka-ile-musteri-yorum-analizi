"""
ADIMLAR:
    1. Streamlit sayfa ayarlarını yap  (başlık, ikon, layout)
    2. Sayfa yüklenince geçmiş analizleri veritabanından çek
    3. Dashboard istatistik kartlarını göster  (toplam / pozitif / negatif / nötr)
    4. Yorum giriş formunu oluştur
    5. Form gönderilince Gemini analizi yap ve sayfayı yenile
    6. Geçmiş analiz listesini göster

KURULUM:
    1. Virtual environment oluşturun (henüz oluşturmadıysanız):
           python -m venv venv
    2. Virtual environment'ı aktif edin:
           - Windows : venv\Scripts\activate
           - Mac/Linux: source venv/bin/activate
    3. requirements.txt dosyasına şunları ekleyin:
           streamlit
           requests
           python-dotenv
    4. Bağımlılıkları yükleyin:
           pip install -r requirements.txt
    5. Uygulamayı başlatmak için:
           streamlit run app.py
    6. Tarayıcıda otomatik açılır:
           http://localhost:8501

NOT:
    Bu dosya Streamlit uygulamasının tek giriş noktasıdır.
    pages/ klasörü kullanmıyoruz — o klasör olunca Streamlit
    otomatik çok sayfalı navigasyon oluşturur, sidebar görünür.
    Tek sayfalı uygulamada her şey bu dosyada.

    st.session_state: Streamlit'te sayfa her etkileşimde yeniden çalışır.
    session_state bu veriyi tarayıcı oturumu boyunca bellekte tutar.
    Böylece her butona basışta veritabanına tekrar sorgu atmayız.

    st.rerun(): Formu gönderdikten sonra sayfayı sıfırdan çizer.
    Böylece yeni analiz anında listenin en üstünde görünür.

    st.container(border=True): Saf Python ile kart görünümü elde etmenin
    en temiz Streamlit yoludur — HTML/CSS gerektirmez.
"""

# =========================================================
# 1. Streamlit sayfa ayarlarını yap
# =========================================================
import streamlit as st
from api_client import analyze_comment, get_history

# set_page_config: her uygulamada ilk çağrılması gereken Streamlit fonksiyonu
st.set_page_config(
    page_title="Yorum Analizi",
    page_icon="🎓",
    layout="wide",
)


# =========================================================
# 2. Sayfa yüklenince geçmiş analizleri veritabanından çek
# =========================================================
def _load_from_db():
    """
    Amaç:
        FastAPI üzerinden veritabanındaki tüm analizleri çekip
        session_state'e kaydetmek.

    Önemli:
        Hata durumunda session_state'e hiç dokunmuyoruz.
        Böylece sayfa her yenilendiğinde tekrar bağlanmayı dener.
        Başarılı olursa session_state'e yazar ve bir daha sorgu atmaz.
    """
    try:
        data = get_history(limit=100)
        st.session_state.analyses = [
            {
                "comment":     a["comment_text"],
                "sentiment":   a["sentiment"],
                "confidence":  a["confidence"],
                "explanation": a.get("explanation", ""),
            }
            for a in data.get("analyses", [])
        ]
    except Exception:
        pass  # session_state'e yazılmadı — sonraki render'da tekrar dener


# İlk açılışta session_state'te veri yoksa veritabanından yükle
if "analyses" not in st.session_state:
    _load_from_db()

# Bağlantı hâlâ başarısız — kullanıcıya bilgi ver ve retry sun
if "analyses" not in st.session_state:
    st.error("Backend'e bağlanılamadı.")
    if st.button("🔄 Yeniden Dene"):
        st.rerun()
    st.stop()

analyses = st.session_state.analyses
total    = len(analyses)
pozitif  = sum(1 for a in analyses if a["sentiment"].lower() == "pozitif")
negatif  = sum(1 for a in analyses if a["sentiment"].lower() == "negatif")
notr     = total - pozitif - negatif

st.title("🎓 Yapay Zeka ile Müşteri Yorum Analizi")


# =========================================================
# 3. Dashboard istatistik kartlarını göster
# =========================================================
# st.metric: sayı + etiket gösteren hazır Streamlit bileşeni
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Toplam",  total)
col2.metric("😊 Pozitif", pozitif)
col3.metric("😠 Negatif", negatif)
col4.metric("😐 Nötr",    notr)

st.divider()

# Sayfayı iki sütuna böl: sol = geçmiş liste, sağ = form
left, right = st.columns([2, 3])


# =========================================================
# 4. Yorum giriş formunu oluştur
# =========================================================
with right:
    st.subheader("💬 Yorum Yaz")

    # st.form: submit butonuna basılana kadar hiçbir şey tetiklenmez
    with st.form("comment_form", clear_on_submit=True):
        comment = st.text_area(
            label="Yorumunuzu yazın:",
            placeholder="Uygulamayı kullandınız mı? Deneyiminizi paylaşın...",
            height=150,
        )
        submitted = st.form_submit_button(
            "🚀 Gönder & Analiz Et",
            use_container_width=True,
        )

    # =========================================================
    # 5. Form gönderilince Gemini analizi yap ve sayfayı yenile
    # =========================================================
    if submitted:
        if not comment.strip():
            st.warning("Lütfen bir yorum girin.")
        else:
            with st.spinner("Gemini analiz ediyor..."):
                try:
                    analyze_comment(comment.strip())  # POST /analysis/
                    _load_from_db()                   # Güncel listeyi çek
                    st.toast("Analiz tamamlandı!", icon="✅")
                    st.rerun()                        # Sayfayı yeniden çiz
                except Exception:
                    st.error("API bağlantı hatası. Backend çalışıyor mu?")


# =========================================================
# 6. Geçmiş analiz listesini göster
# =========================================================
with left:
    st.subheader("📝 Son Analizler")

    if not analyses:
        st.info("Henüz analiz yok. Sağ taraftan bir yorum gönderin.")
    else:
        for a in analyses:
            sentiment = a["sentiment"].lower()
            conf      = int(a["confidence"] * 100)
            short     = a["comment"][:150] + "..." if len(a["comment"]) > 150 else a["comment"]

            # st.container(border=True): kart görünümü — saf Python
            with st.container(border=True):

                # Duyguya göre renkli başlık
                if sentiment == "pozitif":
                    st.success(f"😊 Pozitif  —  %{conf} güven")
                elif sentiment == "negatif":
                    st.error(f"😠 Negatif  —  %{conf} güven")
                else:
                    st.warning(f"😐 Nötr  —  %{conf} güven")

                # Yorum metni ve Gemini açıklaması
                st.write(short)
                if a.get("explanation"):
                    st.caption(f"💡 {a['explanation']}")
