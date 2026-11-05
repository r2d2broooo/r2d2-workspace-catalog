#!/usr/bin/env python3
"""Fail closed on private text markers in export content. Prints locations, never values."""
import argparse
import ipaddress
import json
import os
import re
from pathlib import Path

BINARY={'.png','.jpg','.jpeg','.webp','.gif','.ico','.wav','.mp4','.ogg','.woff','.woff2','.ttf','.eot','.pdf','.zip'}
IPV4=re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
IPV6=re.compile(r'''["']([0-9a-fA-F:]*:[0-9a-fA-F:]*:[0-9a-fA-F:]*)["']''')
EMAIL=re.compile(r'\b[A-Za-z0-9_.+%-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE=re.compile(r'\+\d[\d ()-]{8,}\d')
CHAT=re.compile(r'(?i)(?:chat[_ -]?id|group[_ -]?id)\s*[:=]?\s*-?\d{6,}')


def scan(root):
 findings=[]
 for p in root.rglob('*'):
  if not p.is_file() or any(x in ('.git','__pycache__','.pytest_cache','.venv','venv','node_modules','.state') for x in p.relative_to(root).parts):continue
  if p.suffix.lower() in BINARY:continue
  try:text=p.read_text()
  except (UnicodeDecodeError,OSError):continue
  def hit(kind,at=0):
   findings.append({'path':str(p.relative_to(root)),'kind':kind,'line':text[:at].count('\n')+1})
  for m in IPV4.finditer(text):
   # Browser/PDF generator version strings are software metadata, not addresses.
   if re.search(r'(?:HeadlessChrome|Chrome|Chromium)/$',text[max(0,m.start()-30):m.start()]):continue
   try:ipaddress.ip_address(m.group())
   except ValueError:continue
   hit('literal-ip-address',m.start())
  for m in IPV6.finditer(text):
   try:ipaddress.ip_address(m.group(1))
   except ValueError:continue
   hit('literal-ipv6-address',m.start())
  prefix=os.environ.get('R2D2_SOURCE_HOME',str(Path.home()))
  if prefix in text:hit('workstation-home-path')
  for m in EMAIL.finditer(text):
   if m.group().endswith(('.invalid','.service','.timer','.json','.md','.py','.conf')):continue
   if p.name in ('LICENSE','LICENSE.md','LICENSE.txt','COPYING'):continue # required public upstream attribution
   hit('non-example-email',m.start())
  for regex,kind in ((PHONE,'phone-number'),(CHAT,'chat-identifier')):
   for m in regex.finditer(text):hit(kind,m.start())
  for marker in os.environ.get('R2D2_PRIVATE_MARKERS','').split(','):
   if marker.strip() and marker.lower().strip() in text.lower():hit('private-marker')
 return findings


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);a=parser.parse_args()
 findings=scan(a.root)
 print(json.dumps({'root':a.root.name,'passed':not findings,'findings':findings},indent=2))
 raise SystemExit(bool(findings))

if __name__=='__main__':main()
