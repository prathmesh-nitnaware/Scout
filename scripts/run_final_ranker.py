import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Make scout/pipeline importable for legacy relative imports in final_ranker
PIPELINE_DIR = ROOT / 'scout' / 'pipeline'
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from scout.pipeline import final_ranker

if __name__ == '__main__':
    final_ranker.main()
