from pathlib import Path

# Project root (repo root)
root = Path(__file__).resolve().parents[2]
entries = []
for p in sorted(root.rglob('*')):
    if p.is_dir():
        continue
    rel = p.relative_to(root).as_posix()
    if rel.startswith('scout_env/') or rel.startswith('__MACOSX/'):
        category = 'Cache File'
    elif rel.endswith('.pyc') or '/__pycache__/' in rel or rel.startswith('__pycache__/'):
        category = 'Cache File'
    elif rel.startswith('artifacts/'):
        category = 'Generated Output'
    elif rel.startswith('frontend/'):
        category = 'Production Code'
    elif rel.startswith('api/'):
        category = 'Production Code'
    elif rel.startswith('scout/'):
        category = 'Production Code'
    elif rel.startswith('scripts/'):
        category = 'Debug File'
    elif rel.startswith('data/'):
        category = 'Production Code'
    elif rel.startswith('[PUB]'):
        category = 'Submission Artifact'
    elif rel.endswith('.ipynb'):
        category = 'Temporary Experiment'
    elif rel in ('README.md','requirements.txt','frontend_architecture.md','frontend_plan.md','frontend_todo.md','Scout_Hackathon_Blueprint.md','Scout_Hackathon_Blueprint.docx','structure.txt'):
        category = 'Submission Artifact'
    elif rel in ('submission.csv','submission_final.csv','submission_embedding.csv'):
        category = 'Generated Output'
    elif rel in ('run_phase7cb_validation.py','validate_core_hardening.py','validate_runtime_hardening.py','verify_flags.py','test_runtime.py'):
        category = 'Validation Artifact'
    elif rel == 'structure.txt':
        category = 'Debug File'
    else:
        category = 'Unknown'
    entries.append((rel, category))

counts = {}
for rel, cat in entries:
    counts[cat] = counts.get(cat, 0) + 1
print('COUNTS:', counts)
print('\nTOP-LEVEL FILES:')
for rel, cat in entries:
    if '/' not in rel:
        print(rel, cat)
print('\nUNKNOWN FILES:')
for rel, cat in entries:
    if cat == 'Unknown':
        print(rel)
print('\nSAMPLE FRONTEND FILES:')
for rel, cat in entries[:50]:
    if rel.startswith('frontend/'):
        print(rel, cat)
print('\nSAMPLE ARTIFACT FILES:')
for rel, cat in entries[:50]:
    if rel.startswith('artifacts/'):
        print(rel, cat)