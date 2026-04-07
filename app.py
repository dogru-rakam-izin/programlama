import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Rehabilitasyon Program Denetleyici", layout="wide")

st.title("🗓️ Çizelge Formatlı Akıllı Denetim Sistemi")
st.markdown("SALI, ÇARŞAMBA gibi gün isimli çizelge dosyalarınız için optimize edilmiştir.")

# Dosya Yükleme
uploaded_file = st.file_uploader("Günlük Program CSV Dosyasını Seçin", type=["csv"])

if uploaded_file:
    try:
        # 1. Dosyayı Oku (Ayırıcıyı ve Başlık Satırını Yönet)
        content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        
        # İlk satırda gün ismi (SALI vb.) olduğu için 1. satırı başlık kabul ediyoruz
        df_raw = pd.read_csv(io.StringIO(content), sep=ayirici, skiprows=1)
        
        # Sütun isimlerini temizle
        df_raw.columns = [str(c).strip() for c in df_raw.columns]
        
        # Saat sütunlarını tespit et (İçinde ':' geçen başlıklar)
        saat_sutunlari = [c for c in df_raw.columns if ':' in c]

        if not saat_sutunlari:
            st.error("Hata: Dosyada saat sütunları (09:00, 10:00 vb.) tespit edilemedi.")
            st.info(f"Mevcut Sütunlar: {list(df_raw.columns)}")
        else:
            # 2. Veriyi Anlamlı Bir Listeye Dönüştür
            liste_verisi = []
            for _, row in df_raw.iterrows():
                personel = str(row['PERSONEL']).strip() if 'PERSONEL' in df_raw.columns else "Belirsiz"
                
                for saat in saat_sutunlari:
                    hucre = str(row[saat]).strip()
                    if hucre != "" and hucre.lower() != "nan":
                        liste_verisi.append({
                            "Saat": saat,
                            "Personel": personel,
                            "Ogrenci_Verisi": hucre
                        })

            final_df = pd.DataFrame(liste_verisi)

            # --- DENETİM BAŞLIYOR ---
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🗣️ Dil Konuşma Kontrolü")
                # Hücre içinde "Dil" kelimesi geçenleri bul
                dk_df = final_df[final_df['Ogrenci_Verisi'].str.contains('Dil', case=False, na=False)]
                dk_sayim = dk_df.groupby('Saat').size()
                
                limit_asanlar = dk_sayim[dk_sayim > 3]
                if not limit_asanlar.empty:
                    for s, sayi in limit_asanlar.items():
                        st.error(f"🚨 Saat {s}: {sayi} Dil Konuşma öğrencisi var! (Sınır 3)")
                else:
                    st.success("✅ Dil ve Konuşma kontenjanı uygun.")

            with col2:
                st.subheader("🚐 Güzergah/Saat Yoğunluğu")
                saat_ozet = final_df.groupby('Saat').size().reset_index(name='Öğrenci Sayısı')
                st.bar_chart(saat_ozet.set_index('Saat'))

            # --- DETAYLI TABLO ---
            st.divider()
            st.subheader("📋 Saatlik Detaylı Liste")
            secilen_saat = st.selectbox("Bir saat seçin:", ["Hepsi"] + list(final_df['Saat'].unique()))
            
            if secilen_saat != "Hepsi":
                gosterilecek = final_df[final_df['Saat'] == secilen_saat]
            else:
                gosterilecek = final_df
                
            st.dataframe(gosterilecek, use_container_width=True)

    except Exception as e:
        st.error(f"Dosya işlenirken bir hata oluştu: {e}")
else:
    st.info("Lütfen bir günün program dosyasını (CSV) yükleyin.")
