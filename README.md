# Elmalılı Türkçe Meal — arşiv restorasyonu

Erişime kapanmış olan `enfal.de/m_elmalili_index.htm` sitesinin, Internet Archive
anlık görüntüsünden yeniden ayağa kaldırılmış hâli. Elmalılı Muhammed Hamdi
Yazır'ın "Hak Dini Kur'an Dili" eserine dayanan Türkçe mealin 114 sureden oluşan
statik HTML sunumu.

Bu bir **koruma/restorasyon** çalışmasıdır, yeniden tasarım değildir. Sitenin
sadeliği, renkleri, tipografisi ve sayfa yapısı bilinçli olarak korunmuştur.

## Kullanılan anlık görüntü

- Kaynak: <http://enfal.de/m_elmalili_index.htm> (şu an erişime kapalı)
- Snapshot: <https://web.archive.org/web/20240919080311/http://enfal.de/m_elmalili_index.htm>
- Dizin sayfası 19 Eylül 2024 tarihli capture'dan; sure sayfaları Wayback'in aynı
  URL için verdiği 28 Eylül 2022 tarihli capture'lardan alınmıştır.
- İndirme tarihi: 14 Ağustos 2026

## Orijinal sitenin yapısı

Site tamamen statik HTML'dir. JavaScript, harici CSS dosyası, font dosyası,
form, arama kutusu veya sunucu tarafı hiçbir bileşen yoktur.

```
m_elmalili_index.htm      114 sureye bağlantı veren dizin sayfası
melmalili/<sure>.htm      her sure için bir dosya (114 adet)
ustb.gif, altb.gif        başlık/alt şerit görselleri
kucuk_kuran1.jpg, kuran1.jpg, bismillah.jpg, kabe_resim1.jpg
```

Tespit edilen özellikler:

| | |
|---|---|
| Arka plan | `#1F57A1` (koyu mavi) |
| Metin | dizinde `#000000`, sure sayfalarında `#FFFFFF` |
| Başlıklar | `#33FFFF` (açık camgöbeği), Verdana `size="5"` / `size="4"` |
| Gövde metni | Verdana, Arial, Helvetica, sans-serif — `size="2"` |
| Bağlantılar | beyaz, altı çizgisiz; `:hover` durumunda kırmızı (sayfa içi `<style>`) |
| Dizin tablosu | genişlik `95%`, `border="1"`, `bordercolor="#CCCCCC"`, 4 sütun |
| Ayet metni | `<blockquote>` içinde, her ayet `<p>` + `<a name="N">` çıpası |
| Karakter seti | orijinalde `windows-1254` / `iso-8859-9` |
| Yön | tamamen LTR — arşivlenmiş sayfalarda Arapça metin yoktur |

**Navigasyon:** Dizin sayfası 114 surenin tamamına bağlantı verir. Sure
sayfalarında **hiçbir bağlantı yoktur** — ileri/geri, dizine dönüş bağlantısı
orijinalinde de bulunmamaktadır. Bu davranış olduğu gibi korunmuştur; sonradan
navigasyon eklenmemiştir.

## Restorasyon nasıl yapıldı

1. `tools/fetch_archive.sh` — dizin sayfasını ve 114 sure sayfasını Wayback
   Machine'den indirir; ham hâlleriyle `archive_original/` altında saklanır
   (kanıt kopyası, hiç değiştirilmez). Görseller bilinçli olarak indirilmez.
   `web.archive.org` istekleri sınırladığı için indirme yavaş tempoludur ve
   eksik kalanları birkaç geçişte tamamlar.
