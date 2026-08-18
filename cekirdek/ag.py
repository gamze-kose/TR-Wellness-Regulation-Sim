"""Ayrık Bayes ağı: ileri yönlü (ancestral) örnekleme.

Yalnızca standart kütüphane kullanır. Öğrenme yoktur; koşullu olasılık
tabloları dışarıdan verilir. Çıkarım yapılmaz, yalnızca örnekleme yapılır.
"""

import json
import random


class BayesAgi:
    def __init__(self, tanim):
        self.dugumler = tanim["dugumler"]
        self.sira = self._topolojik_sira()

    def _topolojik_sira(self):
        kalan = dict(self.dugumler)
        sira = []
        yerlesen = set()
        while kalan:
            hazir = [ad for ad, d in kalan.items()
                     if all(e in yerlesen for e in d.get("ebeveynler", []))]
            if not hazir:
                raise ValueError("Ağda döngü var: " + ", ".join(sorted(kalan)))
            for ad in sorted(hazir):
                sira.append(ad)
                yerlesen.add(ad)
                del kalan[ad]
        return sira

    def _anahtar(self, dugum, atama):
        ebeveynler = dugum.get("ebeveynler", [])
        if not ebeveynler:
            return "*"
        return "|".join(atama[e] for e in ebeveynler)

    def _sec(self, durumlar, agirliklar, rnd):
        toplam = sum(agirliklar)
        if toplam <= 0:
            raise ValueError("Olasılık toplamı sıfır")
        esik = rnd.random() * toplam
        birikim = 0.0
        for durum, agirlik in zip(durumlar, agirliklar):
            birikim += agirlik
            if esik <= birikim:
                return durum
        return durumlar[-1]

    def ornekle(self, rnd):
        atama = {}
        for ad in self.sira:
            dugum = self.dugumler[ad]
            anahtar = self._anahtar(dugum, atama)
            satir = dugum["kpt"].get(anahtar)
            if satir is None:
                raise KeyError("Koşullu olasılık tablosu satırı eksik: %s -> %s" % (ad, anahtar))
            atama[ad] = self._sec(dugum["durumlar"], satir, rnd)
        return atama

    def ornekle_izli(self, rnd):
        """Örneklemeyi adım adım kaydederek yapar.

        Bayes ağının nasıl çalıştığını görünür kılmak için kullanılır: her
        düğümde hangi ebeveyn ataması sonucu hangi olasılık satırının
        kullanıldığını ve hangi durumun seçildiğini döndürür.
        """
        atama, iz = {}, []
        for ad in self.sira:
            dugum = self.dugumler[ad]
            ebeveynler = dugum.get("ebeveynler", [])
            anahtar = self._anahtar(dugum, atama)
            satir = dugum["kpt"][anahtar]
            atama[ad] = self._sec(dugum["durumlar"], satir, rnd)
            iz.append({
                "dugum": ad,
                "aciklama": dugum.get("aciklama", ""),
                "ebeveynler": [{"ad": e, "deger": atama[e]} for e in ebeveynler],
                "durumlar": dugum["durumlar"],
                "olasiliklar": satir,
                "secilen": atama[ad],
            })
        return atama, iz

    def yapi(self):
        """Düğüm ve kenar listesi olarak ağ yapısı."""
        return {
            "dugumler": [
                {"ad": ad, "aciklama": d.get("aciklama", ""),
                 "durumlar": d["durumlar"], "ebeveynler": d.get("ebeveynler", []),
                 "kpt": d["kpt"]}
                for ad in self.sira for d in [self.dugumler[ad]]],
            "sira": self.sira,
        }

    def ornekle_coklu(self, n, yineleme_anahtari=0):
        rnd = random.Random(yineleme_anahtari)
        return [self.ornekle(rnd) for _ in range(n)]

    def dogrula(self):
        """Her koşullu olasılık tablosu satırının uzunluğunu ve toplamını denetler."""
        sorunlar = []
        for ad, dugum in self.dugumler.items():
            k = len(dugum["durumlar"])
            beklenen = 1
            for e in dugum.get("ebeveynler", []):
                beklenen *= len(self.dugumler[e]["durumlar"])
            if len(dugum["kpt"]) != beklenen:
                sorunlar.append("%s: %d satır bekleniyordu, %d bulundu"
                                % (ad, beklenen, len(dugum["kpt"])))
            for anahtar, satir in dugum["kpt"].items():
                if len(satir) != k:
                    sorunlar.append("%s[%s]: %d değer bekleniyordu, %d bulundu"
                                    % (ad, anahtar, k, len(satir)))
                elif abs(sum(satir) - 1.0) > 1e-6:
                    sorunlar.append("%s[%s]: toplam %.4f" % (ad, anahtar, sum(satir)))
        return sorunlar


