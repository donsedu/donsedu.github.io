// 模型縮圖產生器（本機 + GitHub Actions 通用）
// 用法: node thumb.js <model_rel_path> <out_png>
//   model_rel_path 如 viewer/models/foo.ldr（相對於 cwd 的 repo root）
// 流程: 起臨時 http.server -> 開檢視器 ?model=<name> -> 跳最後一步 -> 截 canvas
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const modelRel = process.argv[2];
const outPng = process.argv[3];
if (!modelRel || !outPng) {
  console.error('用法: node thumb.js <model_rel_path> <out_png>');
  process.exit(1);
}

const safeName = path.basename(modelRel).replace(/\.ldr$/i, '');
let PORT = 8799;

async function findFreePort() {
  const net = require('net');
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.listen(0, '127.0.0.1', () => {
      const p = srv.address().port;
      srv.close(() => resolve(p));
    });
    srv.on('error', reject);
  });
}

async function main() {
  PORT = await findFreePort();
  // 起 http server
  const server = spawn('python3', ['-m', 'http.server', String(PORT)], { stdio: 'ignore', detached: false });
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(800);

  try {
    const { chromium } = require('playwright');
    const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    const diag = [];
    page.on('pageerror', e => diag.push('PAGEERROR: ' + String(e.message).slice(0, 400)));
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') diag.push('[' + m.type() + '] ' + m.text().slice(0, 300)); });
    page.on('requestfailed', r => diag.push('REQFAIL: ' + r.url().slice(0, 150) + ' -> ' + ((r.failure() && r.failure().errorText) || '')));
    page.on('response', r => { if (r.status() >= 400) diag.push('HTTP' + r.status() + ': ' + r.url().slice(0, 200)); });
    await page.goto(`http://localhost:${PORT}/viewer/custom_instructions.htm?model=${encodeURIComponent(safeName)}`,
      { waitUntil: 'load', timeout: 90000 });

    // 等 manager + 渲染
    let ready = false;
    for (let i = 0; i < 45; i++) {
      await sleep(2000);
      ready = await page.evaluate(() =>
        typeof manager !== 'undefined' && manager.renderer &&
        manager.renderer.info && manager.renderer.info.render.triangles > 0);
      if (ready) break;
    }
    if (!ready) {
      // dump 診斷：manager state + 頁面錯誤，供 Actions log 定位
      let st = {};
      try {
        st = await page.evaluate(() => ({
          hasManager: typeof manager !== 'undefined',
          stepHandler: typeof manager !== 'undefined' && manager.stepHandler ? 'yes' : 'no',
          tri: typeof manager !== 'undefined' && manager.renderer && manager.renderer.info ? manager.renderer.info.render.triangles : -1,
          title: document.title,
          modelEl: document.getElementById('model_title') ? document.getElementById('model_title').textContent : null
        }));
        // loader 內部狀態：mainModel vs partTypes key（null.steps 根因比對）
        const ld = await page.evaluate(() => {
          if (typeof manager === 'undefined' || !manager.ldrLoader) return { err: 'no loader' };
          const ldr = manager.ldrLoader;
          const keys = Object.keys(ldr.partTypes || {});
          return {
            mainModel: ldr.mainModel,
            modelKeys: keys.filter(k => k.includes('火車') || k.includes('ESM') || k.includes('esm')),
            keyCount: keys.length,
            mainHas: (ldr.mainModel && ldr.partTypes) ? ldr.partTypes.hasOwnProperty(ldr.mainModel) : null
          };
        });
        st.loader = ld;
      } catch (e) { st = { evalErr: String(e) }; }
      console.error('DIAG state=' + JSON.stringify(st));
      console.error('DIAG events:\n' + diag.slice(0, 40).join('\n'));
      throw new Error('模型載入逾時');
    }

    // 跳最後一步（完整成品）
    await page.evaluate(() => {
      const total = manager.stepHandler.totalNumberOfSteps;
      for (let i = manager.currentStep; i < total; i++) manager.nextStep();
    });
    await sleep(2500);

    // 截 canvas（乾淨無 UI）
    const box = await page.locator('#main_canvas').boundingBox();
    if (!box) throw new Error('找不到 canvas');
    const buf = await page.screenshot({
      clip: { x: box.x, y: box.y, width: box.width, height: box.height },
      type: 'png'
    });
    fs.writeFileSync(outPng, buf);
    console.log(`✅ 縮圖: ${outPng} (${buf.length} bytes)`);
    await browser.close();
    process.exit(0);
  } catch (e) {
    console.error('❌ 縮圖失敗: ' + e.message);
    process.exit(1);
  } finally {
    server.kill();
  }
}

main();
