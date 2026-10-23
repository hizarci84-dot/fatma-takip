# GİTHUB PAGES İLE WEB UYGULAMASI (PWA) VE CANLI BULUT EŞİTLEME REHBERİ

Bu kılavuz, Fatma ÖZMİL Çalışma Portalı'nı **GitHub Pages** üzerinde gerçek bir mobil uygulama (PWA) olarak yayınlamanızı ve Fatma'nın telefonundan girdiği verilerin (çözülen sorular, etütler, deneme netleri) **anlık olarak sizin ekranınıza ve Google E-Tablonuza akmasını** sağlar.

---

## 🔍 1. Neden Fatma'nın Girişlerini Göremiyordunuz? (Durum Tespiti)

* **Önceki Durum:** Gönderdiğimiz ilk HTML dosyası, Fatma'nın etütlerini ve deneme netlerini yalnızca kendi telefonunun yerel tarayıcı hafızasında (`localStorage`) saklıyordu. Bu yüzden Fatma veri girdiğinde siz kendi bilgisayarınızda göremiyordunuz (yalnızca soru fotoğrafları Apps Script üzerinden Drive ve Gmail'inize geliyordu).
* **Şimdi Geliştirdiğimiz Canlı Bulut Sistemi:**
  1. Artık Fatma telefonda bir etüt tamamladığında veya deneme neti girdiğinde, sistem **arka planda 1 saniye içinde bu veriyi Google Bulut'a (Google Drive ve E-Tablonuza)** aktarır.
  2. Siz kendi bilgisayarınızdan veya telefonunuzdan uygulamayı açtığınızda (veya üstteki **"🔄 Buluttan Eşitle"** butonuna bastığınızda) Fatma'nın tüm netleri, çözdüğü soru sayıları ve başarı grafikleri anında sizin ekranınıza gelir!
  3. Ayrıca Google E-Tablonuzda **"Deneme Sınavları & Netler"** ve **"Günlük Takip & Etütler"** adında iki yeni sayfa otomatik açılır ve her şey tablolara dökülür.

---

## ☁️ 2. Adım: Google Apps Script Kodunu Güncelleme (1 Dakika)

Bulut senkronizasyonunun devreye girmesi için hazırladığımız güncel scripti yüklemeniz gerekir:

