"""Ses Sınırlayıcı: Windows'ta çalan sesin yüksek kısımlarında ana sesi otomatik kısar.

Çalışma mantığı:
- Windows ses ölçeri, sesin ana ses ayarından ÖNCEKİ seviyesini verir (test edildi).
- Duyulan seviye = müzik seviyesi (dBFS) + Windows ana ses ayarı (dB).
- Duyulan seviye tavanı aşarsa ana ses hızla kısılır; müzik sakinleşince yavaşça
  kullanıcının kendi ayarladığı "normal ses"e geri döner.
- Müzikte sessizlik olunca (ör. büyük tutti öncesi duraklama) ses geri açılmaz, olduğu yerde bekler.
"""
import json
import math
import os
import threading
import time
import tkinter as tk
from tkinter import ttk

import comtypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IAudioMeterInformation

AYAR_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ayarlar.json")
VARSAYILAN = {
    "acik": True,
    "tavan_db": -30.0,      # duyulan seviye bunu geçmesin
    "geri_acilma": 3.0,     # dB/saniye
    "bekleme": 2.0,         # kısmadan sonra geri açılmadan önce bekleme (sn)
    "en_fazla_kisma": 30.0, # normal sesin en fazla kaç dB altına inilir
}

ADIM = 0.025              # ölçüm aralığı (sn)
HIZLI_PENCERE = 8         # 8 x 25 ms = 200 ms
SESSIZLIK_DB = -55.0      # bunun altı "duraklama" sayılır, ses geri açılmaz
ATAK_SURESI = 0.08        # kısma zaman sabiti (sn)
ELLE_DEGISIM_DB = 0.6     # bundan büyük fark = kullanıcı sesi elle değiştirdi


def ayarlari_yukle():
    ayar = dict(VARSAYILAN)
    try:
        with open(AYAR_DOSYASI, encoding="utf-8") as f:
            ayar.update({k: v for k, v in json.load(f).items() if k in VARSAYILAN})
    except (OSError, ValueError):
        pass
    return ayar


def ayarlari_kaydet(ayar):
    try:
        with open(AYAR_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(ayar, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def db(x):
    return 20 * math.log10(max(x, 1e-6))


class Cihaz:
    """Varsayılan hoparlörün ses ayarı ve ölçeri."""

    def __init__(self):
        aygit = AudioUtilities.GetSpeakers()
        aygit = getattr(aygit, "_dev", aygit)
        self.ses = aygit.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None).QueryInterface(IAudioEndpointVolume)
        self.olcer = aygit.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None).QueryInterface(IAudioMeterInformation)
        self.en_dusuk = self.ses.GetVolumeRange()[0]

    def seviye(self):
        return self.ses.GetMasterVolumeLevel()

    def ayarla(self, deger_db):
        deger_db = min(0.0, max(self.en_dusuk, deger_db))
        self.ses.SetMasterVolumeLevel(deger_db, None)
        return deger_db

    def yuzde(self):
        return round(self.ses.GetMasterVolumeLevelScalar() * 100)


