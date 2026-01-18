#!/usr/bin/env python
"""Quick test of data cleaning."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src" / "scripts"))

from analyze_results import load_aggregated_results

results = load_aggregated_results(PROJECT_ROOT / 'aggregated_results.csv')
qwen_rows = [r for r in results if 'qwen' in r.get('model_id', '')]
print('Qwen rows after cleaning:')
for r in qwen_rows:
    print(f"{r['model_id']},{r['scenario']},{r['approach']}: acc={r['accuracy']}, var={r['variance']}, errors={r['errors']}")
