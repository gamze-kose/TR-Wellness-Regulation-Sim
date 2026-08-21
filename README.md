<h1 align="center">TR-Wellness-Regulation-Sim</h1>

<p align="center">
  <strong>Temel soru: "Mevzuat belirsizliği ölçülebilir mi?"</strong><br>
  Esenlik Hizmetleri Yönetmeliği ve sağlık turizmi üzerine<br>
  yapay zekâ destekli bir düzenleyici etki analizi aracı.
</p>

<p align="center">
  <a href="https://gamze-kose.github.io/TR-Wellness-Regulation-Sim/"><strong>▶ Aracı tarayıcıda açın</strong></a>
  &nbsp;·&nbsp;
  <a href="#yöntem-ve-teknikler">Yöntem</a>
  &nbsp;·&nbsp;
  <a href="#nasıl-çalışır">Nasıl çalışır</a>
  &nbsp;·&nbsp;
  <a href="#bulgular">Bulgular</a>
  &nbsp;·&nbsp;
  <a href="#english">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/lisans-MIT-black.svg" alt="MIT">
  <img src="https://img.shields.io/badge/kurulum-gerekmez-1D9E75.svg" alt="Kurulum gerekmez">
  <img src="https://img.shields.io/badge/arayüz-Türkçe%20%7C%20English-5B4DA6.svg" alt="İki dilli">
  <img src="https://img.shields.io/badge/mevzuat-RG%2033300-B8641A.svg" alt="RG 33300">
  <br>
  <img src="https://img.shields.io/badge/Bayes%20a%C4%9F%C4%B1-veriden%20%C3%B6%C4%9Frenme-5B4DA6.svg" alt="Bayes ağı">
  <img src="https://img.shields.io/badge/etmen%20temelli-sim%C3%BClasyon-177A5C.svg" alt="Etmen temelli simülasyon">
  <img src="https://img.shields.io/badge/kural%20tabanl%C4%B1-%C3%A7%C4%B1kar%C4%B1m-A5382F.svg" alt="Kural tabanlı çıkarım">
  <img src="https://img.shields.io/badge/Monte%20Carlo-duyarl%C4%B1l%C4%B1k%20analizi-555.svg" alt="Monte Carlo">
</p>

![Aracın ana ekranı ve beş adımlı akışı](gorseller/tr-00-kapak.png)

---

## Sorun

Yeni yayımlanan bir yönetmeliğin hükümleri her zaman tek başına uygulanabilir
değildir. Kimi hüküm ikincil düzenlemeye bırakılır, kimi kavram tanımsız kalır,
kimi takdir yetkisi ölçüt verilmeden tanınır. Bu belirsizlikler hukuk
metinlerinde tartışılır ancak ölçülmez.

Esenlik Hizmetleri Yönetmeliği'nin (4 Temmuz 2026, RG 33300) **17 nci maddesi**
sağlık turizmi kapsamındaki hizmetlerin usul ve esaslarını Sağlık Bakanlığına
bırakmış, ikincil düzenleme yayımlanmamış, denetim aracı olan **EK-4'te ise
konuya ilişkin tek bir soru yer almamıştır**. Bir merkez, yurt dışında ikamet
eden ziyaretçiye hizmet verirken kurala uygun mu aykırı mı davrandığını
bilememektedir.

Bu araç, o boşluğu sayıya döker. Sentetik esenlik merkezleri ve sağlık
turistleri üretir, bunları yönetmelikten aktarılan kurallar karşısında
eşleştirir ve **üç değerli** bir sonuç verir:

| | |
|---|---|
| 🟢 **Uygun** | Hiçbir kural ihlal edilmiyor, hizmet verilebilir. |
| 🟣 **Belirsiz** | Kural ihlali yok, ancak Madde 17 usul ve esas belirlemediği için durum tanımsız. |
| 🔴 **Uygun değil** | En az bir kural ihlal ediliyor. |

Üçüncü durum aracın çekirdeğidir. Bir düzenlemenin *eksikliğini* ölçülebilir bir
kategori hâline getirir ve yöntem, başka mevzuata da aktarılabilir.

## Yöntem ve teknikler

Araç, sembolik ve olasılıksal yapay zekâ yöntemlerini bir arada kullanır. Hiçbir
bileşen kara kutu değildir: öğrenilen tablolar, uygulanan kurallar ve çekim izi
arayüzden tek tek denetlenebilir.

