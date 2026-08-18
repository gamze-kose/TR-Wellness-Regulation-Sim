"""Bayes ağının koşullu olasılık tablolarını gözlemlerden öğrenir.

Ağ elle yazılmış sabit değerlerle başlamaz. Uzmanın verdiği başlangıç
değerleri bir Dirichlet öncülü olarak alınır; her gözlem ilgili satırın
sayaçlarını artırır ve sonsal ortalama yeni tabloyu oluşturur.

Öğrenme iki kaynaktan beslenir:

1. Gerçek veri. Elde ziyaretçi kaydı varsa doğrudan gözlem olarak eklenir.
2. Uzman geri bildirimi. Üretilen bir profil gerçekçi bulunduğunda gözlem
   sayılır; gerçekçi bulunmadığında aynı ağırlık, o düğümün diğer
   durumlarına eşit olarak dağıtılır. Böylece olumsuz oy da bilgi taşır ve
   sayaçlar hiçbir zaman negatife düşmez.

Öncül gücü, kaç gözleme eşdeğer sayılacağını belirler. Güç 20 iken yirmi
gözlem uzman değerini yaklaşık yarı yarıya dengeler.
"""

import copy
import json


class DirichletOgrenici:

    def __init__(self, ag_tanimi, oncul_gucu=20.0):
        self.tanim = copy.deepcopy(ag_tanimi)
        self.oncul_gucu = float(oncul_gucu)
        self.oncul = {}
        self.sayac = {}
        for ad, d in self.tanim["dugumler"].items():
            self.oncul[ad] = {k: [p * self.oncul_gucu for p in satir]
                              for k, satir in d["kpt"].items()}
            self.sayac[ad] = {k: [0.0] * len(satir) for k, satir in d["kpt"].items()}
        self.gozlem_sayisi = 0
        self.olumlu = 0
        self.olumsuz = 0

    # ------------------------------------------------------------------
    def _anahtar(self, ad, atama):
        ebeveynler = self.tanim["dugumler"][ad].get("ebeveynler", [])
        if not ebeveynler:
            return "*"
        return "|".join(atama[e] for e in ebeveynler)

    def gozlem_ekle(self, atama, gercekci=True, agirlik=1.0):
        """Tek bir profili gözlem olarak işler."""
        for ad, d in self.tanim["dugumler"].items():
            if ad not in atama:
                continue
            anahtar = self._anahtar(ad, atama)
            if anahtar not in self.sayac[ad]:
                continue
            durumlar = d["durumlar"]
            i = durumlar.index(atama[ad])
            if gercekci:
                self.sayac[ad][anahtar][i] += agirlik
            elif len(durumlar) > 1:
                pay = agirlik / (len(durumlar) - 1)
                for j in range(len(durumlar)):
                    if j != i:
                        self.sayac[ad][anahtar][j] += pay
        self.gozlem_sayisi += 1
        if gercekci:
            self.olumlu += 1
        else:
            self.olumsuz += 1

    def gozlemleri_ekle(self, profiller, gercekci=True):
        for p in profiller:
            self.gozlem_ekle(p, gercekci=gercekci)

    # ------------------------------------------------------------------
    def egitilmis_tanim(self):
        """Sonsal ortalamalarla güncellenmiş ağ tanımını döndürür."""
        yeni = copy.deepcopy(self.tanim)
        for ad, d in yeni["dugumler"].items():
            for anahtar in d["kpt"]:
                a = self.oncul[ad][anahtar]
                n = self.sayac[ad][anahtar]
                toplam = sum(a) + sum(n)
                satir = [round((a[i] + n[i]) / toplam, 6) for i in range(len(a))]
                satir[-1] = round(1.0 - sum(satir[:-1]), 6)
                d["kpt"][anahtar] = satir
        return yeni

    def degisim_ozeti(self):
        """Her düğümde tabloların ne kadar değiştiğini ölçer.

        Ölçüt toplam değişim uzaklığıdır: satır başına yarım mutlak fark
        toplamı, sonra satırların ortalaması. Sıfır hiç değişmedi, bir
        tamamen değişti demektir.
        """
        egitilmis = self.egitilmis_tanim()["dugumler"]
        ozet = []
        for ad, d in self.tanim["dugumler"].items():
            uzakliklar, gozlem = [], 0.0
            for anahtar, eski in d["kpt"].items():
                yeni = egitilmis[ad]["kpt"][anahtar]
                uzakliklar.append(
                    0.5 * sum(abs(eski[i] - yeni[i]) for i in range(len(eski))))
                gozlem += sum(self.sayac[ad][anahtar])
            ozet.append({
                "dugum": ad,
                "degisim": round(sum(uzakliklar) / len(uzakliklar), 4),
                "gozlem": round(gozlem, 2),
            })
        return sorted(ozet, key=lambda x: -x["degisim"])

    def sifirla(self):
        for ad in self.sayac:
            for anahtar in self.sayac[ad]:
                self.sayac[ad][anahtar] = [0.0] * len(self.sayac[ad][anahtar])
        self.gozlem_sayisi = self.olumlu = self.olumsuz = 0

    def durum(self):
        return {"gozlem": self.gozlem_sayisi, "olumlu": self.olumlu,
                "olumsuz": self.olumsuz, "oncul_gucu": self.oncul_gucu}