2. `tools/restore.py` — `archive_original/` içeriğinden yayımlanan sayfaları
   (deponun kökünde) üretir.
   Sayfa başına yapılan **tek** müdahaleler:
   - Wayback Machine'in enjekte ettiği `<script>`/`<link>` blokları ve sondaki
     arşiv yorumları silinir,
   - mutlak wayback URL'leri sitenin kendi göreli yollarına çevrilir,
   - baytlar `windows-1254`'ten UTF-8'e dönüştürülür ve `<meta charset>` buna
     göre güncellenir,
   - *(talep üzerine)* görselleri taşıyan üç başlık tablosu kaldırılır,
   - *(talep üzerine)* her sayfanın sağ altına, bu README'ye giden bir
     "Kaynak" bağlantısı eklenir,
   - arama motorları için `lang`, canonical ve `<meta description>` etiketleri
     eklenir (hiçbiri görünümü değiştirmez).

   Meal metnine, imlâsına, noktalama işaretlerine, etiket yapısına ve boşluklara
   dokunulmamıştır.

Restorasyonu yeniden üretmek için:

```sh
./tools/fetch_archive.sh     # arşivden indirir (zaten indirilmişse atlar)
python3 tools/restore.py     # sayfaları yeniden üretir
python3 tools/verify.py      # metnin arşivle birebir aynı olduğunu doğrular
```

## Depo düzeni

Restore edilen sayfalar **deponun kökünde** durur; böylece GitHub Pages hiçbir
derleme adımı olmadan doğrudan yayımlayabilir.

```
index.html                yayımlanan dizin sayfası
m_elmalili_index.htm      aynı sayfanın orijinal adıyla kopyası
melmalili/<sure>.htm      114 sure sayfası
.nojekyll                 GitHub Pages'in Jekyll işlemesini atlaması için
README.md
sitemap.xml               arama motorları için sayfa listesi (115 adres)
robots.txt                tarama kuralları + sitemap adresi
links.txt                 114 sure sayfasının listesi
tools/                    indirme, üretme ve doğrulama betikleri
archive_original/         arşivden inen ham dosyalar (kanıt kopyası)
```

## Yerelde çalıştırma

`index.html` dosyasını doğrudan tarayıcıda açmak yeterlidir. Ya da:

```sh
python3 -m http.server 8000
# http://localhost:8000
```

## Yayına alma

Derleme adımı, bağımlılık veya çalışma zamanı gereksinimi yoktur; dosyaları
herhangi bir statik sunucuya kopyalamak yeterlidir (Netlify, Cloudflare Pages,
nginx, Apache…).

**GitHub Pages ile:** depo ayarlarında *Settings → Pages → Build and deployment*
altında **Source: Deploy from a branch**, **Branch: `main`**, **klasör: `/ (root)`**
seçilip kaydedilir. Bir iki dakika içinde site şu adreste yayına girer:

```
https://elmalili-meal.github.io/kuran/
```

Not: GitHub Pages tüm depoyu yayımlar; `archive_original/` ve `tools/` de bu
adres üzerinden erişilebilir olur. Sakıncası yoktur — ikisi de zaten deponun
herkese açık içeriğidir — ancak yalnızca site dosyalarının yayımlanması
istenirse bu iki klasörün ayrı bir dala taşınması gerekir.

`index.html` ile `m_elmalili_index.htm` aynı içeriktedir: ilki sunucuların kök
dizin için varsayılan olarak aradığı ad, ikincisi orijinal dosya adıdır (eski
bağlantılar bozulmasın diye korunmuştur).

## Arama motorlarına kaydetme (Google)

Site indekslenmeye hazırdır: her sayfanın kendine ait bir `<title>`'ı,
kendine ait bir `<meta name="description">` etiketi ve bir canonical adresi
vardır; `sitemap.xml` 115 adresin tamamını listeler; `robots.txt` taramaya izin
verir. Görsel tasarımda hiçbir değişiklik yapılmamıştır.

Yayına aldıktan sonra Google Search Console'da yapılacaklar:

1. <https://search.google.com/search-console> adresinde **URL prefix** türünde
   bir mülk oluşturun: `https://elmalili-meal.github.io/kuran/`
