#!/usr/bin/env python3
"""Read-only release review of working exports, reachable Git history and document metadata.

Prints only finding locations/types, never credential values. Does not alter visibility.
"""
from __future__ import annotations
import argparse
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

import privacy_scan
import secret_scan

HERE=Path(__file__).resolve().parent


def _binary_text(root):
    findings=[]
    with tempfile.TemporaryDirectory(prefix='release-metadata-') as folder:
        scratch=Path(folder)
        for n,p in enumerate(sorted(root.rglob('*.pdf'))):
            text=subprocess.run(['pdftotext',str(p),'-'],capture_output=True,check=True).stdout
            meta=subprocess.run(['pdfinfo',str(p)],capture_output=True,check=True).stdout
            (scratch/f'pdf-{n}.txt').write_bytes(meta+b'\n'+text)
        # Pillow is optional; when present inspect textual metadata, not private profiles.
        from PIL import Image
        for n,p in enumerate(sorted(root.rglob('*.png'))):
            with Image.open(p) as img:
                data={'info':img.info,'exif':dict(img.getexif())}
                (scratch/f'image-{n}.txt').write_text(json.dumps(data,default=str))
        findings.extend(privacy_scan.scan(scratch))
        findings.extend(secret_scan.scan(scratch))
    return findings


def review(root, gitleaks=None):
    findings=privacy_scan.scan(root)+secret_scan.scan(root)
    commits=subprocess.check_output(['git','rev-list','--all'],cwd=root,text=True).splitlines()
    snapshots=0
    for commit in commits:
        with tempfile.TemporaryDirectory(prefix='release-history-') as folder:
            archive=subprocess.check_output(['git','archive',commit],cwd=root)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(folder,filter='data')
            tree=Path(folder)
            for item in privacy_scan.scan(tree)+secret_scan.scan(tree):
                findings.append({**item,'commit':commit[:12]})
            for item in _binary_text(tree):
                findings.append({**item,'commit':commit[:12],'scope':'document-metadata-or-text'})
            snapshots+=1
    leak_exit=None
    if gitleaks:
        result=subprocess.run([gitleaks,'detect','--source',str(root),'--log-opts=--all',
                               '--redact','--no-banner'],capture_output=True,text=True)
        leak_exit=result.returncode
        if leak_exit:findings.append({'kind':'gitleaks-history-scan-failed','exit':leak_exit})
    # Explicitly disallow unintended personal/runtime artifacts in the release index.
    tracked=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines()
    for name in tracked:
        p=Path(name)
        if any(part in ('training-data','cookies','captures','screenshots') for part in p.parts):
            findings.append({'path':name,'kind':'private-capture-path'})
        if p.suffix in ('.db','.sqlite','.sqlite3','.pkl','.joblib','.key','.pem'):
            findings.append({'path':name,'kind':'private-runtime-file'})
    return {'repo':root.name,'passed':not findings,'history_snapshots':snapshots,
            'gitleaks_exit':leak_exit,'findings':findings}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',action='append',required=True)
    parser.add_argument('--gitleaks')
    parser.add_argument('--report',type=Path)
    a=parser.parse_args();cfg=json.loads((HERE/'repos.json').read_text())
    selected=[r for r in cfg['repos'] if 'all' in a.repo or r['name'] in a.repo]
    if not selected:parser.error('No matching catalogue repository')
    results=[]
    for item in selected:
        out=review(HERE.parent/item['name'],a.gitleaks);results.append(out)
        print(json.dumps(out),flush=True)
    if a.report:a.report.write_text(json.dumps({'checks':results},indent=2)+'\n')
    raise SystemExit(any(not r['passed'] for r in results))


if __name__=='__main__':main()
