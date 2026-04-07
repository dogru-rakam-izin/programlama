import streamlit as st
import pandas as pd

# 1. HAFIZA YAPILANDIRMASI
st.set_page_config(page_title="Doğru Rakam Akademi - Program Denetçi", layout="wide")

if 'program_data' not in st.session_state:
    st.session_state.program_data = None

# Yan Menü
st.sidebar.image("https://via.placeholder.com/150?text=REHAB+LOGO") # İsterseniz kurum logonuzu koyabilirsiniz
menu = ["🏠 Ana Sayfa", "📤 Program Yükle ve Denetle", "🔍 Öğrenci Sorgula"]
choice = st.sidebar.selectbox("Menü", menu)

# --- ANA SAYFA ---
if choice == "🏠 Ana Sayfa":
    st.title("Rehabilitasyon Merkezi Program Yönetimi")
    st.info("Sol menüden 'Program Yükle' kısmına geçerek günlük CSV dosyanızı sisteme tanıtabilirsiniz.")
    
    if st.session_state.program_data is not None:
        st.success(f"Sistemde şu an aktif bir program yüklü ({len(st.session_state.program_data)} kayıt).")
    else:
        st.warning("Şu an sistemde yüklü bir program bulunmuyor.")

# --- PROGRAM YÜKLE VE DENETLE ---
elif choice == "📤 Program Yükle ve Denetle":
    st.header("Günlük Program Denetimi")
    
    file = st.file_uploader("CSV dosyasını buraya yükleyin", type=["csv"])
    
    if file:
        try:
            # Dosyanızdaki noktalı virgül (;) ayrımını otomatik çözen ayar:
            df = pd.read_csv(file, sep=';', encoding='utf-8')
            
            # Sütun isimlerini temizle
            df.columns = [str(c).strip() for c in df.columns]
            st.session_state.program_data = df
            
            # --- 3 ÖĞRENCİ SINIRI KONTROLÜ ---
            st.subheader("⚠️ Kontenjan Kontrolü")
            
            # "Dil ve Konuşma" veya "Dil Konuşma" içerenleri yakala
            dk_filtre = df[df['Ders Türü'].str.contains('Dil', case=False, na=False)]
            
            # Saate göre grupla
            saatlik_sayim = dk_filtre.groupby('Saat').size()
            limit_asanlar = saatlik_sayim[saatlik_sayim > 3]

            if not limit_asanlar.empty:
                st.error(f"DİKKAT: Aşağıdaki saatlerde 3 öğrenci sınırı aşılmıştır!")
                for saat, sayi in limit_asanlar.items():
                    st.warning(f"🕒 **Saat {saat}:** {sayi} Dil Konuşma Öğrencisi Tespit Edildi.")
            else:
                st.success("✅ Harika! Tüm Dil Konuşma seansları limit (3) dahilinde.")

            # Tabloyu Göster
            st.divider()
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Dosya okunurken bir hata oluştu: {e}")

# --- ÖĞRENCİ SORGULA ---
elif choice == "🔍 Öğrenci Sorgula":
    st.header("Öğrenci ve Güzergah Takibi")
    
    if st.session_state.program_data is not None:
        df = st.session_state.program_data
        
        c1, c2 = st.columns(2)
        with c1:
            guzergah_list = ["Hepsi"] + list(df['Güzergah'].dropna().unique())
            secilen_guz = st.selectbox("Güzergah Seçin", guzergah_list)
        with c2:
            arama = st.text_input("Öğrenci İsmi Yazın")

        # Filtreleme
        temp_df = df.copy()
        if secilen_guz != "Hepsi":
            temp_df = temp_df[temp_df['Güzergah'] == secilen_guz]
        if arama:
            temp_df = temp_df[temp_df['Adı'].str.contains(arama, case=False, na=False)]

        st.table(temp_df)
    else:
        st.info("Lütfen önce program dosyasını yükleyin.")
