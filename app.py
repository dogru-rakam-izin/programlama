import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Rehabilitasyon Program Denetleyici", layout="wide")
st.title("🗓️ Çizelge Formatlı Program Denetimi")

uploaded_file = st.file_uploader("Çizelge CSV dosyasını yükleyin", type=["csv"])

if uploaded_file:
    try:
        # Dosyayı oku
        content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        raw_df = pd.read_csv(io.StringIO(content), sep=ayirici)

        # --- DÖNÜŞTÜRME MANTIĞI ---
        # Sizin tablonuzdaki saat sütunlarını tespit edelim (Örn: 09:00, 10:00 olanlar)
        saat_sutunlari = [c for c in raw_df.columns if ':' in c or any(char.isdigit() for char in c)]
        
        program_listesi = []

        for index, row in raw_df.iterrows():
            personel = row['PERSONEL'] if 'PERSONEL' in raw_df.columns else "Bilinmiyor"
            
            for saat in saat_sutunlari:
                hucre_verisi = str(row[saat])
                
                # Eğer hücre boş değilse (nan, Empty vb. değilse)
                if hucre_verisi.strip() != "" and hucre_verisi.lower() != "nan":
                    # Burada hücre içindeki veriyi (Örn: "Ahmet - Dil - Güzergah 1") 
                    # parçalamamız gerekebilir. Şimdilik bütün olarak alıyoruz.
                    program_listesi.append({
                        "Personel": personel,
                        "Saat": saat,
                        "Veri": hucre_verisi
                    })

        # Yeni düzenli tabloyu oluştur
        df = pd.DataFrame(program_listesi)

        if not df.empty:
            st.success("✅ Çizelge başarıyla analiz edildi.")
            
            # --- 1. ÇAKIŞMA KONTROLÜ ---
            st.subheader("🕵️ Aynı Saatteki Yoğunluk")
            saatlik_ozet = df.groupby('Saat').size().reset_index(name='Öğrenci Sayısı')
            st.dataframe(saatlik_ozet)

            # --- 2. AYNI SAATTEKİ ÖĞRENCİLER VE PERSONEL ---
            st.subheader("🔍 Saatlik Detaylar")
            secilen_saat = st.selectbox("Detay görmek istediğiniz saati seçin:", df['Saat'].unique())
            detay = df[df['Saat'] == secilen_saat]
            st.table(detay)

            # --- 3. DİL KONUŞMA UYARISI ---
            # Veri içinde "Dil" kelimesi geçiyorsa sayalım
            dk_sayisi = df[df['Veri'].str.contains('Dil', case=False, na=False)].groupby('Saat').size()
            dk_hata = dk_sayisi[dk_sayisi > 3]

            if not dk_hata.empty:
                for s, sayi in dk_hata.items():
                    st.error(f"⚠️ Saat {s} diliminde {sayi} Dil Konuşma kaydı var! (Sınır 3)")
            else:
                st.info("Dil Konuşma kontenjanı şu an için uygun görünüyor.")
        
        else:
            st.warning("Dosya okundu ama içinde veri bulunamadı.")

    except Exception as e:
        st.error(f"Analiz Hatası: {e}")
        st.info("Dosyanızın ilk satırı saatlerden oluşmalı (09:00, 10:00 vb.).")
