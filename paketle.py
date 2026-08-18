# -*- coding: utf-8 -*-
"""Tek dosyalık index.html üretir.

Şablon kural setlerini, dil dosyalarını, önceden hesaplanmış senaryoları ve
Python modüllerini çalışma anında okur. Bu betik hepsini sayfanın içine gömer;
üretilen dosya çift tıklayarak açılır ve açılışta hiçbir hesap yapmaz.

Bayes ağı modülü ES modülü olarak yazıldığı için gömülürken export sözcükleri
kaldırılıp doğrudan sayfaya alınır; tarayıcı yerel dosyada modül çözemez.
"""
import io, json, os, re

VERI = ["diller/tr.json", "diller/en.json", "cikti/onceden.json",
        "veri/ornek_kayitlar.json", "mevzuat/ag_yapisi.json",
        "mevzuat/ek4_denetim.json", "mevzuat/yapisal_kurallar.json",
        "mevzuat/hizmetler.json", "mevzuat/senaryolar.json",
        "mevzuat/belirsizlik_haritasi.json", "mevzuat/uyum_maliyeti.json"]

MODULLER = ["web/model.js", "web/akis.js", "web/analiz.js"]


def paketle(kaynak="sablon.html", hedef="index.html"):
    gomulu = {y: io.open(y, encoding="utf-8").read() for y in VERI}
    sayfa = io.open(kaynak, encoding="utf-8").read()

    # ES modülleri yerel dosyada çözülemediği için export sözcükleri kaldırılıp
    # doğrudan sayfaya alınır.
    def temizle(yol):
        g = io.open(yol, encoding="utf-8").read().replace("export ", "")
        return re.sub(r"^import .*?;\s*$", "", g, flags=re.M)

    govde = "\n".join(temizle(y) for y in MODULLER)
    eski = re.search(r'<script type="module">.*?</script>', sayfa, re.S).group(0)
    sayfa = sayfa.replace(eski, '<script>\n' + govde
                          + '\nwindow.__mod={Model,dagilim,uretec,A:{'
                            'UYGUN,DEGIL,BELIRSIZ,ruhsatIncele,merkezleriUret,'
                            'turizmDurumu,eslestir,kirilim,merkezMaliyeti,yasayabilirlik,'
                            'yasayabilirlikOzeti,duyarlilik,PARAMETRELER}};'
                            '\nwindow.dispatchEvent(new Event("modul-hazir"));\n</script>')

    blok = ('<script id="gomulu-veri" type="application/json">'
            + json.dumps(gomulu, ensure_ascii=False).replace("</", "<\\/")
            + '</script>\n<script>window.GOMULU=JSON.parse('
              'document.getElementById("gomulu-veri").textContent);</script>\n')
    sayfa = sayfa.replace("</head>", blok + "</head>", 1)

    io.open(hedef, "w", encoding="utf-8").write(sayfa)
    return hedef, len(sayfa)


if __name__ == "__main__":
    y, n = paketle()
    print("%s yazildi (%.0f KB)" % (y, n / 1024.0))
