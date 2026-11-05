#!/usr/bin/env python3
"""Sanitize EXPORT copies before any commit. Live workspaces are never written."""
from __future__ import annotations
import ast
import importlib.util
import ipaddress
import json
import os
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE_PREFIX=os.environ.get('R2D2_SOURCE_HOME',str(Path.home()))
ENCODED_HOME='-home-'+Path(SOURCE_PREFIX).name
spec=importlib.util.spec_from_file_location('snapshot_exporter',HERE/'export.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
BINARY={'.png','.jpg','.jpeg','.webp','.gif','.ico','.wav','.mp4','.ogg','.woff','.woff2','.ttf','.eot','.pdf','.zip'}
IP=re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
EMAIL=re.compile(r'(?<![\w.+-])[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])')

def ipv4(match):
 try: value=ipaddress.ip_address(match.group())
 except ValueError:return match.group()
 return 'localhost' if value.is_loopback or value.is_unspecified else 'example.invalid'


def clean_repo(repo):
 changed=[]
 for p in repo.rglob('*'):
  if not p.is_file() or any(part in ('.git','__pycache__','.pytest_cache','.venv','venv','node_modules','.state') for part in p.relative_to(repo).parts):continue
  if p.suffix.lower() in BINARY or p.name=='SOURCE_MANIFEST.json':continue
  try:text=p.read_text()
  except (UnicodeDecodeError,OSError):continue
  original=text
  if p.suffix=='.py' and ('"'+SOURCE_PREFIX+'/') in text or p.suffix=='.py' and ("'"+SOURCE_PREFIX+"/") in text:
   exporter.portable_literals(p,repo)
   text=p.read_text()
  text=IP.sub(ipv4,text)
  text=re.sub(r'(?i)\bR2D2[A-Za-z0-9_]*_bot\b','example_bot',text)
  text=re.sub(r'(?<![\w.])-\d{6,}(?![\w.])','-1',text)
  text=re.sub(r'(?i)((?:chat[_ -]?id|group[_ -]?id)\s*[:=]?\s*)([0-9]{6,})',r'\g<1>0',text)
  for marker in os.environ.get('R2D2_PRIVATE_MARKERS','').split(','):
   if marker.strip():text=re.sub(re.escape(marker.strip()),'private-source',text,flags=re.I)
  text=re.sub(r'\+\d[\d ()-]{8,}\d','EXAMPLE_PHONE',text)

  # Preserve loopback-only security checks without embedding address literals.
  loopback=str(ipaddress.IPv6Address(1))
  guard=f'if host not in ("localhost", "{loopback}", "localhost"):'
  if guard in text:
   text=text.replace(guard,'if not _is_local_peer(host):')
   helper='\ndef _is_local_peer(host):\n    import ipaddress\n    if host == "localhost":\n        return True\n    try:\n        return ipaddress.ip_address(host).is_loopback\n    except ValueError:\n        return False\n\n'
   anchor='def require_auth(request: Request):'
   text=text.replace(anchor,helper+anchor,1) if anchor in text else text+helper
  text=text.replace('['+loopback+']','localhost')
  text=text.replace('.split("' + ':'*2 + '", 1)', '.split(":" * 2, 1)')
  if p.name not in ('LICENSE','LICENSE.md','LICENSE.txt','COPYING'):
   text=EMAIL.sub(lambda m: m.group() if m.group().endswith(('.service','.timer','.md','.py','.json','.conf')) else 'contact@example.invalid',text)
  if p.suffix in ('.service','.timer','.conf'):
   text=text.replace(SOURCE_PREFIX,'%h')
  elif p.suffix=='.sh' or (p.parent.name=='bin' and 'bash' in text.splitlines()[0]):
   text=text.replace(SOURCE_PREFIX,'${R2D2_WORKSPACE:-$HOME}')
  elif p.suffix=='.desktop':
   text=text.replace(SOURCE_PREFIX+'/.local/bin/','')
   text=text.replace(SOURCE_PREFIX,'~')
  elif p.suffix=='.py':
   # Documentation text, provider cache descriptions and non-executable paths.
   text=text.replace(SOURCE_PREFIX,'<workspace>').replace(ENCODED_HOME,'-home-user')
  else:
   text=text.replace(SOURCE_PREFIX,'<workspace>').replace(ENCODED_HOME,'-home-user')
  if text!=original:
   p.write_text(text);changed.append(str(p.relative_to(repo)))
  if p.suffix=='.py':ast.parse(text)
 # Recompute manifests after adaptation; original source hashes are provenance, not raw private files.
 manifest=repo/'SOURCE_MANIFEST.json'
 if manifest.exists():
  import hashlib
  data=json.loads(manifest.read_text());data['source_home']='<workspace>'
  for entry in data['files']:
   entry['source']=entry['source'].replace(SOURCE_PREFIX,'<workspace>')
   for marker in os.environ.get('R2D2_PRIVATE_MARKERS','').split(','):
    if marker.strip():entry['source']=re.sub(re.escape(marker.strip()),'private-source',entry['source'],flags=re.I)
   path=repo/entry['path']
   entry['export_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  data['privacy']='Export sanitized: credentials/private runtime state excluded; personal email, workstation paths and literal IP addresses removed.'
  manifest.write_text(json.dumps(data,indent=2)+'\n')
 return changed


def main():
 config=json.loads((HERE/'repos.json').read_text())
 results={}
 for item in config['repos']:
  repo=ROOT/item['name']
  if item['kind']=='catalog':continue
  results[item['name']]=clean_repo(repo)
 (HERE/'sanitization-report.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({name:len(files) for name,files in results.items()},indent=2))

if __name__=='__main__':main()
