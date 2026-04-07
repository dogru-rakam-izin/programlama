import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Doğru Rakam Akademi - Denetim", layout="wide")

st.title("🎯 Akıllı Program Denetleyicisi")
st.markdown("Ad ve Soyad sütunlarını güvenli şekilde birleştirerek denetim yapar.")

# 1. DOSYA YÜKLEME
col1, col2 = st.columns(2)
with col1:
    master_file = st.file_uploader("📋 1. Ana Öğrenci Listesini Yükleyin", type=["xlsx", "csv"])
with col2:
    daily_file = st.file_uploader("🗓️ 2. Günlük Çizelgeyi Yükleyin (CSV)", type=["csv"])

if master_file and daily_file:
    try:
        # --- ANA LİSTEYİ OKU ---
        if master_file.name.endswith('.csv'):
            m_df = pd.read_csv(master_file, sep=None, engine='python')
        else:
            m_df = pd.read_excel(master_file)
        
        # Sütun isimlerini temizle
        m_df.columns = [str(c).strip().lower() for c in m_df.columns]
        
        # AD ve SOYAD sütunlarını bul
        ad_col = next((c for c in m_df.columns if 'ad' in c and 'soyad' not in c), None)
        soyad_col = next((c for c in m_df.columns if 'soyad' in c), None)
        
        m_isim_col = None
        if ad_col and soyad_col:
            # HATA ÇÖZÜMÜ: Sütunları önce stringe çevir, boşları boşlukla doldur, sonra küçük harf yap
            m_df['tam_isim'] = (
                m_df[ad_col].astype(str).replace('nan', '').str.strip() + " " + 
                m_df[soyad_col].astype(str).replace('nan', '').str.strip()
            ).str.lower()
            m_isim_col = 'tam_isim'
            st.sidebar.success(f"Eşleştirme Başarılı: {ad_col} + {soyad_col}")
        else:
            # Tek bir birleşik sütun varsa (Ad Soyad gibi)
            m_isim_col = next((c for c in m_df.columns if 'ad' in c and 'soyad' in c), None)
            if m_isim_col:
                m_df[m_isim_col] = m_df[m_isim_col].astype(str).str.lower().str.strip()

        # Branş ve Güzergah sütunları
        m_ders_col = next((c for c in m_df.columns if any(k in c for k in ['ders', 'branş', 'engel', 'grup'])), None)
        m_guz_col = next((c for c in m_df.columns if any(k in c for k in ['güz', 'servis', 'güzergah', 'tur'])), None)

        # --- GÜNLÜK ÇİZELGEYİ OKU ---
        content = daily_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        # İlk satırı (gün adı) atla
        d_df = pd.read_csv(io.StringIO(content), sep=ayirici, skiprows=1)
        d_df.columns = [str(c).strip() for c in d_df.columns]

        saat_sutunlari = [c for c in d_df.columns if ':' in c]
        denetim_sonuclari = []

        if m_isim_col:
            for _, row in d_df.iterrows():
                personel = str(row['PERSONEL']).strip() if 'PERSONEL' in d_df.columns else "Bilinmiyor"
                for saat in saat_sutunlari:
                    cizelge_ismi = str(row[saat]).strip().lower()
                    
                    if cizelge_ismi != "" and cizelge_ismi != "nan":
                        # Ana listede bu ismi ara
                        eslesme = m_df[m_df[m_isim_col].str.contains(cizelge_ismi, case=False, na=False)]
                        
                        if not eslesme.empty:
                            bilgi = eslesme.iloc[0]
                            denetim_sonuclari.append({
                                "Saat": saat,
                                "Personel": personel,
                                "Öğrenci": cizelge_ismi.upper(),
                                "Branş": bilgi.get(m_ders_col, "Belirtilmemiş") if m_ders_col else "Bilinmiyor",
                                "Güzergah": bilgi.get(m_guz_col, "Belirtilmemiş") if m_guz_col else "Bilinmiyor",
                                "Durum": "✅ Kayıtlı"
                            })
                        else:
                            denetim_sonuclari.append({
                                "Saat": saat, "Personel": personel, "Öğrenci": cizelge_ismi.upper(),
                                "Branş": "Eşleşme Yok", "Güzergah": "Eşleşme Yok", "Durum": "⚠️ Liste Dışı"
                            })

            analiz_df = pd.DataFrame(denetim_sonuclari)

            # --- RAPORLAMA ---
            st.divider()
            
            # Dil Konuşma Kontenjan Kontrolü
            st.subheader("🚨 Dil ve Konuşma Kontenjanı (Sınır: 3)")
            if not analiz_df.empty:
                dk_analiz = analiz_df[analiz_df['Branş'].astype(str).str.contains('dil', case=False, na=False)]
                dk_sayim = dk_analiz.groupby('Saat').size()
                hatalar = dk_sayim[dk_sayim > 3]

                if not hatalar.empty:
                    for s, sayi in hatalar.items():
                        st.error(f"**Saat {s}:** {sayi} Dil Konuşma öğrencisi var!")
                else:
                    st.success("Tüm saatler kontenjana uygundur.")

            st.subheader("📋 Detaylı Analiz Listesi")
            st.dataframe(analiz_df, use_container_width=True)
        else:
            st.error("Hata: Ana listede isim sütunları (Ad / Soyad) bulunamadı.")
            st.info(f"Mevcut sütunlar: {list(m_df.columns)}")

    except Exception as e:
        st.error(f"Teknik bir sorun oluştu: {e}")
