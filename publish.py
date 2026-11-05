#!/usr/bin/env python3
"""Manual publishing only. Requires both explicit repo selection and --publish."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'repos.json').read_text())


def command(args,cwd=None,capture=False):
 return subprocess.run(args,cwd=cwd,text=True,check=True,capture_output=capture)


def publish(item, allow_public_update=False):
 root=HERE.parent/item['name']
 for scanner in ('secret_scan.py','privacy_scan.py'):
  command([sys.executable,str(HERE/scanner),str(root)])
 if (root/'check.py').exists():command([sys.executable,'check.py'],cwd=root)
 if not (root/'.git').exists():command(['git','init','-b','main'],cwd=root)
 command(['git','config','user.name','Project Maintainer'],cwd=root)
 command(['git','config','user.email','contact@example.invalid'],cwd=root)
 command(['git','add','-A'],cwd=root)
 changed=command(['git','diff','--cached','--name-only'],cwd=root,capture=True).stdout.strip()
 if changed:command(['git','commit','--quiet','-m','Codex: save verified source snapshot and documentation'],cwd=root)
 owner=CONFIG['owner'];full=owner+'/'+item['name']
 found=subprocess.run(['gh','repo','view',full,'--json','isPrivate'],text=True,capture_output=True)
 if found.returncode:
  command(['gh','repo','create',full,'--private','--description',item['description'],
           '--source',str(root),'--remote','origin'])
 elif not json.loads(found.stdout)['isPrivate'] and not allow_public_update:
  raise RuntimeError('Public target: explicit --allow-public-update is required; visibility is never changed by this command')
 else:
  existing=subprocess.run(['git','remote','get-url','origin'],cwd=root,text=True,capture_output=True)
  if existing.returncode:command(['git','remote','add','origin','https://github.com/'+full+'.git'],cwd=root)
  elif existing.stdout.strip() not in ('https://github.com/'+full+'.git',):
   raise RuntimeError('Origin does not match the selected catalogue repository')
 command(['git','push','-u','origin','main'],cwd=root)
 local=command(['git','rev-parse','HEAD'],cwd=root,capture=True).stdout.strip()
 remote=command(['git','ls-remote','origin','refs/heads/main'],cwd=root,capture=True).stdout.split()[0]
 if local!=remote:raise RuntimeError('Uploaded commit verification failed')
 info=json.loads(command(['gh','api','repos/'+full,'--jq',
                         '{name:.name,url:.html_url,private:.private,created_at:.created_at,default_branch:.default_branch}'],capture=True).stdout)
 info['verified_commit']=local if item['kind']!='catalog' else 'verified against remote; self-reference omitted'
 report=HERE/'github-verification.json'
 data=json.loads(report.read_text()) if report.exists() else {}
 data[item['name']]=info;report.write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({'published':full,'private':info['private'],'commit_verified':True}),flush=True)


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--repo',action='append',required=True,choices=['all']+[r['name'] for r in CONFIG['repos']])
 parser.add_argument('--publish',action='store_true',help='Explicitly create/update GitHub repos and push commits now')
 parser.add_argument('--allow-public-update',action='store_true',help='Explicitly permit an update to an existing public target; does not change visibility')
 args=parser.parse_args()
 selected=[r for r in CONFIG['repos'] if 'all' in args.repo or r['name'] in args.repo]
 if not args.publish:
  for item in selected:print('Plan only: '+CONFIG['owner']+'/'+item['name'])
  return
 account=command(['gh','api','user','--jq','.login'],capture=True).stdout.strip()
 if account!=CONFIG['owner']:raise RuntimeError('Authenticated account differs from catalogue owner')
 for item in selected:publish(item,args.allow_public_update)

if __name__=='__main__':main()
