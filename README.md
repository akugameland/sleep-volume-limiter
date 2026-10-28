# Ses Sınırlayıcı

Uyurken dinlenen klasik müzikte yüksek kısımlar gelince Windows sesini otomatik kısar,
müzik sakinleşince yavaşça geri açar. YouTube, Spotify, tarayıcı, her oynatıcıyla çalışır.

## Kurulum
Ayrıca bir şey yapmana gerek yok. Sağ üstteki yeşil **Code** düğmesinden **Download ZIP** ile indir,
bir klasöre çıkar ve `Baslat.bat` dosyasına çift tıkla. İlk açılışta kurulum kendiliğinden yapılır
(internet gerekir, yaklaşık yarım dakika):

- Bilgisayarda Python 3.12 yoksa `winget` ile kullanıcı hesabına kurulur (yönetici izni gerekmez).
- Program, kendi klasöründeki `.venv` içine 3 küçük paket kurar (pycaw, comtypes, psutil).
  Bilgisayarın geri kalanına dokunmaz. Kaldırmak için klasörü silmen yeterli.
- Paketler sabit sürümle ve parmak iziyle (sha256) kurulur. PyPI'daki dosya değiştirilmişse kurulum durur.

Kurulumu baştan yapmak istersen `KURULUM.bat` dosyasını çalıştır.

## Kullanım
1. `Baslat.bat` dosyasına çift tıkla.
2. Sesi her zamanki gibi Windows ses ayarından rahat bir seviyeye getir (bu "normal ses" olur).
3. Müziğin sana fazla gelen bir anında **"Şu anki ses seviyesi tavan olsun"** düğmesine bas.
   Ya da "Ses tavanı" kaydırıcısıyla ayarla (sola = daha sessiz tavan).
4. Pencereyi simge durumuna küçültüp uyuyabilirsin.

Program kapatılınca ses kendi normal ayarına geri döner.

## Ayarlar
- **Ses tavanı:** duyulan ses bu seviyeyi geçince kısılır.
- **Geri açılma hızı:** kısıldıktan sonra sesin geri yükselme hızı. Düşük değer daha yumuşaktır, uyku için 2-3 iyi.
- Müzikte sessizlik ya da duraklama olunca ses geri açılmaz. Böylece büyük bir patlama öncesi
  sessizlikte ses birden açılıp seni uyandırmaz.
- Sesi elle değiştirirsen program bunu yeni "normal ses" olarak kabul eder.
- Ayarlar `ayarlar.json` dosyasına kaydedilir. Dosya bozulursa program çökmez, varsayılan ayarlarla açılır;
  aralık dışındaki değerler güvenli sınırlara çekilir (en fazla kısma 30 dB'yi geçemez).

## Bilinmesi gereken
- Program sesi duyduktan sonra kısar (yaklaşık 0,1 saniye). Çok ani bir davul vuruşunun
  ilk anı kısa bir an geçebilir, sonrası hemen kısılır.
- En fazla 30 dB kısar (sesin tamamen kaybolmaması için).

## Lisans
MIT. Ayrıntı için `LICENSE` dosyasına bak.
