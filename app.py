import streamlit as st
import pandas as pd

# 1. HAFIZA BAŞLATMA (Verilerin kaybolmaması için)
if 'ogrenci_verisi' not in st.session_state:
    st.session_state.ogrenci_verisi = None

# Yan Menü
menu = ["Kayıt Paneli", "Öğrenci Takip", "Program Kontrol 🗓️"]
choice = st.sidebar.selectbox("Menü", menu)

# --- KAYIT PANELİ (Veri Giriş Alanı) ---
if choice == "Kayıt Paneli":
    st.header("📝 Yeni Öğrenci Kaydı")
    # Burada manuel kayıt formunuz olduğunu varsayıyorum
    # Örnek: st.text_input("Adı"), st.button("Kaydet") vb.
    st.info("Manuel kayıt formunu buraya ekleyebilirsiniz. Şu an Excel yükleme odaklı ilerliyoruz.")

# --- PROGRAM KONTROL (Excel Yükleme ve Uyarı) ---
elif choice == "Program Kontrol 🗓️":
    st.header("🗓️ Program Denetleme ve Veri Yükleme")
    
    uploaded_file = st.file_uploader("Güncel Excel Dosyasını Yükleyin", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()
        
        # YÜKLENEN VERİYİ HAFIZAYA AL (Diğer sekmelerde görmek için)
        st.session_state.ogrenci_verisi = df
        
        # Kontroller (Dil Konuşma Sınırı)
        dk_ogrencileri = df[df['Ders Türü'].str.contains('Dil', case=False, na=False)]
        saatlik_sayim = dk_ogrencileri.groupby('Saat').size()
        asimi_yapanlar = saatlik_sayim[saatlik_sayim > 3]

        if not asimi_yapanlar.empty:
            st.error(f"⚠️ Dil Konuşma Sınırı Aşıldı!")
            st.write(asimi_yapanlar)
        else:
            st.success("✅ Program kurallara uygun.")
            
        st.dataframe(df)

# --- ÖĞRENCİ TAKİP (Hafızadaki Veriyi Gösteren Yer) ---
elif choice == "Öğrenci Takip":
    st.header("🔍 Kayıtlı Öğrenci Listesi")
    
    # Hafızada veri var mı kontrol et
    if st.session_state.ogrenci_verisi is not None:
        veri = st.session_state.ogrenci_verisi
        
        # Arama kutusu ekleyelim
        arama = st.text_input("Öğrenci Adı ile Ara")
        if arama:
            filtreli_veri = veri[veri['Adı'].str.contains(arama, case=False, na=False)]
            st.dataframe(filtreli_veri)
        else:
            st.dataframe(veri)
    else:
        st.warning("⚠️ Henüz bir veri yüklenmedi. Lütfen 'Program Kontrol' sekmesinden Excel dosyasını yükleyin.")
