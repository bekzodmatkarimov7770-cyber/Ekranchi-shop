import React, { useLayoutEffect, useRef, useState } from 'react';
import {
  AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate, spring, Easing,
  delayRender, continueRender,
} from 'remotion';
import { Shop, ORDER_INFO } from './Shop';
import {
  FPS, VO_OFFSET, DURATION, VOICE_SEGMENTS, T, CAPTIONS, CAPTIONS_END, TAPS, FINGER_SHOW,
  CAM_START, CAM_MOVES, Cam, SFX, TYPING, typed, BOT,
} from './timeline';

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const outE = Easing.bezier(0.2, 0.9, 0.25, 1);
const io = Easing.inOut(Easing.cubic);
const sp = (t: number, at: number, damping = 14, stiffness = 140) =>
  spring({ frame: (t - at) * FPS, fps: FPS, config: { damping, stiffness, mass: 1 } });
const fmtC = (n: number) => n.toLocaleString('en-US');

/* ---------- shriftlar ---------- */
const FONT_CSS = `
@font-face{font-family:Unbounded;font-weight:500;src:url(${staticFile('fonts/unbounded-latin-500-normal.woff2')})}
@font-face{font-family:Unbounded;font-weight:700;src:url(${staticFile('fonts/unbounded-latin-700-normal.woff2')})}
@font-face{font-family:Unbounded;font-weight:800;src:url(${staticFile('fonts/unbounded-latin-800-normal.woff2')})}
@font-face{font-family:Unbounded;font-weight:700;src:url(${staticFile('fonts/unbounded-latin-ext-700-normal.woff2')});unicode-range:U+0100-02FF}
@font-face{font-family:Unbounded;font-weight:800;src:url(${staticFile('fonts/unbounded-latin-ext-800-normal.woff2')});unicode-range:U+0100-02FF}
@font-face{font-family:Onest;font-weight:400;src:url(${staticFile('fonts/onest-latin-400-normal.woff2')})}
@font-face{font-family:Onest;font-weight:500;src:url(${staticFile('fonts/onest-latin-500-normal.woff2')})}
@font-face{font-family:Onest;font-weight:600;src:url(${staticFile('fonts/onest-latin-600-normal.woff2')})}
@font-face{font-family:Onest;font-weight:700;src:url(${staticFile('fonts/onest-latin-700-normal.woff2')})}
@font-face{font-family:Onest;font-weight:400;src:url(${staticFile('fonts/onest-latin-ext-400-normal.woff2')});unicode-range:U+0100-02FF}
@font-face{font-family:Onest;font-weight:600;src:url(${staticFile('fonts/onest-latin-ext-600-normal.woff2')});unicode-range:U+0100-02FF}
@font-face{font-family:Onest;font-weight:700;src:url(${staticFile('fonts/onest-latin-ext-700-normal.woff2')});unicode-range:U+0100-02FF}
`;
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useLayoutEffect(() => {
    const specs = ['500 20px Unbounded', '700 20px Unbounded', '800 20px Unbounded', '400 20px Onest', '500 20px Onest', '600 20px Onest', '700 20px Onest'];
    Promise.all(specs.flatMap((s) => [document.fonts.load(s, 'abc'), document.fonts.load(s, 'oʻ')]))
      .then(() => document.fonts.ready).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};

/* ---------- kamera ---------- */
const camAt = (t: number): Cam => {
  let cur = { ...CAM_START };
  for (const [a, b, to] of CAM_MOVES) {
    if (t >= b) cur = { ...to };
    else if (t > a) {
      const e = a === 4.95 ? Easing.out(Easing.back(1.15)) : io;
      const k = interpolate(t, [a, b], [0, 1], { ...clamp, easing: e });
      return { s: cur.s + (to.s - cur.s) * k, y: cur.y + (to.y - cur.y) * k, r: cur.r + (to.r - cur.r) * k };
    } else break;
  }
  return cur;
};

/* ---------- sarlavha ---------- */
const Words: React.FC<{ text: string; t: number; at: number; step?: number; style?: React.CSSProperties }> = ({ text, t, at, step = 0.06, style }) => {
  const words = text.split(' ');
  return (
    <span style={style}>
      {words.map((w, i) => {
        const em = /^\*.*\*$/.test(w) || /^\*/.test(w) || /\*$/.test(w);
        const clean = w.replace(/\*/g, '');
        const k = sp(t, at + i * step, 13, 170);
        return (
          <span key={i} style={{
            display: 'inline-block', opacity: Math.min(1, k * 1.4), color: em ? '#F0A531' : undefined,
            transform: `translateY(${(1 - k) * 26}px) scale(${0.92 + 0.08 * k})`, filter: `blur(${Math.max(0, (1 - k) * 6)}px)`,
            marginRight: i < words.length - 1 ? '0.26em' : 0,
          }}>{clean}</span>
        );
      })}
    </span>
  );
};
// *bitta* kabi belgilashni so'zlarga yoyish ("*qabul qilindi*" -> har so'zi alohida)
const spreadEm = (s: string) => s.replace(/\*([^*]+)\*/g, (_, g) => g.split(' ').map((w: string) => `*${w}*`).join(' '));

const Captions: React.FC<{ t: number }> = ({ t }) => {
  const idx = CAPTIONS.findIndex((c, i) => t >= c.t && t < (CAPTIONS[i + 1]?.t ?? CAPTIONS_END));
  if (idx < 0) return null;
  const c = CAPTIONS[idx];
  const end = CAPTIONS[idx + 1]?.t ?? CAPTIONS_END;
  // kamera telefonni yuqoriga surganda sarlavha yo'l beradi
  const cam = camAt(t);
  const phoneTop = 560 - 338 * cam.s + cam.y;
  const room = interpolate(phoneTop, [70, 150], [0, 1], clamp);
  const out = interpolate(t, [end - 0.22, end], [1, 0], clamp) * room;
  const kk = sp(t, c.t, 15, 160);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 44, textAlign: 'center', padding: '0 24px', opacity: out, transform: `translateY(${(1 - out) * -16}px)`, zIndex: 20 }}>
      <div style={{
        display: 'inline-flex', alignItems: 'center', height: 30, padding: '0 14px', borderRadius: 30, background: 'rgba(240,165,49,.16)',
        border: '1px solid rgba(240,165,49,.55)', color: '#FFD08A', fontWeight: 700, fontSize: 12.5, letterSpacing: '.06em',
        opacity: kk, transform: `scale(${0.8 + 0.2 * kk})`,
      }}>{c.kick}</div>
      <div style={{ fontFamily: 'Unbounded', fontWeight: 800, color: '#fff', fontSize: 31, lineHeight: 1.12, letterSpacing: '-.02em', marginTop: 12 }}>
        <Words text={spreadEm(c.title)} t={t} at={c.t + 0.08} />
      </div>
    </div>
  );
};

