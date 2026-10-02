// market.html va data.js dan video uchun kerakli fayllarni yasaydi (do'kon o'zgarsa, qayta ishga tushiring).
const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', '..');
const src = path.join(__dirname, '..', 'src');
const html = fs.readFileSync(path.join(root, 'market.html'), 'utf8');

// 1) Mahsulotlar
const data = fs.readFileSync(path.join(root, 'data.js'), 'utf8');
const products = new Function(data + ';return productsData;')();
fs.writeFileSync(path.join(src, 'products.json'), JSON.stringify(products));

// 2) prettyModel funksiyasi
const lines = html.split('\n');
const s = lines.findIndex((l) => l.includes('function prettyModel(raw, brand)'));
const e = lines.findIndex((l, i) => i > s && l.includes('return { main, alts: parts'));
fs.writeFileSync(path.join(src, 'pretty.ts'), [
  '// @ts-nocheck', '// market.html dagi prettyModel nusxasi (tools/prepare.js yasaydi)',
  'export function prettyModel(raw, brand) {', ...lines.slice(s + 1, e + 2),
  "export const norm = (s) => String(s).toLowerCase().replace(/[\\s\\-_/.()]+/g, '');",
  "export const typeClass = (t) => /oled/i.test(t) ? 'oled' : /servis/i.test(t) ? 'servis' : /tft/i.test(t) ? 'tft' : /incell/i.test(t) ? 'incell' : 'ips';",
].join('\n'));

// 3) CSS: animatsiya va transitionlar olib tashlanadi (Remotion'da hamma harakat kadrdan hisoblanadi)
let c = html.split('<style>')[1].split('</style>')[0];
c = c.replace(/@media[^{]*\{([^{}]*\{[^}]*\})*[^}]*\}/g, '');
c = c.replace(/:root\s*\{/, '.shop {').replace(/html, body \{[^}]*\}/, '').replace(/\n\s*body \{/, '\n.shopbody {');
c = c.replace(/(^|[;{\s])transition:[^;}]*;?/g, '$1').replace(/(^|[;{\s])animation:[^;}]*;?/g, '$1');
c = c.replace(/@keyframes[^{]*\{([^{}]*\{[^}]*\})*[^}]*\}/g, '');
c = c.replace(/\.logo/g, '.shop .logo');
fs.writeFileSync(path.join(src, 'shop.processed.css'), c);
console.log(`Tayyor: ${products.length} ta mahsulot, prettyModel, CSS`);
