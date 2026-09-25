# BREX — Brand Radar API → Excel Pipeline

Ahrefs Brand Radar API'sinden AI görünürlük verisini çekip, Brand Radar arayüzünün
"AI visibility / Platforms" export'uyla aynı yapıda bir Excel dosyasında biriktirme projesi.

**Repo:** `GRM-DAS-Brand-Radar-Api`
**Proje kısaltması:** `BREX`
**Branch:** `main` üzerinde doğrudan değişiklik yapılmaz; her adım kendi branch'inde
yürür. Branch adı adım başlarken belirlenir (ör. `dev/BREX-100-setup`).
**Çıktı dosyası kalıbı:** `BREX_<YYYY-MM-DD>.xlsx`

---

## 1. Amaç ve kapsam

**Amaç:** Marka ve rakiplerin LLM'lerdeki görünürlüğünü (mention, citation, impression,
share of voice) periyodik olarak çekip tek bir Excel dosyasında takip etmek.

**Kapsam:** Brand Radar API'sinin yalnızca **Overview** grubu kullanılacak.

Kapsam dışı:
- AI visibility grubu (`ai-responses`, `cited-pages`, `cited-domains`) — prompt/sayfa
  bazlı ham detay, bu projede gerekmiyor
- Overview history grubu — tarih ekseninde kırılıyor, hedeflenen tablo yapısına uymuyor
  (gerekçe: bkz. §6)

---

## 2. Ön koşullar

Kod yazmadan önce tamamlanması gerekenler:

| # | Ön koşul | Not |
|---|---|---|
| 1 | Ahrefs API key | API tam erişimi Enterprise planlarda; diğer planlarda sınırlı sayıda ücretsiz test sorgusu var |
| 2 | Brand Radar raporu kurulu | Promptlar, tag'ler, marka/rakip seti, ülke arayüzde tanımlı olmalı |
| 3 | `report_id` | Rapor URL'inden alınıyor: `app.ahrefs.com/brand-radar/reports/#report_id#/...` |
| 4 | Marka adı listesi | Yazım varyantlarıyla (ör. `özka` / `ozka`) — mentions ve SoV için |
| 5 | Domain listesi | Her marka için doğrulanmış domain — citations için (bkz. §5) |
| 6 | Custom prompt seti | Takip edilecek sorular, arayüzde yazılmış ve etiketlenmiş |

**Kritik:** 1. ve 2. maddeler netleşmeden kod tarafına geçilmemeli. API sadece
arayüzdeki kurulumu okuyor; kurulum yoksa okunacak veri de yok.

---

## 3. Çıktı formatı

