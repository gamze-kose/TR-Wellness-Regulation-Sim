/* Merkezlerin üretilmesi, kuralların uygulanması ve eşleştirme.

   Üç değerli sonuç kullanılır. "Belirsiz" bir modelleme tercihi değildir:
   Madde 17, esenlik merkez ve ünitelerinin uluslararası sağlık turizmi
   yetkisine ilişkin usul ve esasları Bakanlığın belirlemesine bırakmış,
   belirleme yayımlanmamış ve Esenlik Hizmetleri Yönetmeliği EK-4'ünde
   konuyla ilgili tek bir soru bulunmamaktadır.
*/

export const UYGUN = "uygun", DEGIL = "uygun_degil", BELIRSIZ = "belirsiz";

const YERLESIMLER = ["mustakil_bina", "konaklama_tesisi", "yasli_bakim_merkezi",
                     "engelli_bakim_merkezi", "spor_kulubu"];

/* ---------------- yapısal kurallar: ruhsat aşaması ---------------- */

function ilgili(kural, kayit) {
  const ka = kural.kosul_alan;
  if (ka !== undefined) {
    if (kural.kosul_degerler) { if (!kural.kosul_degerler.includes(kayit[ka])) return false; }
    else if (kayit[ka] !== kural.kosul_deger) return false;
  }
  const eka = kural.ek_kosul_alan;
  if (eka !== undefined && kayit[eka] !== kural.ek_kosul_deger) return false;
  return true;
}

export function ruhsatIncele(basvuru, yapisal) {
  const engel = [];
  for (const k of yapisal.kurallar) {
    if (k.tur === "belirsiz" || (k.asama && k.asama !== "ruhsat")) continue;
    if (!ilgili(k, basvuru)) continue;
    const v = basvuru[k.alan];
    if (v === undefined || v === null) continue;
    let gecti = true;
    if (k.tur === "esik") gecti = v >= k.asgari;
    else if (k.tur === "tavan") gecti = v <= k.azami;
    else gecti = v === k.beklenen;
    if (!gecti) engel.push({ kod: k.kod, dayanak: k.dayanak,
                             metin: k.aciklama, metin_en: k.aciklama_en || "" });
  }
  return { verilir: engel.length === 0, engel };
}

/* ---------------- merkez üretimi ---------------- */

function sepet(arketip, hizmetler, r) {
  const a = hizmetler.arketipler[arketip], p = hizmetler.arketip_perturbasyon;
  const s = new Set();
  a.cekirdek.forEach(h => { if (r() > p.cekirdek_dusurme_olasiligi) s.add(h); });
  a.olasi.forEach(h => { if (r() < p.olasi_ekleme_olasiligi) s.add(h); });
  return [...s];
}

function basvuruUret(r, yapisalUyum) {
  const yerlesim = YERLESIMLER[Math.floor(r() * YERLESIMLER.length)];
  const tur = r() < 0.5 ? "merkez" : "unite";
  const asgari = yerlesim === "mustakil_bina" ? (tur === "merkez" ? 500 : 300) : 0;
  const b = {
    yerlesim, tur,
    kapali_alan_m2: asgari ? Math.round(asgari * (r() < yapisalUyum
      ? 1 + r() * 1.6 : 0.55 + r() * 0.43)) : null,
    oda_sayisi: yerlesim === "konaklama_tesisi"
      ? (r() < yapisalUyum ? [10, 12, 18, 24, 40, 70][Math.floor(r() * 6)]
                           : [6, 8, 9][Math.floor(r() * 3)]) : null,
    mustakil_giris: yerlesim === "mustakil_bina" ? r() < yapisalUyum : true,
    turizm_isletmesi_belgesi: yerlesim === "konaklama_tesisi" ? r() < yapisalUyum : true,
    kurum_izni: ["spor_kulubu", "yasli_bakim_merkezi", "engelli_bakim_merkezi"].includes(yerlesim)
      ? r() < yapisalUyum : true,
    uzman_tabip_var: r() < 0.5,
    mesul_mudur_tabiplik_yili: r() < yapisalUyum
      ? [3, 4, 6, 9, 14, 20][Math.floor(r() * 6)] : [1, 2][Math.floor(r() * 2)],
    mesul_mudur_baska_kurumda: r() > yapisalUyum,
    ruhsattan_faaliyete_ay: r() < yapisalUyum
      ? [1, 2, 3, 4, 5, 6][Math.floor(r() * 6)] : [7, 9][Math.floor(r() * 2)],
  };
  b.uzman_tabip_asgari_yas = b.uzman_tabip_var
    ? (r() < yapisalUyum ? [61, 63, 66, 70][Math.floor(r() * 4)]
                         : [46, 55, 58][Math.floor(r() * 3)]) : null;
  return b;
}