| Teknik | Nerede | Dosya |
|---|---|---|
| **Kural tabanlı çıkarım** (sembolik yapay zekâ) | EK-4'ün 21 denetim sorusu ve maddelerden türetilen 12 yapısal kural | `web/akis.js` · `cekirdek/kural.py` |
| **Üç değerli mantık** | Uygun / uygun değil / belirsiz. Mevzuat boşluğunu ölçülebilir bir kategoriye çevirir | `web/akis.js` |
| **Ayrık Bayes ağı** (olasılıksal grafik model) | Sentetik ziyaretçi üretimi; topolojik sırayla ileri yönlü örnekleme | `web/model.js` · `cekirdek/ag.py` |
| **Dirichlet öncüllü parametre öğrenmesi** | Koşullu olasılık tabloları elle yazılmaz, kayıt setinden kestirilir | `web/model.js` · `cekirdek/ogren.py` |
| **Etmen temelli simülasyon** | Merkezler tek tek izlenen etmenler; kendi durumu, sepeti ve tespit sayaçları | `cekirdek/simulasyon.py` · `cekirdek/merkez.py` |
| **Markov zinciri** | Uyum durumunun yıldan yıla geçişi; ceza alan merkez farklı matris kullanır | `cekirdek/simulasyon.py` |
| **Monte Carlo tekrarları** | Tek kestirim yerine ortanca ve yüzde 10–90 bandı | `cekirdek/gostergeler.py` |
| **Tek değişkenli duyarlılık analizi** | Her parametre alt ve üst değerine çekilip çıktıdaki değişim ölçülür | `web/analiz.js` |
| **Deneysel tasarım ve tabakalı örnekleme** | Merkez konfigürasyonları üretken modelle değil, hukuken ayırt edilebilir sınıflar üzerinden | `web/akis.js` |
| **Geri beslemeli talep dinamiği** | Karşılanamayan talep büyüdükçe ruhsat başvurusu artar, kapasite fazlalaştıkça azalır | `cekirdek/simulasyon.py` |

Çekim, üretim ve simülasyonun tamamı **yinelenebilirdir**: aynı yineleme
anahtarı aynı sonucu verir ve hiçbir çıktı bir dil modeline bağlı değildir.

## Kullanım

Araç tamamen tarayıcıda çalışır. Sunucu, kurulum ya da veri yükleme gerekmez.

**Doğrudan açın:** <https://gamze-kose.github.io/TR-Wellness-Regulation-Sim/>

**Ya da indirin:** `index.html` dosyasını indirip çift tıklayın. Bütün kaynaklar
dosyanın içine gömülüdür; internet bağlantısı olmadan da çalışır.

```bash
git clone https://github.com/gamze-kose/TR-Wellness-Regulation-Sim.git
```

Arayüz Türkçe ve İngilizcedir; sağ üstteki düğmeyle değiştirilir.

---

## Nasıl çalışır

Beş adım, her biri bir öncekinin çıktısını kullanır.

### 01 · Veri ve model

Ziyaretçi modelinin öğrendiği kayıt seti burada. Elle yazılmış olasılık tablosu
yoktur; tablolar bu kayıtlardan öğrenilir. Soldaki tablodan son kaydı silebilir,
başlangıç setine dönebilir ya da tümünü boşaltabilirsiniz; alttaki formdan yeni
kayıt eklersiniz. **Her değişiklikte model yeniden eğitilir** ve sağdaki
dağılımlar anında güncellenir — aşağıda 240 kaydın yaş, genel sağlık, risk,
yaşam tarzı, yakın cerrahî ve nekahet dağılımları görünüyor.

![Kayıt ekleme formu ve değişken dağılımları](gorseller/tr-01-kayit-ekle.png)

Öğrenilen tablolar denetlenebilir durumdadır. Aşağıda genel sağlık düğümünün
tablosu var: yaş grubu ve yaşam tarzının her bileşimi için ayrı bir satır, on iki
satır toplam. En sağdaki **gözlem** sütunu o satırın kaç kayda dayandığını
söyler — beşten az gözleme dayanan satırlar işaretlenir, çünkü üç kayıttan
öğrenilmiş bir olasılık olasılık değildir. Örnekte 35-49 yaş ve hareketsiz
yaşam tarzı satırı yalnızca 11 gözleme dayanıyor.

![Öğrenilen koşullu olasılık tabloları](gorseller/tr-01-ogrenilen-tablo.png)

