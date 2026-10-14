// 用 jsdom 真实渲染 dashboard_static.html，验证脚本执行无错、关键容器有内容
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const file = process.argv[2] || 'dashboard_static.html';
const html = fs.readFileSync(path.resolve(file), 'utf8');

const errors = [];
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(window) {
    window.addEventListener('error', (e) => {
      errors.push('window.onerror: ' + (e.error ? (e.error.stack || e.error.message) : e.message));
    });
    window.addEventListener('unhandledrejection', (e) => {
      errors.push('unhandledrejection: ' + (e.reason && (e.reason.stack || e.reason.message) || e.reason));
    });
    const origErr = window.console.error;
    window.console.error = function (...a) {
      errors.push('console.error: ' + a.map(x => (x && x.stack) || String(x)).join(' '));
      origErr.apply(window.console, a);
    };
  },
});

setTimeout(() => {
  const d = dom.window.document;
  const ids = ['kpiGrid', 'dtb', 'dth', 'moverArea', 'rawTb', 'wl'];
  console.log('=== 渲染结果 ===');
  for (const id of ids) {
    const el = d.getElementById(id);
    const len = el ? (el.innerHTML || '').length : -1;
    console.log(`${id.padEnd(12)} innerHTML 长度 = ${len}${len === 0 ? '   ⚠️ 空' : ''}${el ? '' : '   ⚠️ 元素不存在'}`);
  }
  const trCount = d.querySelectorAll('#dtb tr').length;
  console.log('排行榜行数 =', trCount);
  const title = d.querySelector('.kpi, #kpiGrid .kc');
  console.log('KPI 卡片数 =', d.querySelectorAll('#kpiGrid .kc').length);
  console.log('页面标题 =', d.title || '(无)');

  console.log('\n=== 运行时错误 ===');
  if (errors.length === 0) console.log('无 ✅');
  else errors.slice(0, 10).forEach(e => console.log(' -', e.slice(0, 300)));

  process.exit(trCount > 0 && errors.length === 0 ? 0 : 2);
}, 4000);
