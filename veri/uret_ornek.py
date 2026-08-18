# -*- coding: utf-8 -*-
"""Örnek kayıt seti üretir.

Bu dosya gerçek hasta kaydı değildir. Elde gerçek başvuru kaydı bulunmadığı
için, alan bilgisine dayanan koşullu kurallarla ve gürültüyle kurgulanmış bir
başlangıç seti üretir. Amaç modelin öğreneceği bir veri bulunması; kullanıcı
kendi kayıtlarını girdikçe bu setin ağırlığı azalır.

Değişkenler Madde 10/1'in planlama ölçütlerinden gelir: yaş, genel sağlık
durumu, mevcut risk faktörleri ve yaşam tarzı. Buna Madde 10/8-d gereği
nekahet durumu ve sağlık turizmi kapsamını belirleyen ikamet eklenir.
"""
import json, random, os

r = random.Random(20260704)
YAS = ["18_34", "35_49", "50_64", "65_ustu"]
KRONIK = ["yok", "hafif", "orta", "agir"]
RISK = ["dusuk", "orta", "yuksek"]
YASAM = ["hareketli", "orta", "hareketsiz"]
ARK = ["termal_balneoloji", "getat", "egzersiz", "psikososyal",
       "uyku_beslenme", "rehabilitasyon_destek"]


def sec(secenekler, agirliklar):
    t = sum(agirliklar)
    e = r.random() * t
    b = 0.0
    for s, a in zip(secenekler, agirliklar):
        b += a
        if e <= b:
            return s
    return secenekler[-1]


def kayit():
    yas = sec(YAS, [24, 27, 29, 20])
    yi = YAS.index(yas)

    yasam = sec(YASAM, [40 - 7 * yi, 38, 22 + 8 * yi])
    ki = YASAM.index(yasam)

    kronik = sec(KRONIK, [68 - 18 * yi, 22 + 2 * ki, 8 + 9 * yi, 2 + 7 * yi])
    kri = KRONIK.index(kronik)

    yuk = yi * 0.9 + ki * 1.0 + kri * 0.8
    risk = sec(RISK, [max(0.4, 5.0 - yuk), 2.0 + 0.4 * yuk, max(0.2, 0.3 + 0.75 * yuk)])

    p_cerrahi = min(0.34, 0.03 + 0.035 * yi + 0.055 * kri)
    cerrahi = "var" if r.random() < p_cerrahi else "yok"
    nekahet = "evet" if (cerrahi == "var" and r.random() < 0.45) else "hayir"

    ikamet = "yurt_disi" if r.random() < 0.24 else "yurt_ici"

    ark = sec(ARK, [
        1.0 + 0.55 * yi + 0.30 * kri,
        0.8 + 0.20 * yi + 0.25 * kri,
        max(0.15, 1.8 - 0.40 * yi - 0.45 * kri),
        0.9 + 0.10 * yi + 0.20 * kri,
        1.0 + 0.08 * yi + 0.12 * kri,
        0.2 + 0.30 * yi + 0.85 * kri,
    ])

    return {"yas_grubu": yas, "yasam_tarzi": yasam, "kronik_yuk": kronik,
            "risk_faktoru": risk, "yakin_cerrahi": cerrahi, "nekahet": nekahet,
            "ikamet": ikamet, "talep_arketipi": ark}


kayitlar = [kayit() for _ in range(240)]
os.makedirs("veri", exist_ok=True)
with open("veri/ornek_kayitlar.json", "w", encoding="utf-8") as f:
    json.dump({
        "aciklama": ("Örnek başlangıç seti. Gerçek başvuru kaydı değildir; alan "
                     "bilgisine dayanan koşullu kurallarla kurgulanmıştır. Gerçek "
                     "kayıtlarla değiştirilmesi beklenir."),
        "kaynak": "veri/uret_ornek.py",
        "kayitlar": kayitlar,
    }, f, ensure_ascii=False, indent=1)
print("%d kayit yazildi" % len(kayitlar))
