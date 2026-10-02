// Barcha vaqtlar video soniyalarida. Diktor ovozi VO_OFFSET dan boshlanadi.
export const FPS = 60;
export const VO_OFFSET = 0.5;
export const DURATION = 56;

// Diktor gaplari (voice.mp3 dagi jimliklar bo'yicha aniqlangan, +VO_OFFSET)
export const VOICE_SEGMENTS: [number, number][] = [
  [0.0, 1.01], [1.29, 2.19], [2.62, 4.32], [4.6, 5.97], [6.33, 9.02], [9.32, 10.85], [11.21, 12.69],
  [13.13, 13.7], [13.93, 14.88], [15.24, 18.74], [19.1, 22.8], [23.11, 25.2], [25.59, 27.01],
  [27.29, 28.7], [29.11, 31.66], [32.03, 33.21], [33.6, 35.56], [35.83, 37.01], [37.25, 37.67],
  [38.04, 40.13], [40.5, 42.68], [42.95, 45.01], [45.36, 47.85], [48.23, 49.18], [49.51, 50.35],
  [50.71, 51.95], [52.27, 53.43],
].map(([a, b]) => [a + VO_OFFSET, b + VO_OFFSET] as [number, number]);

// ---- Do'kon ichidagi harakatlar ----
export const T = {
  phoneIn: 4.95,
  startMsg: 5.4,
  welcomeMsg: 5.8,
  openTap: 8.9,
  appUp: 9.0,
  heroOn: 9.9,
  searchTap: 12.5,
  typeA10: [13.63, 14.15] as [number, number],
  typeNote8: [14.45, 15.25] as [number, number],
  counter: [15.8, 17.2] as [number, number],
  highlightRow: 17.6,
  addTap: 19.9,
  qtyAnim: [20.35, 22.35] as [number, number],
  wholesale: 22.45,
  cartTap1: 23.7,
  cartOpen1: [23.85, 25.85] as [number, number],
  closeTap: 25.75,
  clearTap: 26.15,
  typeNote14: [26.45, 27.15] as [number, number],
  scroll: [27.2, 27.75] as [number, number],
  watchTap: 28.5,
  timeSkip: 29.65,
  push: [30.15, 32.1] as [number, number],
  cartTap2: 32.6,
  cartOpen2: 32.75,
  checkoutTap: 33.3,
  checkoutOpen: 33.45,
  btsTap: 35.0,
  taxiTap: 37.8,
  addrTap: 38.6,
  typeAddr: [38.8, 39.95] as [number, number],
  submitTap: 40.25,
  appDown: 40.45,
  svcMsg: 40.95,
  orderMsg: 41.3,
  adminGlow: 43.45,
  shield: [45.86, 48.4] as [number, number],
  outro: 48.5,
  logo: 48.73,
  searchType: [50.05, 51.85] as [number, number],
  result: 52.0,
  cta: 52.77,
};

export const ADDRESS = "Urganch, Al-Xorazmiy ko'chasi 12";
export const BOT = 'ekranchi_bolabot';

export const CAPTIONS: { t: number; kick: string; title: string; sub?: string }[] = [
  { t: 5.1, kick: 'TELEGRAM BOT', title: '*Ekranchi_Bola*' },
  { t: 6.83, kick: '01 · BOTGA KIRING', title: "Do'kon — *bitta* tugmada" },
  { t: 11.71, kick: '02 · TEZ QIDIRUV', title: '*456 ta* model, bir zumda' },
  { t: 19.6, kick: '03 · OPTOM NARX', title: "*50 ta* yig'ing — arzonroq" },
  { t: 26.09, kick: "04 · YO'Q MODEL?", title: "Kelganda bot *o'zi* yozadi" },
  { t: 32.53, kick: '05 · YETKAZIB BERISH', title: '*BTS* yoki *Taksi*' },
  { t: 41.0, kick: '06 · TAYYOR', title: 'Buyurtma *qabul qilindi*' },
];
export const CAPTIONS_END = 48.45;

// Barmoq bosishlari: [vaqt, selector]
export const TAPS: [number, string][] = [
  [T.openTap, '#openBtn'],
  [T.searchTap, '#searchBox'],
  [T.addTap, '[data-add-main]'],
  [T.cartTap1, '#dockBtn'],
  [T.closeTap, '#cartGhost'],
  [T.clearTap, '#clearQ'],
  [T.watchTap, '[data-watch-main]'],
  [T.cartTap2, '#dockBtn'],
  [T.checkoutTap, '#toCheckout'],
  [T.btsTap, '#btnBTS'],
  [T.taxiTap, '#btnTaksi'],
  [T.addrTap, '#custAddress'],
  [T.submitTap, '#submitOrder'],
];
// Barmoq ko'rinadigan oraliqlar
export const FINGER_SHOW: [number, number][] = [
  [8.15, 9.35], [11.95, 12.95], [19.35, 20.35], [23.15, 24.1], [25.2, 26.55],
  [27.85, 28.95], [32.05, 33.75], [34.4, 35.4], [37.25, 38.95], [39.85, 40.6],
];

