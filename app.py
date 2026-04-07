import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Rehabilitasyon Akıllı Denetim", layout="wide")

st.title("🛡️ Veri Tabanı Bağlantılı Program Denetimi")

# 1. DOSYA YÜKLEME ALANI
col_files = st.columns(2)
with col_files[0]:
    master_file = st.file_uploader("📋 Tüm Öğrenci Bilgileri (Ana Liste)", type=["xlsx", "csv"])
with col_files[1]:
    daily_file = st.file_uploader("🗓️ Günlük Program Çizelgesi", type=["csv"])

if master_file and daily_file:
    try:
        # ANA VERİ LİSTESİNİ OKU (Öğrenci Bilgileri)
        if master_file.name.endswith('.csv'):
            master_df = pd.read_csv(master_file, sep=None, engine='python')
        else:
            master_df = pd.read_excel(master_file)
        
        # Sütunları standartlaştır (Küçük harf ve boşluk temizliği)
        master_df.columns = [str(c).strip().lower() for c in master_df.columns]
        
        # GÜNLÜK PROGRAMI OKU (SALI, ÇARŞAMBA vb.)
        content = daily_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        daily_df_raw = pd.read_csv(io.StringIO(content), sep=ayirici, skiprows=1)
        daily_df_raw.columns = [str(c).strip() for c in daily_df_raw.columns]

        # Çizelgeyi Listeye Çevir (Dönüştürme)
        saat_sutunlari = [c for c in daily_df_raw.columns if ':' in c]
        islenen_liste = []

        for _, row in daily_df_raw.iterrows():
            personel = str(row['PERSONEL']).strip() if 'PERSONEL' in daily_df_raw.columns else "Bilinmiyor"
            for saat in saat_sutunlari:
                ogrenci_adi = str(row[saat]).strip()
                if ogrenci_adi != "" and ogrenci_adi.lower() != "nan":
                    # ANA LİSTEDEN ÖĞRENCİYİ BUL
                    # İsmi ana listede arıyoruz (büyük/küçük harf duyarsız)
                    match = master_df[master_df['adı'].str.contains(ogrenci_adi, case=False, na=False)]
                    
                    if not match.empty:
                        info = match.iloc[0]
                        islenen_liste.append({
                            "Saat": saat,
                            "Personel": personel,
                            "Öğrenci": ogrenci_adi,
                            "Ders Türü": info.get('ders türü', 'Bilinmiyor'),
                            "Kayıtlı Güzergah": info.get('güzergah', 'Bilinmiyor'),
                            "Adres": info.get('adres', 'Bilinmiyor'),
                            "Durum": "✅ Kayıtlı"
                        })
                    else:
                        islenen_liste.append({
                            "Saat": saat,
                            "Personel": personel,
                            "Öğrenci": ogrenci_adi,
                            "Ders Türü": "Bilinmiyor",
                            "Kayıtlı Güzergah": "Bilinmiyor",
                            "Adres": "Bilinmiyor",
                            "Durum": "⚠️ Kayıt Bulunamadı"
                        })

        analiz_df = pd.DataFrame(islenen_liste)

        # --- DENETİM RAPORU ---
        st.divider()
        st.subheader("📊 Otomatik Denetim Sonuçları")

        # 1. Dil Konuşma Sınırı Kontrolü
        dk_sayim = analiz_df[analiz_df['Ders Türü'].str.contains('Dil', case=False, na=False)].groupby('Saat').size()
        dk_hata = dk_sayim[dk_sayim > 3]

        if not dk_hata.empty:
            for s, sayi in dk_hata.items():
                st.error(f"🚨 **DİKKAT:** Saat {s}'de {sayi} tane Dil ve Konuşma öğrencisi var! (Sınır 3)")
        else:
            st.success("✅ Dil ve Konuşma kontenjanı tüm saatler için uygundur.")

        # 2. Güzergah Çakışma Kontrolü
        st.subheader("🚐 Güzergah ve Adres Analizi")
        secilen_saat = st.selectbox("Saat Seçin", analiz_df['Saat'].unique())
        saatlik_bakis = analiz_df[analiz_df['Saat'] == secilen_saat]
        st.table(saatlik_bakis[['Öğrenci', 'Personel', 'Kayıtlı Güzergah', 'Adres', 'Durum']])

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
else:
    st.info("Lütfen sol tarafa 'Tüm Öğrenci Listesini', sağ tarafa ise 'Günlük Çizelgeyi' yükleyin.")
