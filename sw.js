const CACHE = 'ps-control-v10';  // v10: 음성 목소리·톤 선택 추가 — 미리캐시된 옛 index.html 을 확실히 버리게 한다
const ASSETS = ['/ps-scoreboard/', '/ps-scoreboard/index.html'];

self.addEventListener('install', e => {
    e.waitUntil(
          caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(() => {})
        );
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
          caches.keys().then(keys =>
                  Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
                                 )
        );
    self.clients.claim();
});

self.addEventListener('fetch', e => {
    if (e.request.url.includes('firebase') || e.request.url.includes('google')) {
          return;
    }
    e.respondWith(
          fetch(e.request).catch(() => caches.match(e.request))
        );
});
