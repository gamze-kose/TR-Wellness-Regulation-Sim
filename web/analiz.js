/* Uyum maliyeti, yaşayabilirlik ve duyarlılık analizi.

   Maliyet tutarları gerçek piyasa verisi değildir; göreli birimdir ve
   arayüzden değiştirilebilir. Amaç mutlak maliyeti kestirmek değil, hangi
   iş modelinin eşiğin altına düştüğünü göstermektir.
*/

import { merkezleriUret, eslestir } from "./akis.js";

export function merkezMaliyeti(m, maliyet) {
  const kalem = [];
  let toplam = 0;
  for (const k of maliyet.kalemler) {
    if (k.yalnizca_yerlesim && !k.yalnizca_yerlesim.includes(m.yerlesim)) continue;
    if (k.tur === "kosullu" && !m[k.kosul_alan]) continue;
    let d = 0;
    if (k.tur === "alana_bagli") d = (m.kapali_alan_m2 || (m.tur === "merkez" ? 320 : 190)) * k.birim_maliyet;
    else if (k.tur === "personele_bagli") d = Math.max(4, Math.round(m.kapasite / 18)) * k.birim_maliyet;
    else if (k.tur === "gelir_kaybi") d = m.kapasite * maliyet.gelir.kisi_basi * k.birim_maliyet;
    else d = k.birim_maliyet;
    kalem.push({ kod: k.kod, ad: k.ad, ad_en: k.ad_en, dayanak: k.dayanak, tutar: d });
    toplam += d;
  }
  return { toplam, kalem };
}

/* Gelir hizmet verilen kişi sayısından gelir; doluluk bilinmiyorsa varsayılan
   kullanılır. Eşiğin altına düşen merkez uzun vadede ayakta kalamaz. */
export function yasayabilirlik(merkezler, maliyet, yuk, varsayilanDoluluk = 0.7) {
  return merkezler.map(m => {
    const mal = merkezMaliyeti(m, maliyet);
    const kisi = yuk && yuk[m.kimlik] !== undefined ? yuk[m.kimlik]
                                                   : Math.round(m.kapasite * varsayilanDoluluk);
    const gelir = kisi * maliyet.gelir.kisi_basi;
    return { kimlik: m.kimlik, yerlesim: m.yerlesim, tur: m.tur, kapasite: m.kapasite,
             kisi, gelir, maliyet: mal.toplam, kalem: mal.kalem,
             marj: gelir - mal.toplam, ayakta: gelir - mal.toplam > 0 };
  });
}

export function yasayabilirlikOzeti(liste) {
  const grup = {};
  for (const y of liste) {
    const a = y.yerlesim + "|" + y.tur;
    if (!grup[a]) grup[a] = { yerlesim: y.yerlesim, tur: y.tur, adet: 0, ayakta: 0, marj: 0 };
    grup[a].adet += 1;
    grup[a].ayakta += y.ayakta ? 1 : 0;
    grup[a].marj += y.marj;
  }
  return Object.values(grup).map(g => ({
    yerlesim: g.yerlesim, tur: g.tur, adet: g.adet, ayakta: g.ayakta,
    oran: g.ayakta / g.adet, ortalama_marj: g.marj / g.adet,
  })).sort((a, b) => a.oran - b.oran);
}

/* Duyarlılık: her parametre tek tek aşağı ve yukarı oynatılır, çıktıdaki
   değişim ölçülür. Çıktı ne koyduğumuza bağlıysa bunu göstermek, gizlemekten
   daha dürüsttür. */
export const PARAMETRELER = [
  { kod: "merkez_sayisi",  taban: 60,   alt: 40,   ust: 100 },
  { kod: "ziyaretci",      taban: 6000, alt: 4000, ust: 9000 },
  { kod: "yapisal_uyum",   taban: 0.90, alt: 0.75, ust: 1.00 },
  { kod: "denetim_uyumu",  taban: 0.98, alt: 0.92, ust: 1.00 },
  { kod: "belirsizlik_istahi", taban: 0.17, alt: 0.05, ust: 0.45 },
];

function tekKosu(model, hizmetler, yapisal, ek4, senaryo, p, uretecFn, anahtar) {
  const r = uretecFn(anahtar);
  const s = merkezleriUret(Math.round(p.merkez_sayisi), hizmetler, yapisal, ek4, r,
    { yapisalUyum: p.yapisal_uyum, denetimUyum: p.denetim_uyumu });
  const z = model.uretCoklu(Math.round(p.ziyaretci), r);
  const e = eslestir(z, s.merkezler, hizmetler, senaryo, r,
    { belirsizlikIstahi: p.belirsizlik_istahi });
  return { uygun: e.oran.uygun, belirsiz: e.oran.belirsiz, doluluk: e.doluluk,
           red: s.red.length / (s.basvuru || 1) };
}

export function duyarlilik(model, hizmetler, yapisal, ek4, senaryo, uretecFn,
                           { anahtar = 4242, tekrar = 3 } = {}) {
  const taban = {};
  PARAMETRELER.forEach(x => taban[x.kod] = x.taban);

  const ortalama = (p) => {
    const t = { uygun: 0, belirsiz: 0, doluluk: 0, red: 0 };
    for (let i = 0; i < tekrar; i++) {
      const k = tekKosu(model, hizmetler, yapisal, ek4, senaryo, p, uretecFn, anahtar + i * 131);
      for (const a in t) t[a] += k[a] / tekrar;
    }
    return t;
  };

  const temel = ortalama(taban);
  const satirlar = PARAMETRELER.map(x => {
    const alt = ortalama(Object.assign({}, taban, { [x.kod]: x.alt }));
    const ust = ortalama(Object.assign({}, taban, { [x.kod]: x.ust }));
    const etki = {};
    for (const a in temel) etki[a] = Math.abs(ust[a] - alt[a]);
    return { parametre: x.kod, alt: x.alt, ust: x.ust, altSonuc: alt, ustSonuc: ust, etki };
  });

  for (const olcut of ["uygun", "belirsiz", "doluluk", "red"]) {
    const enb = Math.max(...satirlar.map(s => s.etki[olcut])) || 1;
    satirlar.forEach(s => s.etki[olcut + "_norm"] = s.etki[olcut] / enb);
  }
  return { temel, satirlar };
}
