// market.html ning Remotion nusxasi: o'sha klasslar va CSS, holat esa kadrdan hisoblanadi.
import React, { useLayoutEffect, useRef } from 'react';
import { interpolate, Easing } from 'remotion';
import './shop.processed.css';
import productsRaw from './products.json';
import { prettyModel, norm, typeClass } from './pretty';
import { T, TYPING, typed, ADDRESS } from './timeline';

type P = { id: number; brand: string; name: string; type: string; retail: number; wholesale: number; stock: number };
const products = (productsRaw as P[]).map((p) => {
  const pm = prettyModel(p.name, p.brand);
  return { ...p, pm, key: norm([p.brand, p.name, pm.main, ...pm.alts].join(' ')) };
});
type PP = (typeof products)[number];
const WHOLESALE_MIN = 50;
const fmtN = (n: number) => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
const fmt = (n: number) => fmtN(n) + ' soʻm';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const outE = Easing.bezier(0.2, 0.9, 0.25, 1);

const search = (q: string) => {
  const nq = norm(q);
  const list = products.filter((p) => !nq || p.key.includes(nq));
  // haqiqiy API kabi: avval bori, keyin tugaganlar
  return [...list.filter((p) => p.stock > 0), ...list.filter((p) => p.stock <= 0)];
};
export const MAIN = search('note8')[0];
export const WATCHED = search('note14').find((p) => p.stock <= 0)!;

/** Sheet ochilish darajasi (0..1) */
const sheetP = (t: number, open: number, close?: number) => {
  const a = interpolate(t, [open, open + 0.38], [0, 1], { ...clamp, easing: outE });
  const b = close === undefined ? 1 : interpolate(t, [close, close + 0.3], [1, 0], { ...clamp, easing: Easing.in(Easing.cubic) });
  return Math.min(a, b);
};

export function shopState(t: number) {
  let query = '';
  if (t >= TYPING[0][0]) query = typed(t, TYPING[0]);
  if (t >= TYPING[1][0]) query = typed(t, TYPING[1]);
  if (t >= T.clearTap + 0.08) query = '';
  if (t >= TYPING[2][0]) query = typed(t, TYPING[2]);

  let qty = 0;
  if (t >= T.addTap + 0.1) qty = 1;
  if (t >= T.qtyAnim[0]) qty = Math.round(interpolate(t, T.qtyAnim, [1, 50], { ...clamp, easing: Easing.inOut(Easing.cubic) }));
  const wholesale = t >= T.wholesale;
  const cart = sheetP(t, T.cartOpen1[0], T.cartOpen1[1]) || sheetP(t, T.cartOpen2, T.checkoutOpen);
  const checkout = sheetP(t, T.checkoutOpen);
  const delivery = t >= T.taxiTap + 0.08 ? 'Taksi' : 'BTS';
  const addr = typed(t, TYPING[3]);
  const watchOn = t >= T.watchTap + 0.08;
  return { query, qty, wholesale, cart, checkout, delivery, addr, watchOn };
}

const Row: React.FC<{ p: PP; t: number; qty: number; wholesale: boolean; watchOn: boolean; main?: boolean; glow?: number }> = ({ p, t, qty, wholesale, watchOn, main, glow = 0 }) => {
  const out = p.stock <= 0;
  const tc = typeClass(p.type);
  // optomga o'tganda narx sanab tushadi
  const k = interpolate(t, [T.wholesale, T.wholesale + 0.6], [0, 1], { ...clamp, easing: outE });
  const shown = p.retail + (p.wholesale - p.retail) * k;
  const watchHere = out && watchOn && p.id === WATCHED.id;
  return (
    <article className={'row' + (out ? ' out' : '') + (qty > 0 ? ' in-cart' : '')}
      style={glow ? { boxShadow: `0 0 0 ${3 * glow}px rgba(240,165,49,${0.9 * glow}), 0 10px 30px -10px rgba(240,165,49,${glow})` } : undefined}>
      <div className={'glyph t-' + tc} />
      <div className="info">
        <div className="meta">
          <span className="br">{p.brand}</span><span className={'type-tag ' + tc}>{p.type}</span>
          {p.pm.tags.map((x: string) => <span key={x} className={'type-tag' + (x === 'Ramkali' ? ' frame' : '')}>{x}</span>)}
        </div>
        <div className="name">{p.pm.main}</div>
        {p.pm.alts.length > 0 && <div className="alts"><b>Mos keladi:</b> {p.pm.alts.join(', ')}</div>}
        <div className="price">
          {out ? <span className="out-label">Hozircha omborda yoʻq</span>
            : k > 0 ? <><b>{fmt(shown)}</b><s>{fmtN(p.retail)}</s></>
              : <><b>{fmt(p.retail)}</b><small>optom <em>{fmtN(p.wholesale)}</em></small></>}
        </div>
      </div>
      <div className="act">
        {out ? (
          <button className={'add watch' + (watchHere ? ' on' : '')} {...(p.id === WATCHED.id ? { 'data-watch-main': 1 } : {})}>
            {watchHere ? '🔔 Kutilmoqda' : '🔔 Xabar bering'}
          </button>
        ) : qty > 0 ? (
          <div className="stepper"><button>−</button><input readOnly value={qty} /><button>+</button></div>
        ) : (
          <button className="add" {...(main ? { 'data-add-main': 1 } : {})}>Qoʻshish</button>
        )}
      </div>
    </article>
  );
};

