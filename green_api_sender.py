# -*- coding: utf-8 -*-
"""
FATMA ÖZMİL - 1. AŞAMA ÇALIŞMA PROGRAMI
GREEN API WHATSAPP GÜNLÜK BİLGİLENDİRME & BOT SİSTEMİ
------------------------------------------------------
Bu script;
1. Günün çalışma programını, etütlerini ve soru hedeflerini WhatsApp için biçimlendirir.
2. Green API üzerinden öğrencinin/ailenin WhatsApp grubuna otomatik mesaj atar.
3. 26 Eylül 2026 - 1 Mayıs 2027 tarihleri arasında her sabah otomatik gönderim yapabilir.
4. İstenirse 'fatma_calisma_ve_deneme_paneli.html' portal dosyasını belge olarak gruba iletir.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import datetime
import argparse
import io

# Windows konsolunda emojilerin düzgün yazılması için UTF-8 yapılandırması
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Program Takvimi ve Dosya Yolları
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "green_api_config.json")
PORTAL_FILE = os.path.join(SCRIPT_DIR, "fatma_calisma_ve_deneme_paneli.html")
LOG_FILE = os.path.join(SCRIPT_DIR, "gunluk_gonderim_gunlugu.log")
LAST_SENT_FILE = os.path.join(SCRIPT_DIR, ".last_sent_date.txt")

PROGRAM_START_DATE = datetime.date(2026, 9, 26)
PROGRAM_END_DATE = datetime.date(2027, 5, 1) # 1 Mayıs 2027 Program Bitişi
TASK_NAME = "Fatma_Gunluk_WhatsApp_Botu"

DAILY_SCHEDULES = {
    0: {
        "name": "Cumartesi",
        "title": "Hafta Sonu Odak Maratonu",
        "target": "220 Soru / 4 Odak Blok",
        "motto": "Hafta sonunu verimli değerlendiren öğrenci hedefine bir adım daha yaklaşır. Bugün zinde ve disiplinli bir başlangıç yapıyoruz!",
        "flow": [
            ("☕ 09:30 - 10:30", "Zinde Kahvaltı & Güne Hazırlık"),
            ("📘 10:30 - 11:30", "*Bilgi Sarmal Matematik SB* (Öğrenme & Beceri Testleri - 2 Test)"),
            ("⚛️ 11:45 - 13:00", "*Çap Maarif Fizik SB* (Sıralı Konu Testi - 1 Test)"),
            ("🍽️ 13:00 - 14:30", "Öğle Yemeği & Yürüyüş / Mola"),
            ("📐 14:30 - 16:00", "*2027 Orijinal Matematik SB* (Beceri Temelli Sorular - 1-2 Test)"),
            ("☕ 16:00 - 16:30", "Çay & Dinlenme Molası"),
            ("🧪 16:30 - 18:00", "*Çap Maarif Kimya SB* (Sıralı Konu Testi - 1 Test)"),
            ("🍲 18:00 - 19:30", "Akşam Yemeği & Aile Zamanı"),
            ("📝 19:30 - 20:30", "Deneme Analizi / Soru Defteri Tekrarı"),
            ("🛋️ 20:30 - 00:00", "Tamamen Serbest Zaman / Film / Dinlenme"),
            ("💤 00:00", "*KESİN UYKU (Biyolojik Kural)*")
        ]
    },
    1: {
        "name": "Pazar",
        "title": "Büyük Deneme & Derinleşme Günü",
        "target": "120 Soruluk Deneme + ~90 Soru",
        "motto": "Pazar sabahı gerçek sınav provasıdır! Süreni iyi yönet, yapamadığın soruları tespit et ve haftalık karneni oluştur.",
        "flow": [
            ("☕ 09:30 - 10:30", "Zinde Başlangıç & Kahvaltı"),
            ("📐 10:30 - 12:00", "*Bilgi Sarmal Geometri SB* (Özel Üçgenler / Benzerlik - 1-2 Test)"),
            ("🧬 12:15 - 13:30", "*Çap Biyoloji SB* (Yaşam & Organizasyon - 1-2 Test)"),
            ("🍽️ 13:30 - 15:00", "Öğle Yemeği & Dinlenme"),
            ("📘 15:00 - 16:30", "*2027 Orijinal Matematik* (Fonksiyonlar & Sayılar - 1 Test)"),
            ("📊 16:45 - 17:45", "*Haftalık İlerleme Raporu:* Portale Test İşleme & Haftalık Karne"),
            ("🛋️ 17:45 - 00:00", "Akşam Yemeği & Mental Şarj (Tamamen Serbest Zaman)"),
            ("💤 00:00", "*KESİN UYKU*")
        ]
    },
    2: {
        "name": "Pazartesi",
        "title": "Hafta Başı & Müfit Hoca Özel Dersi",
        "target": "140 Soru + Özel Ders",
        "motto": "Bugün saat 17:00'de Müfit Hoca ile özel dersimiz var! Hafta boyunca takıldığın soruları masaya yatırıp yeni konuları fethedeceğiz.",
        "flow": [
            ("🏠 16:15 - 17:00", "Eve Geliş, Dinlenme & Özel Ders Hazırlığı"),
            ("🎓 17:00 - 18:00", "*MÜFİT HOCA İLE ÖZEL DERS* (Birebir Seans)"),
            ("☕ 18:00 - 18:15", "Kısa Mola & Zihin Tazeleyici"),
            ("📘 18:15 - 19:15", "*Özel Dersin Tekrarı & Bilgi Sarmal Matematik* (1-2 Test)"),
            ("🍲 19:15 - 20:00", "Akşam Yemeği & Dinlenme"),
            ("📖 20:00 - 20:45", "*Limit Kronometre Paragraf SB* (1 Test, ~20 Soru)"),
            ("🧬 21:00 - 22:00", "*Çap Biyoloji* (Yaşam & Hücre - 1 Test) + Günün Soru Analizi"),
            ("🛋️ 22:00 - 00:00", "Çalışma Bitti! Serbest Zaman, Kitap Okuma & Dinlenme"),
            ("💤 00:00", "*KESİN UYKU (Biyolojik Kural)*")
        ]
    },
    3: {
        "name": "Salı",
        "title": "Fen & Geometri Odaklı Gün",
        "target": "140 Soru / 3 Blok",
        "motto": "Erken geldiğin günleri derinlemesine soru çözerek taçlandır. Geometri ve Fizik sorularında görsele ve mantığa odaklan!",
        "flow": [
            ("🏠 16:15 - 17:00", "Eve Geliş & Dinlenme"),
            ("📖 17:00 - 17:45", "*Limit Paragraf SB* (Gelişme Testleri - 1 Test)"),
            ("📐 18:00 - 19:00", "*Bilgi Sarmal Geometri* (Üçgende Açılar & Özel Üçgenler - 1-2 Test)"),
            ("🍲 19:00 - 19:45", "Akşam Yemeği & Aile Molası"),
            ("⚛️ 19:45 - 20:45", "*Çap Fizik* (Kuvvet, Hareket & Akışkanlar - 1 Test)"),
            ("📝 21:00 - 22:00", "Günün Hata Analizi & Fizik/Geometri Formül Notları"),
            ("🛋️ 22:00 - 00:00", "Serbest Zaman & Erken Rahatlama"),
            ("💤 00:00", "*KESİN UYKU*")
        ]
    },
    4: {
        "name": "Çarşamba",
        "title": "Geç Geliş - Hafifletilmiş Zihin Akışı",
        "target": "80 Soru / 2 Blok",
        "motto": "Okuldan 19:30'da geldiğin yorucu bir gün. Seni asla yormuyoruz; sadece 2 odak blokla günün hakkını verip erkenden dinlenmeye geçeceksin!",
        "flow": [
            ("🏠 19:30 - 20:15", "Eve Geliş, Akşam Yemeği & Dinlenme"),
            ("📖 20:15 - 21:00", "*Limit Paragraf SB* (1 Test, ~20 Soru)"),
            ("🧪 21:15 - 22:15", "*Çap Kimya* (Etkileşim / Atom & Periyodik Sistem - 1 Test)"),
            ("🛋️ 22:15 - 00:00", "Çalışma Bitti! Tamamen Dinlenme & Uyku Hazırlığı"),
            ("💤 00:00", "*KESİN UYKU*")
        ]
    },
    5: {
        "name": "Perşembe",
        "title": "Geç Geliş - Odak Geometri & Paragraf",
        "target": "80 Soru / 2 Blok",
        "motto": "Günün yorgunluğunu hafif bir çalışma temposuyla atlatıyoruz. Paragraf zihnini açacak, Geometri analitik bakışını tazeleyecek.",
        "flow": [
            ("🏠 19:30 - 20:15", "Eve Geliş, Akşam Yemeği & Dinlenme"),
            ("📖 20:15 - 21:00", "*Limit Paragraf SB* (1 Test, ~20 Soru)"),
            ("📐 21:15 - 22:15", "*Bilgi Sarmal Geometri* (Eşlik & Benzerlik - 1 Test)"),
            ("🛋️ 22:15 - 00:00", "Çalışma Bitti! Dinlenme & Zihin Boşaltma"),
            ("💤 00:00", "*KESİN UYKU*")
        ]
    },
    6: {
        "name": "Cuma",
        "title": "Hafta Kapanışı & Soru Havuzu Temizliği",
        "target": "60 Soru + Soru Havuzu Seansı",
        "motto": "Haftayı başarıyla tamamladın! Hafta içi çözemediğin soruları temizle, eksiklerini kapat ve hafta sonuna zihinsel olarak hazır gir.",
        "flow": [
            ("🏠 16:15 - 17:00", "Eve Geliş & Dinlenme"),
            ("🔍 17:00 - 18:00", "*Hafta İçi Yapılamayan Soruların Çözüm Seansı* (Soru Havuzu)"),
            ("📘 18:00 - 19:00", "*2027 Orijinal Matematik SB* (Sayılar İleri Beceri Testi - 1 Test)"),
            ("🍲 19:00 - 19:45", "Akşam Yemeği & Mola"),
            ("🧪 19:45 - 20:45", "*Çap Kimya* (Çeşitlilik & Karışımlar - 1 Test)"),
            ("📝 21:00 - 22:00", "Haftanın Özeti & Yarının Ders Hazırlığı"),
            ("🛋️ 22:00 - 00:00", "Serbest Zaman & Hafta Sonu Karşılaması"),
            ("💤 00:00", "*KESİN UYKU*")
        ]
    }
}

# Haftanın günleri haritası (Python weekday: 0=Pazartesi ... 5=Cumartesi, 6=Pazar)
WEEKDAY_TO_DAY_INDEX = {
    5: 0, # Cumartesi -> Day 0
    6: 1, # Pazar -> Day 1
    0: 2, # Pazartesi -> Day 2
    1: 3, # Salı -> Day 3
    2: 4, # Çarşamba -> Day 4
    3: 5, # Perşembe -> Day 5
    4: 6  # Cuma -> Day 6
}

DAY_NAME_TO_INDEX = {
    "cumartesi": 0, "cts": 0, "0": 0,
    "pazar": 1, "paz": 1, "1": 1,
    "pazartesi": 2, "pzt": 2, "2": 2,
    "salı": 3, "sali": 3, "sal": 3, "3": 3,
    "çarşamba": 4, "carsamba": 4, "car": 4, "4": 4,
    "perşembe": 5, "persembe": 5, "per": 5, "5": 5,
    "cuma": 6, "cum": 6, "6": 6
}


def log_event(message):
    """İşlem kayıtlarını dosyaya yazar."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