2. Doğrulama için **HTML file** yöntemini seçin. Google'ın verdiği
   `google<...>.html` dosyasını deponun köküne ekleyip `main` dalına gönderin.
   (Bu dosya `tools/restore.py` tarafından üretilmediği için silinmez.)
   Alternatif olarak `<meta name="google-site-verification" ...>` yöntemi de
   kullanılabilir; ancak bu etiketin `restore.py` içine eklenmesi gerekir, aksi
   hâlde sayfalar her yeniden üretildiğinde kaybolur.
3. Doğrulama tamamlanınca *Sitemaps* bölümüne `sitemap.xml` adresini girin.
4. Tek tek sayfaları hızlandırmak için *URL Inspection → Request indexing*
   kullanılabilir.

`BASE_URL` değeri `tools/restore.py` içinde tanımlıdır. Site başka bir adrese
taşınırsa yalnızca orayı değiştirip `python3 tools/restore.py` çalıştırmak
yeterlidir; canonical etiketleri, `sitemap.xml` ve `robots.txt` buna göre
yeniden üretilir.

## Bu restorasyonda yapılan bilinçli sapmalar

Aşağıdakiler dışında sayfalar arşivdeki hâliyle aynıdır:

| Sapma | Gerekçe |
|---|---|
| Görseller çıkarıldı (`ustb.gif`, `altb.gif`, `kucuk_kuran1.jpg`, `kuran1.jpg`, `bismillah.jpg`, `kabe_resim1.jpg`) ve bunları taşıyan üç başlık tablosu silindi | Talep üzerine sade metin sürümü |
| Her sayfanın sağ altına README'ye giden "Kaynak" bağlantısı eklendi | Talep üzerine; provenansın sayfadan tek tıkla görülebilmesi için |
| `<html lang="tr">`, `<link rel="canonical">` ve sayfaya özel `<meta name="description">` eklendi | Arama motoru indekslemesi için. Üçü de görünmez etiketlerdir; sayfanın görünümünde hiçbir değişiklik yapmazlar. |
| `sitemap.xml`, `robots.txt` ve `.nojekyll` dosyaları eklendi | Arama motoru indekslemesi ve GitHub Pages için |
| `<meta name="description">` ve `<meta name="keywords">` sadeleştirildi | Talep üzerine. Orijinalleri 2000'lerin başına ait, anahtar kelime yığını hâlindeki uzun etiketlerdi. |
| Tüm `<script>` blokları kaldırıldı | Sayfalardaki tek JavaScript, 7 sure sayfasında kalmış "arkadaşına tavsiye et" formu doğrulama kodudur. Bu formun `<form>` etiketi hiçbir sayfada mevcut değildir — HTTrack kopyalamasından artakalan, hiçbir işlevi olmayan ölü koddur. |
| Karakter seti UTF-8'e çevrildi | `windows-1254` bayt dizisi, `charset=utf-8` başlığı gönderen modern statik sunucularda bozuk görünüyor. Görünen metin birebir aynıdır. |
| `index.html` kopyası eklendi | Statik sunucuların kök dizin varsayılanı |

Altı görsel bu depoda **hiç bulunmamaktadır** — sayfalarda kullanılmadıkları
gibi `archive_original/` altında da saklanmamaktadır. Kullanılmayan, üstelik
hakları belirsiz olan dosyaları yayımlamamak için bilinçli bir tercihtir.
Gerekirse arşivdeki asıllarına şu adresten ulaşılabilir:
`https://web.archive.org/web/20240919080311im_/http://enfal.de/<dosya-adı>`

## Hangi dosya nereden geldi

- **Arşivden birebir alınan:** tüm meal metni, sayfa başlıkları, `<meta>`
  etiketleri, tablo/`blockquote` yapısı, renkler, font tanımları, ayet
  çıpaları (`<a name="N">`), dizin tablosundaki sure adları ve sıralaması.
