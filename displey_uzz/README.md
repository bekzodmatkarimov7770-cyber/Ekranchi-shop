# Displey_Uzz

Ekranchi_Bola do'konining kloni. Bu do'kon telefon displeylarini **donalab** sotadi: optom narx, 50 talik chegara va "Optom / Chakana" tanlovi yo'q.

## Ekranchi'dan farqi

| | Ekranchi_Bola | Displey_Uzz |
|---|---|---|
| Narx | chakana + optom (50+ dona) | faqat dona narx |
| Bot ro'yxatdan o'tish | raqam, keyin "Optom / Chakana" tanlash | faqat raqam |
| Do'kon sahifasi | optom hisoblagich lentasi | lenta yo'q, "1 tadan ham sotamiz" |
| Admin panel | ikkala narx, "Optom va chakana" hisoboti | bitta narx (dona) |
| Hammaga xabar (/hammaga) | Hammaga / Optomchilarga / Donachilarga | Hammaga |
| Baza kalitlari | `users`, `catalog`... | `du:users`, `du:catalog`... (`REDIS_PREFIX`) |

Android ilova (`android/`) va nakladnoy bot (`nakladnoy/`) klonga kiritilmagan.

## Vercel'ga joylash

1. Vercel'da yangi loyiha oching, shu repozitoriyni tanlang va **Root Directory** ni `displey_uzz` qiling.
2. Loyiha: `displey-uzz`, manzil: `displey-uz.vercel.app`. Domen o'zgarsa, `PUBLIC_URL`, `WEB_APP_URL` ni va `market.html` dagi manzilni almashtiring. Framework: **Other** (Flask emas, aks holda sahifalar ochilmaydi).
3. @BotFather'da **yangi bot** oching (masalan `@displey_uzz_bot`).
4. Environment Variables:
   - `BOT_TOKEN`: yangi botning tokeni
   - `ADMIN_ID`: adminlarning Telegram ID raqamlari, vergul bilan (masalan `111,222,333`). Yangi buyurtma hammasiga boradi; birinchisi asosiy admin
   - `WEBHOOK_SECRET`: uzun tasodifiy satr (A-Z a-z 0-9 _ -)
   - `ADMIN_USERNAME`: (ixtiyoriy) admin @username
   - `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`: doimiy baza (Vercel Marketplace > Upstash)
   - `REDIS_PREFIX`: (ixtiyoriy) standart `du:`. Ekranchi bilan bitta bazadan foydalansangiz ham ma'lumotlar aralashmaydi.
5. Deploydan keyin webhookni ulang: `https://displey-uz.vercel.app/api/index?ulash=1&key=<WEBHOOK_SECRET>`

Katalog `catalog.seed.json` dan olinadi (Ekranchi'dagi dona narxlar). Narx va qoldiqni keyin admin paneldan (botga `/panel`) o'zgartirasiz.

## Testlar

```bash
cd displey_uzz && python -m pytest -q && node tests/check_js.mjs
```