/* ---------- fon ---------- */
const Background: React.FC<{ t: number }> = ({ t }) => (
  <AbsoluteFill style={{ background: 'radial-gradient(120% 70% at 50% 0%, #1A5A50 0%, #123F38 45%, #0A2723 100%)', overflow: 'hidden' }}>
    <AbsoluteFill style={{
      opacity: 0.18, backgroundImage: 'linear-gradient(rgba(255,255,255,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.12) 1px, transparent 1px)',
      backgroundSize: '27px 27px', backgroundPosition: `0 ${(t * 6) % 27}px`,
    }} />
    <div style={{ position: 'absolute', width: 360, height: 360, borderRadius: '50%', background: '#F0A531', opacity: 0.25, filter: 'blur(70px)', left: -150 + Math.sin(t * 0.5) * 30, top: 520 + Math.cos(t * 0.4) * 40 }} />
    <div style={{ position: 'absolute', width: 400, height: 400, borderRadius: '50%', background: '#5FD4E8', opacity: 0.2, filter: 'blur(70px)', right: -180 + Math.cos(t * 0.45) * 30, top: 110 + Math.sin(t * 0.35) * 40 }} />
  </AbsoluteFill>
);

/* ---------- intro ---------- */
const Intro: React.FC<{ t: number }> = ({ t }) => {
  if (t > 5.6) return null;
  const a = interpolate(t, [2.95, 3.3], [1, 0], { ...clamp, easing: Easing.in(Easing.cubic) });
  const b = interpolate(t, [4.85, 5.2], [1, 0], { ...clamp, easing: Easing.in(Easing.cubic) });
  const disp = sp(t, 1.75, 12, 120);
  const plane = interpolate(t, [3.1, 4.6], [0, 1], { ...clamp, easing: outE });
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', textAlign: 'center', zIndex: 30 }}>
      {t < 3.3 && (
        <div style={{ opacity: a, transform: `translateY(${(1 - a) * -60}px) scale(${0.94 + 0.06 * a})` }}>
          {/* yonayotgan displey belgisi */}
          <div style={{ width: 110, height: 200, margin: '0 auto 34px', borderRadius: 22, background: '#0A1614', padding: 7, boxShadow: '0 0 0 2px #2E6258, 0 30px 60px -16px rgba(0,0,0,.7)', transform: `rotate(${-8 + 8 * disp}deg) scale(${0.6 + 0.4 * disp})`, opacity: Math.min(1, disp * 2) }}>
            <div style={{
              width: '100%', height: '100%', borderRadius: 16,
              background: 'radial-gradient(90% 70% at 30% 20%, #FFFFFF 0%, #D6F8FF 30%, #7FD6EE 70%, #3C8FB0 100%)',
              transform: `scaleY(${interpolate(t, [1.85, 1.95, 2.25], [0.006, 0.006, 1], clamp)})`,
              filter: `brightness(${interpolate(t, [1.85, 2.3, 2.8], [4, 2, 1], clamp)})`,
              boxShadow: `0 0 ${60 * disp}px rgba(127,214,238,.6)`,
            }} />
          </div>
          <div style={{ fontFamily: 'Unbounded', fontWeight: 800, fontSize: 40, color: '#fff', lineHeight: 1.1, letterSpacing: '-.02em' }}>
            <Words text="Telefon ustalari," t={t} at={0.45} step={0.12} /><br />
            <Words text="*displey* *kerakmi?*" t={t} at={1.75} step={0.14} />
          </div>
        </div>
      )}
      {t >= 3.0 && (
        <div style={{ position: 'absolute', opacity: b, transform: `translateY(${(1 - b) * -50}px)` }}>
          <div style={{
            width: 96, height: 96, margin: '0 auto 30px', borderRadius: '50%', background: 'linear-gradient(160deg,#37AEE2,#1E96C8)', display: 'grid', placeItems: 'center',
            boxShadow: '0 20px 50px -10px rgba(55,174,226,.7)',
            transform: `translate(${(1 - plane) * -260}px, ${(1 - plane) * 120}px) rotate(${(1 - plane) * -30}deg) scale(${0.5 + 0.5 * plane})`, opacity: plane,
          }}>
            <svg viewBox="0 0 24 24" width="52" height="52" fill="#fff"><path d="M21.9 4.6 18.7 19.7c-.2 1-.9 1.3-1.8.8l-4.8-3.6-2.3 2.2c-.3.3-.5.5-1 .5l.3-4.9 8.9-8c.4-.3-.1-.5-.6-.2L6.4 13.4l-4.7-1.5c-1-.3-1-1 .2-1.5L20.6 3.3c.9-.3 1.6.2 1.3 1.3z" /></svg>
          </div>
          <div style={{ fontFamily: 'Unbounded', fontWeight: 800, fontSize: 38, color: '#fff', lineHeight: 1.12, letterSpacing: '-.02em' }}>
            <Words text="Endi hammasi" t={t} at={3.12} step={0.12} /><br />
            <Words text="*Telegramda*" t={t} at={3.6} />
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

/* ---------- Telegram chat ---------- */
const Msg: React.FC<{ t: number; at: number; me?: boolean; svc?: boolean; children: React.ReactNode; glowBtn?: number }> = ({ t, at, me, svc, children }) => {
  if (t < at) return null;
  const k = sp(t, at, 14, 220);
  const base: React.CSSProperties = svc
    ? { alignSelf: 'center', background: 'rgba(0,0,0,.35)', color: '#DDE6EC', fontSize: 12.5, borderRadius: 12, padding: '5px 10px', textAlign: 'center', maxWidth: '92%' }
    : { alignSelf: me ? 'flex-end' : 'flex-start', maxWidth: '86%', background: me ? '#2B5278' : '#182533', color: '#E9EEF2', borderRadius: me ? '16px 16px 4px 16px' : '16px 16px 16px 4px', padding: '9px 12px 7px', fontSize: 14.5, lineHeight: 1.38 };
  return <div style={{ ...base, opacity: Math.min(1, k * 1.5), transform: `translateY(${(1 - k) * 18}px) scale(${0.9 + 0.1 * k})`, transformOrigin: me ? '100% 100%' : '0 100%' }}>{children}</div>;
};
const Tm: React.FC<{ s: string }> = ({ s }) => <span style={{ float: 'right', fontSize: 11, color: '#6D8193', margin: '6px 0 0 10px' }}>{s}</span>;
const Hr = () => <div style={{ borderTop: '1px solid #2A3B4C', margin: '5px 0' }} />;
const StatusBar: React.FC<{ bg: string }> = ({ bg }) => (
  <div style={{ height: 46, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 28px 0 34px', fontWeight: 600, fontSize: 16, color: '#fff' }}>
    <span>9:41</span><span style={{ fontSize: 13, letterSpacing: 2 }}>▂▄▆ 5G ▮</span>
  </div>
);
const Avatar: React.FC<{ size?: number }> = ({ size = 40 }) => (
  <div style={{ width: size, height: size, borderRadius: '50%', background: 'linear-gradient(135deg,#F0A531,#C9741A)', display: 'grid', placeItems: 'center', fontFamily: 'Unbounded', fontWeight: 800, fontSize: size * 0.35, color: '#2B1A00', flex: 'none' }}>EB</div>
);

const Chat: React.FC<{ t: number }> = ({ t }) => {
  const o = ORDER_INFO();
  const admin = interpolate(t, [T.adminGlow, T.adminGlow + 0.3], [0, 1], clamp);
  const btnPress = interpolate(t, [T.openTap - 0.02, T.openTap + 0.08, T.openTap + 0.3], [0, 1, 0], clamp);
  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', background: '#0E1621', fontFamily: 'Onest, "Noto Color Emoji"' }}>
      <StatusBar bg="#17212B" />
      <div style={{ height: 56, background: '#17212B', display: 'flex', alignItems: 'center', gap: 12, padding: '0 14px', color: '#fff' }}>
        <span style={{ fontSize: 28, color: '#6AB2F2', width: 16 }}>‹</span><Avatar />
        <div><b style={{ display: 'block', fontSize: 16.5, fontWeight: 600 }}>Ekranchi_Bola</b><small style={{ color: '#7D8E98', fontSize: 13.5 }}>bot</small></div>
      </div>
      <div style={{ flex: 1, overflow: 'hidden', padding: '12px 10px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', gap: 8,
        background: '#0E1621 radial-gradient(circle at 20% 30%, rgba(106,178,242,.07), transparent 40%)' }}>
        <Msg t={t} at={T.startMsg} me>/start <Tm s="9:41 ✓✓" /></Msg>
        <Msg t={t} at={T.welcomeMsg}>Assalomu alaykum, <b>Sardor</b>! 👋<br /><br />Do'konimizga xush kelibsiz!<br /><br />Pastdagi <b>«🛍 Do'konni ochish»</b> tugmasini bosib buyurtma berishingiz mumkin 👇<Tm s="9:41" /></Msg>
        <Msg t={t} at={T.svcMsg} svc>Data from the “🛍 Do'konni ochish” button was transferred to the bot.</Msg>
        <Msg t={t} at={T.orderMsg}>
          🛒 <b>Buyurtmangiz #E1024 qabul qilindi!</b><Hr />
          👤 <b>Mijoz:</b> Sardor<br />🚚 <b>Yetkazish:</b> Taksi | 📍 {o.addr}<br />📦 <b>Tarkibi:</b><br />• <b>{o.name}</b>: {o.qty} dona<Hr />
          💰 <b>JAMI:</b> <b>{fmtC(o.total)} so'm</b> (Optom narxda, {o.qty} dona)<br /><br />
          💬 <b>To'lov masalasida admin siz bilan o'zi bog'lanadi.</b><br /><br />🛡 Barcha displeylarga <b>2 oy kafolat</b><Tm s="9:43" />
          <div style={{
            marginTop: 8, background: `rgba(106,178,242,${0.14 + 0.25 * admin})`, color: admin ? '#fff' : '#8CC4F7', textAlign: 'center', borderRadius: 10, padding: 8, fontWeight: 600, fontSize: 13.5,
            boxShadow: admin ? `0 0 0 ${2 * admin}px #6AB2F2, 0 0 ${24 * admin}px rgba(106,178,242,.7)` : 'none', transform: `scale(${1 + 0.04 * admin * Math.abs(Math.sin((t - T.adminGlow) * 4))})`,
          }}>💬 Admin bilan bog'lanish</div>
        </Msg>
      </div>
      <div style={{ background: '#17212B', padding: '8px 8px 10px' }}>
        <div id="openBtn" style={{ height: 46, borderRadius: 10, background: '#2B5278', color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 600, fontSize: 15.5, transform: `scale(${1 - 0.04 * btnPress})`, filter: `brightness(${1 + 0.25 * btnPress})` }}>🛍 Do'konni ochish</div>
      </div>
      <div style={{ height: 52, background: '#17212B', display: 'flex', alignItems: 'center', gap: 12, padding: '0 14px 6px', color: '#7D8E98', fontSize: 15, borderTop: '1px solid #0E1621' }}>📎<span style={{ flex: 1 }}>Xabar</span>🎤</div>
    </div>
  );
};

/* ---------- Mini app (Telegram ichida) ---------- */
const MiniApp: React.FC<{ t: number }> = ({ t }) => {
  const up = interpolate(t, [T.appUp, T.appUp + 0.5], [0, 1], { ...clamp, easing: outE });
  const down = interpolate(t, [T.appDown, T.appDown + 0.4], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const p = up * (1 - down);
  if (p <= 0) return null;
  const back = (t > T.cartOpen1[0] && t < T.cartOpen1[1] + 0.3) || (t > T.cartOpen2 && t < T.appDown);
  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', background: '#F3F5F2', transform: `translateY(${(1 - p) * 102}%)`, boxShadow: '0 -20px 40px rgba(0,0,0,.4)' }}>
      <StatusBar bg="#123F38" />
      <div style={{ height: 52, background: '#123F38', color: '#fff', display: 'grid', gridTemplateColumns: '90px 1fr 90px', alignItems: 'center', padding: '0 12px', fontFamily: 'Onest' }}>
        <span style={{ fontSize: 15, fontWeight: 500 }}>{back ? '‹ Orqaga' : '✕ Yopish'}</span>
        <span style={{ textAlign: 'center' }}><b style={{ display: 'block', fontSize: 15.5 }}>Ekranchi_Bola</b><small style={{ fontSize: 12, color: '#9FC9BF' }}>bot</small></span>
        <span style={{ textAlign: 'right', fontSize: 20 }}>⋮</span>
      </div>
      <div style={{ position: 'relative', flex: 1, overflow: 'hidden' }}><Shop t={t} /></div>
    </div>
  );
};

/* ---------- push xabar ---------- */
const Push: React.FC<{ t: number }> = ({ t }) => {
  const [a, b] = T.push;
  if (t < a || t > b + 0.5) return null;
  const k = sp(t, a, 14, 170) - interpolate(t, [b, b + 0.4], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const o = ORDER_INFO();
  return (
    <div style={{ position: 'absolute', left: 10, right: 10, top: 52, zIndex: 300, transform: `translateY(${(k - 1) * 150}%)`, background: 'rgba(30,38,44,.94)', borderRadius: 22, padding: '12px 14px', display: 'flex', gap: 12, color: '#fff', boxShadow: '0 18px 40px -10px rgba(0,0,0,.6)', fontFamily: 'Onest, "Noto Color Emoji"' }}>
      <Avatar size={44} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14 }}><b>Ekranchi_Bola</b><span style={{ color: '#9AA6AE', fontSize: 12.5 }}>hozir</span></div>
        <div style={{ fontSize: 14, lineHeight: 1.35, marginTop: 2 }}>🔔 <b>Siz kutgan ekran omborga keldi!</b><br />{o.watched} — {fmtC(o.wRetail)} so'm</div>
      </div>
    </div>
  );
};

/* ---------- telefon ---------- */
const Phone: React.FC<{ t: number }> = ({ t }) => {
  const c = camAt(t);
  const float = Math.sin(t * 1.3) * 0.6;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: 540, height: 960, transformOrigin: '270px 560px', transform: `translateY(${c.y}px) scale(${c.s}) rotate(${c.r + float * 0.3}deg)`, zIndex: 10 }}>
      <div style={{ position: 'absolute', left: 105, top: 222, width: 330, height: 702, borderRadius: 52, background: 'linear-gradient(145deg,#2C3533,#0D1211)', padding: 10, boxShadow: '0 0 0 1.5px #46524F inset, 0 40px 80px -20px rgba(0,0,0,.75)' }}>
        <div style={{ position: 'relative', width: 310, height: 682, borderRadius: 42, overflow: 'hidden', background: '#000' }}>
          <div style={{ position: 'absolute', left: '50%', top: 9, width: 96, height: 28, marginLeft: -48, background: '#000', borderRadius: 20, zIndex: 500 }} />
          <div style={{ position: 'absolute', left: 0, top: 0, width: 390, height: 858, transform: 'scale(.79487)', transformOrigin: '0 0', overflow: 'hidden' }}>
            <Chat t={t} />
            <MiniApp t={t} />
            <Push t={t} />
          </div>
          {/* ekran yaltirashi */}
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(115deg, rgba(255,255,255,.07) 0%, rgba(255,255,255,0) 35%)', pointerEvents: 'none' }} />
        </div>
      </div>
    </div>
  );
};

