import streamlit as st
import pandas as pd

# 1. SAYFA AYARLARI VE HAFIZA (SESSION STATE) YAPILANDIRMASI
st.set_page_config(page_title="Rehabilitasyon Yönetim Sistemi", layout="wide")

if 'veri' not in st.session_state:
    st.session_state.veri = None

# 2. YAN MENÜ (SIDEBAR)
st.sidebar.title("🚀 Yönetim Paneli")
menu = ["Ana Sayfa", "Program Yükle & Kontrol", "Öğrenci Listesi"]
choice = st.sidebar.selectbox("Gitmek istediğiniz menü:", menu)

# --- ANA SAYFA ---
if choice == "Ana Sayfa":
    st.title("Hoş Geldiniz")
    st.markdown("""
    Bu sistemle rehabilitasyon merkezinizin günlük işleyişini kolaylaştırabilirsiniz:
    * **Program Kontrol:** Excel/CSV yükleyerek Dil ve Konuşma kontenjanlarını denetleyin.
    * **Öğrenci Listesi:** Yüklenen veriler üzerinden hızlı arama yapın.
    """)

# --- PROGRAM YÜKLE & KONTROL ---
elif choice == "Program Yükle & Kontrol":
    st.header("🗓️ Ders Programı Denetimi")
    
    uploaded_file = st.file_uploader("Dosyayı Buraya Bırakın (Excel veya CSV)", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            # Dosya tipine göre okuma
            if uploaded_file.name.endswith('.csv'):
                # CSV için farklı kodlamaları deniyoruz (Türkçe karakterler için)
                try:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
                except:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin5')
            else:
                df = pd.read_excel(uploaded_file)

            # Sütun isimlerini temizle (Baş ve sondaki boşlukları sil)
            df.columns = [str(c).strip() for c in df.columns]
            
            # Veriyi hafızaya al
            st.session_state.veri = df
            st.success("Dosya başarıyla yüklendi!")

            # --- DİL KONUŞMA KONTENJAN KONTROLÜ ---
            # Sütun isimlerini esnek hale getiriyoruz (Küçük/Büyük harf duyarlılığı için)
            ders_sutunu = next((c for c in df.columns if c.lower() == 'ders türü'), None)
            saat_sutunu = next((c for c in df.columns if c.lower() == 'saat'), None)

            if ders_sutunu and saat_sutunu:
                # "Dil" içeren tüm ders türlerini filtrele
                dk_ogrencileri = df[df[ders_sutunu].str.contains('Dil', case=False, na=False)]
                
                # Saat başı sayım yap
                saatlik_sayi = dk_ogrencileri.groupby(saat_sutunu).size()
                limit_asanlar = saatlik_sayi[saatlik_sayi > 3]

                if not limit_asanlar.empty:
                    st.error(f"🚨 KRİTİK UYARI: Toplam {len(limit_asanlar)} saat diliminde 3 öğrenci sınırı aşıldı!")
                    
                    # Şık metrik gösterimi
                    m_cols = st.columns(len(limit_asanlar))
                    for i, (saat, sayi) in enumerate(limit_asanlar.items()):
                        with m_cols[i % 4]:
                            st.metric(label=f"Saat: {saat}", value=f"{sayi} Öğrenci", delta="Limit Aşımı")
                else:
                    st.success("✅ Kontenjan Kontrolü: Tüm saatler 3 öğrenci sınırının altında.")
            else:
                st.warning(f"Uyarı: Dosyada 'Ders Türü' veya 'Saat' sütunu tam olarak bulunamadı. Mevcut sütunlar: {list(df.columns)}")

            # Yüklenen verinin önizlemesi
            st.divider()
            st.subheader("📋 Yüklenen Veri Önizlemesi")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# --- ÖĞRENCİ LİSTESİ (ARAMA) ---
elif choice == "Öğrenci Listesi":
    st.header("🔍 Öğrenci ve Güzergah Takibi")
    
    if st.session_state.veri is not None:
        df = st.session_state.veri
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            guzergah_sutunu = next((c for c in df.columns if c.lower() == 'güzergah'), None)
            if guzergah_sutunu:
                guzergahlar = ["Hepsi"] + list(df[guzergah_sutunu].unique())
                secilen = st.selectbox("Güzergaha Göre Filtrele", guzergahlar)
            else:
                st.warning("Güzergah sütunu bulunamadı.")
                secilen = "Hepsi"

        with col2:
            isim_sutunu = next((c for c in df.columns if c.lower() == 'adı'), None)
            arama = st.text_input("Öğrenci Adı ile Ara")

        # Filtreleme mantığı
        filtreli_df = df.copy()
        if secilen != "Hepsi":
            filtreli_df = filtreli_df[filtreli_df[guzergah_sutunu] == secilen]
        if arama and isim_sutunu:
            filtreli_df = filtreli_df[filtreli_df[isim_sutunu].str.contains(arama, case=False, na=False)]

        st.dataframe(filtreli_df, use_container_width=True)
        st.caption(f"Toplam {len(filtreli_df)} kayıt listeleniyor.")
    else:
        st.info("Henüz bir veri yüklenmedi. Lütfen 'Program Yükle & Kontrol' menüsünden dosyanızı yükleyin.")
