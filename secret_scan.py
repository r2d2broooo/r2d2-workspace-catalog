#!/usr/bin/env python3
"""Scan export content without printing secret values. No network or account calls."""
import argparse
import json
import re
from pathlib import Path

PATTERNS={
 'telegram-token':re.compile(rb'(?<![0-9])\d{8,12}:[A-Za-z0-9_-]{30,}(?![A-Za-z0-9_-])'),
 'github-token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
 'openai-token':re.compile(rb'\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{35,}\b'),
 'aws-key':re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
 'private-key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}
BINARY={'.png','.jpg','.jpeg','.webp','.gif','.ico','.wav','.mp4','.ogg','.woff','.woff2','.ttf','.eot','.pdf','.zip'}


def scan(root):
 findings=[]
 known=[]
 for env in (Path.home()/'telegram-bots/.env',Path.home()/'dashboard/.env'):
  if not env.is_file():continue
  for line in env.read_text().splitlines():
   if '=' not in line or line.lstrip().startswith('#'):continue
   key,value=line.split('=',1)
   value=value.strip().strip('"').strip("'")
   if re.search(r'TOKEN|SECRET|PASSWORD|API_KEY',key,re.I) and len(value)>=12:
    known.append(value.encode())
 for p in root.rglob('*'):
  if not p.is_file() or '.git' in p.relative_to(root).parts:continue
  rel=p.relative_to(root)
  if p.name.startswith('.env') and p.name!='.env.example' or p.suffix in ('.db','.sqlite','.sqlite3','.pem','.key'):
   findings.append({'path':str(rel),'kind':'excluded-runtime-or-secret-file'});continue
  if p.suffix.lower() in BINARY:continue
  content=p.read_bytes()
  if any(value in content for value in known):
   findings.append({'path':str(rel),'kind':'configured-live-secret'})
  for label,pattern in PATTERNS.items():
   for m in pattern.finditer(content):
    # Repeated-character values are intentional security-test fixtures, not credentials.
    value=m.group().split(b':')[-1]
    if len(set(value))<=4:continue
    findings.append({'path':str(rel),'kind':label,'line':content[:m.start()].count(b'\n')+1})
 return findings


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);args=parser.parse_args()
 findings=scan(args.root)
 print(json.dumps({'root':args.root.name,'passed':not findings,'findings':findings},indent=2))
 raise SystemExit(bool(findings))

if __name__=='__main__':main()
