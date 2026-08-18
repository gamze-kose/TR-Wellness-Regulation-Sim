"""Monte Carlo tekrarları ve üç gösterge ailesi.

Bir aylık bir sektörün on yıllık seyri tahmin edilemez; giriş oranı, talep
büyümesi ve uyum davranışı hakkında elimizde veri yok. Bu yüzden tek bir
çizgi değil, tekrarların dağılımı raporlanır. Karşılaştırma senaryolar
arasında yapılır, mutlak sayılara bakılmaz.
"""

from cekirdek.simulasyon import Simulasyon


def _yuzdelik(dizi, p):
    if not dizi:
        return 0.0
    s = sorted(dizi)
    k = (len(s) - 1) * p
    alt, ust = int(k), min(int(k) + 1, len(s) - 1)
    return s[alt] + (s[ust] - s[alt]) * (k - alt)


def bant(seriler):
    """Tekrarlardan yıl bazında ortanca ve yüzde 10-90 aralığı."""
    if not seriler:
        return {"ortanca": [], "alt": [], "ust": []}
    n = len(seriler[0])
    o, a, u = [], [], []
    for i in range(n):
        sutun = [s[i] for s in seriler]
        o.append(round(_yuzdelik(sutun, 0.5), 3))
        a.append(round(_yuzdelik(sutun, 0.10), 3))
        u.append(round(_yuzdelik(sutun, 0.90), 3))
    return {"ortanca": o, "alt": a, "ust": u}


def gostergeler(rapor):
    """Bir koşudan üç gösterge ailesini çıkarır."""
    y = rapor["yillar"]
    mevzuat = {
        "uyum_orani": [], "tanimsiz_talep": [], "ucuncu_tespit": [],
        "iptal": [], "denetlenen": [], "kayit_disi": [], "fiili_denetim_orani": [],
    }
    merkez = {"aktif": [], "doluluk": [], "acilan": [], "kapanan": []}
    turist = {"hizmet_aldi": [], "hizmet_alamadi": [], "belirsiz": [],
              "yurt_disi_hizmet_orani": []}

    for k in y:
        e, d = k["eslesme"], k["denetim"]
        toplam = max(1, e["hizmet_aldi"] + e["hizmet_alamadi"] + e["belirsiz"])
        iyi_orta = k["uyum_dagilimi"]["iyi"] + k["uyum_dagilimi"]["orta"]
        mevzuat["uyum_orani"].append(round(iyi_orta / float(k["aktif_merkez"] or 1), 4))
        mevzuat["tanimsiz_talep"].append(round(e["belirsiz"] / float(toplam), 4))
        mevzuat["ucuncu_tespit"].append(d["kademe3"])
        mevzuat["iptal"].append(d["iptal"])
        mevzuat["denetlenen"].append(d["denetlenen"])
        mevzuat["kayit_disi"].append(k.get("kayit_disi_aktif", 0))
        mevzuat["fiili_denetim_orani"].append(
            round(d["denetlenen"] / float(k["aktif_merkez"] or 1), 4))

        merkez["aktif"].append(k["aktif_merkez"])
        merkez["doluluk"].append(k["doluluk"])
        merkez["acilan"].append(k["acilan"])
        merkez["kapanan"].append(k["kapanan"])

        turist["hizmet_aldi"].append(round(e["hizmet_aldi"] / float(toplam), 4))
        turist["hizmet_alamadi"].append(round(e["hizmet_alamadi"] / float(toplam), 4))
        turist["belirsiz"].append(round(e["belirsiz"] / float(toplam), 4))
        turist["yurt_disi_hizmet_orani"].append(
            round(e["yurt_disi_aldi"] / float(e["yurt_disi_toplam"] or 1), 4))
    return {"mevzuat": mevzuat, "merkez": merkez, "turist": turist}


def senaryo_calistir(ag, veri, senaryo, yil_sayisi=10, tekrar=12, anahtar=0,
                     yalniz_olagan=False):
    """Bir senaryoyu birden çok kez koşturur ve bantları döndürür."""
    kosular, ornek = [], None
    for i in range(tekrar):
        s = Simulasyon(ag, veri, senaryo, yil_sayisi, anahtar + i * 97, yalniz_olagan)
        r = s.calistir()
        kosular.append(gostergeler(r))
        if i == 0:
            ornek = r

    bantlar = {}
    for aile in ("mevzuat", "merkez", "turist"):
        bantlar[aile] = {olcut: bant([k[aile][olcut] for k in kosular])
                         for olcut in kosular[0][aile]}

    yillar = [k["yil"] for k in ornek["yillar"]]
    return {
        "senaryo": senaryo["kod"],
        "senaryo_adi": senaryo["ad"],
        "yillar": yillar,
        "bantlar": bantlar,
        "tekrar": tekrar,
        "ornek_kosu": ozet_kosu(ornek),
    }


def ozet_kosu(rapor):
    """Arayüzde tek tek gösterilecek merkezler ve son yıl bilgileri."""
    merkezler = rapor["merkezler"]
    acik = [m for m in merkezler if m["durum"] == "aktif"]
    kapali = [m for m in merkezler if m["durum"] == "kapali"]
    ornek = sorted(merkezler, key=lambda m: (m["durum"] != "aktif", m["acilis_yili"]))
    return {
        "toplam_merkez": len(merkezler),
        "acik": len(acik),
        "kapali_iptal": sum(1 for m in kapali if m["kapanma_nedeni"] == "ruhsat_iptali"),
        "kapali_ekonomik": sum(1 for m in kapali if m["kapanma_nedeni"] == "ekonomik"),
        "reddedilen_basvuru": rapor["reddedilen_basvuru"],
        "kayit_disi_toplam": rapor.get("kayit_disi_toplam", 0),
        "red_nedenleri": rapor["red_nedenleri"],
        "merkez_ornekleri": ornek[:12],
        "son_yil": rapor["yillar"][-1],
    }
