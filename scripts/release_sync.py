#!/usr/bin/env python3
"""Check or regenerate release metadata and local skill exports. Uses only Python's standard library."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
registry_path=root/'release-registry.json'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write',action='store_true',help='Regenerate exports after bumping the registry version.')
parser.add_argument('--check-base',help='Compare changed instruction versions with this Git revision.')
args=parser.parse_args()
registry=json.loads(registry_path.read_text())
errors=[]
if args.check_base:
 previous=subprocess.run(['git','show',args.check_base+':release-registry.json'],cwd=root,capture_output=True,text=True)
 if previous.returncode==0:
  old_skills={s['path']:s for s in json.loads(previous.stdout).get('skills',[])}
  for skill in registry['skills']:
   old=old_skills.get(skill['path'])
   if old and old['sha256']!=skill['sha256'] and old['version']==skill['version']:errors.append(f'{skill["path"]}: changed instructions require a new version')

def save(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def expected_version(text):
 header=text.split('---',2)[1]
 match=re.search(r'(?m)^\s*version:\s*[\x27\x22]?([^\s\x27\x22]+)',header)
 return match[1] if match else None

def valid(v):return bool(re.fullmatch(r'[1-9]\d*\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?',v))

for skill in registry['skills']:
 path=root/skill['source']; text=path.read_text();v=skill['version']
 if not valid(v):errors.append(f'{skill["path"]}: use a version starting at 1.0.0 or higher')
 if expected_version(text)!=v:errors.append(f'{skill["source"]}: version differs from release-registry.json')
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 if digest!=skill['sha256']:
  if args.write:
   previous=subprocess.run(['git','show','HEAD:release-registry.json'],cwd=root,capture_output=True,text=True)
   old=next((s for s in json.loads(previous.stdout).get('skills',[]) if s['path']==skill['path']),None) if previous.returncode==0 else None
   if old and old['sha256']!=digest and old['version']==v:errors.append(f'{skill["source"]}: bump its registry and frontmatter version before accepting changed instructions')
   else:skill['sha256']=digest
  else:errors.append(f'{skill["source"]}: changed instructions; bump the version and run --write')
 if skill['source']!=skill['path']:
  generated=root/skill['path']
  if not generated.exists() or expected_version(generated.read_text())!=v:errors.append(f'{skill["path"]}: regenerate from its template')
  elif '## Purpose in plain English' not in generated.read_text():errors.append(f'{skill["path"]}: generated instructions are stale')

for copy in registry.get('copies',[]):
 source,target=root/copy['source'],root/copy['target']
 if args.write:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
 elif not target.exists() or source.read_bytes()!=target.read_bytes():errors.append(f'{copy["target"]}: differs from canonical {copy["source"]}')

for package in registry.get('packages',[]):
 v=package['version']
 if not valid(v):errors.append(f'{package["name"]}: invalid release version {v}')
 for skill_path in package['skills']:
  skill=next(s for s in registry['skills'] if s['path']==skill_path)
  if skill['version']!=v:errors.append(f'{skill_path}: version differs from containing package')
 for manifest in package['manifests']:
  path=root/manifest;data=json.loads(path.read_text())
  if args.write:data['version']=v;save(path,data)
  elif data.get('version')!=v:errors.append(f'{manifest}: version differs from registry')
 for path in root.rglob('marketplace.json'):
  if any(p in path.parts for p in ['node_modules','.git']):continue
  data=json.loads(path.read_text());changed=False
  for entry in data.get('plugins',[]):
   if entry.get('name')==package['name']:
    if args.write:entry['version']=v;changed=True
    elif entry.get('version')!=v:errors.append(f'{path.relative_to(root)}: {package["name"]} version differs')
  if changed:save(path,data)

for collection in registry.get('collections',[]):
 v=collection['version'];mapping=json.loads((root/collection['sourceMap']).read_text())
 if mapping['collectionVersion']!=v:errors.append('Collection source map version differs from registry')
 seen=set()
 for entry in mapping['entries']:
  if entry.get('export'):
   key=(entry['repository'],entry['source_path'])
   if key in seen:errors.append(f'Duplicate current export: {key}')
   seen.add(key)
 for manifest in collection['manifests']:
  path=root/manifest;data=json.loads(path.read_text())
  if args.write:data['version']=v;save(path,data)
  elif data.get('version')!=v:errors.append(f'{manifest}: collection version differs')

if errors:
 for message in errors:print(message)
 raise SystemExit(1)
if args.write:save(registry_path,registry)
print(f'OK: {len(registry["skills"])} canonical skills, {len(registry.get("packages",[]))} packages; versions and local exports agree.')
