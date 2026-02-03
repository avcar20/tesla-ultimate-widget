# 🏎️ Tesla Ultimate Desktop Widget

Tesla'nızın şarj durumunu, menzilini, sıcaklığını ve güvenlik uyarılarını masaüstünüzden anlık olarak takip edin. Bu widget, **TeslaMate** verilerini MQTT üzerinden çekerek çalışır.

## ✨ Özellikler
- 🔋 **Anlık Pil & Menzil:** Kalan yüzde ve tahmini menzil.
- 🏠 **İç & Dış Sıcaklık:** Aracın iç ve dış ısısı.
- ⚡ **Şarj Paneli:** Şarj olurken otomatik açılır; güç (kW), maliyet (₺), süre ve eklenen enerji (kWh) bilgilerini gösterir.
- 🚨 **Güvenlik Bildirimleri:** Araç kilitliyken kapı açılırsa veya hareket algılanırsa masaüstü bildirimi gönderir.
- 💰 **Maliyet Hesaplama:** Elektrik birim fiyatına göre dolum maliyetini gösterir.

## 🚀 Kurulum ve Çalıştırma
🏎️ Tesla Ultimate Desktop Widget & Dashboard
Bu proje, Tesla aracınızın verilerini TeslaMate üzerinden çekerek masaüstünüzde şık bir widget ve detaylı bir analiz paneli sunar.
Hiçbir teknik kurulumla uğraşmanıza gerek kalmadan, sadece Docker kullanarak tüm sistemi ayağa kaldırabilirsiniz.

🚀 Hızlı Kurulum
1. Adım: Docker'ı İndirin (https://www.docker.com/products/docker-desktop/)
Sistemin çalışması için bilgisayarınızda Docker yüklü olmalıdır.
Docker Desktop indirip kurun ve bilgisayarınızı yeniden başlatın.

2. Adım: Sistemi Başlatın
Proje klasörüne girip bir terminal açın ve şu komutu yazın:

docker-compose up -d

Bu komut; TeslaMate, veritabanı, MQTT sunucusu ve masaüstü widget'ını otomatik olarak kurup başlatacaktır.

3. Adım: Aracınızı Bağlayın (Token Alma)
Sistemi aracınıza tanıtmak için şu adımları izleyin:
-Token Alın: Access Token Generator for Tesla eklentisini kurun (https://chromewebstore.google.com/detail/access-token-generator-fo/djpjpanpjaimfjalnpkppkjiedmgpjpe).
Eklenti üzerinden Tesla hesabınızla giriş yaparak Access ve Refresh kodlarınızı alın.
-Sisteme Giriş Yapın: Tarayıcınızdan http://localhost:4000 adresine gidin ve aldığınız kodları yapıştırın.
-Hızlı Veri Ayarı: Sağ üstten Ayarlar (Settings) kısmına girin ve "Streaming API" (Eşzamanlı-API) seçeneğini AÇIK (Enabled) yapıp kaydedin.
📊 Neler Dahil?
-Masaüstü Widget: Sol altta anlık pil yüzdesi, menzil ve sıcaklık bilgileri.
-Güvenlik: Araç kilitliyken kapı açılırsa veya hareket algılanırsa masaüstü bildirimi gönderir.
-Detaylı Analiz (Grafana): http://localhost:3000 adresinden (Kullanıcı: admin, Şifre: admin) şarj geçmişinizi ve batarya sağlığınızı takip edebilirsiniz.

🖱️ Kullanım İpuçları
Kapatma: Widget üzerine çift tıklayarak uygulamayı sonlandırabilirsiniz.
Veri Gelmiyorsa: Aracın uyanması için telefon uygulamasından bir kez kilidi aç-kapat yapmanız yeterlidir.
Uygulamayı Başka zamanda kullanmak için docker programını çalıştırıp teslax.py dosyasına çift tıklayınca yine sol altta açılıyor.

Açıklama;
Eğer elektriğin birim fiyatı değiştirmek isterseniz teslax.py dosyasını notepad ile açıp "ELECTRICITY_PRICE = 3.45" bölümünden değiştirebilirsiniz.