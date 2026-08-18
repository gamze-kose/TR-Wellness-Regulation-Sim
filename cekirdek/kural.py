"""Kural motoru.

İki ayrı kural kümesi var ve ikisi farklı anlarda işler:

Yapısal kurallar yönetmelik maddelerinden gelir ve ruhsat aşamasında bakılır.
Metrekare, oda sayısı, kurum izni, mesul müdürün kıdemi gibi şartları
sağlamayan başvuru ruhsat alamaz. Bu kuralların EK-4 denetim formunda
karşılığı yok; form yalnızca işleyişi sorguluyor, tanımları değil.

EK-4 kuralları işletme sırasında, denetimde bakılır. Her biri için form
birinci, ikinci ve üçüncü tespitte ayrı yaptırım tanımlar.

Sonuç kümesi üç değerli. "Belirsiz" bir modelleme tercihi değil: Madde 17
sağlık turizmi kapsamındaki hizmetlerin usul ve esaslarını Bakanlığa bırakmış,
düzenleme yayımlanmamış ve EK-4'te konuyla ilgili tek bir soru bile yok.
"""

import json

UYGUN = "uygun"
UYGUN_DEGIL = "uygun_degil"
BELIRSIZ = "belirsiz"


def yukle(klasor="mevzuat"):
    def ac(ad):
        with open("%s/%s" % (klasor, ad), encoding="utf-8") as f:
            return json.load(f)
    return {
        "ek4": ac("ek4_denetim.json"),
        "yapisal": ac("yapisal_kurallar.json"),
        "hizmetler": ac("hizmetler.json"),
        "senaryolar": ac("senaryolar.json"),
    }


# ----------------------------------------------------------------------
def ruhsat_incele(basvuru, yapisal):
    """Ruhsat başvurusunu yapısal kurallara göre değerlendirir.

    Dönen değer (verilir_mi, engelleyen_kurallar).
    """
    engel = []
    for k in yapisal["kurallar"]:
        if k["tur"] == "belirsiz":
            continue
        # Ruhsat sonrası doğan yükümlülükler ruhsat verilmesini engellemez.
        if k.get("asama", "ruhsat") != "ruhsat":
            continue
        if not _kural_ilgili(k, basvuru):
            continue
        deger = basvuru.get(k["alan"])
        if deger is None:
            continue
        gecti = True
        if k["tur"] == "esik":
            gecti = deger >= k["asgari"]
        elif k["tur"] == "tavan":
            gecti = deger <= k["azami"]
        elif k["tur"] in ("mantiksal", "mantiksal_coklu"):
            gecti = deger == k["beklenen"]
        if not gecti:
            engel.append({"kod": k["kod"], "dayanak": k["dayanak"],
                          "metin": k["aciklama"], "metin_en": k.get("aciklama_en", "")})
    return (not engel), engel


def _kural_ilgili(kural, kayit):
    ka = kural.get("kosul_alan")
    if ka is not None:
        if "kosul_degerler" in kural:
            if kayit.get(ka) not in kural["kosul_degerler"]:
                return False
        elif kayit.get(ka) != kural["kosul_deger"]:
            return False
    eka = kural.get("ek_kosul_alan")
    if eka is not None and kayit.get(eka) != kural["ek_kosul_deger"]:
        return False
    return True


# ----------------------------------------------------------------------
def denetim_kurallari(ek4, yalniz_olagan=False):
    """Denetimde sorgulanacak EK-4 kuralları.

    Formda yıldızlı sorular olağan denetimde sorulmuyor; şikâyet ya da
    olağan dışı denetimde gündeme geliyor.
    """
    kurallar = [k for k in ek4["kurallar"] if k["duzey"] == "merkez"]
    if yalniz_olagan:
        kurallar = [k for k in kurallar if k["olagan_denetimde_sorulur"]]
    return kurallar


def yaptirim_kademesi(kural, kademe):
    """Kaçıncı tespit olduğuna göre EK-4'teki yaptırımı döndürür."""
    anahtar = str(min(kademe, 3))
    return kural["yaptirim"][anahtar]


def yaptirim_etkisi(kademe):
    """Yaptırımın simülasyondaki sayısal karşılığı.

    EK-4 para cezalarını brüt gelire oranlı tanımlıyor, mutlak tutar
    merkezin cirosuna bağlı. Modelde ceza birimi olarak sayıyoruz; asıl
    izlenen şey faaliyet durdurma günü ve ruhsat iptali riski.
    """
    if kademe <= 1:
        return {"ceza_birimi": 1, "durdurma_gun": 0}
    if kademe == 2:
        return {"ceza_birimi": 2, "durdurma_gun": 0}
    return {"ceza_birimi": 3, "durdurma_gun": 5}


# ----------------------------------------------------------------------
def turizm_durumu(senaryo, yil, merkez):
    """Yurt dışında ikamet eden ziyaretçi için merkezin hukuki konumu.

    Madde 17 kapsamındaki düzenleme yürürlüğe girmemişse durum tanımsızdır.
    Kısıtlayıcı düzenlemede üniteler kapsam dışı kalır.
    """
    m17 = senaryo.get("madde17", "yok")
    if m17 == "yok":
        return BELIRSIZ
    if yil < senaryo.get("yururluk_yili", 9999):
        return BELIRSIZ
    if m17 == "kisitlayici" and merkez.tur == "unite":
        return UYGUN_DEGIL
    return UYGUN
