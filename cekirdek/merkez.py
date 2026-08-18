"""Esenlik merkezi etmeni.

Her merkez tek tek izlenir. Kendi ruhsat tarihi, hizmet sepeti, uyum durumu
ve en önemlisi kendi tespit sayaçları vardır. EK-4 yaptırımları birinci,
ikinci ve üçüncü tespitte farklı sonuç doğurduğu için sayaçların merkez
bazında tutulması şart; ortalamaya indirgenirse merdiven anlamını yitirir.
"""

AKTIF = "aktif"
KAPALI = "kapali"

# Kapanma nedenleri
IPTAL = "ruhsat_iptali"
ZARAR = "ekonomik"


class Merkez:

    def __init__(self, kimlik, yil, yerlesim, tur, kapali_alan, oda_sayisi,
                 arketip, hizmet_sepeti, uyum_durumu, kapasite):
        self.kimlik = kimlik
        self.acilis_yili = yil
        self.yerlesim = yerlesim
        self.tur = tur
        self.kapali_alan = kapali_alan
        self.oda_sayisi = oda_sayisi
        self.arketip = arketip
        self.hizmet_sepeti = set(hizmet_sepeti)
        self.uyum_durumu = uyum_durumu
        self.kapasite = kapasite

        self.ruhsatsiz = False
        self.durum = AKTIF
        self.kapanma_yili = None
        self.kapanma_nedeni = None

        self.zayif_kurallar = set()  # tekrar tekrar takıldığı EK-4 soruları
        self.tespit = {}            # kural kodu -> kaçıncı tespit
        self.tespit_gecmisi = []    # (yıl, kural, kademe)
        self.ceza_toplami = 0
        self.durdurulan_gun = 0
        self.son_yil_cezali = False

        self.hizmet_verdigi = {}    # yıl -> kişi sayısı
        self.zarar_yili = 0
        self.gecmis = []            # yıl -> özet kayıt

    # ------------------------------------------------------------------
    @property
    def acik(self):
        return self.durum == AKTIF

    def yillik_kapasite(self, yil):
        """Faaliyet durdurma cezası o yılın kapasitesini kırpar."""
        if not self.acik:
            return 0
        kayip = min(self.durdurulan_gun, 300) / 365.0
        return int(round(self.kapasite * (1.0 - kayip)))

    def doluluk(self, yil):
        tavan = self.yillik_kapasite(yil)
        if tavan <= 0:
            return 0.0
        return self.hizmet_verdigi.get(yil, 0) / float(tavan)

    def tespit_ekle(self, yil, kural_kodu):
        """Bir ihlali kaydeder ve kaçıncı tespit olduğunu döndürür."""
        kademe = self.tespit.get(kural_kodu, 0) + 1
        self.tespit[kural_kodu] = kademe
        self.tespit_gecmisi.append((yil, kural_kodu, kademe))
        return kademe

    def kapat(self, yil, neden):
        self.durum = KAPALI
        self.kapanma_yili = yil
        self.kapanma_nedeni = neden

    def yasi(self, yil):
        return yil - self.acilis_yili

    def ozet(self):
        return {
            "kimlik": self.kimlik,
            "acilis_yili": self.acilis_yili,
            "yerlesim": self.yerlesim,
            "tur": self.tur,
            "kapali_alan": self.kapali_alan,
            "oda_sayisi": self.oda_sayisi,
            "arketip": self.arketip,
            "hizmet_sepeti": sorted(self.hizmet_sepeti),
            "kapasite": self.kapasite,
            "uyum_durumu": self.uyum_durumu,
            "durum": self.durum,
            "kapanma_yili": self.kapanma_yili,
            "kapanma_nedeni": self.kapanma_nedeni,
            "ucuncu_tespit": sum(1 for k in self.tespit.values() if k >= 3),
            "toplam_tespit": sum(self.tespit.values()),
            "zayif_kurallar": sorted(self.zayif_kurallar),
            "tespit": dict(self.tespit),
            "tespit_gecmisi": list(self.tespit_gecmisi),
            "ceza_toplami": self.ceza_toplami,
            "gecmis": self.gecmis,
        }
