"""Yıllık simülasyon döngüsü.

Bir yılda sırayla şunlar olur:

1. Ruhsat başvuruları gelir, yapısal kurallardan geçenler açılır.
2. Ziyaretçi kohortu Bayes ağıyla üretilir.
3. Ziyaretçiler merkezlerle eşleştirilir, hizmet alan alır.
4. Merkezlerin bir bölümü denetlenir, ihlaller tespit sayaçlarını artırır.
5. Yaptırımlar uygulanır, üçüncü tespitler faaliyeti durdurur.
6. Uyum durumu Markov geçişiyle güncellenir; ceza alan toparlanır.
7. Doluluğu iki yıl üst üste eşiğin altında kalan merkez kapanır.

Açılış sayısı sabit değil. Karşılanamayan talep büyükse başvuru artar,
kapasite fazlaysa azalır. Bu geri besleme sayesinde Madde 17'nin belirsizliği
yalnızca bir sınıflandırma sorunu olmaktan çıkıp sektörün büyüklüğünü
belirleyen bir mekanizmaya dönüşür.
"""

import random

from cekirdek import kural as K
from cekirdek.merkez import Merkez, IPTAL, ZARAR

YERLESIMLER = ["mustakil_bina", "konaklama_tesisi", "yasli_bakim_merkezi",
               "engelli_bakim_merkezi", "spor_kulubu"]


