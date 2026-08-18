/* Ziyaretçi modeli.

   Ağın yapısı uzman tarafından belirlenir: hangi değişkenler var, hangisi
   hangisine bağlı. Olasılık tablolarının içeriği ise veriden öğrenilir.
   Elle yazılmış tablo yoktur.

   Öğrenme, sayımlara düzgün dağılımlı bir Dirichlet öncülü eklenerek yapılır.
   Öncül gücü küçük tutulur; amacı hiç gözlem düşmemiş satırları tanımsız
   bırakmamaktır. Kayıt sayısı arttıkça öncülün etkisi kaybolur.
*/

export class Model {
  constructor(yapi, kayitlar, oncul = 1) {
    this.yapi = yapi;
    this.dugumler = yapi.dugumler;
    this.oncul = oncul;
    this.sira = this.topolojikSira();
    this.egit(kayitlar || []);
  }

  topolojikSira() {
    const kalan = new Set(Object.keys(this.dugumler));
    const yerlesen = new Set(), sira = [];
    while (kalan.size) {
      const hazir = [...kalan].filter(a =>
        (this.dugumler[a].ebeveynler || []).every(e => yerlesen.has(e)));
      if (!hazir.length) throw new Error("Ağda döngü var");
      hazir.sort().forEach(a => { sira.push(a); yerlesen.add(a); kalan.delete(a); });
    }
    return sira;
  }

  anahtar(ad, kayit) {
    const eb = this.dugumler[ad].ebeveynler || [];
    return eb.length ? eb.map(e => kayit[e]).join("|") : "*";
  }

  /* Bir düğümün ebeveyn bileşimlerinin tamamı. Veri düşmemiş satırların da
     tabloda görünmesi gerekir; eksik olduklarını göstermek için. */
  tumAnahtarlar(ad) {
    const eb = this.dugumler[ad].ebeveynler || [];
    if (!eb.length) return ["*"];
    let liste = [""];
    for (const e of eb) {
      const yeni = [];
      for (const p of liste) for (const d of this.dugumler[e].durumlar)
        yeni.push(p ? p + "|" + d : d);
      liste = yeni;
    }
    return liste;
  }

  egit(kayitlar) {
    this.kayitSayisi = kayitlar.length;
    this.sayim = {}; this.kpt = {};
    for (const ad of this.sira) {
      const k = this.dugumler[ad].durumlar.length;
      this.sayim[ad] = {};
      for (const a of this.tumAnahtarlar(ad)) this.sayim[ad][a] = new Array(k).fill(0);
    }
    for (const kayit of kayitlar) {
      for (const ad of this.sira) {
        if (!(ad in kayit)) continue;
        const a = this.anahtar(ad, kayit);
        const i = this.dugumler[ad].durumlar.indexOf(kayit[ad]);
        if (i >= 0 && this.sayim[ad][a]) this.sayim[ad][a][i] += 1;
      }
    }
    for (const ad of this.sira) {
      this.kpt[ad] = {};
      for (const a of Object.keys(this.sayim[ad])) {
        const s = this.sayim[ad][a];
        const t = s.reduce((x, y) => x + y, 0) + this.oncul * s.length;
        this.kpt[ad][a] = s.map(v => (v + this.oncul) / t);
      }
    }
  }

  /* Satırın kaç gözleme dayandığı. Az gözlemli satırlar arayüzde işaretlenir. */
  gozlem(ad, a) {
    return (this.sayim[ad][a] || []).reduce((x, y) => x + y, 0);
  }

  zayifSatirlar(esik = 5) {
    const liste = [];
    for (const ad of this.sira)
      for (const a of Object.keys(this.sayim[ad]))
        if (this.gozlem(ad, a) < esik) liste.push({ dugum: ad, anahtar: a, gozlem: this.gozlem(ad, a) });
    return liste;
  }

  sec(durumlar, agirliklar, rastgele) {
    const t = agirliklar.reduce((a, b) => a + b, 0);
    let e = rastgele() * t, b = 0;
    for (let i = 0; i < durumlar.length; i++) { b += agirliklar[i]; if (e <= b) return i; }
    return durumlar.length - 1;
  }

  /* Örneklemeyi adım adım kaydeder: hangi ebeveyn bileşimi hangi satırı seçti,
     o satır kaç gözleme dayanıyor, hangi değer çekildi. */
  uretIzli(rastgele = Math.random) {
    const atama = {}, iz = [];
    for (const ad of this.sira) {
      const d = this.dugumler[ad];
      const a = this.anahtar(ad, atama);
      const satir = this.kpt[ad][a];
      const i = this.sec(d.durumlar, satir, rastgele);
      atama[ad] = d.durumlar[i];
      iz.push({
        dugum: ad, anahtar: a,
        ebeveynler: (d.ebeveynler || []).map(e => ({ ad: e, deger: atama[e] })),
        durumlar: d.durumlar, olasiliklar: satir,
        secilen: d.durumlar[i], olasilik: satir[i], gozlem: this.gozlem(ad, a),
      });
    }
    return { atama, iz };
  }

  uret(rastgele = Math.random) { return this.uretIzli(rastgele).atama; }

  uretCoklu(n, rastgele = Math.random) {
    const c = [];
    for (let i = 0; i < n; i++) c.push(this.uret(rastgele));
    return c;
  }
}

/* Kayıt setinden değişken dağılımlarını çıkarır. Veri sekmesinde gösterilir. */
export function dagilim(kayitlar, dugum, durumlar) {
  const s = {};
  durumlar.forEach(d => s[d] = 0);
  kayitlar.forEach(k => { if (k[dugum] in s) s[k[dugum]] += 1; });
  const n = kayitlar.length || 1;
  return durumlar.map(d => ({ durum: d, adet: s[d], oran: s[d] / n }));
}

/* Yineleme anahtarından türeyen üreteç. Aynı anahtar aynı diziyi verir. */
export function uretec(anahtar) {
  let s = (anahtar >>> 0) || 1;
  return function () {
    s ^= s << 13; s >>>= 0;
    s ^= s >> 17;
    s ^= s << 5; s >>>= 0;
    return s / 4294967296;
  };
}
