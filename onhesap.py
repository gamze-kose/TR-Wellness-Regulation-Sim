# -*- coding: utf-8 -*-
"""Senaryoları önceden koşturup sonuçları sayfaya gömülecek biçimde saklar.

Tarayıcıda on yıllık koşu dakikalar sürüyor; telefonda daha da uzun. Açılışta
hazır sonuç gösterilir, kullanıcı parametreleri değiştirmek isterse hesap o
zaman yapılır.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cekirdek.ag import BayesAgi
from cekirdek.ogren import kayitlardan_ogren
from cekirdek import kural as K
from cekirdek.gostergeler import senaryo_calistir

# Model elle yazılmış tablolarla değil, kayıt setinden öğrenilerek kurulur.
_yapi = json.load(open("mevzuat/ag_yapisi.json", encoding="utf-8"))
_kayit = json.load(open("veri/ornek_kayitlar.json", encoding="utf-8"))["kayitlar"]
ag = BayesAgi(kayitlardan_ogren(_yapi, _kayit))
veri = K.yukle("mevzuat")
ANAHTAR, TEKRAR = 20260704, 8

cikti = {"anahtar": ANAHTAR, "tekrar": TEKRAR, "kosular": {}}
t0 = time.time()
for ufuk in (5, 10):
    for s in veri["senaryolar"]["senaryolar"]:
        t = time.time()
        r = senaryo_calistir(ag, veri, s, ufuk, TEKRAR, anahtar=ANAHTAR)
        # Sayfa boyutunu şişirmemek için örnek koşudan yalnızca gerekli alanlar
        o = r["ornek_kosu"]
        o["merkez_ornekleri"] = [
            {k: m[k] for k in ("kimlik", "acilis_yili", "yerlesim", "tur", "kapasite",
                               "arketip", "hizmet_sepeti", "uyum_durumu", "durum",
                               "kapanma_yili", "kapanma_nedeni", "zayif_kurallar",
                               "tespit", "tespit_gecmisi", "gecmis")}
            for m in o["merkez_ornekleri"]]
        o.pop("son_yil", None)
        cikti["kosular"]["%s_%d" % (s["kod"], ufuk)] = r
        print("  %s %2d yil  %5.1f sn" % (s["kod"], ufuk, time.time() - t))

os.makedirs("cikti", exist_ok=True)
yol = "cikti/onceden.json"
with open(yol, "w", encoding="utf-8") as f:
    json.dump(cikti, f, ensure_ascii=False, separators=(",", ":"))
print("toplam %.0f sn, %s %.0f KB" % (time.time() - t0, yol, os.path.getsize(yol) / 1024))