Hedef Excel yapısı (referans dosya: Brand Radar Platforms export'u):

```
satır 1:  |        | Mentions                                   | Citations ... | AI Share of Voice
satır 2:  Platform | Brand | Total | Only Brand | With Others | Others Only | ...
satır 3+: All platforms | lassa | 4056 | 1239 | 2817 | 16445 | ...
```

- 10 platform × N marka satır
- 3 metrik bloku × 4 alt kolon + 1 SoV kolonu = 15 kolon
- Doğrulama kuralı: her blokta `Total = Only Brand + With Others`
- Her çalıştırma dosyaya **tarih adlı yeni bir sheet** olarak yazılır (format bozulmadan
  geçmiş birikir)

---

## 4. Endpoint eşlemesi

Tüm çağrılar **POST**. Gerekçe: marka tanımı iç içe nesne (`url_groups` → `target` +
`scope`), query string'e sığmıyor; ayrıca `citations-overview`'ın GET versiyonu yok.

| Excel kolonu | Endpoint | API alanı |
|---|---|---|
| Mentions / Total | `mentions-overview` | `total` |
| Mentions / Only Brand | `mentions-overview` | `only_target_brand` |
| Mentions / With Others | `mentions-overview` | `target_and_competitors_brands` |
| Mentions / Others Only | `mentions-overview` | `only_competitors_brands` |
| Citations / … | `citations-overview` | aynı 4 alan |
| Impressions / … | `impressions-overview` | aynı 4 alan |
| AI Share of Voice | `sov-overview` | `share_of_voice` |

Base URL: `https://api.ahrefs.com/v3/brand-radar`

Kullanılmayan alan: `no_tracked_brands` — yalnızca `market` parametresi verildiğinde
dolu geliyor, export'ta karşılığı yok.

---

## 5. Marka tanımı — iki farklı liste

Endpoint'e göre marka farklı şekilde tanımlanıyor:

- **Mentions / SoV** → marka **adı** ile eşleşiyor → `{"names": ["lassa"]}`
- **Citations** → **URL** ile eşleşiyor → `{"url_groups": [{"target": "lassa.com.tr", "scope": "subdomains"}]}`

`citations-overview` dokümantasyonu bunu zorunlu kılıyor: her marka en az bir
`url_groups` içermeli, yalnızca `names`'ten oluşan kayıt desteklenmiyor.

**scope seçenekleri:** `url` | `path` | `domain` | `subdomains`
→ Tüm markalara **aynı** scope verilmeli (`subdomains` öneriliyor), aksi halde biri
daha geniş küme sayar ve karşılaştırma bozulur.

**Sessiz hata riski:** Yanlış/eksik domain hata döndürmez, o markanın citation değeri
sıfır gelir. Liste kurulurken her domain tek tek doğrulanmalı.

---

## 6. İstek mantığı

### Boyutlar

Tek istekte hangi boyut çoğaltılabilir:

| Boyut | Tek istekte çoklu? |
|---|---|
| Marka | Evet — `brands` dizisi, dönüşte marka başına satır |
| Platform | **Hayır** — birden fazla `data_source` yazılırsa toplanır, kırılım gelmez |
| Tag | **Hayır** — `tags_filter` bir filtre, group-by değil |
| Metrik | **Hayır** — 4 ayrı endpoint |

→ Çağrı sayısı = platform × tag × metrik

### Platform → data_source eşlemesi

| Excel etiketi | `data_source` |
|---|---|
| All platforms | hepsi birlikte |
| AIO (prompts) | `google_ai_overviews` |
| AIM (prompts) | `google_ai_mode` |
| ChatGPT | `chatgpt` |
| Gemini | `gemini` |
| Perplexity | `perplexity` |
| Copilot | `copilot` |
| Grok | `grok` |
| AIO (search queries) | `google_ai_overviews_keywords` |
| AIM (search queries) | `google_ai_mode_keywords` |

`*_keywords` modelleri prompt yerine Google arama sorgularından türetilen AI Overviews /
AI Mode görünürlüğünü raporluyor.

### brands / competitors rotasyonu

Tablodaki her satır ayrı bir perspektif: o satırın markası `brands` (target), kalan
markalar `competitors`. Dolayısıyla:

- `only_target_brand` → sadece target'ın geçtiği cevaplar
- `target_and_competitors_brands` → target + rakip birlikte
- `only_competitors_brands` → sadece rakipler, target yok

**Sonuç:** Kolonlar markalar arası toplanamaz. "Others Only" kolonunun toplamı
anlamsızdır. Markaya sunulurken bu belirtilmeli.

### ⚠️ Doğrulanacak nokta

Dokümantasyon `brand` alanı için "senin markan ya da istekte verilen bir rakip" diyor,
yani tek çağrıda tüm markalar `brands`'e konursa marka başına satır dönebilir.
Ancak her satırın 4'lü kırılımının **hangi perspektiften** hesaplandığı dokümantasyondan
net çıkmıyor.

→ **İlk iş:** Tek platformda (ör. ChatGPT) iki yöntem karşılaştırılacak:
  - (a) tek çağrı, tüm markalar `brands` içinde
  - (b) rotasyon, her markaya ayrı çağrı

Sayılar tutuyorsa (a) kullanılır → ~40 istek. Tutmuyorsa (b) → ~360 istek.

---

## 7. Maliyet ve limitler

- `prompts: "custom"` → yalnızca custom prompt verisi dönen istekler **unit tüketmiyor**
- `prompts` belirtilmezse hem custom hem Ahrefs prompt verisi gelir → unit yakar
- **Bu parametre kodda sabitlenmeli, opsiyonel bırakılmamalı**
- Tüketilen unit'ler iade edilmiyor
- Kalan limit: Subscription Information endpoint'inden takip edilebilir
- `management/brand-radar-reports` unit tüketmiyor → ilk bağlantı testi bununla yapılmalı

---

## 8. Bilinen kısıtlar ve tuzaklar

1. **Overview'da tarih parametresi yok.** Anlık fotoğraf döner. Trend için her
   çalıştırma ayrı sheet olarak saklanır, karşılaştırma Excel tarafında yapılır.
2. **Rakip seti değişirse geçmişle karşılaştırma bozulur** — özellikle SoV ve
   "Others Only". Set değiştirilirse tarih ve değişiklik dosyaya not düşülmeli.
3. **`search_volume_type` 30 Eylül 2026'da kaldırılıyor**, tüm istekler yeni AI adjusted
   volume'a geçiyor. Impressions ve SoV hacim bağlı → o tarihte seride kırılma olacak,
   dosyaya not düşülmeli.
4. **`report_id` + ayrıca `country`/filtre gönderilirse**, gönderilen değer rapordakini
   ezer. Bilinçli değilse bu alanlar boş bırakılmalı.
5. **Tag'ler MECE değil** — bir prompt birden fazla tag taşıyabilir, tag toplamları genel
   toplamı aşabilir. Raporda belirtilmeli.
6. **Türkçe karakter / CSV ayracı** — çıktı CSV olarak açılacaksa UTF-8 ve ayraç ayarı
   kontrol edilmeli.

---

## 9. Yol haritası

| Adım | Branch | İş | Bitti sayılır |
|---|---|---|---|
| 1 | `dev/BREX-100-setup` | Kurulum + bağlantı testi: Ahrefs plan durumu, API key, `.env`; `management/brand-radar-reports` ile bağlantı testi, `report_id` al | Rapor listesi API'den dönüyor |
| 2 | adım başında belirlenecek | Marka adı + domain listesini doğrula ve sabitle; §6'daki rotasyon testi ve yöntem kararı | Marka/domain listesi sabit, (a)/(b) yöntemi seçilmiş |
| 3 | adım başında belirlenecek | Veri çekme + Excel: 4 endpoint, önce ChatGPT sonra tüm platformlar; `Total = Only + With Others` doğrulaması | Tarih adlı sheet §3 formatında yazılıyor |
| 4 | adım başında belirlenecek | Zamanlama (cron / task scheduler) ve hata bildirimi | Otomatik çalışma + hata bildirimi aktif |
| (5) | gerekirse belirlenecek | *Opsiyonel:* tag kırılımı. Çağrı sayısını tag sayısıyla çarpar; karar verilirse 3. adımın üzerine eklenir | — |

---

## 10. Teknik notlar

**Bağımlılıklar:** `requests`, `pandas`, `openpyxl`, `python-dotenv`
(+ opsiyonel `tenacity` — 429 retry)

**Auth:** Her istekte `Authorization: Bearer <API_KEY>` header'ı.
Key koda gömülmeyecek, `.env` dosyasında tutulacak, `.env` `.gitignore`'a eklenecek.

**Hata yönetimi:** Endpoint'ler 400/401/403/429/500 dönebiliyor.
429'da exponential backoff, diğerlerinde log + durdurma.

**Idempotency:** Aynı tarih iki kez çalıştırılırsa sheet üzerine yazılır, çift kayıt olmaz.
