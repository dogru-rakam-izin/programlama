import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Rehabilitasyon Denetim Sistemi", layout="wide")

st.title("🎯 Akıllı Program Denetleyicisi")
st.markdown("Ana listedeki verilere bakarak günlük çizelgeyi otomatik kontrol eder.")

# 1. DOSYA YÜKLEME
col1, col2 = st.columns(2)
with col1:
    master_file = st.file_uploader("📋 Tüm Öğrenci Bilgileri (Ana Liste / Excel)", type=["xlsx", "csv"])
with col2:
    daily_file = st.file_uploader("🗓️ Günlük Çizelge (SALI, ÇARŞAMBA vb. / CSV)", type=["csv"])

if master_file and daily_file:
    try:
        # --- ANA LİSTEYİ OKU ---
        if master_file.name.endswith('.csv'):
            m_df = pd.read_csv(master_file, sep=None, engine='python')
        else:
            m_df = pd.read_excel(master_file)
        
        # Sütun isimlerini temizle ve küçük harf yap
        m_df.columns = [str(c).strip().lower() for c in m_df.columns]
        
        # Sütunları Akıllıca Bul (İçinde 'ad', 'ders', 'güz' geçenleri yakala)
        m_isim_col = next((c for c in m_df.columns if 'ad' in c), None)
        m_ders_col = next((c for c in m_df.columns if 'ders' in c or 'branş' in c or 'engel' in c), None)
        m_guz_col = next((c for c in m_df.columns if 'güz' in c or 'servis' in c or 'güzergah' in c), None)

        # --- GÜNLÜK ÇİZELGEYİ OKU ---
        content = daily_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        # Çizelgelerin tepesindeki 'SALI' gibi gün ismini atlamak için skiprows=1
        d_df = pd.read_csv(io.StringIO(content), sep=ayirici, skiprows=1)
        d_df.columns = [str(c).strip() for c in d_df.columns]

        # Saat sütunlarını bul (09:00:00 gibi içinde ':' olanlar)
        saat_sutunlari = [c for c in d_df.columns if ':' in c]
        
        denetim_sonuclari = []

        # --- EŞLEŞTİRME VE DENETİM MOTORU ---
        if m_isim_col:
            for _, row in d_df.iterrows():
                personel = str(row['PERSONEL']).strip() if 'PERSONEL' in d_df.columns else "Bilinmiyor"
                
                for saat in saat_sutunlari:
                    cizelge_ismi = str(row[saat]).strip()
                    
                    # Eğer hücre boş değilse kontrol et
                    if cizelge_ismi != "" and cizelge_ismi.lower() != "nan":
                        # Ana listede bu öğrenciyi ara
                        eslesme = m_df[m_df[m_isim_col].str.contains(cizelge_ismi, case=False, na=False)]
                        
                        if not eslesme.empty:
                            bilgi = eslesme.iloc[0]
                            denetim_sonuclari.append({
                                "Saat": saat,
                                "Personel": personel,
                                "Öğrenci": cizelge_ismi,
                                "Ders Türü": bilgi.get(m_ders_col, "Bilinmiyor") if m_ders_col else "Bilinmiyor",
                                "Güzergah": bilgi.get(m_guz_col, "Bilinmiyor") if m_guz_col else "Bilinmiyor",
                                "Durum": "✅ Kayıtlı"
                            })
                        else:
                            denetim_sonuclari.append({
                                "Saat": saat, "Personel": personel, "Öğrenci": cizelge_ismi,
                                "Ders Türü": "Bulunamadı", "Güzergah": "Bulunamadı", "Durum": "⚠️ Ana Listede Yok"
                            })

            analiz_df = pd.DataFrame(denetim_sonuclari)

            # --- EKRANA RAPORLAMA ---
            st.divider()
            
            # 1. Kontenjan Kontrolü (Dil ve Konuşma)
            st.subheader("🚨 Dil ve Konuşma Kontenjan Uyarıları")
            if not analiz_df.empty:
                # Branş sütununda 'dil' geçenleri saatlik say
                dk_analiz = analiz_df[analiz_df['Ders Türü'].astype(str).str.contains('dil', case=False, na=False)]
                dk_sayim = dk_analiz.groupby('Saat').size()
                limit_asanlar = dk_sayim[dk_sayim > 3]

                if not limit_asanlar.empty:
                    for s, sayi in limit_asanlar.items():
                        st.error(f"Saat **{s}** seansında **{sayi}** Dil Konuşma öğrencisi var! (Limit: 3)")
                else:
                    st.success("Tüm Dil ve Konuşma seansları kontenjana uygun.")

            # 2. Detaylı Tablo
            st.subheader("🔍 Program Detayları ve Güzergahlar")
            st.dataframe(analiz_df, use_container_width=True)

        else:
            st.error("Hata: Ana listede öğrenci isimlerinin olduğu sütun (Ad Soyad) bulunamadı.")

    except Exception as e:
        st.error(f"Teknik bir hata oluştu: {e}")