export const Shop: React.FC<{ t: number }> = ({ t }) => {
  const st = shopState(t);
  const rows = search(st.query).slice(0, 9);
  const contentRef = useRef<HTMLDivElement>(null);
  const toolbarRef = useRef<HTMLDivElement>(null);
  const totalQ = st.qty;
  const w = st.wholesale;
  const sum = st.qty * (w ? MAIN.wholesale : MAIN.retail);
  const watchCardH = interpolate(t, [T.watchTap + 0.08, T.watchTap + 0.45], [0, 1], { ...clamp, easing: outE });

  // aylantirish: tugagan qatorni ko'rinadigan joyga olib kelamiz (tartib o'lchab hisoblanadi)
  useLayoutEffect(() => {
    const c = contentRef.current, tb = toolbarRef.current;
    if (!c || !tb) return;
    let scroll = 0;
    if (t >= T.scroll[0] && st.query) {
      const row = c.querySelector('[data-watch-main]')?.closest('.row') as HTMLElement | null;
      if (row) {
        // offsetTop kuzatuv kartasi balandligini ham o'z ichiga oladi, shuning uchun qator joyidan siljimaydi
        const k = interpolate(t, T.scroll, [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
        scroll = Math.max(0, row.offsetTop - 330) * k;
      }
    }
    c.style.transform = `translateY(${-scroll}px)`;
    tb.style.transform = `translateY(${Math.max(0, scroll - tb.offsetTop)}px)`;
  });

  const toast = (() => {
    const list = [
      { at: T.wholesale, d: 2.1, text: 'Optom narx yoqildi, hamma narx arzonlashdi' },
      { at: T.watchTap + 0.1, d: 1.6, text: 'Kelganda bot sizga xabar beradi' },
    ];
    for (const x of list) {
      if (t >= x.at && t < x.at + x.d + 0.4) {
        const inn = interpolate(t, [x.at, x.at + 0.35], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
        const outp = interpolate(t, [x.at + x.d, x.at + x.d + 0.3], [0, 1], clamp);
        return { text: x.text, y: -160 + 160 * inn - 160 * outp };
      }
    }
    return null;
  })();

  const dockShow = interpolate(t, [T.addTap + 0.1, T.addTap + 0.5], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.4)) });
  const tapeW = Math.min(100, (totalQ / WHOLESALE_MIN) * 100);
  const heroOn = interpolate(t, [T.heroOn, T.heroOn + 0.25, T.heroOn + 0.6, T.heroOn + 1.1], [0, 1, 1, 1], clamp);
  const heroScaleY = interpolate(t, [T.heroOn, T.heroOn + 0.12, T.heroOn + 0.5], [0.006, 0.006, 1], clamp);
  const heroBright = interpolate(t, [T.heroOn, T.heroOn + 0.5, T.heroOn + 1.1], [4, 2.2, 1], clamp);
  const devCount = Math.round(interpolate(t, [T.heroOn + 0.4, T.heroOn + 1.4], [0, 456], { ...clamp, easing: outE }));
  const highlight = interpolate(t, [T.highlightRow, T.highlightRow + 0.3, T.addTap - 0.2, T.addTap + 0.2], [0, 1, 1, 0], clamp);
  const lines = st.qty > 0 ? [MAIN] : [];
  const diff = st.qty * (MAIN.retail - MAIN.wholesale);
  const saveGlow = interpolate(t, [T.cartOpen1[0] + 0.5, T.cartOpen1[0] + 0.8], [0, 1], clamp) * (t < T.cartOpen1[1] ? 1 : 0);

  return (
    <div className={'shop shopbody' + (w ? ' wholesale' : '')} style={{ position: 'absolute', inset: 0, overflow: 'hidden', background: 'var(--paper)', transform: 'translateZ(0)' }}>
      <div ref={contentRef}>
        <header className="hero">
          <div className="hero-glow" style={{ opacity: heroOn }} />
          <div className="hero-copy">
            <h1 className="logo">Ekranchi<em>_Bola</em><span>Telefon displeylari ulgurji va donalab</span></h1>
            <p className="hero-note">Barcha displeylarga <b>2 oy kafolat</b></p>
          </div>
          <div className="device">
            <div className="device-screen" style={{ transform: `scaleY(${heroScaleY})`, filter: `brightness(${heroBright})`, opacity: heroOn }}>
              <div className="device-count" style={{ opacity: interpolate(t, [T.heroOn + 0.3, T.heroOn + 0.6], [0, 1], clamp) }}>
                <strong>{devCount}</strong><small>ta model</small>
              </div>
            </div>
          </div>
        </header>
        <section className={'tape-wrap' + (totalQ >= WHOLESALE_MIN ? ' done' : '')}>
          <div className="tape-head">
            <b>{totalQ >= WHOLESALE_MIN ? 'Optom narx yoqildi' : totalQ ? `Optom narxgacha yana ${WHOLESALE_MIN - totalQ} ta` : `${WHOLESALE_MIN} ta olsangiz, optom narx`}</b>
            <span className="count">{totalQ >= WHOLESALE_MIN ? `${totalQ} ta` : `${totalQ}/${WHOLESALE_MIN}`}</span>
          </div>
          <div className="ruler"><div className="tape" style={{ width: tapeW + '%' }} /></div>
        </section>
        <div className="toolbar" ref={toolbarRef} style={{ position: 'relative', zIndex: 30 }}>
          <label className={'search' + (st.query ? ' has-text' : '')} id="searchBox"
            style={t > T.searchTap && t < T.cartTap1 || (t > T.clearTap && t < T.cartTap2) ? { borderColor: 'var(--mat)' } : undefined}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#62716D" strokeWidth="2"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
            <span style={{ flex: 1, fontSize: 16, color: st.query ? 'var(--ink)' : '#8A9692', whiteSpace: 'nowrap', overflow: 'hidden' }}>
              {st.query || 'Model: A10, Note 8, 13C…'}
              {((t > T.searchTap && t < T.typeNote8[1] + 0.8) || (t > T.clearTap && t < T.typeNote14[1] + 0.6)) && Math.floor(t * 2.4) % 2 === 0 &&
                <span style={{ display: 'inline-block', width: 2, height: 19, background: 'var(--mat)', verticalAlign: -3, marginLeft: 1 }} />}
            </span>
            <button className="clear" id="clearQ">✕</button>
          </label>
          <div className="chips">
            {[['Barchasi', 456], ['Samsung', 126], ['iPhone', 43], ['Redmi', 87], ['Xiaomi', 21]].map(([b, n], i) => (
              <button key={b} className="chip" aria-pressed={i === 0 ? 'true' : 'false'}><span>{b}</span><i>{n}</i></button>
            ))}
          </div>
        </div>
        <div className="notes" style={{ display: watchCardH > 0 ? 'flex' : 'none', maxHeight: 80 * watchCardH, overflow: 'hidden', opacity: watchCardH }}>
          <div className="note-card watching">
            <div className="tx"><b>🔔 1 ta model kutilmoqda</b>Buyurtma bilan birga yuboriladi</div>
            <button>Tasdiqlash</button>
          </div>
        </div>
        <div className="result-meta">{rows.length && st.query ? `${search(st.query).length} ta model` : '456 ta model'}</div>
        <main className="list">
          {rows.map((p) => (
            <Row key={p.id} p={p} t={t} qty={p.id === MAIN.id ? st.qty : 0} wholesale={w} watchOn={st.watchOn}
              main={p.id === MAIN.id} glow={p.id === MAIN.id ? highlight : 0} />
          ))}
        </main>
      </div>

      <div className="dock" style={{ transform: `translateY(${(1 - dockShow) * 140}%)` }}>
        <div className="dock-sum">
          <small>{totalQ} ta ekran, {w ? 'optom' : 'chakana'}</small>
          <strong>{fmt(sum)}</strong>
        </div>
        <button className="dock-btn" id="dockBtn">Savatni ochish</button>
      </div>

      <div className="scrim" style={{ opacity: Math.max(st.cart, st.checkout) }} />
      <section className="sheet" style={{ transform: `translateY(${(1 - st.cart) * 105}%)`, visibility: st.cart > 0 ? 'visible' : 'hidden' }}>
        <div className="grab" />
        <div className="sheet-head"><h2>Savat</h2><button className="link-btn">Tozalash</button></div>
        <div className="sheet-body">
          {lines.map((p) => {
            const pr = w ? p.wholesale : p.retail;
            return (
              <div className="line" key={p.id}>
                <div><div className="nm">{p.brand} {p.pm.main}{p.pm.alts.length ? ` (+${p.pm.alts.length} mos model)` : ''}</div>
                  <div className="sub">{st.qty} × {fmtN(pr)} = <b>{fmt(pr * st.qty)}</b></div></div>
                <div className="stepper"><button>−</button><input readOnly value={st.qty} /><button>+</button></div>
              </div>
            );
          })}
        </div>
        <div className="sheet-foot">
          <div className="total"><span>{w ? 'Optom narxda' : 'Chakana narxda'}</span><strong>{fmt(sum)}</strong></div>
          <div className="save-note" style={saveGlow ? { background: `rgba(15,107,90,${0.12 * saveGlow})`, borderRadius: 8, padding: '4px 8px', margin: '0 -8px 12px', boxShadow: `0 0 0 ${2 * saveGlow}px rgba(15,107,90,.5)` } : undefined}>
            {w ? `Optom narx bilan ${fmt(diff)} tejadingiz 🎉` : ''}
          </div>
          <button className="primary" id="toCheckout">Rasmiylashtirish</button>
          <button className="ghost" id="cartGhost">Xaridni davom ettirish</button>
        </div>
      </section>

      <section className="sheet" style={{ transform: `translateY(${(1 - st.checkout) * 105}%)`, visibility: st.checkout > 0 ? 'visible' : 'hidden' }}>
        <div className="grab" />
        <div className="sheet-head"><h2>Yetkazib berish</h2></div>
        <div className="sheet-body">
          <div className="field"><label>Ismingiz</label><input readOnly value="Sardor" /></div>
          <div className="field">
            <label>Qanday yetkazamiz?</label>
            <div className="seg">
              <button id="btnBTS" aria-pressed={st.delivery === 'BTS' ? 'true' : 'false'}
                style={pulse(t, T.btsTap)}>BTS pochta<small>Viloyatlarga</small></button>
              <button id="btnTaksi" aria-pressed={st.delivery === 'Taksi' ? 'true' : 'false'}
                style={pulse(t, T.taxiTap)}>Taksi<small>Tezkor, shahar ichida</small></button>
            </div>
          </div>
          <div className="field">
            <label>{st.delivery === 'BTS' ? 'BTS filiali va shahar/tuman' : 'Taksi uchun aniq manzil'}</label>
            <div id="custAddress" style={{
              width: '100%', border: '1.5px solid ' + (t > T.addrTap ? 'var(--mat)' : 'var(--hair)'), background: t > T.addrTap ? '#fff' : 'var(--paper)',
              borderRadius: 12, padding: '12px 14px', fontSize: 16, minHeight: 72, color: st.addr ? 'var(--ink)' : '#8A9692',
            }}>
              {st.addr || (st.delivery === 'BTS' ? 'Viloyat, tuman, filial' : 'Koʻcha, uy, moʻljal')}
              {t > T.addrTap && t < T.submitTap && Math.floor(t * 2.4) % 2 === 0 && <span style={{ display: 'inline-block', width: 2, height: 19, background: 'var(--mat)', verticalAlign: -3, marginLeft: 1 }} />}
            </div>
          </div>
        </div>
        <div className="sheet-foot">
          <div className="total"><span>{totalQ} ta, {w ? 'optom' : 'chakana'}</span><strong>{fmt(sum)}</strong></div>
          <div className="save-note" />
          <button className="primary" id="submitOrder" style={pulse(t, T.submitTap)}>Buyurtmani yuborish</button>
          <button className="ghost">Savatga qaytish</button>
        </div>
      </section>

      {toast && <div className="toast" style={{ transform: `translate(-50%, ${toast.y}%)` }}>{toast.text}</div>}
    </div>
  );
};

/** Bosilgan tugma qisqa "chuqurlashadi" */
function pulse(t: number, at: number): React.CSSProperties {
  const k = interpolate(t, [at - 0.02, at + 0.08, at + 0.3], [0, 1, 0], clamp);
  return k ? { transform: `scale(${1 - 0.05 * k})`, filter: `brightness(${1 - 0.08 * k})` } : {};
}

export const ORDER_INFO = () => ({
  name: `${MAIN.brand} ${MAIN.name}`.slice(0, 40), qty: 50, total: 50 * MAIN.wholesale, addr: ADDRESS,
  watched: `${WATCHED.brand} ${WATCHED.pm.main}`, wRetail: WATCHED.retail, wWholesale: WATCHED.wholesale,
});
