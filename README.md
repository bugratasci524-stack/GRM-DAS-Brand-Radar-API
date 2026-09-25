# BREX — Brand Radar API → Excel Pipeline

Ahrefs Brand Radar API'sinden marka ve rakiplerin AI görünürlük verisini (mention, citation,
impression, share of voice) çekip Brand Radar "AI visibility / Platforms" export'uyla aynı
yapıda bir Excel dosyasında biriktirir.

Kapsam, endpoint eşlemesi, kısıtlar ve yol haritası için: [plan.md](plan.md)

## Kurulum

Python 3.11+ gerekir.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` dosyasını açıp doldurun:

```
AHREFS_API_KEY=<Ahrefs API key>
BREX_REPORT_ID=<rapor id>
```

- `.env` git'e girmez (`.gitignore`). Key'i koda veya `.env.example`'a yazmayın.
- `BREX_REPORT_ID` rapor URL'inden alınır: `app.ahrefs.com/brand-radar/reports/<report_id>/...`
  Bilmiyorsanız bağlantı testi hesaptaki raporları listeler.

## Bağlantı testi

Repo klasöründen çalıştırın:

```powershell
.\.venv\Scripts\python -m scripts.auth_test
```

`management/brand-radar-reports` endpoint'ini çağırır (unit tüketmez) ve hesaptaki Brand Radar
raporlarını JSON olarak basar.

## Yapı

```
brex/
  config.py      .env okuma, sabitler (prompts="custom")
  client.py      Ahrefs API istemcisi: Bearer auth, 429'da exponential backoff
scripts/
  auth_test.py   bağlantı testi
plan.md          proje planı
```

## Notlar

- Tüm Brand Radar veri çağrıları POST'tur (`citations-overview`'ın GET versiyonu yok).
- `prompts="custom"` kodda sabittir; yalnızca custom prompt verisi dönen istekler unit tüketmez.
- `main` üzerinde doğrudan değişiklik yapılmaz, her adım kendi branch'inde yürür.
- Çıktı dosyaları (`*.xlsx`, `*.csv`, `outputs/`) marka verisi içerdiği için git'e girmez.