def load_config():
    """Green API ayarlarını yükler veya oluşturur."""
    if not os.path.exists(CONFIG_FILE):
        default_conf = {
            "host": "https://api.green-api.com",
            "idInstance": "",
            "apiTokenInstance": "",
            "chatId": ""
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_conf, f, ensure_ascii=False, indent=2)
        return default_conf
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(conf):
    """Green API ayarlarını kaydeder."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(conf, f, ensure_ascii=False, indent=2)


def generate_whatsapp_message(day_index=None, custom_date_str=None):
    """Belirtilen gün için WhatsApp biçimlendirmeli mesaj üretir."""
    if day_index is None:
        now = datetime.datetime.now()
        day_index = WEEKDAY_TO_DAY_INDEX.get(now.weekday(), 0)
        date_str = now.strftime("%d.%m.%Y")
    else:
        date_str = custom_date_str or datetime.datetime.now().strftime("%d.%m.%Y")

    data = DAILY_SCHEDULES.get(day_index, DAILY_SCHEDULES[0])
    day_name = data["name"]

    lines = []
    lines.append(f"📚 *FATMA ÖZMİL - 1. AŞAMA GÜNLÜK ÇALIŞMA PROGRAMI*")
    lines.append(f"🗓️ *{date_str} {day_name}* | 🎯 *Hedef: {data['target']}*")
    lines.append(f"📌 _{data['title']}_")
    lines.append("────────────────────────")
    lines.append(f"🌤️ *GÜNAYDIN FATMA!*")
    lines.append(f"_{data['motto']}_")
    lines.append("")
    lines.append("⏱️ *BUGÜNKÜ ETÜT VE ZAMAN AKIŞI:*")
    
    for time_slot, task_desc in data["flow"]:
        lines.append(f"{time_slot} | {task_desc}")
    
    lines.append("")
    lines.append("────────────────────────")
    lines.append("📌 *ÖNEMLİ HATIRLATMALAR:*")
    lines.append("📸 Çözemediğin her sorunun fotoğrafını portaldaki *Soru Havuzu*'na yükle, bana anında bildirim gelecek!")
    lines.append("✅ Her etüt bitiminde portaldaki *Doğrula* butonundan çözdüğün soru sayılarını girmeyi unutma.")
    lines.append("💤 *Saat 00:00'da çalışma biter ve dinlenmeye geçilir.* Dinlenmiş zihin başarının ilk şartıdır.")
    lines.append("")
    lines.append("İyi ve verimli çalışmalar dilerim! 🚀")
    lines.append("*Müfit Hoca* (Müfit Hoca ile Matematik)")

    return "\n".join(lines)


def send_message_via_green_api(message_text, chat_id=None, is_auto=False):
    """Green API ile WhatsApp metin mesajı gönderir."""
    today = datetime.date.today()
    if today > PROGRAM_END_DATE:
        msg = f"Program 1 Mayıs 2027 itibarıyla tamamlandı. Gönderim yapılmadı."
        print(f"ℹ️ {msg}")
        log_event(msg)
        return False

    if is_auto and os.path.exists(LAST_SENT_FILE):
        try:
            with open(LAST_SENT_FILE, "r", encoding="utf-8") as f:
                last_date = f.read().strip()
                if last_date == today.isoformat():
                    msg = f"Bugün ({today.isoformat()}) için mesaj zaten iletilmiş. Çift gönderimi önlemek için atlandı."
                    print(f"ℹ️ {msg}")
                    log_event(msg)
                    return True
        except Exception:
            pass

    conf = load_config()
    host = conf.get("host", "https://api.green-api.com").rstrip("/")
    id_instance = conf.get("idInstance", "").strip()
    token = conf.get("apiTokenInstance", "").strip()
    target_chat = chat_id or conf.get("chatId", "").strip()

    if not id_instance or not token or not target_chat:
        msg = "HATA: Green API bilgileri eksik (idInstance, apiTokenInstance veya chatId boş)."
        print(f"\n❌ {msg}")
        print(f"Lütfen '{CONFIG_FILE}' dosyasını açıp bilgileri tamamlayın.")
        log_event(msg)
        return False

    url = f"{host}/waInstance{id_instance}/sendMessage/{token}"
    payload = {
        "chatId": target_chat,
        "message": message_text
    }

    data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json; charset=utf-8"})

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            succ_msg = f"Mesaj başarıyla WhatsApp grubuna iletildi! (HTTP {resp.status})"
            print(f"✅ {succ_msg}")
            log_event(f"{succ_msg} - Alıcı: {target_chat}")
            
            # Son gönderim tarihini mühürle
            try:
                with open(LAST_SENT_FILE, "w", encoding="utf-8") as f:
                    f.write(today.isoformat())
            except Exception:
                pass

            return True
    except urllib.error.HTTPError as e:
        err_msg = f"Sunucu Hatası ({e.code}): {e.read().decode('utf-8')}"
        print(f"\n❌ {err_msg}")
        log_event(f"HATA: {err_msg}")
        return False
    except Exception as e:
        err_msg = f"İstek gönderilirken hata oluştu: {e}"
        print(f"\n❌ {err_msg}")
        log_event(f"HATA: {err_msg}")
        return False


def send_file_via_green_api(file_path=PORTAL_FILE, caption="Fatma ÖZMİL Çalışma Portalı (HTML)", chat_id=None):
    """Green API ile HTML portal dosyasını WhatsApp grubuna belge olarak gönderir."""
    conf = load_config()
    host = conf.get("host", "https://api.green-api.com").rstrip("/")
    id_instance = conf.get("idInstance", "").strip()
    token = conf.get("apiTokenInstance", "").strip()
    target_chat = chat_id or conf.get("chatId", "").strip()

    if not id_instance or not token or not target_chat:
        print("\n❌ HATA: Green API bilgileri eksik!")
        return False

    if not os.path.exists(file_path):
        print(f"\n❌ Dosya bulunamadı: {file_path}")
        return False

    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    url = f"{host}/waInstance{id_instance}/sendFileByUpload/{token}"
    boundary = "----WebKitFormBoundary" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="chatId"\r\n\r\n{target_chat}\r\n'.encode("utf-8"))
    
    if caption:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode("utf-8"))

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'.encode("utf-8"))
    body.extend(b'Content-Type: text/html; charset=utf-8\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )

    try:
        print(f"📤 '{file_name}' ({len(file_bytes)} bayt) WhatsApp grubuna yükleniyor...")
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            print(f"✅ Dosya başarıyla WhatsApp grubuna gönderildi! (HTTP {resp.status})")
            log_event(f"Portal dosyası WhatsApp grubuna iletildi: {target_chat}")
            return True
    except urllib.error.HTTPError as e:
        print(f"\n❌ Sunucu Hatası ({e.code}): {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"\n❌ Dosya gönderilirken hata oluştu: {e}")
        return False


def install_windows_task(run_time="08:30"):
    """Windows Görev Zamanlayıcısına günlük otomatik çalışma ekler."""
    bat_path = os.path.join(SCRIPT_DIR, "calistir_oto.bat")
    cmd = f'schtasks /create /tn "{TASK_NAME}" /tr "\\"{bat_path}\\"" /sc daily /st {run_time} /f'
    print(f"\n⚙️ Windows Görev Zamanlayıcısı Yapılandırılıyor ({run_time})...")
    ret = os.system(cmd)
    if ret == 0:
        print(f"✅ Görev başarıyla oluşturuldu! 1 Mayıs 2027'ye kadar her gün saat {run_time}'da otomatik çalışacak.")
        log_event(f"Windows Görev Zamanlayıcısı kuruldu: {run_time}")
        return True
    else:
        print("❌ Görev oluşturulurken hata oluştu. Komut satırını yönetici olarak çalıştırmayı deneyin.")
        return False


def uninstall_windows_task():
    """Windows Görev Zamanlayıcısından görevi siler."""
    cmd = f'schtasks /delete /tn "{TASK_NAME}" /f'
    ret = os.system(cmd)
    if ret == 0:
        print("✅ Görev başarıyla kaldırıldı.")
        log_event("Windows Görev Zamanlayıcısı kaldırıldı.")
        return True
    else:
        print("❌ Görev bulunamadı veya yetki hatası.")
        return False


def list_and_select_group():
    """Green API'den tüm sohbetleri/grupları çeker ve kullanıcının seçmesini sağlar."""
    conf = load_config()
    host = conf.get("host", "https://api.green-api.com").rstrip("/")
    id_instance = conf.get("idInstance", "").strip()
    token = conf.get("apiTokenInstance", "").strip()

    if not id_instance or not token or "BURAYA" in token:
        print("\n❌ HATA: apiTokenInstance henüz girilmemiş!")
        print("Lütfen önce menüden 5'e basarak veya 'green_api_config.json' dosyasından tokeninizi girin.")
        return False

    url = f"{host}/waInstance{id_instance}/getChats/{token}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    print("\n🔍 Green API'den WhatsApp sohbetleriniz taranıyor...")
    try:
        with urllib.request.urlopen(req) as resp:
            chats = json.loads(resp.read().decode('utf-8'))
            if not chats:
                print("ℹ️ Sohbet bulunamadı.")
                return False
            
            groups = [c for c in chats if c.get("id", "").endswith("@g.us")]
            other_chats = [c for c in chats if not c.get("id", "").endswith("@g.us")][:10]

            print("\n" + "=" * 68)
            print("📱 BULUNAN WHATSAPP GRUPLARINIZ:")
            print("=" * 68)
            all_selectable = []
            idx = 1
            for g in groups:
                name = g.get("name") or "İsimsiz Grup"
                gid = g.get("id")
                print(f"  [{idx}] 👥 {name}")
                print(f"       Grup Kodu (chatId): {gid}")
                all_selectable.append((name, gid))
                idx += 1

            if other_chats:
                print("\n📞 BİREYSEL NUMARALAR (Son 10):")
                for c in other_chats:
                    name = c.get("name") or c.get("id")
                    cid = c.get("id")
                    print(f"  [{idx}] 👤 {name} ({cid})")
                    all_selectable.append((name, cid))
                    idx += 1

            print("-" * 68)
            sel = input("\nFatma için kurduğunuz grubun numarasını seçin (Örn: 1) veya Vazgeçmek için 'v': ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(all_selectable):
                chosen_name, chosen_id = all_selectable[int(sel) - 1]
                conf["chatId"] = chosen_id
                save_config(conf)
                print(f"\n✅ Harika! '{chosen_name}' grubu başarıyla kaydedildi! (ID: {chosen_id})")
                return True
            else:
                print("İşlem iptal edildi.")
                return False
    except Exception as e:
        print(f"❌ Sohbetler çekilirken hata oluştu: {e}")
        return False


def interactive_menu():
    """Komut satırından kullanıcı dostu menü."""
    print("=" * 68)
    print("🤖 FATMA ÖZMİL ÇALIŞMA PROGRAMI - GREEN API WHATSAPP BOTU")
    print(f"📅 Takvim: 26 Eylül 2026 - 1 Mayıs 2027 (31 Hafta)")
    print("=" * 68)
    
    conf = load_config()
    print(f"📌 Mevcut Ayarlar:")
    print(f"   • Host: {conf.get('host', 'Tanımsız')}")
    print(f"   • idInstance: {conf.get('idInstance') or '❌ (Eksik)'}")
    print(f"   • apiTokenInstance: {'*' * 8 if conf.get('apiTokenInstance') and 'BURAYA' not in conf.get('apiTokenInstance') else '❌ (Eksik)'}")
    print(f"   • Grup/Numara ChatId: {conf.get('chatId') if conf.get('chatId') and 'BURAYA' not in conf.get('chatId') else '❌ (Eksik)'}")
    print("-" * 68)

    print("1. 📤 Bugünkü Programı WhatsApp Grubu'na Hemen Gönder")
    print("2. 👁️ Bugünkü Programı Ekranda Önizle (Göndermeden Gör)")
    print("3. 🗓️ Belirli Bir Günün Programını Seçip Gönder / Önizle")
    print("4. 📎 Portal HTML Dosyasını (fatma_calisma_ve_deneme_paneli.html) Gruba Gönder")
    print("5. ⚙️ Green API Bilgilerini Güncelle (idInstance, Token, ChatId)")
    print("6. 🔍 Sohbetleri Listele & Fatma'nın Grubunu Otomatik Seç")
    print("7. ⏰ Her Sabah Otomatik Gönderim Kur (Windows Görev Zamanlayıcısı)")
    print("8. 🗑️ Otomatik Günlük Görevi Kaldır")
    print("0. Çıkış")
    print("-" * 68)

    choice = input("Seçiminiz (0-8): ").strip()

    if choice == "1":
        msg = generate_whatsapp_message()
        print("\n--- GÖNDERİLECEK MESAJ ---")
        print(msg)
        print("--------------------------")
        confirm = input("Bu mesajı gruba göndermek istiyor musunuz? (e/h): ").strip().lower()
        if confirm == 'e':
            send_message_via_green_api(msg)
    elif choice == "2":
        msg = generate_whatsapp_message()
        print("\n" + "=" * 60)
        print(msg)
        print("=" * 60)
    elif choice == "3":
        print("\nGün Seçin:")
        for idx, d in DAILY_SCHEDULES.items():
            print(f"  {idx}: {d['name']} ({d['title']})")
        sel = input("Gün Numarası (0-6): ").strip()
        if sel.isdigit() and int(sel) in DAILY_SCHEDULES:
            idx = int(sel)
            msg = generate_whatsapp_message(day_index=idx)
            print("\n" + "=" * 60)
            print(msg)
            print("=" * 60)
            confirm = input("Bu mesajı gruba göndermek istiyor musunuz? (e/h): ").strip().lower()
            if confirm == 'e':
                send_message_via_green_api(msg)
    elif choice == "4":
        confirm = input("HTML Portal dosyasını gruba göndermek istiyor musunuz? (e/h): ").strip().lower()
        if confirm == 'e':
            send_file_via_green_api()
    elif choice == "5":
        id_inst = input(f"Yeni idInstance [{conf.get('idInstance')}]: ").strip() or conf.get('idInstance')
        tok = input(f"Yeni apiTokenInstance: ").strip() or conf.get('apiTokenInstance')
        cid = input(f"Yeni WhatsApp ChatId [{conf.get('chatId')}]: ").strip() or conf.get('chatId')
        conf['idInstance'] = id_inst
        conf['apiTokenInstance'] = tok
        conf['chatId'] = cid
        save_config(conf)
        print("✅ Ayarlar kaydedildi!")
    elif choice == "6":
        list_and_select_group()
    elif choice == "7":
        hour = input("Mesaj her sabah saat kaçta gönderilsin? [Varsayılan: 08:30]: ").strip() or "08:30"
        install_windows_task(hour)
    elif choice == "8":
        uninstall_windows_task()
    elif choice == "0":
        print("Çıkış yapıldı.")


def main():
    parser = argparse.ArgumentParser(description="Green API WhatsApp Günlük Program Gönderici")
    parser.add_argument("--day", help="Gönderilecek gün (Cumartesi, Pazar, Pazartesi vb.)")
    parser.add_argument("--preview", action="store_true", help="Mesajı sadece ekranda gösterir, göndermez")
    parser.add_argument("--send", action="store_true", help="Mesajı Green API ile hemen gönderir")
    parser.add_argument("--auto", action="store_true", help="Zamanlanmış otomatik mod (tarih ve çift gönderim korumalı)")
    parser.add_argument("--send-file", action="store_true", help="Portal HTML dosyasını belge olarak gönderir")
    parser.add_argument("--list-chats", action="store_true", help="WhatsApp gruplarını ve sohbetlerini listeler")
    parser.add_argument("--install-task", help="Windows Görev Zamanlayıcısına günlük kur (örn: 08:30)")
    parser.add_argument("--uninstall-task", action="store_true", help="Windows Görev Zamanlayıcısından kaldır")
    parser.add_argument("--chat-id", help="Özel hedef WhatsApp chatId (Grup veya numara)")

    args = parser.parse_args()

    if args.list_chats:
        list_and_select_group()
        return

    if args.install_task:
        install_windows_task(args.install_task)
        return

    if args.uninstall_task:
        uninstall_windows_task()
        return

    if len(sys.argv) == 1:
        interactive_menu()
        return

    day_idx = None
    if args.day:
        normalized = args.day.lower().strip()
        day_idx = DAY_NAME_TO_INDEX.get(normalized, None)

    msg = generate_whatsapp_message(day_index=day_idx)

    if args.preview:
        print("\n" + "=" * 60)
        print(msg)
        print("=" * 60)

    if args.send:
        send_message_via_green_api(msg, chat_id=args.chat_id)

    if args.auto:
        send_message_via_green_api(msg, chat_id=args.chat_id, is_auto=True)

    if args.send_file:
        send_file_via_green_api(chat_id=args.chat_id)


if __name__ == "__main__":
    main()