class Sinirlayici(threading.Thread):
    def __init__(self, ayar):
        super().__init__(daemon=True)
        self.ayar = ayar
        self.durdur = threading.Event()
        self.kilit = threading.Lock()
        self.durum = {"muzik_db": -100.0, "duyulan_db": -100.0, "kisma_db": 0.0,
                      "normal_yuzde": 0, "hata": ""}
        self.tavani_simdi_al = False

    def run(self):
        comtypes.CoInitialize()
        try:
            while not self.durdur.is_set():
                try:
                    self._dongu()
                except (OSError, comtypes.COMError) as e:
                    # Kulaklık takılıp çıkarılınca vb. cihaz değişir: yeniden bağlan.
                    with self.kilit:
                        self.durum["hata"] = f"Ses cihazı bulunamadı, yeniden deneniyor ({e.__class__.__name__})"
                    time.sleep(2)
        finally:
            comtypes.CoUninitialize()

    def _dongu(self):
        cihaz = Cihaz()
        normal = cihaz.seviye()          # kullanıcının istediği ses (dB)
        normal_yuzde = cihaz.yuzde()
        simdiki = normal                 # programın hedeflediği ses (dB)
        son_ayarlanan = normal
        son_kisma_zamani = 0.0
        tepeler = []
        with self.kilit:
            self.durum["hata"] = ""
        try:
            while not self.durdur.is_set():
                t0 = time.monotonic()
                tepeler.append(cihaz.olcer.GetPeakValue())
                if len(tepeler) > HIZLI_PENCERE:
                    tepeler.pop(0)
                muzik_db = 10 * math.log10(max(sum(p * p for p in tepeler) / len(tepeler), 1e-12))

                # Kullanıcı Windows sesini elle değiştirdiyse yeni "normal ses" odur.
                gercek = cihaz.seviye()
                if abs(gercek - son_ayarlanan) > ELLE_DEGISIM_DB:
                    normal = simdiki = son_ayarlanan = gercek
                    normal_yuzde = cihaz.yuzde()

                acik = self.ayar["acik"]
                if self.tavani_simdi_al:
                    self.tavani_simdi_al = False
                    if muzik_db > SESSIZLIK_DB:
                        self.ayar["tavan_db"] = round(muzik_db + simdiki, 1)

                if acik:
                    tavan = self.ayar["tavan_db"]
                    taban = normal - self.ayar["en_fazla_kisma"]
                    hedef = max(taban, min(normal, tavan - muzik_db))
                    if hedef < simdiki:
                        simdiki += (hedef - simdiki) * (1 - math.exp(-ADIM / ATAK_SURESI))
                        son_kisma_zamani = t0
                    elif (muzik_db > SESSIZLIK_DB
                          and t0 - son_kisma_zamani > self.ayar["bekleme"]):
                        simdiki = min(hedef, simdiki + self.ayar["geri_acilma"] * ADIM)
                else:
                    simdiki = normal

                if abs(simdiki - son_ayarlanan) > 0.2 or (simdiki == normal and son_ayarlanan != normal):
                    son_ayarlanan = cihaz.ayarla(simdiki)

                with self.kilit:
                    self.durum.update(muzik_db=muzik_db, duyulan_db=muzik_db + son_ayarlanan,
                                      kisma_db=normal - son_ayarlanan, normal_yuzde=normal_yuzde)
                time.sleep(max(0.0, ADIM - (time.monotonic() - t0)))
        finally:
            # Çıkarken sesi kullanıcının normal ayarına geri ver.
            try:
                cihaz.ayarla(normal)
            except (OSError, comtypes.COMError):
                pass


# ---------------------------------------------------------------- arayüz
ARKA = "#15171c"
KUTU = "#1f232b"
YAZI = "#d8dce4"
SOLUK = "#8a909c"
YESIL = "#3fae6a"
SARI = "#d7a531"
KIRMIZI = "#d0504a"
OLCER_MIN, OLCER_MAX = -80.0, 0.0


