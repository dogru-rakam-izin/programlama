import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Rehabilitasyon Program Denetleyici", layout="wide")

st.title("🗓️ Akıllı Ders Programı ve Kontrol Paneli")
st.markdown("Excel dosyanızı yükleyerek kontenjan ve güzergah kontrollerini yapabilirsiniz.")

# 1. Dosya Yükleme Alanı
uploaded_file = st.file_uploader("Program Excelini Yükleyin", type=["xlsx", "xls"])

if uploaded_file:
    # Excel'i oku
    df = pd.read_excel(uploaded_file)
    
    # Boşlukları temizle (Sütun isimlerinde hata olmaması için)
    df.columns = df.columns.str.strip()

    # --- KONTROL MEKANİZMASI ---
    
    # Gerekli sütunların varlığını kontrol et
    required_cols = ['Adı', 'Soyadı', 'Saat', 'Ders Türü', 'Güzergah']
    if all(col in df.columns for col in required_cols):
        
        # Dil ve Konuşma öğrencilerini filtrele (Küçük/büyük harf duyarlılığını azaltmak için)
        dk_filtre = df[df['Ders Türü'].str.contains('Dil', case=False, na=False)]
        
        # Saatlere göre grupla ve say
        saatlik_sayim = dk_filtre.groupby('Saat').size()
        
        # Hata veren (3'ten fazla olan) saatleri bul
        hatali_saatler = saatlik_sayim[saatlik_sayim > 3]

        # --- UYARI EKRANI ---
        if not hatali_saatler.empty:
            st.error(f"🚨 KRİTİK UYARI: Toplam {len(hatali_saatler)} farklı saat diliminde Dil ve Konuşma öğrenci sınırı aşıldı!")
            
            cols = st.columns(len(hatali_saatler) if len(hatali_saatler) < 4 else 4)
            for i, (saat, sayi) in enumerate(hatali_saatler.items()):
                with cols[i % 4]:
                    st.metric(label=f"Saat: {saat}", value=f"{sayi} Öğrenci", delta="Limit Aşımı", delta_color="inverse")
        else:
            st.success("✅ Tüm saat dilimleri uygun. Dil ve Konuşma yoğunluğu limitlerin altında.")

        # --- GÜZERGAH VE LİSTELEME ---
        st.divider()
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("🚐 Güzergah Filtresi")
            secilen_guzergah = st.selectbox("Görüntülenecek Güzergah", ["Hepsi"] + list(df['Güzergah'].unique()))
        
        with col2:
            st.subheader("📋 Ders Listesi")
            if secilen_guzergah != "Hepsi":
                gosterilecek_df = df[df['Güzergah'] == secilen_guzergah]
            else:
                gosterilecek_df = df
            
            st.dataframe(gosterilecek_df, use_container_width=True)

    else:
        st.warning(f"Lütfen Excel dosyanızdaki sütun isimlerinin şunlar olduğundan emin olun: {', '.join(required_cols)}")

else:
    st.info("Sistemin çalışması için lütfen üstteki alandan ders programı Excel'inizi yükleyin.")