class BagimsizOrnekleyici:
    """Karşılaştırma için: aynı marjinallerden bağımsız örnekleme.

    Bayes ağının neden gerektiğini göstermek üzere kullanılır. Bağımlılıkları
    yok saydığı için içtutarsız profiller üretir.
    """

    def __init__(self, marjinaller):
        self.marjinaller = marjinaller

    def ornekle_izli(self, rnd):
        """Örneklemeyi adım adım kaydederek yapar.

        Bayes ağının nasıl çalıştığını görünür kılmak için kullanılır: her
        düğümde hangi ebeveyn ataması sonucu hangi olasılık satırının
        kullanıldığını ve hangi durumun seçildiğini döndürür.
        """
        atama, iz = {}, []
        for ad in self.sira:
            dugum = self.dugumler[ad]
            ebeveynler = dugum.get("ebeveynler", [])
            anahtar = self._anahtar(dugum, atama)
            satir = dugum["kpt"][anahtar]
            atama[ad] = self._sec(dugum["durumlar"], satir, rnd)
            iz.append({
                "dugum": ad,
                "aciklama": dugum.get("aciklama", ""),
                "ebeveynler": [{"ad": e, "deger": atama[e]} for e in ebeveynler],
                "durumlar": dugum["durumlar"],
                "olasiliklar": satir,
                "secilen": atama[ad],
            })
        return atama, iz

    def yapi(self):
        """Düğüm ve kenar listesi olarak ağ yapısı."""
        return {
            "dugumler": [
                {"ad": ad, "aciklama": d.get("aciklama", ""),
                 "durumlar": d["durumlar"], "ebeveynler": d.get("ebeveynler", []),
                 "kpt": d["kpt"]}
                for ad in self.sira for d in [self.dugumler[ad]]],
            "sira": self.sira,
        }

    def ornekle_coklu(self, n, yineleme_anahtari=0):
        rnd = random.Random(yineleme_anahtari)
        cikti = []
        for _ in range(n):
            atama = {}
            for ad, (durumlar, agirliklar) in self.marjinaller.items():
                toplam = sum(agirliklar)
                esik = rnd.random() * toplam
                birikim = 0.0
                for durum, agirlik in zip(durumlar, agirliklar):
                    birikim += agirlik
                    if esik <= birikim:
                        atama[ad] = durum
                        break
                else:
                    atama[ad] = durumlar[-1]
            cikti.append(atama)
        return cikti


def marjinalleri_cikar(ornekler, dugum_adlari):
    """Örnek kümesinden ampirik marjinalleri hesaplar."""
    marjinaller = {}
    for ad in dugum_adlari:
        sayac = {}
        for o in ornekler:
            sayac[o[ad]] = sayac.get(o[ad], 0) + 1
        durumlar = sorted(sayac)
        toplam = float(len(ornekler))
        marjinaller[ad] = (durumlar, [sayac[d] / toplam for d in durumlar])
    return marjinaller


def ag_yukle(yol):
    with open(yol, encoding="utf-8") as f:
        return BayesAgi(json.load(f))