class Simulasyon:

    def __init__(self, ag, veri, senaryo, yil_sayisi=10, anahtar=0,
                 yalniz_olagan=False):
        self.ag = ag
        self.veri = veri
        self.senaryo = senaryo
        self.ortak = veri["senaryolar"]["ortak"]
        self.uyum = veri["senaryolar"]["uyum_durumlari"]
        self.yil_sayisi = yil_sayisi
        self.rnd = random.Random(anahtar)
        self.anahtar = anahtar
        self.denetim_kurallari = K.denetim_kurallari(veri["ek4"], yalniz_olagan)

        self.merkezler = []
        self.kayit_disi = []
        self.sayac = 0
        self.yillar = []
        self.reddedilen_basvuru = 0
        self.red_nedenleri = {}

    # ------------------------------------------------------------------
    def _basvuru_uret(self, yil):
        r = self.rnd
        yerlesim = r.choice(YERLESIMLER)
        tur = r.choice(["merkez", "unite"])
        asgari = (500 if tur == "merkez" else 300) if yerlesim == "mustakil_bina" else 0
        kayit = {
            "yerlesim": yerlesim,
            "tur": tur,
            "kapali_alan_m2": int(asgari * r.uniform(0.7, 2.6)) if asgari else None,
            "oda_sayisi": r.choice([6, 8, 10, 14, 22, 40, 70]) if yerlesim == "konaklama_tesisi" else None,
            "mustakil_giris": r.random() < 0.93,
            "turizm_isletmesi_belgesi": r.random() < 0.94,
            "kurum_izni": r.random() < 0.92,
            "uzman_tabip_var": r.random() < 0.5,
            "mesul_mudur_tabiplik_yili": r.choice([1, 2, 3, 4, 6, 9, 14, 20]),
            "mesul_mudur_baska_kurumda": r.random() < 0.07,
            "ruhsattan_faaliyete_ay": r.choice([1, 2, 3, 4, 5, 6, 8]),
        }
        kayit["uzman_tabip_asgari_yas"] = (
            r.choice([46, 55, 61, 64, 68]) if kayit["uzman_tabip_var"] else None)
        return kayit

    def _sepet(self, arketip):
        a = self.veri["hizmetler"]["arketipler"][arketip]
        p = self.veri["hizmetler"]["arketip_perturbasyon"]
        sepet = {h for h in a["cekirdek"]
                 if self.rnd.random() > p["cekirdek_dusurme_olasiligi"]}
        sepet |= {h for h in a["olasi"]
                  if self.rnd.random() < p["olasi_ekleme_olasiligi"]}
        return sepet

    def _merkez_ac(self, yil, basvuru):
        self.sayac += 1
        arketip = self.rnd.choice(sorted(self.veri["hizmetler"]["arketipler"]))
        taban = 155 if basvuru["tur"] == "merkez" else 88
        kapasite = int(taban * self.rnd.uniform(0.75, 1.5))
        m = Merkez(
            kimlik="M%04d" % self.sayac, yil=yil,
            yerlesim=basvuru["yerlesim"], tur=basvuru["tur"],
            kapali_alan=basvuru["kapali_alan_m2"], oda_sayisi=basvuru["oda_sayisi"],
            arketip=arketip, hizmet_sepeti=self._sepet(arketip),
            uyum_durumu=self._rastgele_durum(), kapasite=kapasite)
        # Her merkezin kendi zayıf noktaları var: kayıt tutmayan merkez her
        # denetimde kayıt sorularından, personel düzeni bozuk merkez personel
        # sorularından takılır. İhlallerin yirmi bir kurala eşit dağıldığını
        # varsaymak, yaptırım merdivenini hiç işlemez hâle getirir.
        kodlar = ["S%02d" % k["soru_no"] for k in self.denetim_kurallari]
        m.zayif_kurallar = set(self.rnd.sample(kodlar, self.rnd.randint(2, 4)))
        self.merkezler.append(m)
        return m

    def _rastgele_durum(self):
        p = self.rnd.random()
        if p < 0.55:
            return "iyi"
        if p < 0.88:
            return "orta"
        return "zayif"

    # ------------------------------------------------------------------
    def _giris(self, yil, onceki_karsilanamayan):
        """Başvuru sayısı karşılanamayan talebe göre belirlenir."""
        taban = self.ortak["yillik_basvuru_tabani"]
        acik = [m for m in self.merkezler if m.acik]
        kapasite = sum(m.kapasite for m in acik) or 1
        baski = onceki_karsilanamayan / float(kapasite)
        beklenen = taban * max(0.15, min(2.4, 0.35 + 1.9 * baski))
        adet = max(0, int(self.rnd.gauss(beklenen, beklenen * 0.22)))

        acilan = 0
        for _ in range(adet):
            basvuru = self._basvuru_uret(yil)
            verilir, engel = K.ruhsat_incele(basvuru, self.veri["yapisal"])
            if verilir:
                self._merkez_ac(yil, basvuru)
                acilan += 1
            else:
                self.reddedilen_basvuru += 1
                for e in engel:
                    self.red_nedenleri[e["dayanak"]] = \
                        self.red_nedenleri.get(e["dayanak"], 0) + 1
                # Ruhsat alamayan işletmenin bir bölümü faaliyete yine de başlar.
                # Madde 10/8-a bunu yasaklıyor; yakalanması denetime bağlı.
                if self.rnd.random() < self.ortak.get("kayit_disi_egilimi", 0.0):
                    m = self._merkez_ac(yil, basvuru)
                    m.ruhsatsiz = True
                    self.merkezler.remove(m)
                    self.kayit_disi.append(m)
        return adet, acilan

    # ------------------------------------------------------------------
    def _ziyaretciler(self, yil, sira):
        adet = int(self.ortak["yillik_ziyaretci"]
                   * (1 + self.ortak["talep_buyume"]) ** sira)
        return self.ag.ornekle_coklu(adet, yineleme_anahtari=self.anahtar * 1000 + sira)

    def _eslestir(self, yil, ziyaretciler):
        """Her ziyaretçiyi kabul edebilecek bir merkeze yerleştirir."""
        acik = [m for m in self.merkezler if m.acik]
        for m in acik:
            m.hizmet_verdigi[yil] = 0
        kalan = {m.kimlik: m.yillik_kapasite(yil) for m in acik}
        arketipler = self.veri["hizmetler"]["arketipler"]
        kabul_orani = self.senaryo["turizm_kabul_orani"]

        # Yurt dışı ziyaretçi kabulü merkezin o yıl için verdiği bir karardır,
        # her ziyaretçide yeniden çekilmez. Durum tanımsızken merkezlerin
        # çoğu riski almaz.
        belirsizlik_istahi = self.ortak["belirsizlik_kabul_orani"]
        kabul = {}
        for m in acik:
            d = K.turizm_durumu(self.senaryo, yil, m)
            if d == K.UYGUN:
                kabul[m.kimlik] = self.rnd.random() < kabul_orani
            elif d == K.BELIRSIZ:
                kabul[m.kimlik] = self.rnd.random() < belirsizlik_istahi
            else:
                kabul[m.kimlik] = False

        sonuc = {"hizmet_aldi": 0, "belirsiz": 0, "hizmet_alamadi": 0,
                 "yurt_disi_aldi": 0, "yurt_disi_toplam": 0,
                 "nekahet_dislandi": 0,
                 "hizmet_yok": 0, "kapasite_dolu": 0,
                 # Tanımsız sonucun kaynağına göre dağılımı. Yalnızca ilki
                 # senaryolarla çözülür.
                 "bel_17": 0, "bel_nekahet": 0, "bel_tedavi": 0}
        nekahet_gri = self.ortak.get("nekahet_gri_pay", 0.35)
        tedavi_gri = self.ortak.get("tedavi_gri_pay", 0.45)

        for z in ziyaretciler:
            yurt_disi = z["ikamet"] == "yurt_disi"
            if yurt_disi:
                sonuc["yurt_disi_toplam"] += 1

            # Madde 10/8-d: yasak nettir, dayandığı kavram değil. Nekahet
            # döneminin tanımı bulunmadığından sınırdaki kişilerde durum
            # tanımsız kalır. Bu belirsizlik hiçbir senaryoyla çözülmez.
            if z["nekahet"] == "evet":
                if self.rnd.random() < nekahet_gri:
                    sonuc["belirsiz"] += 1
                    sonuc["bel_nekahet"] += 1
                    continue
                sonuc["nekahet_dislandi"] += 1
                sonuc["hizmet_alamadi"] += 1
                continue
            if z.get("yakin_cerrahi") == "var" and self.rnd.random() < nekahet_gri:
                sonuc["belirsiz"] += 1
                sonuc["bel_nekahet"] += 1
                continue

            # Madde 4/1-c: esenlik hizmeti tedavi amacı taşımaz; ölçüt yok.
            # Ağır kronik yükte rehabilitasyon destekli hizmetin esenlik mi
            # tedavi mi olduğu belirsizdir. Senaryolarla çözülmez.
            if (z.get("kronik_yuk") == "agir"
                    and z["talep_arketipi"] == "rehabilitasyon_destek"
                    and self.rnd.random() < tedavi_gri):
                sonuc["belirsiz"] += 1
                sonuc["bel_tedavi"] += 1
                continue

            cekirdek = set(arketipler[z["talep_arketipi"]]["cekirdek"])
            esik = max(1, len(cekirdek) // 2)
            hizmet_veren = [m for m in acik if len(cekirdek & m.hizmet_sepeti) >= esik]
            if not hizmet_veren:
                sonuc["hizmet_yok"] += 1
                sonuc["hizmet_alamadi"] += 1
                continue
            adaylar = [m for m in hizmet_veren if kalan[m.kimlik] > 0]
            if not adaylar:
                sonuc["kapasite_dolu"] += 1
                sonuc["hizmet_alamadi"] += 1
                continue

            if yurt_disi:
                uygunlar = [m for m in adaylar if kabul[m.kimlik]]
                if not uygunlar:
                    durum = K.turizm_durumu(self.senaryo, yil, adaylar[0])
                    if durum == K.BELIRSIZ:
                        sonuc["belirsiz"] += 1
                        sonuc["bel_17"] += 1
                    else:
                        sonuc["hizmet_alamadi"] += 1
                    continue
                adaylar = uygunlar

            m = self.rnd.choice(adaylar)
            kalan[m.kimlik] -= 1
            m.hizmet_verdigi[yil] = m.hizmet_verdigi.get(yil, 0) + 1
            sonuc["hizmet_aldi"] += 1
            if yurt_disi:
                sonuc["yurt_disi_aldi"] += 1
        return sonuc

    # ------------------------------------------------------------------
    def _denetim(self, yil):
        oran = self.senaryo["denetim_orani"]
        # Denetim kapasitesi sınırsız değildir. Merkez sayısı büyüdükçe hedeflenen
        # oran tutturulamaz; fiilî oran kapasiteye göre düşer.
        acik_sayisi = len([x for x in self.merkezler if x.acik])
        kapasite = self.ortak.get("yillik_denetim_kapasitesi", 0)
        if kapasite and acik_sayisi:
            oran = min(oran, kapasite / float(acik_sayisi))
        uyum_olasilik = self.uyum["kural_uyum_olasiligi"]
        sayim = {"denetlenen": 0, "ihlal": 0, "kademe1": 0, "kademe2": 0,
                 "kademe3": 0, "iptal": 0, "durdurma_gun": 0}
        kural_sayaci = {}

        for m in [x for x in self.merkezler if x.acik]:
            m.durdurulan_gun = 0
            m.son_yil_cezali = False
            if self.rnd.random() >= oran:
                continue
            sayim["denetlenen"] += 1
            zayif_p = uyum_olasilik[m.uyum_durumu]
            saglam_p = self.uyum["saglam_kural_uyumu"]
            ucuncu = 0
            for k in self.denetim_kurallari:
                kod = "S%02d" % k["soru_no"]
                p = zayif_p if kod in m.zayif_kurallar else saglam_p
                if self.rnd.random() < p:
                    continue
                kademe = m.tespit_ekle(yil, kod)
                etki = K.yaptirim_etkisi(kademe)
                m.ceza_toplami += etki["ceza_birimi"]
                m.durdurulan_gun += etki["durdurma_gun"]
                m.son_yil_cezali = True
                sayim["ihlal"] += 1
                sayim["kademe%d" % min(kademe, 3)] += 1
                kural_sayaci[k["dayanak"]] = kural_sayaci.get(k["dayanak"], 0) + 1
                if kademe >= 3:
                    ucuncu += 1
            sayim["durdurma_gun"] += m.durdurulan_gun
            # İki ayrı kuralda üçüncü tespite ulaşan merkezin ruhsatı iptal edilir.
            if ucuncu >= 2:
                m.kapat(yil, IPTAL)
                sayim["iptal"] += 1
        return sayim, kural_sayaci

    def _uyum_guncelle(self):
        durumlar = self.uyum["durumlar"]
        for m in [x for x in self.merkezler if x.acik]:
            tablo = (self.uyum["gecis_cezali"] if m.son_yil_cezali
                     else self.uyum["gecis_cezasiz"])[m.uyum_durumu]
            esik = self.rnd.random()
            birikim = 0.0
            for i, p in enumerate(tablo):
                birikim += p
                if esik <= birikim:
                    m.uyum_durumu = durumlar[i]
                    break

    def _cikis(self, yil):
        esik = self.ortak["doluluk_esigi"]
        sinir = self.ortak["arka_arkaya_zarar_yili"]
        kapanan = 0
        for m in [x for x in self.merkezler if x.acik]:
            if m.yasi(yil) < 1:
                continue
            if m.doluluk(yil) < esik:
                m.zarar_yili += 1
            else:
                m.zarar_yili = 0
            if m.zarar_yili >= sinir:
                m.kapat(yil, ZARAR)
                kapanan += 1
        return kapanan

    # ------------------------------------------------------------------
    def calistir(self):
        yil0 = self.ortak["baslangic_yili"]
        for _ in range(self.ortak["baslangic_merkez_sayisi"]):
            while True:
                b = self._basvuru_uret(yil0)
                verilir, _ = K.ruhsat_incele(b, self.veri["yapisal"])
                if verilir:
                    self._merkez_ac(yil0, b)
                    break

        karsilanamayan = 0
        for sira in range(self.yil_sayisi):
            yil = yil0 + sira
            basvuru, acilan = (0, 0) if sira == 0 else self._giris(yil, karsilanamayan)
            ziyaretciler = self._ziyaretciler(yil, sira)
            eslesme = self._eslestir(yil, ziyaretciler)
            kd = self._kayit_disi_denetim(yil)
            denetim, kural_sayaci = self._denetim(yil)
            self._uyum_guncelle()
            kapanan = self._cikis(yil)
            karsilanamayan = eslesme["hizmet_alamadi"] + eslesme["belirsiz"]

            acik = [m for m in self.merkezler if m.acik]
            toplam_kapasite = sum(m.yillik_kapasite(yil) for m in acik)
            for m in acik:
                m.gecmis.append({"yil": yil, "hizmet": m.hizmet_verdigi.get(yil, 0),
                                 "uyum": m.uyum_durumu})

            self.yillar.append({
                "yil": yil,
                "kayit_disi_aktif": len([x for x in self.kayit_disi if x.acik]),
                "kayit_disi_kapanan": kd,
                "basvuru": basvuru,
                "acilan": acilan,
                "kapanan": kapanan,
                "aktif_merkez": len(acik),
                "kapasite": toplam_kapasite,
                "doluluk": round(eslesme["hizmet_aldi"] / float(toplam_kapasite or 1), 4),
                "ziyaretci": len(ziyaretciler),
                "eslesme": eslesme,
                "denetim": denetim,
                "kural_sayaci": kural_sayaci,
                "uyum_dagilimi": self._uyum_dagilimi(acik),
                "turizm_durumu": K.turizm_durumu(
                    self.senaryo, yil, acik[0]) if acik else K.BELIRSIZ,
            })
        return self.rapor()

    def _kayit_disi_denetim(self, yil):
        """Ruhsatsız işletmeler denetimde yakalanınca faaliyetten men edilir."""
        oran = self.senaryo["denetim_orani"]
        kapanan = 0
        for m in [x for x in self.kayit_disi if x.acik]:
            m.hizmet_verdigi[yil] = int(m.kapasite * self.rnd.uniform(0.3, 0.8))
            if self.rnd.random() < oran:
                m.tespit_ekle(yil, "S01")
                m.kapat(yil, IPTAL)
                kapanan += 1
        return kapanan

    def _uyum_dagilimi(self, acik):
        d = {k: 0 for k in self.uyum["durumlar"]}
        for m in acik:
            d[m.uyum_durumu] += 1
        return d

    def rapor(self):
        return {
            "senaryo": self.senaryo["kod"],
            "yillar": self.yillar,
            "merkezler": [m.ozet() for m in self.merkezler],
            "reddedilen_basvuru": self.reddedilen_basvuru,
            "kayit_disi_toplam": len(self.kayit_disi),
            "red_nedenleri": dict(sorted(self.red_nedenleri.items(),
                                         key=lambda x: -x[1])),
        }
