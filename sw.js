const CACHE = 'ps-control-v23';  // v23: 세트·매치 포인트 콜 버튼(Set · Match) — 판정은 TV·OBS 와 같은 함수다. 이전 v22: 세트 게임 수를 설정에서 고른다(4·6·8) — 6 이 코드에 박혀 있어 8게임 경기가 6-6 에서 제멋대로 타이브레이크로 넘어갔다. 이전 v21: 페이드 길이를 설정 슬라이더로(기본 3초) — 콜 덕킹은 그대로 빠르게
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
