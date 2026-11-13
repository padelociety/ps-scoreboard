const CACHE = 'ps-control-v37';  // v37: [Save Set] 두 번 누름 막기(0–0 세트 · 슈퍼TB 중 · 경기 끝이면 저장 안 함) · 버튼에 저장할 점수 · 저장 결과를 화면 한가운데 크게. 이전 v36: 빈 클립(0바이트·디코드 실패)은 없는 것으로 쳐서 브라우저 TTS 로 떨어진다(예전엔 무음). 이전 v35: 클립 무음 자르기가 마찰음 첫소리(fifteen 의 f)를 자르던 것 — 가장자리를 -50dB 까지 늘린다. 이전 v34: 듀스 콜 'First deuce'·'Second deuce' · 어드밴티지 콜 'Advantage in/out'(서브권 기준). 이전 v33: 방송 위 띠 소식(scoreboard.ticker)을 점수 푸시가 지우지 않고 되싣는다(banner-edit.html 이 적는다). 이전 v32: 대회 운영 점검(2026-11-12) — 대회 경기를 고르면 2듀스·형식대로 게임 수·슈퍼TB 꺼짐 · set2super 1–1 이면 [Save Set] 이 슈퍼TB 를 켠다 · 타이브레이크 7점·슈퍼TB 10점(2점 차)을 따면 그 자리에서 게임/3세트 저장 · 40-40 에서 −Point 정정해도 듀스 횟수를 지우지 않는다. 이전 v31: 리그·매치·목소리 목록을 innerHTML 대신 Option 으로 만든다(서버가 준 리그·선수 이름이 HTML 로 풀리던 것 — 심판 콘솔에 운영자 토큰이 있다) · 세트 칩 값도 글자로만. TV b25 는 대회 팀·선수 이름을 이스케이프. 이전 v30: 리그 결과 저장 상태 줄에 이 경기 PAR 이 어떻게 됐는지 붙인다 — 저장 뒤 다시 읽은 그 경기의 서버 기록(parStatus — 앱 결과 칩과 같은 말)이 먼저, 없으면 서버 문장 끝 괄호('(PAR 반영 완료)' · '(친선 매치 — PAR 반영 안 됨)') · 점수 정정의 '재계산 불가' 는 어디 있든 ⚠️ · 저장 중엔 버튼을 잠근다(두 번 누르면 같은 결과가 두 번 갔다). 예전엔 응답을 버리고 '순위 반영' 만 적었다. 이전 v29: 방송 이름 — 리그 이름 불러오기가 선수의 onAir.name(닉네임을 고른 회원은 닉네임, 비면 '선수')으로 채운다(TV·OBS·앱 라이브에 나가는 이름) · 매치 목록은 실명 그대로. 이전 v28: 푸시할 때 visible:true(리그 태블릿이 남긴 false 로 OBS 점수판이 사라지던 것) · 초기화·리그 이름 불러오기가 고른 녹아웃 경기를 놓는다 · Today 는 오늘(·어제 시작한 진행중)·두 팀 소속 대회만. 이전 v27: 글꼴 IBM Plex Sans KR(앱·웹 통일 — 마루부리·Playfair·Inter 걷어냄). 이전 v26: 헤더에 빌드 배지(b26) — 어느 버전이 떠 있는지 눈으로 확인할 방법이 없었다. [Set · Match] 버튼은 꺼져 있어도 이름표를 달고, 켜지면 눈에 들어온다. 이전 v25: 대회 점수 저장을 **녹아웃(8강·4강·결승)에만** — 조별리그는 선수 태블릿이 올리는 자리라 덮어쓰면 안 된다. 세트제 라운드는 세트 승수+세트별 점수로 보낸다. 이전 v23: 세트·매치 포인트 콜 버튼(Set · Match) — 판정은 TV·OBS 와 같은 함수다. 이전 v22: 세트 게임 수를 설정에서 고른다(4·6·8) — 6 이 코드에 박혀 있어 8게임 경기가 6-6 에서 제멋대로 타이브레이크로 넘어갔다. 이전 v21: 페이드 길이를 설정 슬라이더로(기본 3초) — 콜 덕킹은 그대로 빠르게
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
