import json
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scout.pipeline.jd_parser import parse_jd

p = Path('artifacts/jd_profile.json')
if not p.exists():
    print('artifacts/jd_profile.json not found')
    raise SystemExit(1)

data = json.loads(p.read_text(encoding='utf-8'))
raw = data.get('raw_text') or data.get('raw_jd') or data.get('raw_text')
if not raw:
    print('No raw_text in artifacts/jd_profile.json')
    raw = p.read_text(encoding='utf-8')

parsed = parse_jd(raw)
print(json.dumps(parsed, indent=2))
print('\nRequired skills extracted:')
for s in parsed.get('required_skills', []):
    print('-', s)
