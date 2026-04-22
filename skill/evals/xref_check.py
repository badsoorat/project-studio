"""Cross-reference hallucination check for project-studio skill."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

actual = set()
for dp, ds, fs in os.walk('.'):
    if 'evals' in dp:
        continue
    for f in fs:
        actual.add(os.path.relpath(os.path.join(dp, f), '.').replace('\\', '/'))

# Greedy: allow .md.tmpl and .yaml.tmpl as well as plain extensions, with a word-boundary-ish end
PAT = re.compile(r'((?:references|templates|protocol|scripts)/[\w./\-]+?\.(?:md\.tmpl|yaml\.tmpl|md|py|json|yaml|tmpl|sh))')

def finalize(path):
    # Collapse trailing punctuation
    while path and path[-1] in '.,)':
        path = path[:-1]
    return path

# Override: for each match, keep extending greedily if .tmpl or .md follows
def scan_file(src):
    content = open(src, encoding='utf-8', errors='replace').read()
    # Simpler: find all candidate prefixes, then extend to longest valid suffix
    candidates = []
    # Use a greedy approach: match path + ext, then check if next chars are .tmpl
    for m in re.finditer(r'((?:references|templates|protocol|scripts)/[\w./\-]+?)(\.(?:md|yaml|json|py|tmpl))', content):
        start = m.start()
        end = m.end()
        # Check for .tmpl suffix
        if content[end:end+5] == '.tmpl':
            end += 5
        path = content[start:end]
        path = finalize(path)
        candidates.append(path)
    return candidates

referenced = {}

SCAN = [
    'SKILL.md',
    'references/setup-flow.md',
    'references/parent-architecture.md',
    'references/parent-module-handoff.md',
    'references/module-communication.md',
    'references/conflict-resolution.md',
    'references/classifier-rules.md',
    'references/persona-schema.md',
    'references/multi-project.md',
    'references/workflow.md',
    'references/patterns.md',
    'references/team-archetypes.md',
    'references/scale-modes.md',
    'references/contamination-checklist.md',
    'references/connectors.md',
    'references/registers.md',
    'references/import-slices.md',
    'references/skill-catalog.md',
    'protocol/boot.md',
    'protocol/boot-light.md',
    'protocol/resume.md',
    'protocol/invariants.md',
]

for src in SCAN:
    if not os.path.exists(src):
        print(f"SCAN-MISSING: {src}")
        continue
    for path in scan_file(src):
        referenced.setdefault(path, set()).add(src)

missing = {p: s for p, s in referenced.items() if p not in actual}
found = {p: s for p, s in referenced.items() if p in actual}

print(f"REFERENCED: {len(referenced)}   FOUND: {len(found)}   MISSING: {len(missing)}")

if missing:
    print("\n=== MISSING REFERENCES (possible hallucinations) ===")
    for p, srcs in sorted(missing.items()):
        print(f"  [MISSING] {p}")
        for s in sorted(srcs):
            print(f"      from: {s}")
else:
    print("\nAll referenced skill files exist. NO HALLUCINATED PATHS.")

orphans = sorted([
    p for p in actual
    if p not in referenced and p != 'SKILL.md'
    and p.startswith(('references/', 'templates/', 'protocol/', 'scripts/'))
])
print(f"\n=== FILES NOT REFERENCED BY ANY SCANNED FILE ({len(orphans)}) ===")
for p in orphans:
    print(f"  [ORPHAN] {p}")

sys.exit(0 if not missing else 1)
