const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const html = fs.readFileSync(path.join(__dirname, 'ui.html'), 'utf8');
const context = vm.createContext({});
vm.runInContext(html.slice(html.indexOf('function adjustmentGeometry('),
  html.indexOf('async function openAdjust(')), context);

test('straightened exports have no empty corners for any supported orientation', () => {
  for (const [w, h] of [[4000, 3000], [3000, 4000], [768, 576], [1000, 1000]]) {
    for (let turns = -4; turns <= 4; turns++) {
      for (const angle of [-15, -10, -5, 0, 5, 10, 15]) {
        const g = context.adjustmentGeometry(w, h, turns, angle);
        const c = Math.cos(-g.radians), s = Math.sin(-g.radians);
        for (const x of [-g.width / 2, g.width / 2]) {
          for (const y of [-g.height / 2, g.height / 2]) {
            assert(Math.abs(c * x - s * y) <= w / 2 + 1e-7);
            assert(Math.abs(s * x + c * y) <= h / 2 + 1e-7);
          }
        }
        if (angle === 0) {
          assert.equal(g.width, Math.abs(turns) % 2 ? h : w);
          assert.equal(g.height, Math.abs(turns) % 2 ? w : h);
        }
      }
    }
  }
});

test('preview and export use the same rotation and preserve source pixels', () => {
  const bitmap = { width: 4000, height: 3000 };
  function render(preview) {
    const calls = [];
    const drawing = Object.fromEntries(['translate', 'scale', 'rotate', 'drawImage',
      'setTransform', 'beginPath', 'moveTo', 'lineTo', 'stroke']
      .map(name => [name, (...args) => calls.push([name, ...args])]));
    const canvas = { getContext: () => drawing };
    context.drawAdjustment(canvas, bitmap, 1, 10, preview);
    return { canvas, calls };
  }
  const preview = render(true), output = render(false);
  assert.deepEqual(preview.calls.find(c => c[0] === 'rotate'), output.calls.find(c => c[0] === 'rotate'));
  assert.deepEqual(preview.calls.find(c => c[0] === 'drawImage'), output.calls.find(c => c[0] === 'drawImage'));
  assert(preview.canvas.width <= 900 && preview.canvas.height <= 600);
  assert(output.canvas.width > preview.canvas.width);
  assert(preview.calls.some(c => c[0] === 'stroke'), 'Preview shows the alignment grid');
  assert(!output.calls.some(c => c[0] === 'stroke'), 'Export contains no grid');
  assert(preview.calls.findIndex(c => c[0] === 'setTransform') >
    preview.calls.findIndex(c => c[0] === 'drawImage'), 'Grid stays horizontal and vertical after rotation');
  assert.deepEqual(bitmap, { width: 4000, height: 3000 });
});

test('all inline scripts parse', () => {
  for (const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) new vm.Script(m[1]);
});
