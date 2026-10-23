# Google Apps Script Kurulum Kılavuzu (2 Dakikada Tam Kurulum)

Bu kılavuz, Fatma'nın portala yüklediği soru fotoğraflarının otomatik olarak **Google Drive'ınıza kaydedilmesi**, **Google E-Tablo'ya işlenmesi** ve **Gmail adresinize anında fotoğraflı bildirim gelmesi** için gerekli 2 dakikalık kurulumu açıklar.

---

## 🚀 5 Adımda Kurulum

### 1. Adım: Yeni Bir Google E-Tablo Açın
1. Tarayıcınızda [sheets.google.com](https://sheets.google.com) adresine gidin.
2. Boş bir e-tablo oluşturun ve adını **`Fatma ÖZMİL - Soru Takip Çizelgesi`** yapın.

---

### 2. Adım: Apps Script Editörünü Açın
1. Üst menüden **Uzantılar (Extensions)** $\rightarrow$ **Apps Script** seçeneğine tıklayın.
2. Açılan kod editöründeki mevcut tüm yazıları silin (boşaltın).

---

### 3. Adım: Kodu Yapıştırın
1. Proje klasörünüzde bulunan [google_apps_script.js](file:///c:/Users/hizar/OneDrive/Desktop/projeler/FATMA%201.A%C5%9EAMA%20%C3%87ALI%C5%9EMA%20PROGRAMI%20%28%202026-2027%29/google_apps_script.js) dosyasının tüm içeriğini kopyalayın.
2. Apps Script editörüne yapıştırın.
3. *(İsteğe Bağlı)* Eğer bildirimlerin kendi Gmail'inizden farklı özel bir adrese gitmesini isterseniz 12. satırdaki `const NOTIFICATION_EMAIL = "";` tırnaklarının içine o e-postayı yazabilirsiniz. Boş bırakırsanız scripti çalıştıran kendi Gmail adresinize gönderir.
4. Üstteki **Kaydet (Disket)** simgesine basın.

---

### 4. Adım: Web Uygulaması Olarak Dağıtın (En Önemli Adım)
1. Sağ üst köşedeki mavi **Dağıt (Deploy)** butonuna tıklayın $\rightarrow$ **Yeni Dağıtım (New deployment)** seçin.
2. Sol taraftaki çark (ayar) simgesine basıp tür olarak **Web Uygulaması (Web app)** seçin.
3. Açılan pencerede şu iki ayarı yapın:
   * **Çalıştıran (Execute as):** `Ben (<sizin_mailiniz@gmail.com>)` (Varsayılan olarak seçilidir).
   * **Erişimi olanlar (Who has access):** **`Herkes (Anyone)`** olarak seçin! *(Bunu seçmezseniz portalden gelen sorular onay hatası verir).*
4. **Dağıt (Deploy)** butonuna basın.
5. Google ilk seferde sizden *"Erişime İzin Ver (Authorize access)"* isteyecektir:
   * Kendi Google hesabınızı seçin.
   * *"Gelişmiş (Advanced)"* $\rightarrow$ *"Fatma Soru Havuzu (Güvenli değil / Go to project)"* seçeneğine tıklayın ve **İzin Ver (Allow)** deyin. *(Bu standart Google onay adımıdır).*
6. Dağıtım tamamlandığında ekranda beliren **Web Uygulaması URL'sini (Web App URL)** kopyalayın.
   *(Örn: `https://script.google.com/macros/s/AKfycbx.../exec`)*

---

### 5. Adım: URL'yi Portala Yapıştırın
1. [fatma_calisma_ve_deneme_paneli.html](file:///c:/Users/hizar/OneDrive/Desktop/projeler/FATMA%201.A%C5%9EAMA%20%C3%87ALI%C5%9EMA%20PROGRAMI%20%28%202026-2027%29/fatma_calisma_ve_deneme_paneli.html) dosyasını tarayıcınızda açın.
2. Üst menüde yer alan **"⚙️ Bulut Bağlantısı"** butonuna tıklayın.
3. Kopyaladığınız Web App URL'sini yapıştırın ve **"Kaydet & Bağlantıyı Test Et"** butonuna basın.
4. Yeşil renkli *"Bağlantı Başarılı! ✓"* onayını gördüğünüzde sistem tamamen hazır demektir!

---

## 🎯 Artık Ne Olacak?
1. Fatma portaldaki **"+ Yeni Soru Ekle"** veya etüt içindeki **"Doğrula"** butonundan soru fotoğrafı yüklediğinde:
   * Fotoğraf anında sıkıştırılıp Google Drive'ınızdaki **"Fatma ÖZMİL - Soru Havuzu"** klasörüne yüklenir.
   * Google E-Tablonuza otomatik olarak tarih, ders, soru notu ve Drive linki satır olarak işlenir.
   * Telefonunuzdaki/bilgisayarınızdaki **Gmail** kutunuza anında sorunun fotoğrafı ve notuyla birlikte bildirim e-postası düşer!
2. Pazartesi günü 17:00-18:00 özel dersinde Müfit Hoca portali açtığında havuzdaki fotoğrafa tıklayarak soruyu tam ekran büyüteç ile net bir şekilde inceleyebilir.