export function merkezleriUret(adet, hizmetler, yapisal, ek4, r,
                               { yapisalUyum = 0.9, denetimUyum = 0.985 } = {}) {
  const arketipler = Object.keys(hizmetler.arketipler).sort();
  const ek4Alanlari = ek4.kurallar.filter(k => k.duzey === "merkez");
  const kabul = [], red = [], redNedeni = {};
  let sayac = 0, deneme = 0;

  while (kabul.length < adet && deneme < adet * 40) {
    deneme++;
    const b = basvuruUret(r, yapisalUyum);
    const s = ruhsatIncele(b, yapisal);
    if (!s.verilir) {
      red.push({ basvuru: b, engel: s.engel });
      s.engel.forEach(e => redNedeni[e.dayanak] = (redNedeni[e.dayanak] || 0) + 1);
      continue;
    }
    sayac++;
    const ark = arketipler[Math.floor(r() * arketipler.length)];
    const m = Object.assign({}, b, {
      kimlik: "M" + String(sayac).padStart(3, "0"),
      arketip: ark,
      hizmet_sepeti: sepet(ark, hizmetler, r),
      kapasite: Math.round((b.tur === "merkez" ? 150 : 85) * (0.75 + r() * 0.75)),
      ihlaller: [],
    });
    ek4Alanlari.forEach(k => {
      const uygun = r() < denetimUyum;
      m[k.alan] = uygun ? k.beklenen : !k.beklenen;
      if (!uygun) m.ihlaller.push({ kod: "S" + String(k.soru_no).padStart(2, "0"),
                                    dayanak: k.dayanak, metin: k.soru,
                                    metin_en: k.soru_en || "" });
    });
    m.durum = m.ihlaller.length ? DEGIL : UYGUN;
    kabul.push(m);
  }
  return { merkezler: kabul, red, redNedeni, basvuru: deneme };
}

/* ---------------- eşleştirme ---------------- */

export function turizmDurumu(senaryo, merkez) {
  const m17 = senaryo.madde17 || "yok";
  if (m17 === "yok") return BELIRSIZ;
  if (m17 === "kisitlayici" && merkez.tur === "unite") return DEGIL;
  return UYGUN;
}

export function eslestir(ziyaretciler, merkezler, hizmetler, senaryo, r,
                         { belirsizlikIstahi = 0.17 } = {}) {
  const acik = merkezler.filter(m => m.durum === UYGUN);
  const kalan = {}; acik.forEach(m => kalan[m.kimlik] = m.kapasite);
  const yuk = {}; merkezler.forEach(m => yuk[m.kimlik] = 0);

  /* Yurt dışı ziyaretçi kabulü merkezin kararıdır, her ziyaretçide yeniden
     çekilmez. Durum tanımsızken merkezlerin çoğu riski almaz. */
  const kabul = {};
  acik.forEach(m => {
    const d = turizmDurumu(senaryo, m);
    kabul[m.kimlik] = d === UYGUN ? true : (d === BELIRSIZ ? r() < belirsizlikIstahi : false);
  });

  const sonuc = [];
  const sayim = { uygun: 0, belirsiz: 0, uygun_degil: 0 };
  const neden = {};
  const ekle = (d, k) => { neden[k] = (neden[k] || 0) + 1; sayim[d] += 1; };

  for (const z of ziyaretciler) {
    const kayit = { ziyaretci: z, merkez: null, durum: null, neden: null };

    if (z.nekahet === "evet") {                       // Madde 10/8-d
      kayit.durum = DEGIL; kayit.neden = "10/8-d";
      ekle(DEGIL, "10/8-d"); sonuc.push(kayit); continue;
    }
    const cekirdek = hizmetler.arketipler[z.talep_arketipi].cekirdek;
    const esik = Math.max(1, Math.floor(cekirdek.length / 2));
    const hizmetVeren = acik.filter(m =>
      cekirdek.filter(h => m.hizmet_sepeti.includes(h)).length >= esik);
    if (!hizmetVeren.length) {                        // aradığı hizmeti sunan merkez yok
      kayit.durum = DEGIL; kayit.neden = "hizmet_yok";
      ekle(DEGIL, "hizmet_yok"); sonuc.push(kayit); continue;
    }
    let adaylar = hizmetVeren.filter(m => kalan[m.kimlik] > 0);
    if (!adaylar.length) {                            // hizmet var, kapasite dolu
      kayit.durum = DEGIL; kayit.neden = "kapasite_dolu";
      ekle(DEGIL, "kapasite_dolu"); sonuc.push(kayit); continue;
    }
    if (z.ikamet === "yurt_disi") {                   // Madde 17
      const izinli = adaylar.filter(m => kabul[m.kimlik]);
      if (!izinli.length) {
        const d = turizmDurumu(senaryo, adaylar[0]);
        kayit.durum = d === BELIRSIZ ? BELIRSIZ : DEGIL;
        kayit.neden = "17/1";
        ekle(kayit.durum, "17/1"); sonuc.push(kayit); continue;
      }
      adaylar = izinli;
    }
    const m = adaylar[Math.floor(r() * adaylar.length)];
    kalan[m.kimlik] -= 1; yuk[m.kimlik] += 1;
    kayit.merkez = m.kimlik; kayit.durum = UYGUN;
    ekle(UYGUN, "hizmet"); sonuc.push(kayit);
  }

  const toplam = ziyaretciler.length || 1;
  return {
    kayitlar: sonuc, sayim, neden, yuk,
    oran: { uygun: sayim.uygun / toplam, belirsiz: sayim.belirsiz / toplam,
            uygun_degil: sayim.uygun_degil / toplam },
    doluluk: acik.length
      ? acik.reduce((s, m) => s + yuk[m.kimlik], 0) / acik.reduce((s, m) => s + m.kapasite, 0) : 0,
  };
}

/* Segment kırılımı: hangi ziyaretçi grubu ne sonuç aldı. */
export function kirilim(kayitlar, alan) {
  const t = {};
  for (const k of kayitlar) {
    const g = k.ziyaretci[alan];
    if (!t[g]) t[g] = { uygun: 0, belirsiz: 0, uygun_degil: 0, toplam: 0 };
    t[g][k.durum] += 1; t[g].toplam += 1;
  }
  return t;
}
