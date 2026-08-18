"""Tüm senaryoları koşturur ve özet basar."""
import json, os, sys
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
YIL, TEKRAR = 10, 10

sonuc = {}
for s in veri["senaryolar"]["senaryolar"]:
    r = senaryo_calistir(ag, veri, s, YIL, TEKRAR, anahtar=20260704)
    sonuc[s["kod"]] = r
    b, o = r["bantlar"], r["ornek_kosu"]
    print("%s  %-32s aktif merkez %3d -> %3d | yurt disi hizmet %.0f%% -> %.0f%% | tanimsiz talep %.0f%% -> %.0f%%" % (
        s["kod"], s["ad"],
        b["merkez"]["aktif"]["ortanca"][0], b["merkez"]["aktif"]["ortanca"][-1],
        100*b["turist"]["yurt_disi_hizmet_orani"]["ortanca"][0],
        100*b["turist"]["yurt_disi_hizmet_orani"]["ortanca"][-1],
        100*b["mevzuat"]["tanimsiz_talep"]["ortanca"][0],
        100*b["mevzuat"]["tanimsiz_talep"]["ortanca"][-1]))

os.makedirs("cikti", exist_ok=True)
json.dump(sonuc, open("cikti/senaryolar.json","w",encoding="utf-8"), ensure_ascii=False)
r0 = sonuc["S0"]["ornek_kosu"]
print("\nS0 ornek kosu: acik %d, ruhsat iptali %d, ekonomik kapanma %d, reddedilen basvuru %d" % (
    r0["acik"], r0["kapali_iptal"], r0["kapali_ekonomik"], r0["reddedilen_basvuru"]))
print("red nedenleri:", list(r0["red_nedenleri"].items())[:4])
