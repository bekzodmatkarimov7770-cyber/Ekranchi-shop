// market.html va admin.html ichidagi <script> bloklari sintaksis xatosiz ekanini tekshiradi.
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
let bad = 0;
for (const file of ['market.html', 'admin.html', 'data.js']) {
  const src = readFileSync(new URL('../' + file, import.meta.url), 'utf8');
  const blocks = file.endsWith('.js') ? [src] : [...src.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  blocks.forEach((code, i) => {
    try { new vm.Script(code, { filename: `${file}#${i}` }); }
    catch (e) { bad++; console.error(`${file} (script ${i}): ${e.message}`); }
  });
  console.log(`${file}: ${blocks.length} ta blok tekshirildi`);
}
process.exit(bad ? 1 : 0);