Modelden tek tek profil çekilebilir. Ağ topolojik sırayla dolaşılır; sağdaki
tablo her düğümde hangi değerin çekildiğini, o değerin olasılığını ve satırın
kaç gözleme dayandığını gösterir. Aşağıdaki çekimde nekahet dönemi **1,00**
olasılıkla "hayır" çıkmış, çünkü kişinin yakın cerrahî girişimi yok. Model bu
bağımlılığı kuraldan değil veriden öğrenmiştir.

![Bayes ağı ve profil çekim izi](gorseller/tr-01-profil-cekimi.png)

### 02 · Merkezler

Başvurular önce **yapısal kurallardan** geçirilir: metrekare eşiği, oda sayısı,
kurum izni ve mesul müdür şartları. Aşağıdaki koşuda 89 başvurudan 60'ı ruhsat
almış, 29'u reddedilmiş, ruhsat alanların 16'sında denetim kuralı ihlali
çıkmış. Red gerekçeleri madde numarasıyla listelenir; en sık gerekçe mesul
müdürün üç yıllık tabiplik şartıdır (11/4-c), onu mesul müdürün başka kurumda
çalışamaması (11/6) izler.

![Ruhsatlandırma sonuçları ve red gerekçeleri](gorseller/tr-02-ruhsat.png)

Ruhsat alanlar **EK-4 denetim kurallarına** göre değerlendirilir. Her kart bir
merkezdir: yerleşim türü, merkez mi ünite mi olduğu ve ihlal sayısı görünür.
Karta tıklayınca hizmet sepeti ve hangi kuralı ihlal ettiği açılır.

![Üretilen merkezlerin kartları](gorseller/tr-02-merkez-kartlari.png)

Yönetmeliğin yüklediği şartların bir de maliyeti vardır. Bu katman **hangi iş
modelinin ayakta kalabildiğini** gösterir. Aşağıdaki tabloda müstakil binada
açılan ünitelerin hiçbiri (0/5) ve yaşlı bakım merkezi bünyesindeki ünitelerin
hiçbiri (0/4) geliriyle maliyetini karşılayamıyor; buna karşılık konaklama
tesisi ve bakım merkezi bünyesindeki merkezler karşılıyor. Sabit yükümlülükler
küçük ölçeği orantısız etkiler.

![Uyum maliyeti ve merkez türüne göre yaşayabilirlik](gorseller/tr-02-yasayabilirlik.png)

Maliyet kalemlerinin her biri bir hükme bağlıdır: kapalı alan (4/1-f, 4/1-ı),
acil müdahale odası (10/3), tam zamanlı mesul müdür (11/2, 11/6), altmış yaş
üstü uzman tabip (10/6), hastane iş birliği (13/2), bilgi yönetim sistemi
(14/1, 14/2, 14/4), personel belgeleri (10/7, 15/1) ve ürün satışı yasağının
doğurduğu gelir kaybı (10/8-f).

![Maliyet kalemleri ve dayanakları](gorseller/tr-02-maliyet-kalemleri.png)

### 03 · Ziyaretçiler

Sentetik sağlık turistleri eğitilmiş modelden çekilir ve tek tek merkezlerle
eşleştirilir. Nekahet dönemindeki kişi Madde 10/8-d gereği hizmet alamaz; yurt
dışında ikamet edenlerde Madde 17 devreye girer.

Senaryo seçildiğinde bilgi kutusu açılır: Madde 17'nin durumu, yürürlük yılı,
düzenleme sonrası kabul oranı, denetim oranı ve ünitelerin kapsamda olup
olmadığı. Aşağıda **S0 — Belirsizlik sürüyor** senaryosu; ikincil düzenleme hiç
yayımlanmıyor ve sonuç şeridinde mor bir **Tanımsız %3** bandı beliriyor.

![S0 senaryosu, tanımsız bandı görünür](gorseller/tr-03-senaryo-s0.png)

Aynı ekran **S1 — İzin verici düzenleme** ile. Düzenleme 2028'de yayımlanıyor,
mor bant tamamen kayboluyor: **Tanımsız %0**. İki koşuda ziyaretçi sayısı farklı
olduğu için yeşil ve kırmızı bantları karşılaştırmayın; senaryonun etkisini
gösteren şey mor bandın varlığı ve yokluğudur.

![S1 senaryosu, tanımsız bandı yok](gorseller/tr-03-senaryo-s1.png)

### 04 · Sonuçlar

