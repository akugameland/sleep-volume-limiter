# Ses Sınırlayıcı

Uyurken dinlenen klasik müzikte yüksek kısımlar gelince Windows sesini otomatik kısar,
müzik sakinleşince yavaşça geri açar. YouTube, Spotify, tarayıcı, her oynatıcıyla çalışır.

## Kurulum (bir kere)
```
python -m pip install -r requirements.txt
```

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
- Ayarlar `ayarlar.json` dosyasına kaydedilir.

## Bilinmesi gereken
- Program sesi duyduktan sonra kısar (yaklaşık 0,1 saniye). Çok ani bir davul vuruşunun
  ilk anı kısa bir an geçebilir, sonrası hemen kısılır.
- En fazla 30 dB kısar (sesin tamamen kaybolmaması için).

## Lisans
MIT. Ayrıntı için `LICENSE` dosyasına bak.
