import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rehabilitasyon Çakışma Denetleyici", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = None

st.title("⚖️ Program Çakışma ve Güzergah Denetimi")

uploaded_file = st.file_uploader("Program CSV dosyasını yükleyin", type=["csv"])

if uploaded_file:
    try:
        # Dosyanızdaki noktalı virgül yapısına göre okuma
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        df.columns = [c.strip() for c in df.columns]
        st.session_state.df = df

        # --- 1. AYNI SAATTEKİ TÜM ÇAKIŞMALAR ---
        st.subheader("🕵️ Saatlik Genel Yoğunluk")
        
        # Her saatte kaç öğrenci olduğunu say
        saat_ozet = df.groupby('Saat').agg(
            Ogrenci_Sayisi=('Adı', 'count'),
            Guzergahlar=('Güzergah', lambda x: ", ".join(x.unique()))
        ).reset_index()

        # Tabloyu göster
        st.dataframe(saat_ozet, use_container_width=True)

        # --- 2. GÜZERGAH UYGUNLUK DENETİMİ ---
        st.subheader("🚐 Güzergah Çakışma Analizi")
        st.info("Aynı saatte farklı güzergahlara gitmesi gereken öğrenciler servis planını zorlaştırabilir. Aşağıda bu durumlar listelenmiştir:")

        # Aynı saatte birden fazla BENZERSİZ güzergah olan saatleri bul
        cakisma_listesi = []
        for saat in df['Saat'].unique():
            saatlik_dilim = df[df['Saat'] == saat]
            farkli_guzergahlar = saatlik_dilim['Güzergah'].dropna().unique()
            
            if len(farkli_guzergahlar) > 1:
                cakisma_listesi.append({
                    "Saat": saat,
                    "Öğrenci Sayısı": len(saatlik_dilim),
                    "Çakışan Güzergahlar": " ↔️ ".join(farkli_guzergahlar),
                    "Öğrenciler": ", ".join(saatlik_dilim['Adı'].tolist())
                })

        if cakisma_listesi:
            cakisma_df = pd.DataFrame(cakisma_listesi)
            st.warning(f"⚠️ Toplam {len(cakisma_df)} saat diliminde güzergah karmaşası tespit edildi!")
            st.table(cakisma_df)
        else:
            st.success("✅ Güzergahlar saatlere göre uyumlu görünüyor.")

        # --- 3. ÖZEL DERS TÜRÜ KONTROLÜ (DİKKAT!) ---
        st.subheader("🗣️ Dil Konuşma Kontenjanı (Maks: 3)")
        dk_df = df[df['Ders Türü'].str.contains('Dil', case=False, na=False)]
        dk_sayim = dk_df.groupby('Saat').size()
        dk_hata = dk_sayim[dk_sayim > 3]

        if not dk_hata.empty:
            for s, sayi in dk_hata.items():
                st.error(f"❌ Saat {s}: {sayi} Dil Konuşma öğrencisi var! (Limit 3)")

    except Exception as e:
        st.error(f"Dosya işlenirken hata oluştu. Lütfen CSV formatını kontrol edin. Hata: {e}")

else:
    st.write("Lütfen analiz için sol taraftan dosyanızı seçin.")