// Kamera: [boshlanish, tugash, holat]
export type Cam = { s: number; y: number; r: number };
export const CAM_START: Cam = { s: 0.9, y: 1050, r: -8 };
export const CAM_MOVES: [number, number, Cam][] = [
  [4.95, 5.85, { s: 1, y: 0, r: 0 }],
  [9.9, 10.5, { s: 1.15, y: 82, r: 0 }],
  [11.3, 11.8, { s: 1, y: 0, r: 0 }],
  [12.0, 12.5, { s: 1.12, y: -56, r: 0 }],
  [15.5, 16.0, { s: 1, y: 0, r: 0 }],
  [20.0, 20.5, { s: 1.2, y: -52, r: 0 }],
  [22.8, 23.3, { s: 1, y: 0, r: 0 }],
  [24.0, 24.5, { s: 1.15, y: -180, r: 0 }],
  [25.45, 25.9, { s: 1, y: 0, r: 0 }],
  [27.7, 28.2, { s: 1.12, y: -127, r: 0 }],
  [29.3, 29.7, { s: 1, y: 0, r: 0 }],
  [33.5, 34.0, { s: 1.15, y: -148, r: 0 }],
  [39.7, 40.1, { s: 1, y: 0, r: 0 }],
  [43.2, 43.7, { s: 1.1, y: -140, r: 0 }],
  [45.5, 46.0, { s: 0.92, y: 30, r: 0 }],
  [48.5, 49.1, { s: 0.85, y: 1080, r: 6 }],
];

// Matn yozish: [boshlanish, tugash, matn]
export const TYPING: [number, number, string][] = [
  [T.typeA10[0], T.typeA10[1], 'a10'],
  [T.typeNote8[0], T.typeNote8[1], 'note8'],
  [T.typeNote14[0], T.typeNote14[1], 'note14'],
  [T.typeAddr[0], T.typeAddr[1], ADDRESS],
  [T.searchType[0], T.searchType[1], BOT],
];
export const typed = (t: number, [a, b, s]: [number, number, string]) => {
  if (t < a) return '';
  if (t >= b) return s;
  return s.slice(0, Math.max(1, Math.ceil(((t - a) / (b - a)) * s.length)));
};

// Tovush effektlari: [vaqt, fayl, balandlik]
export const SFX: [number, string, number][] = (() => {
  const out: [number, string, number][] = [
    [0.45, 'pop', 0.5], [1.75, 'pop', 0.5], [3.0, 'whoosh', 0.45], [4.9, 'whoosh', 0.6], [5.15, 'impact', 0.45],
    [T.startMsg, 'pop', 0.45], [T.welcomeMsg, 'notify', 0.5], [T.appUp, 'whoosh', 0.55], [T.heroOn + 0.2, 'ding', 0.35],
    [T.counter[0], 'riser', 0.3], [T.counter[1], 'ding', 0.35], [T.highlightRow, 'pop', 0.4],
    [T.wholesale, 'coin', 0.55], [T.wholesale + 0.1, 'ding', 0.5],
    [T.cartOpen1[0], 'swish', 0.5], [T.cartOpen1[1], 'swish', 0.4], [T.scroll[0], 'swish', 0.4],
    [T.watchTap + 0.05, 'ding', 0.35], [T.timeSkip, 'whoosh', 0.4], [T.push[0], 'notify', 0.55],
    [T.cartOpen2, 'swish', 0.5], [T.checkoutOpen, 'swish', 0.5], [T.appDown, 'whoosh', 0.55],
    [T.svcMsg, 'pop', 0.35], [T.orderMsg, 'notify', 0.55], [T.adminGlow, 'pop', 0.4],
    [T.shield[0], 'impact', 0.5], [T.shield[0] + 0.15, 'ding', 0.45],
    [T.outro, 'whoosh', 0.6], [T.logo, 'impact', 0.6], [T.result, 'pop', 0.5], [T.cta, 'ding', 0.5],
  ];
  for (const [t] of TAPS) out.push([t, 'tap', 0.55]);
  for (const c of CAPTIONS) out.push([c.t, 'swish', 0.3]);
  for (const ty of TYPING) {
    const n = ty[2].length;
    for (let i = 0; i < n; i++) out.push([ty[0] + ((ty[1] - ty[0]) * i) / n, 'key', 0.35]);
  }
  // son 1 -> 50 ga o'sayotganda tiqillash
  for (let i = 0; i < 12; i++) {
    const k = i / 11;
    out.push([T.qtyAnim[0] + (T.qtyAnim[1] - T.qtyAnim[0]) * Math.sqrt(k), 'key', 0.3]);
  }
  return out;
})();
