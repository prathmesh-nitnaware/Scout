import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with open(root / 'artifacts' / 'jd_profile.json', encoding='utf-8') as f:
    j = json.load(f)
raw = j['raw_text']
req = urllib.request.Request(
    'http://127.0.0.1:8000/rank-candidates',
    data=json.dumps({'jd_text': raw}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req, timeout=60) as resp:
    out = resp.read().decode('utf-8')
    with open(root / 'scripts' / 'rank_response.json', 'w', encoding='utf-8') as fw:
        fw.write(out)
    print(out)
