#!/usr/bin/env python3
"""Validate skills in this repo.
- Every skills/<name>/SKILL.md must have a parseable YAML frontmatter with name + description.
- No skill may contain node_modules / __pycache__ / .env files with secrets.
- skills-manifest.json must list exactly the current skill directories (names match).
Exit non-zero on any failure (CI red).
"""
import os, re, sys, json, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, 'skills')
manifest_path = os.path.join(ROOT, 'skills-manifest.json')

try:
    import yaml
except ImportError:
    print('PyYAML not available; install pyyaml'); sys.exit(2)

errors = []

def walk_files(d):
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in ('.git', '__pycache__', 'node_modules')]
        for f in files:
            yield os.path.join(root, f)

# 1) frontmatter + forbidden files
skill_names = []
for name in sorted(os.listdir(SKILLS)):
    sp = os.path.join(SKILLS, name)
    if not os.path.isdir(sp):
        continue
    skill_names.append(name)
    sk = os.path.join(sp, 'SKILL.md')
    if not os.path.exists(sk):
        errors.append(f'[{name}] missing SKILL.md')
        continue
    txt = open(sk, encoding='utf-8').read()
    m = re.match(r'^---\n(.*?)\n---\n', txt, re.S)
    if not m:
        errors.append(f'[{name}] no YAML frontmatter block')
        continue
    try:
        fm = yaml.safe_load(m.group(1))
    except Exception as e:
        errors.append(f'[{name}] frontmatter YAML error: {e}')
        continue
    if not fm.get('name'):
        errors.append(f'[{name}] frontmatter missing name')
    if not fm.get('description'):
        errors.append(f'[{name}] frontmatter missing description')
    # forbidden content
    for fp in walk_files(sp):
        rel = os.path.relpath(fp, sp)
        base = os.path.basename(fp)
        if 'node_modules' in rel.split(os.sep):
            errors.append(f'[{name}] contains node_modules: {rel}')
        if base in ('.env', '.env.cookies') and os.path.getsize(fp) > 0:
            errors.append(f'[{name}] contains secret file: {rel}')

# 2) manifest consistency (names only; skip sha recompute for speed)
if os.path.exists(manifest_path):
    try:
        man = json.load(open(manifest_path, encoding='utf-8'))
        man_names = set(man.get('skills', {}).keys())
        cur = set(skill_names)
        missing = cur - man_names
        extra = man_names - cur
        if missing:
            errors.append(f'manifest missing skills: {sorted(missing)}')
        if extra:
            errors.append(f'manifest has stale skills: {sorted(extra)}')
    except Exception as e:
        errors.append(f'manifest parse error: {e}')

if errors:
    print('VALIDATION FAILED:')
    for e in errors:
        print('  -', e)
    sys.exit(1)
print(f'VALIDATION OK: {len(skill_names)} skills validated, manifest consistent.')