- **Bu restorasyonda yazılan:** `README.md`, `tools/fetch_archive.sh`,
  `tools/restore.py`, `tools/verify.py`, `links.txt`, `sitemap.xml`,
  `robots.txt`, sayfaların sağ altındaki "Kaynak" bağlantısı ve
  arama motorlarına yönelik görünmez etiketler.
- **Depoya hiç alınmayan:** 6 görsel (ve onları taşıyan başlık tabloları);
  ayrıca Wayback Machine'in enjekte ettiği script/stil blokları ile orijinal
  kopyalamadan artakalan işlevsiz "tavsiye" JavaScript kodu.

## Provenans ve telif hakkı

Bunlar birbirinden ayrı şeylerdir ve tek bir "kamu malı" etiketi altında
toplanamaz:

- **Elmalılı'nın özgün eseri.** Muhammed Hamdi Yazır 1942'de vefat etmiştir.
  Türkiye'de koruma süresi ölümden itibaren 70 yıl olduğundan özgün eser
  2013 başı itibarıyla kamuya mal olmuştur.
- **Metnin bu sürümü.** Arşivlenen sayfalardaki metin, Elmalılı'nın 1930'lardaki
  özgün dili değil, sadeleştirilmiş bir meal metnidir. Sayfaların `<meta
  name="description">` etiketi "T.C. Diyanet İşleri Başkanlığınca ve Merhum
  Elmalılı … hazırlanan Türkçe meali" ifadesini kullanmaktadır. Sadeleştirme /
  redaksiyon işi, özgün eserden ayrı bir emek ürünüdür ve **kimin yaptığı,
  hangi baskıya dayandığı ve telif durumunun ne olduğu bu arşivden tespit
  edilememiştir.** Bu, bu projedeki en önemli belirsizliktir.
- **Sitenin HTML/CSS'i.** Sayfalardaki HTML yorumu şunu göstermektedir:
  `Mirrored from www.kuranikerim.com by HTTrack Website Copier/3.x [XR,YP'2001]`
  — yani `enfal.de` kendisi de `kuranikerim.com` sitesinin HTTrack ile alınmış
  bir kopyasıdır. Sayfalarda kalan `tppabs` öznitelikleri de bu kopyalamanın
  izidir. Dolayısıyla sayfa düzeninin asıl sahibi büyük olasılıkla
  `kuranikerim.com`'dur. Her iki sitede de telif bildirimi veya lisans ifadesi
  bulunmamaktadır.
- **Görseller.** Orijinal sitedeki altı görselin kaynağı ve hak sahibi
  bilinmemektedir. Tam olarak bu belirsizlik nedeniyle bu depoya hiç
  alınmamışlardır.
- **Editoryal malzeme.** Arşivlenen sayfalarda önsöz, dipnot veya açıklama
  metni bulunmamaktadır; yalnızca meal metni vardır.

Bu depo, erişilemez hâle gelmiş bir kaynağın korunması amacıyla hazırlanmıştır.
Yeniden yayımlamayı düşünüyorsanız, özellikle sadeleştirilmiş metnin telif
durumunun netleştirilmesi tavsiye edilir.

## Telif hakkı itirazı / iletişim

Bu depodaki herhangi bir içerik üzerinde hak sahibi olduğunuzu düşünüyor ve/veya
yayımlanmasına itiraz ediyorsanız, lütfen bir **GitHub Issue** açarak bildirin:

<https://github.com/elmalili-meal/kuran/issues>

Bildirimde hangi dosya veya bölümden söz ettiğinizi belirtmeniz yeterlidir;
haklı bulunan talepler üzerine ilgili içerik gecikmeden kaldırılacaktır.

Bu çalışma ticari değildir; erişime kapanmış bir kaynağın kaybolmaması amacıyla
hazırlanmıştır. Hak ihlali iddiası varsa çözüm yolu içeriğin kaldırılmasıdır.