1. Proje klasörünüzdeki [google_apps_script.js](file:///c:/Users/hizar/OneDrive/Desktop/projeler/FATMA%201.A%C5%9EAMA%20%C3%87ALI%C5%9EMA%20PROGRAMI%20%28%202026-2027%29/google_apps_script.js) dosyasının tüm kodlarını kopyalayın (`Ctrl + A` $\rightarrow$ `Ctrl + C`).
2. Google E-Tablonuzdaki **Uzantılar $\rightarrow$ Apps Script** editörüne girin.
3. `Kod.gs` içindeki kodları silip bu yeni kodları yapıştırın ve kaydedin (`Ctrl + S`).
4. Sağ üstteki mavi **"Dağıt" (Deploy)** butonuna tıklayın $\rightarrow$ **"Dağıtımları Yönet" (Manage Deployments)** deyin.
5. Açılan pencerede **Kalem (Düzenle)** simgesine tıklayın $\rightarrow$ **Sürüm:** **"Yeni Sürüm" (New version)** seçin $\rightarrow$ **"Dağıt"** deyin.

*(Böylece Web App linkiniz değişmez, fakat canlı senkronizasyon yeteneği anında aktif olur).*

---

## 🚀 3. Adım: GitHub Üzerinde Uygulama Olarak Yayınlama (GitHub Pages)

Artık Fatma'ya dosya göndermek yerine, ona tıpkı bir web sitesi/mobil uygulama linki vereceksiniz:  
`https://<github-kullanici-adiniz>.github.io/fatma-takip/`

### A) GitHub'da Yeni Depo (Repository) Açma:
1. [github.com](https://github.com) adresine giriş yapın.
2. Sağ üstteki **"+"** simgesine tıklayıp **"New repository"** seçin.
3. **Repository name:** `fatma-takip` (veya istediğiniz bir isim) yazın.
4. **Public** seçili olsun.
5. En alttaki yeşil **"Create repository"** butonuna basın.

### B) Dosyaları Yükleme (En Kolay Yol - Sürükle Bırak):
1. Açılan sayfada **"uploading an existing file"** linkine tıklayın.
2. Masaüstünüzdeki `FATMA 1.AŞAMA ÇALIŞMA PROGRAMI ( 2026-2027)` klasöründen şu dosyaları sürükleyip tarayıcıya bırakın:
   * **`index.html`** *(Çok önemli: Ana uygulama dosyasıdır)*
   * **`manifest.json`** *(Telefonun uygulamayı tanımasını sağlar)*
   * **`sw.js`** *(Çevrimdışı ve PWA motorudur)*
   * **`favicon.png`**
   * **`apple-touch-icon.png`**
   * **`icon-192.png`**
   * **`icon-512.png`**
   * **`mufit_hoca_logo.jpg`**
3. Alttaki yeşil **"Commit changes"** butonuna basın.

### C) GitHub Pages'i Aktif Etme:
1. Deponuzun üst menüsündeki **"Settings" (Ayarlar)** sekmesine tıklayın.
2. Sol menüden **"Pages"** bölümüne girin.
3. **Build and deployment $\rightarrow$ Branch** kısmında `None` yerine **`main`** seçin, klasör olarak `/ (root)` seçip **"Save"** butonuna basın.
4. 1-2 dakika içinde sayfanın üstünde yeşil kutuda canlı linkiniz belirecektir:  
   👉 **`https://<kullanici-adiniz>.github.io/fatma-takip/`**

---

## 📱 4. Adım: Fatma'nın Telefonuna Uygulama Olarak Yükleme (PWA)

Bu linki WhatsApp'tan Fatma'ya atın. Fatma linke tıkladığında:

* **iPhone (Safari) Kullanıyorsa:**
  1. Safari'de linki açar.
  2. Ekranın alt ortasındaki **Paylaş** *(kare içinden yukarı ok çıkan simge)* butonuna basar.
  3. Aşağı kaydırıp **"Ana Ekrana Ekle" (Add to Home Screen)** seçeneğine tıklar.
  4. Telefonun ana ekranına **Müfit Hoca logolu "Fatma Takip"** uygulaması kurulur!

* **Android (Chrome) Kullanıyorsa:**
  1. Chrome'da linki açar.
  2. Ekranın sağ üstündeki 3 noktaya basıp **"Uygulamayı Yükle"** veya **"Ana Ekrana Ekle"** der.
  3. Uygulama tıpkı Play Store'dan inmiş gibi ana ekrana yerleşir!

---

## 🔄 5. Adım: Fatma'nın Önceki Verilerini Kaybetmemesi İçin (1 Seferlik Aktarım)

Fatma şu an eski HTML dosyasında bazı veriler girdiyse, onları kaybetmeden yeni sisteme aktarması çok kolaydır:

1. Fatma telefonundaki eski HTML dosyasını açar $\rightarrow$ Üst menüdeki **"Yedekle (JSON)"** butonuna basar (küçük bir dosya iner).
2. Ardından yeni GitHub linkini (veya ana ekrana eklediği uygulamayı) açar $\rightarrow$ Üst menüdeki **"İçe Aktar"** butonuna basıp o inen JSON dosyasını seçer.
3. **BUM!** Fatma'nın eski tüm verileri yeni uygulamaya yüklenir VE sistem anında bu verileri Google Bulut'a eşitler!
4. Siz de kendi bilgisayarınızdan veya telefonunuzdan aynı linki açıp **"🔄 Buluttan Eşitle"** butonuna bastığınızda Fatma'nın tüm çalışmalarını canlı olarak görürsünüz!
