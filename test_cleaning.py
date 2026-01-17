#!/usr/bin/env python
"""Quick test of data cleaning."""
from analyze_results import load_aggregated_results
from pathlib import Path

results = load_aggregated_results(Path('aggregated_results.csv'))
qwen_rows = [r for r in results if 'qwen' in r.get('model_id', '')]
print('Qwen rows after cleaning:')
for r in qwen_rows:
    print(f"{r['model_id']},{r['scenario']},{r['approach']}: acc={r['accuracy']}, var={r['variance']}, errors={r['errors']}")
