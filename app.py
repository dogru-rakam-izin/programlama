import streamlit as st
import pandas as pd

# 1. Menü Yapılandırması
menu = ["Kayıt Paneli", "Öğrenci Takip", "Program Kontrol 🗓️"]
choice = st.sidebar.selectbox("Menü", menu)

# --- PROGRAM KONTROL SEKEMESİ ---
if choice == "Program Kontrol 🗓️":
    st.header("Akıllı Ders Programı ve Kontrol Paneli")
    
    uploaded_file = st.file_uploader("Ders Programı Excelini Buraya Bırakın", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip() # Başlık temizliği

        # 2. Mantıksal Filtreler ve Kontroller
        # Ders Türü sütununda "Dil" geçenleri bulur
        dk_ogrencileri = df[df['Ders Türü'].str.contains('Dil', case=False, na=False)]
        
        # Saat başına öğrenci sayısını hesapla
        saatlik_ozet = dk_ogrencileri.groupby('Saat').size()
        
        # 3 kişiyi geçen saatleri tespit et
        asimi_yapanlar = saatlik_ozet[saatlik_ozet > 3]

        # 3. Görsel Uyarılar
        if not asimi_yapanlar.empty:
            st.error(f"⚠️ DİKKAT: Dil ve Konuşma limitini aşan {len(asimi_yapanlar)} saat var!")
            
            # Yan yana metrikler halinde gösterelim
            cols = st.columns(len(asimi_yapanlar))
            for i, (saat, sayi) in enumerate(asimi_yapanlar.items()):
                with cols[i]:
                    st.metric(label=f"Saat: {saat}", value=f"{sayi} Kişi", delta="+3 Limit Aşımı", delta_color="inverse")
        else:
            st.success("✅ Dil ve Konuşma programı dengeli (Maksimum 3 öğrenci).")

        # 4. Güzergah Filtreleme (Sizin için lojistik kolaylık)
        st.divider()
        guzergahlar = ["Hepsi"] + list(df['Güzergah'].unique())
        secilen_guzergah = st.selectbox("🚛 Güzergaha Göre Filtrele", guzergahlar)

        if secilen_guzergah != "Hepsi":
            gosterilecek_df = df[df['Güzergah'] == secilen_guzergah]
        else:
            gosterilecek_df = df

        st.dataframe(gosterilecek_df, use_container_width=True)
        
    else:
        st.info("Lütfen güncel ders programı dosyanızı yükleyin.")

# Diğer menü seçenekleriniz (Kayıt Paneli vb.) buranın altında devam eder...
