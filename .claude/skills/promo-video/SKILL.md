---
name: promo-video
description: Ekranchi_Bola bot/do'koni uchun reklama videosini Remotion'da yasash (vertikal 1080x1920, 60 fps, diktor ovozi, tovush effektlari, motion animatsiyalar). "Video yasa", "reklama videosi", "promo", "Reels/TikTok uchun video", "videoni yangila" deyilganda ishlating.
---

# Ekranchi promo video (Remotion)

Loyiha: `promo-video/`. Telefon ichidagi do'kon `market.html` ning aniq nusxasi: o'sha CSS, klasslar va `data.js` dagi haqiqiy modellar. Har bir harakat (barmoq, yozish, lenta, sheetlar, kamera) **kadrdan hisoblanadi**, shuning uchun video 60 fps bo'lsa ham silliq chiqadi. Brauzerni jonli yozib olmang: u sekundiga taxminan 25 kadr beradi va video notekis chiqadi.

## Avval foydalanuvchi bilan kelishing
Yasashdan oldin quyidagilarni so'rang yoki tasdiqlating:
1. Format (odatda vertikal 9:16), uzunligi (45–60 s) va qaysi qulayliklar ko'rsatilishi.
2. **Diktor matni.** Ssenariyni yozib bering. Raqamlarni so'z bilan yozing ("a o'n", "nout sakkiz", "bi-ti-es"), qavs va izohlar bo'lmasin. Foydalanuvchi uni ElevenLabs kabi xizmatda ovozga aylantirib, MP3 yuboradi. Bu muhitdan TTS xizmatlariga ulanib bo'lmaydi.
3. Musiqa: `tools/sfx.py` yaratgan ritm diktor paytida avtomatik pasayadi. Foydalanuvchi o'z musiqasini ham berishi mumkin.
4. Bot havolasi: **@ekranchi_bolabot**.

## Ish tartibi
```bash
cd promo-video
npm install
npm run prepare-assets          # market.html/data.js -> src/, tovushlar -> public/sfx (numpy kerak)
cp <diktor.mp3> public/voice.mp3
```

1. **Diktor vaqtlarini aniqlang.** Har bir gap bo'lagi qachon boshlanishini toping:
   ```bash
   ffmpeg -i public/voice.mp3 -af silencedetect=noise=-35dB:d=0.18 -f null - 2>&1 | grep silence_
   ```
   Jimliklar orasidagi bo'laklarni ssenariydagi vergul va nuqtalarga moslang. Tekshirish uchun: o'zbekcha diktor sekundiga taxminan 17–19 belgi o'qiydi. Natijani `src/timeline.ts` dagi `VOICE_SEGMENTS` ga yozing.
2. **Sahnalarni gaplarga bog'lang.** `src/timeline.ts`:
   - `T`: do'kondagi har bir harakat vaqti;
   - `TAPS`: barmoq bosishlari (`[vaqt, selector]`), `FINGER_SHOW`: barmoq ko'rinadigan oraliqlar;
   - `CAM_MOVES`: kamera yaqinlashuvi, `CAPTIONS`: tepadagi yozuvlar, `TYPING`: yozilayotgan matnlar;
   - `SFX`: tovushlar. Bosish va yozish tovushlari avtomatik qo'shiladi.

   Bosish diktor o'sha so'zni aytayotgan paytga to'g'ri kelsin.
3. **Kadrlarni tekshiring.** Butun videoni yasashdan oldin:
   ```bash
   npx remotion still src/index.ts Promo out/s.jpg --frame=<soniya*60> --scale=0.5
   ```
   Bir nechta kadrni `ffmpeg ... tile=6x2` bilan bitta rasmga yig'ib ko'ring. Tekshiring: yozuv telefon ostida qolmasin, barmoq tugma ustida bo'lsin, matn sig'sin.
4. **Yasash:** `npm run render -- --concurrency=4`. 4 yadroda 56 soniyalik video taxminan 40–50 daqiqada tayyor bo'ladi, shuning uchun fonda ishga tushiring. Natija: `out/ekranchi_promo_60fps.mp4`.
5. Tekshiring: `ffprobe` 1080x1920 va 60/1 ko'rsatsin. Videoni foydalanuvchiga yuboring.

## Qoidalar
- `Shop.tsx` da CSS transition yoki animation ishlatmang. Holat faqat `t` (soniya) dan `interpolate`/`spring` bilan hisoblanadi. `tools/prepare.js` do'kon CSS'idagi animatsiyalarni o'zi olib tashlaydi.
- Do'kon dizayni o'zgarsa, `npm run prepare-assets` ni qayta ishga tushiring.
- Bot xabarlarining matni `api/index.py` dagi haqiqiy matnlarga mos bo'lsin. Karta raqami ko'rsatilmaydi: to'lov bo'yicha "admin o'zi bog'lanadi".
- Remotion bepul: jismoniy shaxslar va 3 kishigacha kompaniyalar uchun. Kattaroq kompaniyaga uning pullik litsenziyasi kerak.
