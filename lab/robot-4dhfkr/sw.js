/**
 * 邏輯機器人 — Service Worker
 *
 * 目的：讓「加到主畫面」之後可以離線玩（教室網路不穩時很重要）。
 *
 * 策略：
 *   ① 導覽請求（HTML）→ 先試網路，3 秒沒回應就用快取。
 *      為什麼不用 cache-first？因為這樣你更新版本後，學生會一直拿到舊版，
 *      要清快取才會更新——對「我會持續改」的專案來說是災難。
 *   ② 其他資源（icon、manifest）→ cache-first，反正很少變。
 *
 * ⚠️ CACHE 版本由 build 腳本依單檔內容的雜湊自動改寫，
 *    所以每次改版都會產生新的快取、舊的會被清掉。
 */
const CACHE = 'robot-puzzle-39b2b431b3';
const SHELL = './index.html';
// 這些在 install 時就全部抓下來 → 離線開啟時不會缺圖
const PRECACHE = [
  SHELL,
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((c) => c.addAll(PRECACHE))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 只管自己站上的東西

  // ① 導覽：網路優先（3 秒逾時），失敗才用快取
  if (req.mode === 'navigate') {
    event.respondWith(
      (async () => {
        try {
          const res = await Promise.race([
            fetch(req),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 3000)),
          ]);
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(SHELL, copy));
          }
          return res;
        } catch (err) {
          const hit = await caches.match(SHELL);
          return hit || Response.error();
        }
      })()
    );
    return;
  }

  // ② 其他資源：快取優先
  event.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req).then((res) => {
          if (res && res.ok && res.type === 'basic') {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
    )
  );
});
