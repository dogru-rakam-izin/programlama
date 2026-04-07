import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Doğru Rakam Akademi - Denetim", layout="wide")

st.title("🎯 Akıllı Program Denetleyicisi")
st.markdown("Ayrı Ad-Soyad sütunlarını birleştirerek günlük çizelgeyle eşleştirme yapar.")

# 1. DOSYA YÜKLEME
col1, col2 = st.columns(2)
with col1:
    master_file = st.file_uploader("📋 Ana Öğrenci Listesi (Adı ve Soyadı ayrı sütunlarda olabilir)", type=["xlsx", "csv"])
with col2:
    daily_file = st.file_uploader("🗓️ Günlük Çizelge (SALI, CUMA vb.)", type=["csv"])

if master_file and daily_file:
    try:
        # --- ANA LİSTEYİ OKU VE HAZIRLA ---
        if master_file.name.endswith('.csv'):
            m_df = pd.read_csv(master_file, sep=None, engine='python')
        else:
            m_df = pd.read_excel(master_file)
        
        # Sütun isimlerini temizle
        m_df.columns = [str(c).strip().lower() for c in m_df.columns]
        
        # AD ve SOYAD sütunlarını tespit et
        ad_col = next((c for c in m_df.columns if 'adı' == c or 'ad' == c), None)
        soyad_col = next((c for c in m_df.columns if 'soyad' in c), None)
        
        if ad_col and soyad_col:
            # İki sütunu birleştirip 'tam_isim' oluştur (Eşleştirme için)
            m_df['tam_isim'] = m_df[ad_col].astype(str) + " " + m_df[soyad_col].astype(str)
            m_df['tam_isim'] = m_df['tam_isim'].str.strip().lower()
            m_isim_col = 'tam_isim'
        else:
            # Eğer zaten birleşik bir isim sütunu varsa onu bul
            m_isim_col = next((c for c in m_df.columns if 'ad' in c and 'soyad' in c) or (c for c in m_df.columns if 'ad' in c), None)

        m_ders_col = next((c for c in m_df.columns if 'ders' in c or 'branş' in c or 'engel' in c), None)
        m_guz_col = next((c for c in m_df.columns if 'güz' in c or 'servis' in c or 'güzergah' in c), None)

        # --- GÜNLÜK ÇİZELGEYİ OKU ---
        content = daily_file.getvalue().decode('utf-8', errors='ignore')
        ayirici = ';' if ';' in content.splitlines()[0] else ','
        d_df = pd.read_csv(io.StringIO(content), sep=ayirici, skiprows=1)
        d_df.columns = [str(c).strip() for c in d_df.columns]

        saat_sutunlari = [c for c in d_df.columns if ':' in c]
        denetim_sonuclari = []

        # --- EŞLEŞTİRME MOTORU ---
        if m_isim_col:
            for _, row in d_df.iterrows():
                personel = str(row['PERSONEL']).strip() if 'PERSONEL' in d_df.columns else "Bilinmiyor"
                
                for saat in saat_sutunlari:
                    cizelge_ismi = str(row[saat]).strip().lower()
                    
                    if cizelge_ismi != "" and cizelge_ismi != "nan":
                        # Ana listede bu ismi ara (İsim içinde geçiyor mu?)
                        eslesme = m_df[m_df[m_isim_col].str.contains(cizelge_ismi, case=False, na=False)]
                        
                        if not eslesme.empty:
                            bilgi = eslesme.iloc[0]
                            denetim_sonuclari.append({
                                "Saat": saat,
                                "Personel": personel,
                                "Öğrenci": cizelge_ismi.upper(),
                                "Branş": bilgi.get(m_ders_col, "Bilinmiyor") if m_ders_col else "Bilinmiyor",
                                "Güzergah": bilgi.get(m_guz_col, "Bilinmiyor") if m_guz_col else "Bilinmiyor",
                                "Durum": "✅ Doğrulandı"
                            })
                        else:
                            denetim_sonuclari.append({
                                "Saat": saat, "Personel": personel, "Öğrenci": cizelge_ismi.upper(),
                                "Branş": "Bulunamadı", "Güzergah": "Bulunamadı", "Durum": "⚠️ Listede Yok"
                            })

            analiz_df = pd.DataFrame(denetim_sonuclari)

            # --- RAPORLAMA ---
            st.divider()
            
            # Kontenjan Kontrolü
            st.subheader("🚨 Kontenjan Uyarıları (Dil ve Konuşma)")
            if not analiz_df.empty:
                dk_analiz = analiz_df[analiz_df['Branş'].astype(str).str.contains('dil', case=False, na=False)]
                dk_sayim = dk_analiz.groupby('Saat').size()
                limit_asanlar = dk_sayim[dk_sayim > 3]

                if not limit_asanlar.empty:
                    for s, sayi in limit_asanlar.items():
                        st.error(f"**Saat {s}:** {sayi} Dil Konuşma öğrencisi var! (Limit: 3)")
                else:
                    st.success("Kontenjanlar tüm saatlerde uygun.")

            st.subheader("🔍 Detaylı Program Analizi")
            st.dataframe(analiz_df, use_container_width=True)

        else:
            st.error("Hata: Ana listede isim sütunu tespit edilemedi.")

    except Exception as e:
        st.error(f"Teknik hata: {e}")
