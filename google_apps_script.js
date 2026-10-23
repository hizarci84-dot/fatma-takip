/**
 * FATMA ÖZMİL - 1. AŞAMA ÇALIŞMA PROGRAMI & SORU HAVUZU
 * Google Apps Script Webhook Altyapısı
 * 
 * Bu script:
 * 1. Portaldan gelen soru fotoğrafını ve bilgilerini alır.
 * 2. Google Drive'da "Fatma ÖZMİL - Soru Havuzu" klasörüne fotoğrafı kaydeder.
 * 3. Google E-Tablo'ya satır olarak işler.
 * 4. Öğretmenin Gmail adresine anında fotoğraflı bildirim e-postası fırlatır!
 */

// BİLDİRİM GÖNDERİLECEK ÖĞRETMEN E-POSTA ADRESİ:
const NOTIFICATION_EMAIL = "hizarci84@gmail.com";

const FOLDER_NAME = "Fatma ÖZMİL - Soru Havuzu";
const SHEET_NAME = "Soru Takip Çizelgesi";
const DB_FILE_NAME = "Fatma_Portal_Veritabani.json";

/**
 * Web App GET İsteği (Bağlantı Testi & Buluttan Veri Çekme)
 */
function doGet(e) {
  // 1. Buluttaki portal durumunu yükleme isteği
  if (e && e.parameter && (e.parameter.action === "load_state" || e.parameter.action === "get_state")) {
    const state = loadPortalState();
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      state: state,
      updatedAt: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  }

  // 2. Standart Webhook Sağlık Testi
  return ContentService.createTextOutput(JSON.stringify({
    status: "success",
    message: "Fatma ÖZMİL Soru Havuzu & Canlı Senkronizasyon Altyapısı Aktif!",
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

/**
 * Web App POST İsteği (Durum Senkronizasyonu & Soru Yükleme)
 */
function doPost(e) {
  try {
    const rawData = e.postData.contents;
    const data = JSON.parse(rawData);

    // 1. DURUM SENKRONİZASYONU (Etüt İlerlemeleri, Çözülen Sorular, Deneme Netleri)
    if (data.action === "save_state" || data.action === "sync_state") {
      const stateObj = data.state || data;
      const res = savePortalState(stateObj);
      return ContentService.createTextOutput(JSON.stringify(res))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // 2. YENİ SORU & FOTOĞRAF YÜKLEME
    const studentName = data.studentName || "Fatma ÖZMİL";
    const dateStr = data.date || Utilities.formatDate(new Date(), "GMT+3", "dd.MM.yyyy HH:mm");
    const subject = data.subject || "Genel Ders";
    const source = data.source || "Belirtilmemiş";
    const notes = data.notes || "Not bulunmuyor";
    const imageBase64 = data.imageBase64 || "";

    let fileUrl = "";
    let fileId = "";
    let imageBlob = null;

    // A) Google Drive Klasörünü Bul veya Oluştur
    const folder = getOrCreateFolder(FOLDER_NAME);

    // B) Fotoğraf Varsa Drive'a Kaydet
    if (imageBase64 && imageBase64.indexOf("base64,") !== -1) {
      const pureBase64 = imageBase64.split("base64,")[1];
      const decodedBytes = Utilities.base64Decode(pureBase64);
      
      const fileName = `Fatma_Soru_${Utilities.formatDate(new Date(), "GMT+3", "yyyyMMdd_HHmmss")}.jpg`;
      imageBlob = Utilities.newBlob(decodedBytes, "image/jpeg", fileName);
      
      const driveFile = folder.createFile(imageBlob);
      driveFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      
      fileUrl = driveFile.getUrl();
      fileId = driveFile.getId();
    }

    // C) Google E-Tablo'ya Satır Ekle
    const targetSheet = getOrCreateSheet(SHEET_NAME);
    targetSheet.appendRow([
      dateStr,
      studentName,
      subject,
      source,
      notes,
      fileUrl ? fileUrl : "Fotoğraf Yok",
      "Bekliyor (Müfit Hoca İle Çözülecek)",
      new Date()
    ]);

    // D) Öğretmene Gmail İle Fotoğraflı Bildirim Gönder
    const recipient = NOTIFICATION_EMAIL || Session.getEffectiveUser().getEmail() || Session.getActiveUser().getEmail();
    let emailSent = false;
    if (recipient && recipient.includes('@')) {
      try {
        sendNotificationEmail(recipient, studentName, subject, source, notes, fileUrl, imageBlob, dateStr);
        emailSent = true;
      } catch (mailErr) {
        console.error("Mail bildirim hatası:", mailErr);
      }
    }

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: emailSent 
        ? "Soru başarıyla Drive'a kaydedildi ve e-posta bildirimi gönderildi." 
        : "Soru başarıyla Drive'a ve E-Tabloya kaydedildi.",
      fileUrl: fileUrl,
      fileId: fileId
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Portaldaki Veritabanı Dosyasını Bul veya Oluştur
 */
function getOrCreateDatabaseFile(folder) {
  const files = folder.getFilesByName(DB_FILE_NAME);
  if (files.hasNext()) {
    return files.next();
  }
  return folder.createFile(DB_FILE_NAME, JSON.stringify({
    exams: [],
    curriculumProgress: {},
    scheduleProgress: {},
    blockLogs: {},
    questionPool: [],
    updatedAt: new Date().toISOString()
  }), MimeType.PLAIN_TEXT);
}

/**
 * Fatma'nın Girdiği Tüm Verileri Buluta (Drive & E-Tablo) Kaydet
 */
function savePortalState(stateData) {
  try {
    const folder = getOrCreateFolder(FOLDER_NAME);
    const dbFile = getOrCreateDatabaseFile(folder);
    const jsonStr = typeof stateData === "string" ? stateData : JSON.stringify(stateData);
    dbFile.setContent(jsonStr);

    // E-Tabloya da temiz tablolar olarak yaz (Müfit Hoca'nın takip etmesi için)
    if (typeof stateData === "object" && stateData !== null) {
      syncStateToSheets(stateData);
    }

    return {
      status: "success",
      message: "Veriler Google Drive ve E-Tabloya başarıyla senkronize edildi.",
      updatedAt: new Date().toISOString()
    };
  } catch (err) {
    return {
      status: "error",
      message: "Buluta kaydetme hatası: " + err.toString()
    };
  }
}

/**
 * Buluttaki Son Veritabanını Oku ve Portala Gönder
 */
function loadPortalState() {
  try {
    const folder = getOrCreateFolder(FOLDER_NAME);
    const dbFile = getOrCreateDatabaseFile(folder);
    const content = dbFile.getBlob().getDataAsString("utf-8");
    return JSON.parse(content);
  } catch (err) {
    console.error("loadPortalState error:", err);
    return null;
  }
}

/**
 * Deneme Sınavlarını ve Günlük Etütleri E-Tablo Sayfalarına İndeksle
 */
function syncStateToSheets(stateData) {
  try {
    let ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) {
      const files = DriveApp.getFilesByName("Fatma ÖZMİL - Akademik Takip Tablosu");
      if (files.hasNext()) {
        ss = SpreadsheetApp.open(files.next());
      } else {
        ss = SpreadsheetApp.create("Fatma ÖZMİL - Akademik Takip Tablosu");
      }
    }

    // 1. DENEME SINAVLARI & NETLER TABLOSU
    if (stateData.exams && Array.isArray(stateData.exams)) {
      let examSheet = ss.getSheetByName("Deneme Sınavları & Netler");
      if (!examSheet) {
        examSheet = ss.insertSheet("Deneme Sınavları & Netler");
      }
      examSheet.clearContents();
      
      const examHeaders = [
        "Sınav Adı", "Tarih", "Türkçe (D/Y)", "Türkçe Net", 
        "Matematik (D/Y)", "Matematik Net", 
        "Fen (D/Y)", "Fen Net", 
        "Sosyal (D/Y)", "Sosyal Net", 
        "TOPLAM NET", "Süre (Dk)", "Hedef Durumu", "Notlar"
      ];
      examSheet.appendRow(examHeaders);
      examSheet.getRange(1, 1, 1, examHeaders.length)
        .setFontWeight("bold")
        .setBackground("#4f46e5")
        .setFontColor("#ffffff");
      examSheet.setFrozenRows(1);

      stateData.exams.forEach(ex => {
        const turkNet = (ex.turkD || 0) - ((ex.turkY || 0) / 4);
        const matNet = (ex.matD || 0) - ((ex.matY || 0) / 4);
        const fenNet = (ex.fenD || 0) - ((ex.fenY || 0) / 4);
        const sosNet = (ex.sosD || 0) - ((ex.sosY || 0) / 4);
        const totalNet = ex.netTotal !== undefined ? ex.netTotal : (turkNet + matNet + fenNet + sosNet);

        examSheet.appendRow([
          ex.title || "Deneme",
          ex.date || "",
          `${ex.turkD || 0}D / ${ex.turkY || 0}Y`,
          turkNet.toFixed(2),
          `${ex.matD || 0}D / ${ex.matY || 0}Y`,
          matNet.toFixed(2),
          `${ex.fenD || 0}D / ${ex.fenY || 0}Y`,
          fenNet.toFixed(2),
          `${ex.sosD || 0}D / ${ex.sosY || 0}Y`,
          sosNet.toFixed(2),
          Number(totalNet).toFixed(2),
          ex.duration || 135,
          totalNet >= 80 ? "Hedef Üstü ⭐" : totalNet >= 60 ? "İyi Seviye 👍" : "Geliştirilmeli 📌",
          ex.notes || ""
        ]);
      });
    }

    // 2. GÜNLÜK ETÜT & SORU ÇÖZÜM TABLOSU
    if (stateData.blockLogs && typeof stateData.blockLogs === "object") {
      let logSheet = ss.getSheetByName("Günlük Takip & Etütler");
      if (!logSheet) {
        logSheet = ss.insertSheet("Günlük Takip & Etütler");
      }
      logSheet.clearContents();

      const logHeaders = ["Etüt Kodu", "Çözülen Soru", "Doğru", "Yanlış", "Boş", "Başarı Yüzdesi (%)", "Öğrenci Notu", "Kayıt Zamanı"];
      logSheet.appendRow(logHeaders);
      logSheet.getRange(1, 1, 1, logHeaders.length)
        .setFontWeight("bold")
        .setBackground("#059669")
        .setFontColor("#ffffff");
      logSheet.setFrozenRows(1);

      Object.keys(stateData.blockLogs).forEach(key => {
        const log = stateData.blockLogs[key];
        if (log && (log.solved > 0 || log.d > 0)) {
          const acc = (log.d + log.y) > 0 ? Math.round((log.d / (log.d + log.y)) * 100) : 100;
          logSheet.appendRow([
            key,
            log.solved || (log.d + log.y + (log.b || 0)),
            log.d || 0,
            log.y || 0,
            log.b || 0,
            `%${acc}`,
            log.notes || "",
            log.timestamp || new Date().toLocaleString("tr-TR")
          ]);
        }
      });
    }

  } catch(e) {
    console.error("syncStateToSheets error:", e);
  }
}

/**
 * Drive Klasörü Bul veya Oluştur
 */
function getOrCreateFolder(folderName) {
  const folders = DriveApp.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  return DriveApp.createFolder(folderName);
}

/**
 * E-Tablo Sayfası Bul veya Oluştur
 */
function getOrCreateSheet(sheetName) {
  let ss = SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) {
    // Bağımsız script olarak çalıştırılıyorsa yeni dosya açar
    const files = DriveApp.getFilesByName("Fatma ÖZMİL - Akademik Takip Tablosu");
    if (files.hasNext()) {
      ss = SpreadsheetApp.open(files.next());
    } else {
      ss = SpreadsheetApp.create("Fatma ÖZMİL - Akademik Takip Tablosu");
    }
  }

  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    // Başlık satırı
    sheet.appendRow([
      "Tarih & Saat",
      "Öğrenci",
      "Ders / Alan",
      "Kaynak & Soru No",
      "Takılınan Nokta / Not",
      "Drive Fotoğraf Linki",
      "Durum",
      "Kayıt Zaman Damgası"
    ]);
    sheet.getRange(1, 1, 1, 8).setFontWeight("bold").setBackground("#4f46e5").setFontColor("#ffffff");
    sheet.setFrozenRows(1);
  }
  return sheet;
}

/**
 * Gmail İle Şık HTML Bildirim E-postası
 */
function sendNotificationEmail(toEmail, studentName, subject, source, notes, fileUrl, imageBlob, dateStr) {
  const emailSubject = `🚨 [${studentName}] Yeni Soru Eklendi: ${subject} (${source})`;
  
  let htmlBody = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; rounded: 12px; background-color: #ffffff;">
      <div style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); padding: 18px 20px; border-radius: 10px; color: white;">
        <h2 style="margin: 0; font-size: 18px; font-weight: bold;">🎓 Müfit Hoca & Öğretmen Soru Masası</h2>
        <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">Yeni Çözülemeyen Soru Bildirimi</p>
      </div>

      <div style="padding: 20px 0;">
        <p style="font-size: 14px; color: #1e293b; margin-top: 0;">
          <strong>${studentName}</strong>, çalışma programında takıldığı yeni bir soruyu portale yükledi:
        </p>

        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin: 15px 0;">
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 8px 0; color: #64748b; width: 140px;">📅 Tarih:</td>
            <td style="padding: 8px 0; font-weight: bold; color: #0f172a;">${dateStr}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 8px 0; color: #64748b;">📚 Ders / Alan:</td>
            <td style="padding: 8px 0; font-weight: bold; color: #4f46e5;">${subject}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 8px 0; color: #64748b;">📖 Kaynak & No:</td>
            <td style="padding: 8px 0; font-weight: bold; color: #0f172a;">${source}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 8px 0; color: #64748b;">✍️ Takılınan Nokta:</td>
            <td style="padding: 8px 0; color: #b91c1c; font-style: italic;">"${notes}"</td>
          </tr>
        </table>

        ${fileUrl ? `
          <div style="margin: 20px 0; text-align: center;">
            <a href="${fileUrl}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 8px; font-size: 13px; font-weight: bold;">
              📁 Sorunun Fotoğrafını Google Drive'da Aç
            </a>
          </div>
          <div style="text-align: center; margin-top: 15px;">
            <img src="cid:questionPhoto" style="max-width: 100%; max-height: 400px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);" alt="Soru Fotoğrafı">
          </div>
        ` : `
          <p style="font-size: 12px; color: #94a3b8; font-style: italic;">Bu soru için fotoğraf eklenmedi.</p>
        `}

        <div style="margin-top: 25px; padding: 12px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #4f46e5; font-size: 12px; color: #475569;">
          💡 <strong>Hatırlatma:</strong> Bu soru, <strong>Pazartesi 17:00 - 18:00</strong> Müfit Hoca özel dersi soru havuzuna kaydedilmiştir.
        </div>
      </div>

      <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; text-align: center; font-size: 11px; color: #94a3b8;">
        Fatma ÖZMİL 1. Aşama Maarif Modeli Çalışma Portalı Otomatik Bildirim Sistemi
      </div>
    </div>
  `;

  const options = {
    htmlBody: htmlBody
  };

  if (imageBlob) {
    options.inlineImages = {
      questionPhoto: imageBlob
    };
    options.attachments = [imageBlob];
  }

  GmailApp.sendEmail(toEmail, emailSubject, `Fatma ÖZMİL yeni bir soru ekledi: ${subject} - ${source}\nNot: ${notes}`, options);
}

/**
 * -------------------------------------------------------------
 * 7/24 BULUT OTOMASYONU: GREEN API İLE GÜNLÜK WHATSAPP GÖNDERİMİ
 * (Google Zaman Tetikleyicisi İle Bilgisayarınız Kapalıyken Bile Çalışır)
 * -------------------------------------------------------------
 */
const GREEN_API_CONFIG = {
  host: "https://7107.api.greenapi.com",
  idInstance: "7107639595",
  apiTokenInstance: "41919f0f1ff94b00a0daf0b5a20028811dba6ffbe274471bbd",
  chatId: "120363382488413187@g.us" // FATMA İLE MATEMATİK
};

function sendDailyWhatsAppViaGreenApi() {
  const now = new Date();
  const endDate = new Date(2027, 4, 1, 23, 59, 59); // 1 Mayıs 2027
  if (now > endDate) {
    console.log("Program 1 Mayıs 2027 itibarıyla tamamlandı.");
    return;
  }

  if (!GREEN_API_CONFIG.idInstance || !GREEN_API_CONFIG.apiTokenInstance || !GREEN_API_CONFIG.chatId) {
    console.log("Green API bilgileri tanımlanmamış. Lütfen GREEN_API_CONFIG nesnesini doldurun.");
    return;
  }

  const dayOfWeek = now.getDay(); // 0: Pazar, 1: Pzt, 2: Salı, 3: Çarşamba, 4: Perşembe, 5: Cuma, 6: Cts
  const dateStr = Utilities.formatDate(now, Session.getScriptTimeZone() || "GMT+3", "dd.MM.yyyy");

  let dayTitle = "";
  let target = "";
  let motto = "";
  let flow = [];

  if (dayOfWeek === 6) { // Cumartesi
    dayTitle = "Cumartesi - Hafta Sonu Odak Maratonu";
    target = "220 Soru / 4 Odak Blok";
    motto = "Hafta sonunu verimli değerlendiren öğrenci hedefine bir adım daha yaklaşır. Bugün zinde ve disiplinli bir başlangıç yapıyoruz!";
    flow = [
      "☕ 09:30 - 10:30 | Zinde Kahvaltı & Güne Hazırlık",
      "📘 10:30 - 11:30 | *Bilgi Sarmal Matematik SB* (2 Test)",
      "⚛️ 11:45 - 13:00 | *Çap Maarif Fizik SB* (1 Test)",
      "🍽️ 13:00 - 14:30 | Öğle Yemeği & Mola",
      "📐 14:30 - 16:00 | *2027 Orijinal Matematik SB* (1-2 Test)",
      "☕ 16:00 - 16:30 | Çay & Dinlenme Molası",
      "🧪 16:30 - 18:00 | *Çap Maarif Kimya SB* (1 Test)",
      "🍲 18:00 - 19:30 | Akşam Yemeği & Aile Zamanı",
      "📝 19:30 - 20:30 | Deneme Analizi / Soru Defteri Tekrarı",
      "🛋️ 20:30 - 00:00 | Tamamen Serbest Zaman",
      "💤 00:00 | *KESİN UYKU (Biyolojik Kural)*"
    ];
  } else if (dayOfWeek === 0) { // Pazar
    dayTitle = "Pazar - Büyük Deneme & Derinleşme Günü";
    target = "120 Soruluk Deneme + ~90 Soru";
    motto = "Pazar sabahı gerçek sınav provasıdır! Süreni iyi yönet, yapamadığın soruları tespit et ve haftalık karneni oluştur.";
    flow = [
      "☕ 09:30 - 10:30 | Zinde Başlangıç & Kahvaltı",
      "📐 10:30 - 12:00 | *Bilgi Sarmal Geometri SB* (1-2 Test)",
      "🧬 12:15 - 13:30 | *Çap Biyoloji SB* (1-2 Test)",
      "🍽️ 13:30 - 15:00 | Öğle Yemeği & Dinlenme",
      "📘 15:00 - 16:30 | *2027 Orijinal Matematik* (1 Test)",
      "📊 16:45 - 17:45 | *Haftalık İlerleme Raporu:* Portale Test İşleme & Haftalık Karne",
      "🛋️ 17:45 - 00:00 | Mental Şarj & Serbest Zaman",
      "💤 00:00 | *KESİN UYKU*"
    ];
  } else if (dayOfWeek === 1) { // Pazartesi
    dayTitle = "Pazartesi - Hafta Başı & Müfit Hoca Özel Dersi";
    target = "140 Soru + Özel Ders";
    motto = "Bugün saat 17:00'de Müfit Hoca ile özel dersimiz var! Hafta boyunca takıldığın soruları masaya yatıracağız.";
    flow = [
      "🏠 16:15 - 17:00 | Eve Geliş & Dinlenme",
      "🎓 17:00 - 18:00 | *MÜFİT HOCA İLE ÖZEL DERS* (Birebir Seans)",
      "☕ 18:00 - 18:15 | Kısa Mola & Zihin Tazeleyici",
      "📘 18:15 - 19:15 | *Özel Dersin Tekrarı & Bilgi Sarmal Mat* (1-2 Test)",
      "🍲 19:15 - 20:00 | Akşam Yemeği & Dinlenme",
      "📖 20:00 - 20:45 | *Limit Kronometre Paragraf SB* (1 Test, ~20 Soru)",
      "🧬 21:00 - 22:00 | *Çap Biyoloji* (1 Test) + Günün Soru Analizi",
      "🛋️ 22:00 - 00:00 | Çalışma Bitti! Serbest Zaman & Dinlenme",
      "💤 00:00 | *KESİN UYKU*"
    ];
  } else if (dayOfWeek === 2) { // Salı
    dayTitle = "Salı - Fen & Geometri Odaklı Gün";
    target = "140 Soru / 3 Blok";
    motto = "Erken geldiğin günleri derinlemesine soru çözerek taçlandır. Geometri ve Fizik sorularına odaklan!";
    flow = [
      "🏠 16:15 - 17:00 | Eve Geliş & Dinlenme",
      "📖 17:00 - 17:45 | *Limit Paragraf SB* (1 Test)",
      "📐 18:00 - 19:00 | *Bilgi Sarmal Geometri* (1-2 Test)",
      "🍲 19:00 - 19:45 | Akşam Yemeği & Mola",
      "⚛️ 19:45 - 20:45 | *Çap Fizik* (1 Test)",
      "📝 21:00 - 22:00 | Günün Hata Analizi & Formül Notları",
      "🛋️ 22:00 - 00:00 | Serbest Zaman",
      "💤 00:00 | *KESİN UYKU*"
    ];
  } else if (dayOfWeek === 3) { // Çarşamba
    dayTitle = "Çarşamba - Hafifletilmiş Zihin Akışı (Geç Geliş)";
    target = "80 Soru / 2 Blok";
    motto = "Okuldan 19:30'da geldiğin gün. Seni yormuyoruz; 2 blokla günü tamamlayıp erkenden dinlenmeye geçeceksin!";
    flow = [
      "🏠 19:30 - 20:15 | Eve Geliş, Akşam Yemeği & Dinlenme",
      "📖 20:15 - 21:00 | *Limit Paragraf SB* (1 Test)",
      "🧪 21:15 - 22:15 | *Çap Kimya* (1 Test)",
      "🛋️ 22:15 - 00:00 | Çalışma Bitti! Dinlenme & Uyku Hazırlığı",
      "💤 00:00 | *KESİN UYKU*"
    ];
  } else if (dayOfWeek === 4) { // Perşembe
    dayTitle = "Perşembe - Odak Geometri & Paragraf (Geç Geliş)";
    target = "80 Soru / 2 Blok";
    motto = "Günün yorgunluğunu hafif bir tempoyla atlatıyoruz. Paragraf zihnini açacak, Geometri analitik bakışını tazeleyecek.";
    flow = [
      "🏠 19:30 - 20:15 | Eve Geliş, Akşam Yemeği & Dinlenme",
      "📖 20:15 - 21:00 | *Limit Paragraf SB* (1 Test)",
      "📐 21:15 - 22:15 | *Bilgi Sarmal Geometri* (1 Test)",
      "🛋️ 22:15 - 00:00 | Çalışma Bitti! Dinlenme",
      "💤 00:00 | *KESİN UYKU*"
    ];
  } else if (dayOfWeek === 5) { // Cuma
    dayTitle = "Cuma - Hafta Kapanışı & Soru Havuzu Temizliği";
    target = "60 Soru + Soru Havuzu Seansı";
    motto = "Haftayı başarıyla tamamladın! Hafta içi çözemediğin soruları temizle ve hafta sonuna zihinsel olarak hazır gir.";
    flow = [
      "🏠 16:15 - 17:00 | Eve Geliş & Dinlenme",
      "🔍 17:00 - 18:00 | *Hafta İçi Yapılamayan Soruların Çözüm Seansı* (Soru Havuzu)",
      "📘 18:00 - 19:00 | *2027 Orijinal Matematik SB* (1 Test)",
      "🍲 19:00 - 19:45 | Akşam Yemeği & Mola",
      "🧪 19:45 - 20:45 | *Çap Kimya* (1 Test)",
      "📝 21:00 - 22:00 | Haftanın Özeti & Yarının Ders Hazırlığı",
      "🛋️ 22:00 - 00:00 | Hafta Sonu Karşılaması & Serbest Zaman",
      "💤 00:00 | *KESİN UYKU*"
    ];
  }

  let msg = `📚 *FATMA ÖZMİL - 1. AŞAMA GÜNLÜK ÇALIŞMA PROGRAMI*\n`;
  msg += `🗓️ *${dateStr}* | 🎯 *Hedef: ${target}*\n`;
  msg += `📌 _${dayTitle}_\n`;
  msg += `────────────────────────\n`;
  msg += `🌤️ *GÜNAYDIN FATMA!*\n`;
  msg += `_${motto}_\n\n`;
  msg += `⏱️ *BUGÜNKÜ ETÜT VE ZAMAN AKIŞI:*\n`;
  msg += flow.join("\n") + "\n\n";
  msg += `────────────────────────\n`;
  msg += `📌 *ÖNEMLİ HATIRLATMALAR:*\n`;
  msg += `📸 Çözemediğin her sorunun fotoğrafını portaldaki *Soru Havuzu*'na yükle, bana anında bildirim gelecek!\n`;
  msg += `✅ Her etüt bitiminde portaldaki *Doğrula* butonundan çözdüğün soru sayılarını girmeyi unutma.\n`;
  msg += `💤 *Saat 00:00'da çalışma biter ve dinlenmeye geçilir.* Dinlenmiş zihin başarının ilk şartıdır.\n\n`;
  msg += `İyi ve verimli çalışmalar dilerim! 🚀\n`;
  msg += `*Müfit Hoca* (Müfit Hoca ile Matematik)`;

  const url = `${GREEN_API_CONFIG.host.replace(/\/$/, "")}/waInstance${GREEN_API_CONFIG.idInstance}/sendMessage/${GREEN_API_CONFIG.apiTokenInstance}`;
  const payload = {
    chatId: GREEN_API_CONFIG.chatId,
    message: msg
  };

  const response = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  console.log("Green API Yanıtı:", response.getContentText());
}