Her ziyaretçi için sonucu belirleyen hüküm kayıt altına alınır. Aşağıdaki
koşuda ziyaretçilerin %71'i hizmet almış; %14'ü aradığı hizmeti sunan merkez
bulamamış, %10'u Madde 10/8-d'ye takılmış, %6'sı kapasite dolduğu için hizmet
alamamış. Segment kırılımı ikamete, yaşa ve talep edilen hizmete göre verilir —
rehabilitasyon talebinin karşılanma oranının belirgin biçimde düşük olması,
merkezlerin hizmet sepetlerinden kaynaklanan bir arz sorununu gösterir.

![Sonuçlar, belirleyici hükümler ve segment kırılımı](gorseller/tr-04-sonuclar.png)

Simülasyonun serbest parametreleri vardır ve çıktı bir ölçüde onlara bağlıdır.
Bunu gizlemek yerine ölçüyoruz: her parametre tek tek alt ve üst değerine
çekilir, çıktıdaki değişim kaydedilir. Aşağıdaki tabloda **ruhsat şartlarına
uyum** satırı ruhsat reddi sütununda 64,1 ile en uzun çubuğa sahipken hizmet
alma oranı sütununda yalnızca 1,3; yani ruhsat şartları kimin sektöre
girebileceğini belirliyor, kimin hizmet alabileceğini değil.

![Duyarlılık analizi](gorseller/tr-04-duyarlilik.png)

Beş senaryonun on yıllık seyri. Koyu çizgi ortanca, açık alan tekrarların yüzde
10–90 aralığıdır. Sekiz gösterge izlenir: yurt dışı ziyaretçinin hizmet alma
oranı, tanımsız kalan talep, açık merkez sayısı, uyum durumu, ortalama doluluk,
üçüncü tespite ulaşan ihlal, faaliyetteki ruhsatsız işletme ve fiilî denetim
oranı. Son iki gösterge yönetmeliğin dolaylı etkilerini yakalar: ruhsat
alamayanların bir bölümü kayıt dışı çalışır, denetim kapasitesi sınırlı olduğu
için sektör büyüdükçe fiilî denetim oranı hedefin altına düşer.

![Çok yıllı projeksiyon, S0 senaryosu](gorseller/tr-04-projeksiyon.png)

### 05 · Belirsizlik

Yönetmelik metninin madde madde taranmasıyla çıkarılan katalog: **on dört kayıt,
altı tür**, üçü doğrudan sağlık turizmini etkiliyor. Her kayıt hükmün tek başına
uygulanmasını engelleyen bir eksiği gösterir ve türe göre süzülebilir.

