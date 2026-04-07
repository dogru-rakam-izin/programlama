import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rehabilitasyon Program Takip", layout="wide")

st.title("🗓️ Ders Programı ve Kontrol Paneli")

# 1. Excel Dosyası Yükleme
uploaded_file = st.file_uploader("Ders Programı Excel Dosyasını Seçin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Veri setini görüntüle
    st.subheader("Mevcut Program")
    st.dataframe(df)

    # 2. Dil ve Konuşma Kontrolü
    # Not: Excel'inizde 'Saat' ve 'Ders_Turu' sütunları olduğunu varsayıyorum
    if 'Saat' in df.columns and 'Ders_Turu' in df.columns:
        
        # Saatlere göre gruplayıp Dil ve Konuşma öğrencilerini sayalım
        dk_sayimi = df[df['Ders_Turu'] == 'Dil Konuşma'].groupby('Saat').size()
        
        kritik_saatler = dk_sayimi[dk_sayimi > 3]

        if not kritik_saatler.empty:
            st.error("⚠️ DİKKAT: Dil ve Konuşma Kontenjanı Aşıldı!")
            for saat, sayi in kritik_saatler.items():
                st.warning(f"Saat {saat} diliminde {sayi} öğrenci var! (Limit: 3)")
        else:
            st.success("✅ Dil ve Konuşma öğrenci dağılımı limitler dahilinde.")

    # 3. Güzergah Filtreleme
    if 'Guzergah' in df.columns:
        st.divider()
        st.subheader("🚐 Güzergah Sorgulama")
        secilen_guzergah = st.selectbox("Güzergah Seçiniz", df['Guzergah'].unique())
        filtreli_df = df[df['Guzergah'] == secilen_guzergah]
        st.table(filtreli_df[['Saat', 'Ogrenci_Adı', 'Adres']])

else:
    st.info("Lütfen işlem yapmak için bir Excel dosyası yükleyin.")
