# 스코어보드 콘솔 음성 콜 클립 생성기.
#
#   python pwa-scoreboard/voice-gen.py --voice en-US-ChristopherNeural --key christopher
#
# 콜 문구는 닫힌 집합이다 — index.html 의 speakPoint/speakGame/speakSet 이 만드는 문장을
# 여기서 똑같이 만들어 mp3 로 굽는다. 콘솔은 문장을 slug 로 바꿔 audio/<key>/<slug>.mp3 를
# 찾고, 없으면 브라우저 TTS 로 떨어진다. 그래서 문장 규칙이 바뀌면 여기도 같이 바꿔야 한다.
#
# 왜 클립인가: 브라우저 TTS 는 태블릿에 깔린 음성에 좌우된다(싸구려 목소리·비원어민 발음).
# Microsoft 신경망 음성(edge-tts)으로 한 번 만들어 두면 기종·언어팩·와이파이와 무관하게
# 항상 같은 원어민 발음이, 지연 없이 나온다.
#
# 준비: python -m pip install edge-tts
import argparse, asyncio, json, os, re, sys

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts 가 없다: python -m pip install edge-tts")

PT = ['love', 'fifteen', 'thirty', 'forty']
NUM = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
       'eleven', 'twelve']


def games_phrase(a, b):
    """index.html gamesPhrase() 와 글자 단위로 같아야 한다."""
    if a == b:
        return f"{NUM[a]} {'game' if a == 1 else 'games'} all"
    hi, lo = max(a, b), min(a, b)
    return f"{NUM[hi]} {'game' if hi == 1 else 'games'} to {NUM[lo]}"