Aşağıda ölçüt verilmeden idareye bırakılmış takdir yetkileri süzülmüş durumda:
"hizmetin niteliğine uygun mekân" ölçütünün verilmemesi (10/4 — buna karşılık
EK-4'ün beşinci sorusu bu şartı denetliyor), tıbbi cihaz izninin usulünün
düzenlenmemesi (10/2), hizmet alımı sınırının belirsizliği (12/1) ve "telafisi
güç durumlar" ifadesinin ölçütsüzlüğü (18/2). **Madde 17 bu kataloğun yalnızca
bir satırıdır.**

![Yönetmelikteki belirsizlikler kataloğu](gorseller/tr-05-belirsizlik.png)

---

## Bulgular

Aşağıdaki sayılar aracın varsayılan ayarlarıyla üretilmiştir ve gerçek veriyle
doğrulanmamıştır. Anlamlı olan mutlak değerler değil, senaryolar arasındaki
farklar ve duyarlılık sıralamasıdır.

- **On dört belirsizlik kaydı** belirlendi; üçü doğrudan sağlık turizmini
  etkiliyor. En sık tür, ölçüt verilmeden bırakılmış takdir yetkisi.
- **Denetim formunun hiçbir sorusu** yönetmeliğin yapısal tanımlarını
  sorgulamıyor. Kapalı alan, oda sayısı, kurum izni ve altmış yaş şartı ruhsat
  aşamasında aranıyor, işletme sırasında denetlenmiyor.
- İkincil düzenlemenin hiç yayımlanmadığı senaryoda yurt dışında ikamet eden
  ziyaretçilerin hizmet alma oranı onuncu yılda **%46**'ya geriliyor ve talebin
  **%11**'i kalıcı olarak tanımsız kalıyor. Düzenlemenin 2028'de yayımlandığı
  senaryolarda oran **%86**'ya çıkıyor.
- Duyarlılık analizine göre **ruhsat şartlarına uyum, ruhsat reddini neredeyse
  tek başına belirliyor** ama ziyaretçilerin hizmete erişimini hemen hiç
  etkilemiyor. Erişimi belirleyen kapasite.
- Uyum maliyeti katmanında **sabit yükümlülükler küçük ölçeği orantısız
  etkiliyor**; müstakil binada açılan üniteler eşiğin altında kalıyor.

---

## Yöntemin ayrıntısı

### Olasılıksal katman: Bayes ağı ve veriden öğrenme

Ziyaretçi modeli sekiz düğümlü ayrık bir Bayes ağıdır. **Yapı** uzman tarafından
belirlenir — hangi değişkenler var, hangisi hangisine bağlı. Değişkenler Madde
10/1'deki kişiye özgü planlama ölçütlerinden alınmıştır: yaş, genel sağlık
durumu, mevcut risk faktörleri ve yaşam tarzı. Buna Madde 10/8-d gereği nekahet
durumu ve Madde 17 gereği ikamet eklenmiştir.

**Parametreler** ise veriden kestirilir. Her düğümün her ebeveyn bileşimi için
sayımlar tutulur, bunlara düzgün dağılımlı küçük bir Dirichlet öncülü eklenir ve
sonsal ortalama tabloyu oluşturur. Öncülün tek amacı hiç gözlem düşmemiş satırı
tanımsız bırakmamaktır; kayıt sayısı arttıkça etkisi kaybolur. Az gözleme
dayanan satırlar arayüzde işaretlenir.

Üretim ileri yönlü örneklemedir: ağ topolojik sırayla dolaşılır, her düğümde
ebeveyn değerlerine karşılık gelen satırdan çekim yapılır. Çekim izi adım adım
kaydedilir ve gösterilir.

### Sembolik katman: kural tabanlı çıkarım ve üç değerli mantık

EK-4 denetim formundaki 21 soru ile yönetmelik maddelerinden türetilen 12
yapısal kural, madde referanslarıyla birlikte makine okunabilir biçimde
kodlanmıştır. İki küme farklı anlarda işler: **yapısal kurallar ruhsat
aşamasında**, **EK-4 kuralları işletme sırasında**.

Çıkarımın sonucu ikili değil üç değerlidir. Bir kural ihlal edilirse *uygun
değil*; ihlal yoksa ancak Madde 17 devredeyse *belirsiz*; ikisi de yoksa
*uygun*. Üçüncü değer bir modelleme kolaylığı değil, mevzuatın kendi
eksikliğinin karşılığıdır.

### Etmen temelli katman: yaptırım merdiveni ve Markov geçişleri

Merkezler tek tek izlenen etmenlerdir; her birinin kendi ruhsat tarihi, hizmet
sepeti, zayıf noktaları ve **EK-4 kurallarının her biri için ayrı tespit
sayacı** vardır. Bu şart: form birinci, ikinci ve üçüncü tespitte farklı
yaptırım tanımladığı için merdiven ancak sayaçlar merkez bazında tutulursa
işler, ortalamaya indirgenirse anlamını yitirir.

Uyum durumu üç kademeli bir Markov zinciri izler (iyi, orta, zayıf). Geçiş
olasılıkları o yıl ceza alınıp alınmadığına göre iki ayrı matristen okunur;
ceza alan merkez toparlanma yönünde daha yüksek olasılık taşır.

### Belirsizlik ve düzenleyici etki katmanları

Sonuçlar **Monte Carlo tekrarlarıyla** üretilir ve tek bir kestirim yerine
ortanca ile yüzde 10–90 bandı raporlanır. **Tek değişkenli duyarlılık analizi**
her parametreyi tek tek alt ve üst değerine çekip çıktıdaki değişimi ölçer;
böylece hangi sonucun hangi varsayıma bağlı olduğu görünür kalır.

Düzenleyici etki tarafında üç katman daha vardır: uyum maliyetleri, ruhsat
alamayan işletmelerin kayıt dışı faaliyet dalı ve sınırlı denetim kapasitesi.
Sonuncusu sektör büyüdükçe fiilî denetim oranının hedefin altına düşmesine yol
açar.

---

## Uyarılar

> **Bu bir öngörü değildir.** Bir aylık bir sektörün on yıllık seyrini kestirecek
> veri yoktur. Giriş oranı, talep büyümesi, uyum davranışı ve maliyet tutarları
> varsayımdır. Sonuçlar tek bir kestirim yerine tekrarların ortancası ve yüzde
> 10–90 aralığı olarak raporlanır.

> **Veri sentetiktir.** Tüm merkezler ve ziyaretçiler üretilmiştir. Gerçek kişi
> ya da kuruluş verisi kullanılmaz. `veri/ornek_kayitlar.json` gerçek başvuru
> kaydı değil, alan bilgisine dayanan kurallarla kurgulanmış bir başlangıç
> setidir ve gerçek kayıtlarla değiştirilmesi beklenir.

> **Bağlayıcı metin Resmî Gazete'dir.** Kural setleri yönetmelikten
> aktarılmıştır; hukuki bir yorum ya da danışmanlık değildir.

---

## Dosyalar

| Yol | İçerik |
|---|---|
| `index.html` | Tek dosyalık arayüz, doğrudan açılır |
| `sablon.html` · `paketle.py` | Arayüz kaynağı ve paketleyici |
| `mevzuat/ek4_denetim.json` | EK-4 denetim formunun 21 kuralı |
| `mevzuat/yapisal_kurallar.json` | Madde metinlerinden türetilen 12 kural |
| `mevzuat/belirsizlik_haritasi.json` | 14 kayıtlık belirsizlik kataloğu |
| `mevzuat/uyum_maliyeti.json` | 8 kalemlik uyum maliyeti |
| `mevzuat/hizmetler.json` | Madde 4/1-c'deki 24 hizmet |
| `mevzuat/ag_yapisi.json` | Ziyaretçi ağının yapısı |
| `mevzuat/senaryolar.json` | Beş mevzuat senaryosu |
| `veri/` | Başlangıç kayıt seti ve üreten betik |
| `web/model.js` | Bayes ağı ve veriden öğrenme |
| `web/akis.js` | Merkez üretimi, kural denetimi, eşleştirme |
| `web/analiz.js` | Uyum maliyeti ve duyarlılık analizi |
| `cekirdek/` | Çok yıllı simülasyon (Python) |
| `gorseller/` | README ekran görüntüleri |

### Geliştirme

```bash
python3 veri/uret_ornek.py   # başlangıç kayıt setini yeniden üretir
python3 calistir.py          # beş senaryoyu komut satırında koşturur
python3 onhesap.py           # projeksiyonları hesaplar
python3 paketle.py           # index.html dosyasını yeniden üretir
```

Çekirdek yalnızca standart kütüphaneye bağlıdır; kurulum gerekmez.

---

## İlgili bildiri

> Köse, G. & Köse, U. (2026). Measuring Uncertainty: An Artificial Intelligence
> Assisted Regulatory Impact Analysis of the Wellness Services Regulation and
> Health Tourism. *INNOVAHEALTH 2026 — 3rd International Congress on Innovative
> Approaches in Health Sciences*, 2–5 Eylül 2026, Girne, KKTC.

## Lisans

MIT — ayrıntı için [LICENSE](LICENSE).

<br>

---
<br>

<h1 align="center" id="english">TR-Wellness-Regulation-Sim</h1>

<p align="center">
  <strong>Main question: "Can regulatory uncertainty be measured?"</strong><br>
  An artificial intelligence assisted regulatory impact analysis tool<br>
  for Turkey's Wellness Services Regulation and health tourism.
</p>

<p align="center">
  <a href="https://gamze-kose.github.io/TR-Wellness-Regulation-Sim/"><strong>▶ Open the tool in your browser</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Bayesian%20network-learned%20from%20data-5B4DA6.svg" alt="Bayesian network">
  <img src="https://img.shields.io/badge/agent--based-simulation-177A5C.svg" alt="Agent-based simulation">
  <img src="https://img.shields.io/badge/rule--based-inference-A5382F.svg" alt="Rule-based inference">
  <img src="https://img.shields.io/badge/Monte%20Carlo-sensitivity%20analysis-555.svg" alt="Monte Carlo">
</p>

## The problem

The provisions of a newly published regulation are not always applicable on
their own. Some are deferred to secondary regulation, some concepts are left
undefined, some discretion is granted without criteria. Such uncertainties are
debated in legal texts but not measured.

Article 17 of the Wellness Services Regulation (4 July 2026, Official Gazette
33300) defers the procedures for wellness services within health tourism to the
Ministry of Health, that secondary regulation has not been issued, and **Annex 4,
the inspection instrument, contains no question on it**. A centre cannot know
whether serving a visitor resident abroad complies with the rules.

The tool turns that gap into a number. It generates synthetic wellness centres
and health tourists, matches them against rules transcribed from the regulation
and returns a **three-valued** outcome:

| | |
|---|---|
| 🟢 **Compliant** | No rule is violated; service can be provided. |
| 🟣 **Undefined** | No rule is violated, but the status is undetermined because Article 17 has set no procedures. |
| 🔴 **Non-compliant** | At least one rule is violated. |

The third state is the core of the tool. It turns the *absence* of a provision
into a measurable category, and the method transfers to other legislation.

## Methods and techniques

The tool combines symbolic and probabilistic artificial intelligence. No
component is a black box: the learned tables, the rules applied and the sampling
trace can each be inspected from the interface.

| Technique | Where | File |
|---|---|---|
| **Rule-based inference** (symbolic AI) | Twenty-one Annex 4 inspection questions and twelve structural rules derived from the articles | `web/akis.js` · `cekirdek/kural.py` |
| **Three-valued logic** | Compliant / non-compliant / undefined. Turns a regulatory gap into a measurable category | `web/akis.js` |
| **Discrete Bayesian network** (probabilistic graphical model) | Synthetic visitor generation; ancestral sampling in topological order | `web/model.js` · `cekirdek/ag.py` |
| **Dirichlet-prior parameter learning** | Conditional probability tables are estimated from the record set, not hand-written | `web/model.js` · `cekirdek/ogren.py` |
| **Agent-based simulation** | Centres are individually tracked agents with their own state, service basket and detection counters | `cekirdek/simulasyon.py` · `cekirdek/merkez.py` |
| **Markov chain** | Year-to-year transition of the compliance state; a sanctioned centre uses a different matrix | `cekirdek/simulasyon.py` |
| **Monte Carlo repetitions** | Median and 10–90 percentile band instead of a single estimate | `cekirdek/gostergeler.py` |
| **One-at-a-time sensitivity analysis** | Each parameter is moved to its lower and upper bound and the change is measured | `web/analiz.js` |
| **Design of experiments and stratified sampling** | Centre configurations come from legally distinguishable classes, not a generative model | `web/akis.js` |
| **Feedback demand dynamics** | Licence applications rise as unmet demand grows and fall as capacity accumulates | `cekirdek/simulasyon.py` |

Generation, sampling and simulation are all **reproducible**: the same
reproducibility key yields the same result, and no output depends on a language
model.

## Usage

The tool runs entirely in the browser. No server, installation or data upload
is required.

**Open it directly:** <https://gamze-kose.github.io/TR-Wellness-Regulation-Sim/>

**Or download:** grab `index.html` and double-click it. All resources are
embedded in the file; it works without an internet connection.

```bash
git clone https://github.com/gamze-kose/TR-Wellness-Regulation-Sim.git
```

The interface is fully bilingual — every label, rule text, service name and
uncertainty entry exists in both languages. The screenshots below show the
English interface; use the button at the top right to switch.

---

## How it works

Five steps, each consuming the output of the previous one.

### 01 · Data and model

The record set the visitor model learns from. There are no hand-written
probability tables; they are learned from these records. Records can be added
and deleted, and **every change retrains the model**, with the distributions on
the right updating immediately. The starter set of 240 records is not real
intake data and is expected to be replaced.

![Record set and model training](gorseller/en-01-data-and-model.png)

The learned tables are inspectable, and each row reports how many observations
it rests on; rows below five are flagged, because a probability learned from
three records is not a probability. Individual profiles can be drawn from the
model, with the draw traced node by node in topological order.

### 02 · Centres

Applications first pass the **structural rules**: closed area, room count,
institutional permits and responsible-manager conditions. The grounds for
refusal are listed with their article references — below, the most frequent is
the responsible manager's exclusivity requirement (11/6), followed by the
three-year practice requirement (11/4-c) and the sixty-year condition for
specialist physicians (10/6).

Licensed centres are then assessed against the **Annex 4 inspection rules**.
Each card is a centre, showing its setting, whether it is a centre or a unit,
and how many violations it carries.

![Grounds for refusal and generated centres](gorseller/en-02-centres.png)

A compliance cost layer prices the obligations the regulation imposes — closed
area, emergency room, full-time responsible manager, hospital cooperation,
information system, and the revenue lost to the prohibition on product sales —
and shows which business models remain viable. Fixed obligations affect small
operators disproportionately.

### 03 · Visitors

Synthetic health tourists are drawn from the trained model and matched against
the centres one by one. A person in convalescence is ineligible under Article
10(8)(d); for those resident abroad, Article 17 comes into play.

Selecting a scenario opens a detail panel: the status of Article 17, the year it
comes into force, the acceptance rate afterwards, the inspection rate and
whether units fall within scope. Below is **S3 — Permissive with intensive
inspection**: the regulation is in force from 2028 and the annual inspection
rate nearly doubles to 68%. Because Article 17 is settled in this scenario, the
purple **Undefined** band reads 0%.

![Matching under scenario S3](gorseller/en-03-visitors.png)

### 04 · Results

The provision determining the outcome is recorded for every visitor. In the run
below, 81% were served, 11% found the centres offering their service at
capacity, and 8% were ineligible under Article 10(8)(d). The breakdown by
residence, age group and service sought shows where the shortfall concentrates —
thermal and balneology demand is met noticeably less often than the rest.

![Results and segment breakdown](gorseller/en-04-results.png)

A sensitivity analysis moves each free parameter to its lower and upper bound
and measures the change in the outcome, and a ten-year projection tracks eight
indicators across the five scenarios, including unlicensed operation and the
actual inspection rate.

### 05 · Uncertainty

A catalogue of **fourteen entries across six types**, three bearing directly on
health tourism, produced by reading the regulation article by article. Each
entry marks a gap that prevents a provision from being applied on its own, and
the list can be filtered by type.

Article 17 is only the first line. It is followed by the mismatch between the
heading and the text of the same article, the open-ended service list of Article
4(1)(c), the undefined notion of convalescence in Article 10(8)(d) — a
prohibition with severe sanctions resting on a concept without criteria — and
the absence of any criterion for space appropriate to the service in Article
10(4).

![Uncertainties in the regulation](gorseller/en-05-uncertainty.png)

---

## Findings

The figures come from the tool's default settings and are not validated against
real data. What matters is not the absolute values but the differences between
scenarios and the ranking of sensitivities.

- **Fourteen uncertainty entries** were identified, three bearing directly on
  health tourism; the most frequent type is discretion without criteria.
- **No inspection question** addresses the structural definitions of the
  regulation.
- Where the deferred regulation is never issued, the share of visitors resident
  abroad obtaining service falls to **46%** by the tenth year and **11%** of
  demand remains undefined; where it is issued in 2028, the share rises to
  **86%**.
- Compliance with licensing conditions **almost wholly determines licence
  refusal** yet barely affects access to services, which is governed by capacity.
- In the compliance cost layer, **fixed obligations affect small operators
  disproportionately**; units in detached buildings fall below the viability
  threshold.

## Method

**Visitor model.** The structure of the network is set by domain expertise. The
variables come from the individual planning criteria of Article 10(1) — age,
general health status, existing risk factors and lifestyle — extended with
convalescence under Article 10(8)(d) and residence under Article 17. The
probability tables are learned from the record set. A small uniform Dirichlet
prior is added to the counts, solely so that rows with no observations are not
left undefined; its influence vanishes as records accumulate.

**Rule engine.** Twenty-one inspection questions from Annex 4 and twelve
structural rules derived from the articles. The two sets act at different
moments: structural rules at licensing, Annex 4 rules during operation.

**Sanction ladder.** Annex 4 defines a distinct sanction for the first, second
and third detection of each rule. Centres are tracked individually with their
own detection counters; the ladder can only operate this way and loses its
meaning if reduced to an average.

**Regulatory impact layers.** Compliance costs, an unlicensed operation branch
for refused applications, limited inspection capacity, and a sensitivity
analysis over every parameter.

## Caveats

> **This is not a forecast.** There is no data to project a sector one month old
> across ten years. Entry rate, demand growth, compliance behaviour and cost
> figures are assumptions. Results are reported as the median and the 10–90
> percentile range across repetitions rather than as a single estimate.

> **The data is synthetic.** All centres and visitors are generated. No real
> person or institution data is used. `veri/ornek_kayitlar.json` is not real
> intake data but a starter set constructed from domain rules, expected to be
> replaced with real records.

> **The binding text is the Official Gazette.** The rule sets are transcriptions
> of the regulation and constitute neither legal interpretation nor advice.

## Development

```bash
python3 veri/uret_ornek.py   # regenerate the starter record set
python3 calistir.py          # run the five scenarios on the command line
python3 onhesap.py           # compute the projections
python3 paketle.py           # rebuild index.html
```

The core depends only on the standard library; no installation is needed.

## Related paper

> Köse, G. & Köse, U. (2026). Measuring Uncertainty: An Artificial Intelligence
> Assisted Regulatory Impact Analysis of the Wellness Services Regulation and
> Health Tourism. *INNOVAHEALTH 2026 — 3rd International Congress on Innovative
> Approaches in Health Sciences*, 2–5 September 2026, Kyrenia, TRNC.

## License

MIT — see [LICENSE](LICENSE).
