import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Rehabilitasyon Program Denetleyici", layout="wide")

st.title("⚖️ Program Çakışma ve Güzergah Denetimi")

uploaded_file = st.file_uploader("Program CSV dosyasını yükleyin", type=["csv"])

if uploaded_file:
    try:
        # 1. AYIRICI VE ENCODING TESPİTİ
        # Dosyayı önce bayt olarak okuyup ayırıcıyı (sep) tahmin edelim
        content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        if ';' in content.splitlines()[0]:
            ayirici = ';'
        else:
            ayirici = ','
        
        # Datayı oku
        df = pd.read_csv(io.StringIO(content), sep=ayirici)
        
        # 2. SÜTUN İSİMLERİNİ TEMİZLE VE STANDARTLAŞTIR
        # Görünmeyen boşlukları sil ve her şeyi küçük harfe çevirerek eşleştirme yapalım
        df.columns = [c.strip() for c in df.columns]
        sutun_haritasi = {c.lower(): c for c in df.columns}

        # İhtiyacımız olan sütunların dosyadaki gerçek isimlerini bulalım
        saat_col = sutun_haritasi.get('saat')
        guzergah_col = sutun_haritasi.get('güzergah')
        adi_col = sutun_haritasi.get('adı')
        ders_col = sutun_haritasi.get('ders türü')

        if saat_col and adi_col:
            # --- ANALİZ BAŞLIYOR ---
            st.success(f"Dosya başarıyla yüklendi. (Ayırıcı: '{ayirici}')")
            
            # 1. SAATLİK YOĞUNLUK
            st.subheader("🕵️ Saatlik Genel Yoğunluk")
            saat_ozet = df.groupby(saat_col).agg(
                Öğrenci_Sayısı=(adi_col, 'count'),
                Güzergahlar=(guzergah_col, lambda x: ", ".join(x.dropna().unique()) if guzergah_col else "Yok")
            ).reset_index()
            st.dataframe(saat_ozet, use_container_width=True)

            # 2. GÜZERGAH ÇAKIŞMA ANALİZİ
            if guzergah_col:
                st.subheader("🚐 Güzergah Çakışma Analizi")
                cakisma_listesi = []
                for saat in df[saat_col].unique():
                    saatlik_dilim = df[df[saat_col] == saat]
                    farkli_guzergahlar = saatlik_dilim[guzergah_col].dropna().unique()
                    
                    if len(farkli_guzergahlar) > 1:
                        cakisma_listesi.append({
                            "Saat": saat,
                            "Öğrenci Sayısı": len(saatlik_dilim),
                            "Çakışan Güzergahlar": " ↔️ ".join(farkli_guzergahlar),
                            "Öğrenciler": ", ".join(saatlik_dilim[adi_col].astype(str).tolist())
                        })

                if cakisma_listesi:
                    st.warning(f"⚠️ {len(cakisma_listesi)} saat diliminde farklı güzergahlar çakışıyor!")
                    st.table(pd.DataFrame(cakisma_listesi))
                else:
                    st.success("✅ Güzergahlar saatlere göre uyumlu.")

            # 3. DİL KONUŞMA KONTROLÜ
            if ders_col:
                st.subheader("🗣️ Dil Konuşma Kontenjanı (Maks: 3)")
                dk_df = df[df[ders_col].str.contains('Dil', case=False, na=False)]
                dk_sayim = dk_df.groupby(saat_col).size()
                dk_hata = dk_sayim[dk_sayim > 3]

                if not dk_hata.empty:
                    for s, sayi in dk_hata.items():
                        st.error(f"❌ Saat {s}: {sayi} Dil Konuşma öğrencisi var!")
                else:
                    st.success("✅ Kontenjanlar uygun.")
        else:
            st.error(f"Hata: Dosyada 'Saat' veya 'Adı' sütunu bulunamadı.")
            st.info(f"Tespit edilen sütunlar: {list(df.columns)}")

    except Exception as e:
        st.error(f"Dosya işlenirken teknik bir hata oluştu: {e}")