def phrases():
    out = []
    # 포인트 — 서브 팀 먼저 (a,b 순서 그대로 문장이 되므로 12+3)
    for sp in range(4):
        for rp in range(4):
            if sp == rp:
                if sp < 3:
                    out.append(f"{PT[sp]} all")
            else:
                out.append(f"{PT[sp]}, {PT[rp]}")
    # 'Set point'·'Match point' — 콘솔의 [Set · Match] 버튼이 부른다(critOf 판정).
    out += ['Deuce', 'Advantage', 'Star point', 'Golden point', 'Set point', 'Match point',
            'Undo', 'Voice on']
    # b34(2026-11-13): 몇 번째 듀스 · 서브권 기준 어드밴티지 — index.html pointCallOf() 와 같은 말.
    out += ['Advantage in', 'Advantage out']
    out += [f'{o} deuce' for o in ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']]
    out.append('Fifteen, love. Deuce. Advantage, server.')     # 목소리 고르기 샘플
    # 게임 — 1~9 게임 범위. ⚠️ 8게임 세트(gameTarget=8)가 생기면서 8·9 가 나온다 —
    #    안 굽으면 그 콜만 브라우저 TTS 로 떨어져 목소리가 바뀜다.
    for hi in range(1, 10):
        for lo in range(0, hi):
            out.append(f"Game. {games_phrase(hi, lo)}.")
        out.append(f"Game. {games_phrase(hi, hi)}.")
    # 세트 — 4·6·8게임 세트의 끝나는 점수를 전부(4-5 / 6-7 / 8-9), 1~3세트
    for ordn in ['first', 'second', 'third']:
        for hi in (4, 5, 6, 7, 8, 9):
            for lo in range(0, hi):
                out.append(f"Game and {ordn} set. {games_phrase(hi, lo)}.")
            out.append(f"Game and {ordn} set. {games_phrase(hi, hi)}.")
    # 타이브레이크 숫자 — 콘솔이 "x, y" 를 두 클립으로 이어 붙인다
    out += NUM
    # 중복 제거, 순서 유지
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq


# 콩글리시(2026-11-13 · 사용자 "보이스 중에 콩글리시를 원하는 사람들이 있네") — 한국어 신경망 음성(ko-KR)에게
# 영어 콜을 **한글로 적어** 읽힌다("Fifteen, love" → "피프틴, 러브"). 파일 이름(slug)은 영어 문장 그대로라
# 콘솔은 아무것도 바꾸지 않는다 — 목소리 목록에서 고르기만 하면 된다. 모르는 낱말이 나오면 굽기 전에 멈춘다
# (영어 철자를 한국어 음성이 읽으면 "에프 아이 에프…" 가 된다).
KONGLISH = {
    'love': '러브', 'fifteen': '피프틴', 'thirty': '써티', 'forty': '포티', 'all': '올',
    'deuce': '듀스', 'advantage': '어드밴티지', 'in': '인', 'out': '아웃', 'server': '서버',
    'star': '스타', 'golden': '골든', 'point': '포인트', 'set': '셋', 'match': '매치',
    'undo': '언두', 'voice': '보이스', 'on': '온', 'game': '게임', 'games': '게임', 'to': '투', 'and': '앤',
    'first': '퍼스트', 'second': '세컨', 'third': '써드', 'fourth': '포스', 'fifth': '피프스', 'sixth': '식스스',
    'seventh': '세븐스', 'eighth': '에잇스', 'ninth': '나인스', 'tenth': '텐스',
    'zero': '제로', 'one': '원', 'two': '투', 'three': '쓰리', 'four': '포', 'five': '파이브', 'six': '식스',
    'seven': '세븐', 'eight': '에잇', 'nine': '나인', 'ten': '텐', 'eleven': '일레븐', 'twelve': '트웰브',
}


def konglish(text):
    def word(m):
        w = m.group(0)
        k = KONGLISH.get(w.lower())
        if k is None:
            raise KeyError(f"콩글리시 표에 없는 낱말: {w!r} (문장: {text!r}) — KONGLISH 에 한 줄 더하세요")
        return k
    return re.sub(r'[A-Za-z]+', word, text)


def slug(text):
    """index.html slug() 와 같아야 한다: 소문자, 영숫자 외는 '-', 양끝 '-' 제거."""
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', text.lower()))


async def gen_one(sem, voice, rate, text, path, spoken=None):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return 'skip'
    async with sem:
        err = None
        for attempt in range(3):
            try:
                await edge_tts.Communicate(spoken or text, voice, rate=rate).save(path)
                return 'ok'
            except Exception as e:  # 네트워크 흔들림 — 재시도
                err = e
                await asyncio.sleep(1 + attempt)
        return f'FAIL {err}'


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voice', required=True, help='edge-tts 음성 이름 (예 en-US-ChristopherNeural)')
    ap.add_argument('--key', required=True, help='폴더 이름 (예 christopher)')
    ap.add_argument('--rate', default='-5%', help='말 속도 (심판 콜은 살짝 느리게)')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio'))
    ap.add_argument('--konglish', action='store_true', help='한국어 음성에게 콜을 한글로 적어 읽힌다(콩글리시)')
    ap.add_argument('--label', help='다 구운 뒤 audio/voices.json 에 이 이름으로 올린다(예 "콩글리시 · 한국 남")')
    ap.add_argument('--gender', default='m', choices=['m', 'f'])
    a = ap.parse_args()

    folder = os.path.join(a.out, a.key)
    os.makedirs(folder, exist_ok=True)
    ps = phrases()
    spoken = {p: (konglish(p) if a.konglish else p) for p in ps}   # 모르는 낱말이면 여기서 멈춘다(굽기 전)
    sem = asyncio.Semaphore(6)
    tasks = [gen_one(sem, a.voice, a.rate, p, os.path.join(folder, slug(p) + '.mp3'), spoken[p]) for p in ps]
    results = await asyncio.gather(*tasks)

    manifest = {'voice': a.voice, 'rate': a.rate,
                'phrases': [{'text': p, 'file': slug(p) + '.mp3'} for p in ps]}
    with open(os.path.join(folder, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    ok = sum(r == 'ok' for r in results); sk = sum(r == 'skip' for r in results)
    fails = [(p, r) for p, r in zip(ps, results) if r.startswith('FAIL')]
    total = sum(os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder))
    # 윈도 콘솔(cp949)에서 특수문자로 죽지 않게 — 출력은 ASCII 구두점만
    print(f"{a.key}: {len(ps)} phrases - made {ok}, skipped {sk}, failed {len(fails)} / folder {total/1024:.0f}KB")
    for p, r in fails:
        print('  ', r, '<-', p)
    if fails:
        sys.exit(1)
    # 다 구웠을 때만 목록에 올린다 — 빈 폴더를 고르면 콘솔이 브라우저 TTS 로 떨어진다.
    if a.label:
        vpath = os.path.join(a.out, 'voices.json')
        vj = json.load(open(vpath, encoding='utf-8')) if os.path.exists(vpath) else {'voices': []}
        if not any(v.get('key') == a.key for v in vj['voices']):
            vj['voices'].append({'key': a.key, 'label': a.label, 'voice': a.voice, 'gender': a.gender})
            with open(vpath, 'w', encoding='utf-8') as f:
                json.dump(vj, f, ensure_ascii=False, indent=2)
                f.write('\n')
            print(f"voices.json: added {a.key}")


if __name__ == '__main__':
    asyncio.run(main())