def veriden_ogren(ag_tanimi, kayitlar, oncul_gucu=20.0):
    """Gerçek ziyaretçi kayıtlarından koşullu olasılık tablolarını kestirir.

    kayitlar: her biri düğüm adlarını durum değerlerine eşleyen sözlük listesi.
    """
    o = DirichletOgrenici(ag_tanimi, oncul_gucu)
    o.gozlemleri_ekle(kayitlar, gercekci=True)
    return o.egitilmis_tanim(), o.degisim_ozeti()


def jsondan_ogren(ag_yolu, veri_yolu, cikti_yolu, oncul_gucu=20.0):
    with open(ag_yolu, encoding="utf-8") as f:
        ag = json.load(f)
    with open(veri_yolu, encoding="utf-8") as f:
        kayitlar = json.load(f)
    yeni, ozet = veriden_ogren(ag, kayitlar, oncul_gucu)
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        json.dump(yeni, f, ensure_ascii=False, indent=1)
    return ozet


def kayitlardan_ogren(yapi, kayitlar, oncul=1.0):
    """Ağ yapısını ve kayıt setini alıp koşullu olasılık tablolarını çıkarır.

    Elle yazılmış tablo yoktur. Sayımlara düzgün dağılımlı küçük bir Dirichlet
    öncülü eklenir; amacı hiç gözlem düşmemiş satırı tanımsız bırakmamaktır.
    Kayıt sayısı arttıkça öncülün etkisi kaybolur.
    """
    import copy, itertools

    tanim = copy.deepcopy(yapi)
    dugumler = tanim["dugumler"]

    def anahtarlar(ad):
        eb = dugumler[ad].get("ebeveynler", [])
        if not eb:
            return ["*"]
        return ["|".join(p) for p in itertools.product(
            *[dugumler[e]["durumlar"] for e in eb])]

    sayim = {ad: {a: [0.0] * len(dugumler[ad]["durumlar"]) for a in anahtarlar(ad)}
             for ad in dugumler}
    for k in kayitlar:
        for ad, d in dugumler.items():
            if ad not in k:
                continue
            eb = d.get("ebeveynler", [])
            a = "|".join(k[e] for e in eb) if eb else "*"
            if a in sayim[ad] and k[ad] in d["durumlar"]:
                sayim[ad][a][d["durumlar"].index(k[ad])] += 1

    for ad, d in dugumler.items():
        d["kpt"] = {}
        for a, s in sayim[ad].items():
            t = sum(s) + oncul * len(s)
            satir = [round((v + oncul) / t, 6) for v in s]
            satir[-1] = round(1.0 - sum(satir[:-1]), 6)
            d["kpt"][a] = satir
        d["gozlem"] = {a: int(sum(v)) for a, v in sayim[ad].items()}
    return tanim