class Arayuz:
    def __init__(self):
        self.ayar = ayarlari_yukle()
        self.motor = Sinirlayici(self.ayar)

        self.kok = tk.Tk()
        self.kok.title("Ses Sınırlayıcı")
        self.kok.configure(bg=ARKA)
        self.kok.resizable(False, False)
        self.kok.protocol("WM_DELETE_WINDOW", self.kapat)

        stil = ttk.Style()
        stil.theme_use("clam")
        stil.configure("TScale", background=ARKA, troughcolor=KUTU)

        cerceve = tk.Frame(self.kok, bg=ARKA, padx=16, pady=14)
        cerceve.pack()

        self.dugme = tk.Button(cerceve, font=("Segoe UI", 13, "bold"), width=22, relief="flat",
                               fg="white", activeforeground="white", command=self.ac_kapa)
        self.dugme.pack(pady=(0, 12))

        self.olcer = tk.Canvas(cerceve, width=380, height=34, bg=KUTU, highlightthickness=0)
        self.olcer.pack()
        self.bilgi = tk.Label(cerceve, bg=ARKA, fg=YAZI, font=("Segoe UI", 10), justify="left")
        self.bilgi.pack(anchor="w", pady=(6, 10))

        self.tavan = tk.DoubleVar(value=self.ayar["tavan_db"])
        self.tavan_yazi = self._kaydirici(cerceve, "Ses tavanı (en yüksek izin verilen seviye)",
                                          self.tavan, -70, -5, self._tavan_degisti)
        tk.Button(cerceve, text="Şu anki ses seviyesi tavan olsun", font=("Segoe UI", 10),
                  bg=KUTU, fg=YAZI, activebackground="#2b303a", activeforeground=YAZI,
                  relief="flat", command=self.tavani_simdi_al).pack(fill="x", pady=(2, 12))

        self.hiz = tk.DoubleVar(value=self.ayar["geri_acilma"])
        self.hiz_yazi = self._kaydirici(cerceve, "Geri açılma hızı (düşük = daha yumuşak)",
                                        self.hiz, 0.5, 10, self._hiz_degisti)

        tk.Label(cerceve, bg=ARKA, fg=SOLUK, font=("Segoe UI", 9), justify="left", wraplength=380,
                 text="Normal sesi her zamanki gibi Windows ses ayarından yap. Program yalnızca "
                      "yüksek kısımlarda kısar, sonra yavaşça geri açar. Kapatınca ses normale döner.",
                 ).pack(anchor="w", pady=(10, 0))

        self._tavan_degisti()
        self._hiz_degisti()
        self._dugmeyi_guncelle()
        self.motor.start()
        self._yenile()

    def _kaydirici(self, ust, baslik, degisken, en_az, en_cok, komut):
        satir = tk.Frame(ust, bg=ARKA)
        satir.pack(fill="x")
        tk.Label(satir, text=baslik, bg=ARKA, fg=YAZI, font=("Segoe UI", 10)).pack(side="left")
        deger = tk.Label(satir, bg=ARKA, fg=SARI, font=("Segoe UI", 10, "bold"))
        deger.pack(side="right")
        ttk.Scale(ust, from_=en_az, to=en_cok, variable=degisken, length=380,
                  command=lambda _: komut()).pack(fill="x")
        return deger

    def _tavan_degisti(self):
        self.ayar["tavan_db"] = round(self.tavan.get(), 1)
        self.tavan_yazi.config(text=f"{self.ayar['tavan_db']:.0f} dB")

    def _hiz_degisti(self):
        self.ayar["geri_acilma"] = round(self.hiz.get(), 1)
        self.hiz_yazi.config(text=f"{self.ayar['geri_acilma']:.1f} dB/sn")

    def tavani_simdi_al(self):
        self.motor.tavani_simdi_al = True

    def ac_kapa(self):
        self.ayar["acik"] = not self.ayar["acik"]
        self._dugmeyi_guncelle()

    def _dugmeyi_guncelle(self):
        if self.ayar["acik"]:
            self.dugme.config(text="AÇIK: yüksek sesler kısılıyor", bg=YESIL, activebackground=YESIL)
        else:
            self.dugme.config(text="KAPALI: ses olduğu gibi", bg="#555b66", activebackground="#555b66")

    def _x(self, deger_db):
        oran = (min(OLCER_MAX, max(OLCER_MIN, deger_db)) - OLCER_MIN) / (OLCER_MAX - OLCER_MIN)
        return oran * 380

    def _yenile(self):
        with self.motor.kilit:
            d = dict(self.motor.durum)
        # Tavan "Şu anki seviye" ile değiştiyse kaydırıcıyı eşitle.
        if abs(self.tavan.get() - self.ayar["tavan_db"]) > 0.05:
            self.tavan.set(self.ayar["tavan_db"])
            self._tavan_degisti()

        c = self.olcer
        c.delete("all")
        duyulan, tavan = d["duyulan_db"], self.ayar["tavan_db"]
        renk = KIRMIZI if duyulan > tavan + 1 else (SARI if d["kisma_db"] > 0.5 else YESIL)
        if d["muzik_db"] > -90:
            c.create_rectangle(0, 6, self._x(duyulan), 28, fill=renk, width=0)
        tx = self._x(tavan)
        c.create_line(tx, 0, tx, 34, fill="white", width=2)
        c.create_text(min(tx + 4, 340), 3, text="tavan", anchor="nw", fill=SOLUK, font=("Segoe UI", 8))

        if d["hata"]:
            metin = d["hata"]
        else:
            kisma = d["kisma_db"]
            durum = f"{kisma:.0f} dB kısıldı" if kisma > 0.5 else "kısma yok"
            seviye = f"{duyulan:.0f} dB" if d["muzik_db"] > -90 else "ses yok"
            metin = (f"Duyulan seviye: {seviye}   |   {durum}\n"
                     f"Normal ses (Windows): %{d['normal_yuzde']}")
        self.bilgi.config(text=metin)
        self.kok.after(100, self._yenile)

    def kapat(self):
        ayarlari_kaydet(self.ayar)
        self.motor.durdur.set()
        self.motor.join(timeout=2)
        self.kok.destroy()

    def calistir(self):
        self.kok.mainloop()


if __name__ == "__main__":
    Arayuz().calistir()
