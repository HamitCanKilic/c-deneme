# Telegram ile Değişen Dış IP Bildirimi

Bu repo içindeki `ip_notifier.py`, dış IP adresini kontrol eder ve önceki IP'den farklıysa Telegram botu üzerinden mesaj atar.

## 1) Telegram ayarları

1. `@BotFather` üzerinden bir bot oluşturun ve token alın.
2. Bot ile bir konuşma başlatın (veya gruba ekleyin).
3. `chat_id` değerinizi öğrenin. Pratik yöntem:
   - `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` çağırın.
   - JSON içinde `chat.id` alanını bulun.

## 2) Ortam değişkenleri

```bash
export TELEGRAM_BOT_TOKEN="123456:ABCDEF..."
export TELEGRAM_CHAT_ID="987654321"
```

Opsiyonel:

```bash
export IP_STATE_FILE="$HOME/.ip-notifier/last_ip.txt"
export IP_SERVICE_URL="https://api.ipify.org"
export IP_NOTIFIER_TIMEOUT="10"
```

## 3) Manuel test

```bash
python3 ip_notifier.py --state-file "$HOME/.ip-notifier/last_ip.txt"
```

- İlk çalışmada mevcut IP'yi "ilk kayıt" olarak bildirir.
- Sonraki çalışmalarda sadece değişiklik olursa mesaj yollar.

## 4) Elektrik sonrası otomatik çalışma (önerilen)

Elektrik gidip gelince cihazınız yeniden açıldığında kontrol etmesi için `cron` kullanabilirsiniz:

```bash
crontab -e
```

Açılan dosyaya şunları ekleyin:

```cron
@reboot sleep 60 && /usr/bin/env TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..." /usr/bin/python3 /path/to/ip_notifier.py --state-file /home/<kullanici>/.ip-notifier/last_ip.txt >> /home/<kullanici>/ip-notifier.log 2>&1
*/5 * * * * /usr/bin/env TELEGRAM_BOT_TOKEN="..." TELEGRAM_CHAT_ID="..." /usr/bin/python3 /path/to/ip_notifier.py --state-file /home/<kullanici>/.ip-notifier/last_ip.txt >> /home/<kullanici>/ip-notifier.log 2>&1
```

- `@reboot`: Elektrik geldiğinde cihaz açılır açılmaz (60 sn gecikmeyle) kontrol eder.
- `*/5`: Her 5 dakikada bir kontrol eder (modem yeniden bağlanınca IP değişimini kaçırmamak için).

## 5) Notlar

- CGNAT kullanıyorsanız dış IP değişebilir ama evdeki cihazlara doğrudan erişim yine kısıtlı olabilir.
- Dış IP kaynağını değiştirmek isterseniz `--ip-service` kullanabilirsiniz.

---

## Raspberry Pi için çalışan mini demo (Web UI + GPIO)

`pi_mini_demo/` klasöründe, tarayıcıdan açılan modern bir panel bulunur:

- LED aç/kapat (`GPIO 17`)
- Demo sıcaklık kartı
- Raspberry Pi dışındaki ortamlarda otomatik `mock` mod

### Kurulum

```bash
cd pi_mini_demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Tarayıcıdan açın:

- `http://<raspberrypi-ip>:5000`

### Donanım bağlantısı (opsiyonel)

- LED uzun bacak (anot) → 330Ω direnç → GPIO17 (Pin 11)
- LED kısa bacak (katot) → GND

> Uyarı: GPIO pinine doğrudan (dirençsiz) LED bağlamayın.