/* ---------- qo'shimcha overlaylar ---------- */
const Counter: React.FC<{ t: number }> = ({ t }) => {
  const [a, b] = T.counter;
  if (t < a - 0.1 || t > T.addTap) return null;
  const k = sp(t, a, 12, 150);
  const out = interpolate(t, [T.addTap - 0.6, T.addTap - 0.2], [1, 0], clamp);
  const n = Math.round(interpolate(t, [a, b], [0, 456], { ...clamp, easing: outE }));
  return (
    <div style={{ position: 'absolute', right: 22, top: 205, zIndex: 25, transform: `scale(${k * out}) rotate(${(1 - k) * 20 + 6}deg)`, transformOrigin: '80% 20%',
      background: '#F0A531', color: '#2B1A00', borderRadius: 24, padding: '12px 18px 10px', textAlign: 'center', boxShadow: '0 20px 40px -10px rgba(240,165,49,.8)' }}>
      <div style={{ fontFamily: 'Unbounded', fontWeight: 800, fontSize: 40, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{n}</div>
      <div style={{ fontWeight: 700, fontSize: 14, marginTop: 2 }}>ta model</div>
    </div>
  );
};
const TimeSkip: React.FC<{ t: number }> = ({ t }) => {
  const a = T.timeSkip;
  if (t < a || t > T.push[1]) return null;
  const k = sp(t, a, 13, 160) * interpolate(t, [T.push[1] - 0.3, T.push[1]], [1, 0], clamp);
  return (
    <div style={{ position: 'absolute', left: 0, right: 0, top: 168, display: 'flex', justifyContent: 'center', zIndex: 26 }}>
      <div style={{ background: 'rgba(255,255,255,.12)', border: '1px solid rgba(255,255,255,.3)', color: '#fff', borderRadius: 30, height: 34, padding: '0 16px', display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 14.5, opacity: k, transform: `scale(${0.8 + 0.2 * k})` }}>
        ⏱ 2 kundan keyin…
      </div>
    </div>
  );
};
const Shield: React.FC<{ t: number }> = ({ t }) => {
  const [a, b] = T.shield;
  if (t < a || t > b + 0.4) return null;
  const k = sp(t, a, 11, 150) * interpolate(t, [b, b + 0.35], [1, 0], clamp);
  const rays = interpolate(t, [a, a + 0.8], [0.4, 1.3], { ...clamp, easing: outE });
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', zIndex: 40 }}>
      <AbsoluteFill style={{ background: 'rgba(6,24,21,.55)', opacity: Math.min(1, k) }} />
      <div style={{ position: 'absolute', width: 520, height: 520, borderRadius: '50%', opacity: 0.5 * k, transform: `scale(${rays}) rotate(${t * 12}deg)`,
        background: 'repeating-conic-gradient(rgba(240,165,49,.35) 0 8deg, transparent 8deg 22deg)', maskImage: 'radial-gradient(circle, #000 20%, transparent 70%)', WebkitMaskImage: 'radial-gradient(circle, #000 20%, transparent 70%)' }} />
      <div style={{ position: 'relative', textAlign: 'center', transform: `scale(${0.4 + 0.6 * k})`, opacity: Math.min(1, k * 1.3) }}>
        <svg width="150" height="170" viewBox="0 0 24 27" style={{ filter: 'drop-shadow(0 18px 30px rgba(240,165,49,.6))' }}>
          <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FFC768" /><stop offset="1" stopColor="#D88812" /></linearGradient></defs>
          <path d="M12 1 2 5v7c0 6.6 4.3 11.9 10 14 5.7-2.1 10-7.4 10-14V5L12 1z" fill="url(#sg)" />
          <path d="m7.5 13.5 3 3 6-6.5" stroke="#2B1A00" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round"
            strokeDasharray="20" strokeDashoffset={20 * (1 - interpolate(t, [a + 0.3, a + 0.7], [0, 1], clamp))} />
        </svg>
        <div style={{ fontFamily: 'Unbounded', fontWeight: 800, fontSize: 56, color: '#fff', lineHeight: 1, marginTop: 14, letterSpacing: '-.03em' }}>2 OY</div>
        <div style={{ fontFamily: 'Unbounded', fontWeight: 800, fontSize: 30, color: '#F0A531', letterSpacing: '.04em', marginTop: 6 }}>KAFOLAT</div>
        <div style={{ color: '#CFE9E2', fontSize: 16, fontWeight: 600, marginTop: 12 }}>Barcha displeylarga</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- final ---------- */
const Outro: React.FC<{ t: number }> = ({ t }) => {
  if (t < T.logo - 0.05) return null;
  const lk = sp(t, T.logo, 11, 140);
  const chips = ['456 ta model', 'Optom va dona', '2 oy kafolat', 'BTS · Taksi'];
  const sk = sp(t, T.searchType[0] - 0.25, 14, 160);
  const q = typed(t, TYPING[4]);
  const rk = sp(t, T.result, 13, 170);
  const ck = sp(t, T.cta, 10, 140);
  const pulse = t > T.cta + 0.5 ? 1 + 0.035 * Math.sin((t - T.cta) * 5) : 1;
  return (
    <AbsoluteFill style={{ alignItems: 'center', paddingTop: 150, textAlign: 'center', zIndex: 35 }}>
      <div style={{ fontFamily: 'Unbounded', fontWeight: 800, color: '#fff', fontSize: 54, letterSpacing: '-.03em', lineHeight: 0.95, transform: `scale(${0.6 + 0.4 * lk})`, opacity: Math.min(1, lk * 1.4) }}>
        Ekranchi<span style={{ display: 'block', color: '#F0A531' }}>_Bola</span>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 10, marginTop: 26, padding: '0 30px' }}>
        {chips.map((c, i) => {
          const k = sp(t, T.logo + 0.35 + i * 0.1, 14, 180);
          return <span key={c} style={{ height: 40, padding: '0 16px', borderRadius: 40, background: 'rgba(255,255,255,.08)', border: '1px solid rgba(255,255,255,.22)', color: '#fff', display: 'inline-flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 15, opacity: k, transform: `translateY(${(1 - k) * 20}px)` }}><i style={{ fontStyle: 'normal', color: '#F0A531' }}>✓</i>{c}</span>;
        })}
      </div>
      {/* Telegram qidiruvi */}
      <div style={{ width: 430, marginTop: 44, opacity: Math.min(1, sk * 1.3), transform: `translateY(${(1 - sk) * 40}px)` }}>
        <div style={{ height: 54, borderRadius: 16, background: '#17212B', display: 'flex', alignItems: 'center', gap: 12, padding: '0 16px', color: '#fff', fontSize: 18, boxShadow: '0 20px 40px -14px rgba(0,0,0,.6)' }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7D8E98" strokeWidth="2.2"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
          <span style={{ color: q ? '#fff' : '#7D8E98' }}>{q ? '@' + q : 'Qidirish'}{t < T.result && Math.floor(t * 2.4) % 2 === 0 && <span style={{ display: 'inline-block', width: 2, height: 21, background: '#6AB2F2', verticalAlign: -4, marginLeft: 2 }} />}</span>
        </div>
        <div style={{ marginTop: 8, borderRadius: 16, background: '#17212B', display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', textAlign: 'left', opacity: rk, transform: `translateY(${(1 - rk) * -14}px) scale(${0.96 + 0.04 * rk})`, boxShadow: '0 20px 40px -14px rgba(0,0,0,.6)' }}>
          <Avatar size={48} />
          <div><b style={{ color: '#fff', fontSize: 17 }}>Ekranchi_Bola</b><div style={{ color: '#6AB2F2', fontSize: 15 }}>@{BOT}</div></div>
        </div>
      </div>
      <div style={{ marginTop: 40, height: 66, padding: '0 30px', borderRadius: 20, background: '#F0A531', color: '#2B1A00', display: 'inline-flex', alignItems: 'center', gap: 12, fontFamily: 'Unbounded', fontWeight: 800, fontSize: 19,
        boxShadow: `0 18px ${40 + 20 * (pulse - 1) * 20}px -12px rgba(240,165,49,.8)`, transform: `scale(${ck * pulse})`, opacity: Math.min(1, ck * 1.5) }}>
        <svg viewBox="0 0 24 24" width="26" height="26" fill="#2B1A00"><path d="M21.9 4.6 18.7 19.7c-.2 1-.9 1.3-1.8.8l-4.8-3.6-2.3 2.2c-.3.3-.5.5-1 .5l.3-4.9 8.9-8c.4-.3-.1-.5-.6-.2L6.4 13.4l-4.7-1.5c-1-.3-1-1 .2-1.5L20.6 3.3c.9-.3 1.6.2 1.3 1.3z" /></svg>
        Hoziroq buyurtma bering
      </div>
    </AbsoluteFill>
  );
};

/* ---------- barmoq ---------- */
const Finger: React.FC<{ t: number }> = ({ t }) => {
  const ref = useRef<HTMLDivElement>(null);
  const rip = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = ref.current!, rp = rip.current!;
    const stage = document.getElementById('stage')!.getBoundingClientRect();
    const S = stage.width / 540;
    const pos = (sel: string) => {
      const n = document.querySelector(sel);
      if (!n) return null;
      const r = n.getBoundingClientRect();
      return { x: (r.left + r.width / 2 - stage.left) / S, y: (r.top + r.height / 2 - stage.top) / S };
    };
    const show = FINGER_SHOW.find(([a, b]) => t >= a && t <= b);
    const vis = show ? Math.min(interpolate(t, [show[0], show[0] + 0.2], [0, 1], clamp), interpolate(t, [show[1] - 0.2, show[1]], [1, 0], clamp)) : 0;
    // keyingi va oldingi bosish
    let i = TAPS.findIndex(([at]) => at >= t);
    if (i < 0) i = TAPS.length - 1;
    const next = TAPS[i], prev = TAPS[i - 1];
    const pn = pos(next[1]);
    let p = pn;
    if (prev && show && prev[0] >= show[0]) {
      const pp = pos(prev[1]);
      const travel = Math.min(0.5, next[0] - prev[0] - 0.15);
      const k = interpolate(t, [next[0] - travel, next[0] - 0.08], [0, 1], { ...clamp, easing: io });
      if (pp && pn) p = { x: pp.x + (pn.x - pp.x) * k, y: pp.y + (pn.y - pp.y) * k - Math.sin(k * Math.PI) * 28 };
    } else if (pn && show) {
      // kirib kelish: pastdan
      const k = interpolate(t, [show[0], next[0] - 0.08], [0, 1], { ...clamp, easing: outE });
      p = { x: pn.x + (1 - k) * 60, y: pn.y + (1 - k) * 160 };
    }
    // oxirgi bosishdan keyin o'sha joyda turadi
    const last = [...TAPS].reverse().find(([at]) => at <= t);
    if (last && show && last[0] >= show[0] && (!next || next[0] > show[1])) { const pl = pos(last[1]); if (pl) p = { x: pl.x + (t - last[0]) * 30, y: pl.y + (t - last[0]) * 60 }; }
    if (!p) { el.style.opacity = '0'; rp.style.opacity = '0'; return; }
    const press = TAPS.reduce((m, [at]) => Math.max(m, interpolate(t, [at - 0.06, at, at + 0.14], [0, 1, 0], clamp)), 0);
    el.style.opacity = String(vis);
    el.style.transform = `translate(${p.x - 23}px, ${p.y - 23}px) scale(${1 - 0.22 * press})`;
    const lt = TAPS.filter(([at]) => at <= t && t < at + 0.55).pop();
    if (lt && vis > 0) {
      const k = (t - lt[0]) / 0.55;
      rp.style.opacity = String((1 - k) * 0.9);
      rp.style.transform = `translate(${p.x - 10}px, ${p.y - 10}px) scale(${0.6 + 3 * k})`;
    } else rp.style.opacity = '0';
  });
  return (
    <>
      <div ref={rip} style={{ position: 'absolute', left: 0, top: 0, width: 20, height: 20, borderRadius: '50%', border: '3px solid #fff', zIndex: 59, opacity: 0 }} />
      <div ref={ref} style={{ position: 'absolute', left: 0, top: 0, width: 46, height: 46, borderRadius: '50%', zIndex: 60, opacity: 0,
        background: 'radial-gradient(circle, rgba(255,255,255,.96) 0 38%, rgba(255,255,255,.55) 40% 62%, rgba(255,255,255,0) 64%)', boxShadow: '0 6px 18px rgba(0,0,0,.35)' }} />
    </>
  );
};

const Flash: React.FC<{ t: number }> = ({ t }) => {
  const f = (at: number, a: number) => interpolate(t, [at, at + 0.08, at + 0.45], [0, a, 0], clamp);
  const o = Math.max(f(5.12, 0.45), f(T.wholesale, 0.25), f(T.logo, 0.4), f(T.shield[0], 0.3));
  return <AbsoluteFill style={{ background: 'radial-gradient(circle at 50% 50%, rgba(214,248,255,.9), rgba(214,248,255,0) 60%)', opacity: o, zIndex: 45, pointerEvents: 'none' }} />;
};

/* ---------- audio ---------- */
const voiceActive = (t: number) => {
  // diktor gapirayotganida musiqa pasayadi (silliq)
  let v = 0;
  for (const [a, b] of VOICE_SEGMENTS) v = Math.max(v, interpolate(t, [a - 0.15, a, b, b + 0.35], [0, 1, 1, 0], clamp));
  return v;
};
const AudioTrack: React.FC = () => (
  <>
    <Sequence from={Math.round(VO_OFFSET * FPS)}><Audio src={staticFile('voice.mp3')} volume={1} /></Sequence>
    <Audio src={staticFile('sfx/beat.wav')} volume={(f) => {
      const t = f / FPS;
      const fade = interpolate(t, [0, 1.2, DURATION - 2.2, DURATION - 0.2], [0, 1, 1, 0], clamp);
      return fade * (0.26 - 0.17 * voiceActive(t));
    }} />
    {SFX.map(([t, n, g], i) => (
      <Sequence key={i} from={Math.max(0, Math.round(t * FPS))} durationInFrames={Math.round(2 * FPS)}>
        <Audio src={staticFile(`sfx/${n}.wav`)} volume={g * 0.85} />
      </Sequence>
    ))}
  </>
);

export const Promo: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame();
  const t = frame / FPS;
  return (
    <AbsoluteFill style={{ background: '#0A2723' }}>
      <style>{FONT_CSS}</style>
      <div id="stage" style={{ position: 'absolute', left: 0, top: 0, width: 540, height: 960, transform: 'scale(2)', transformOrigin: '0 0', overflow: 'hidden', fontFamily: 'Onest, "Noto Color Emoji", sans-serif' }}>
        <Background t={t} />
        <Captions t={t} />
        <TimeSkip t={t} />
        <Phone t={t} />
        <Counter t={t} />
        <Intro t={t} />
        <Shield t={t} />
        <Outro t={t} />
        <Flash t={t} />
        <Finger t={t} />
      </div>
      <AudioTrack />
    </AbsoluteFill>
  );
};
