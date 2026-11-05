#!/usr/bin/env python3
"""Explicit source snapshot exporter. Never calls GitHub, commits, pushes or installs jobs."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = Path(os.environ.get('R2D2_SOURCE_HOME', str(Path.home())))
CONFIG = json.loads((HERE/'repos.json').read_text())
SKIP = {'.git','.venv','venv','venv-train','venv-forecast','node_modules','__pycache__',
        '.pytest_cache','.mypy_cache','.cache','.serena','.claude','.codex','data','training-data','runs',
        'cloud-workdir','claude-sessions','shared-claude','report-review-workdir','models'}
BAD_EXT = {'.db','.sqlite','.sqlite3','.pyc','.joblib','.pkl','.log','.out','.pem','.key'}
AGENT = ['activity','agent_projects','agent_registry','agents','chat_log','desk_quota',
         'grok_runner','group_chat','llm_session','memory','model_choices','project_observability',
         'prompt_guard','run_budget','secret_redaction','session_day','session_memory',
         'supervisor','telegram_runtime','telegram_sender','terminal_usage','token_guard','token_usage']
BROWSER = ['browser_client','scrape_client','clean_extract','youtube_transcripts','agent_browser','desktop','screen_recorder']
SKILLS = ['systematic-debugging','book-to-skill','trading-wiki','holistic-stock-analysis',
          'diagram-design','anatomy','frontend-design','test-driven-development',
          'stock-pattern-recognition','forecast-model-methods','verification-before-completion',
          'graphify','taste-skill','claude-compatible-browser','reverse-engineer-anything']


def safe(path):
    return not any(p in SKIP for p in path.parts) and path.suffix.lower() not in BAD_EXT \
        and (not path.name.startswith('.env') or path.name=='.env.example') \
        and not any(p in ('credentials.json','token.json','auth.json','cookies.json') for p in path.parts)


def copy_file(src, dst, ledger, origin=None):
    src, dst = Path(src), Path(dst)
    if not src.is_file():
        return
    # Dereference source symlinks deliberately: exports contain no dangling host links.
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst, follow_symlinks=True)
    ledger.append({'source': str(origin or src), 'path': str(dst),
                   'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest()})


def tree(src, dst, ledger, predicate=None):
    src, dst=Path(src),Path(dst)
    for root, dirs, files in os.walk(src, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
        for name in files:
            p=Path(root)/name
            rel=p.relative_to(src)
            if safe(rel) and (predicate is None or predicate(rel)):
                copy_file(p,dst/rel,ledger)


def tracked(src,dst,ledger):
    files=subprocess.check_output(['git','-C',str(src),'ls-files','-z']).decode().split('\0')
    for name in files:
        if name and safe(Path(name)) and name != '.git' and not name.startswith('.git/'):
            copy_file(src/name,dst/name,ledger)


def portable_literals(path, workspace):
    """Adapt absolute legacy path literals in exported toolkit copies only; keep comments/source formatting."""
    text=path.read_text()
    parsed=ast.parse(text)
    lines=text.splitlines(keepends=True)
    offsets=[0]
    for line in lines: offsets.append(offsets[-1]+len(line))
    parents={child:parent for parent in ast.walk(parsed) for child in ast.iter_child_nodes(parent)}
    edits=[]
    for node in ast.walk(parsed):
        if not isinstance(node,ast.Constant) or not isinstance(node.value,str) or not node.value.startswith(str(SOURCE) + '/'):
            continue
        if isinstance(parents.get(node),ast.JoinedStr): continue
        suffix=node.value.removeprefix(str(SOURCE) + '/')
        expression=f"str(_export_pathlib.Path(_export_os.environ.get('R2D2_WORKSPACE', {str(workspace)!r})) / {suffix!r})"
        # Default must follow the clone, not this export machine.
        expression=expression.replace(repr(str(workspace)), f"str(_export_pathlib.Path(__file__).resolve().parents[{len(path.relative_to(workspace).parts)-1}])")
        a=offsets[node.lineno-1]+node.col_offset
        b=offsets[node.end_lineno-1]+node.end_col_offset
        edits.append((a,b,expression))
    if edits:
        for a,b,v in sorted(edits,reverse=True): text=text[:a]+v+text[b:]
        parsed=ast.parse(text)
        future=[n.end_lineno for n in parsed.body if isinstance(n,ast.ImportFrom) and n.module=='__future__']
        doc=parsed.body[0].end_lineno if parsed.body and isinstance(parsed.body[0],ast.Expr) and isinstance(parsed.body[0].value,ast.Constant) else 0
        at=max(future+[doc,0]); ls=text.splitlines(keepends=True)
        ls.insert(at,'\nimport os as _export_os\nimport pathlib as _export_pathlib\n')
        path.write_text(''.join(ls))
        ast.parse(path.read_text())


def write_check(dst, kind):
    script='''#!/usr/bin/env python3
"""Read-only source checks; never calls providers, sends notices or starts services."""
import ast, json, shutil, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
counts={'python':0,'shell':0,'javascript':0,'json':0}
for path in root.rglob('*'):
    if not path.is_file() or any(p in ('.git','.venv','venv','node_modules','__pycache__') for p in path.relative_to(root).parts): continue
    if path.suffix=='.py' or (path.parent.name=='bin' and b'python' in path.read_bytes().split(b'\n')[0]):
        ast.parse(path.read_text()); counts['python']+=1
    elif path.suffix=='.sh' or (path.parent.name=='bin' and b'bash' in path.read_bytes().split(b'\\n')[0]):
        subprocess.run(['bash','-n',str(path)],check=True); counts['shell']+=1
    elif path.suffix=='.js' and shutil.which('node'):
        subprocess.run(['node','--check',str(path)],check=True,capture_output=True); counts['javascript']+=1
    elif path.suffix=='.json':
        json.loads(path.read_text()); counts['json']+=1
print(json.dumps({'source_checks':'passed','counts':counts}))
'''
    (dst/'check.py').write_text(script)


def build(repo):
    dst=BASE/repo['name'];dst.mkdir(exist_ok=True)
    previous=json.loads((dst/'SOURCE_MANIFEST.json').read_text()).get('files',[]) if (dst/'SOURCE_MANIFEST.json').exists() else []
    ledger=[]; kind=repo['kind']
    if kind=='catalog': return
    if kind=='integrated':
        for name in ('telegram-bots','dashboard'):
            tracked(SOURCE/name,dst/name,ledger)
        tree(SOURCE/'trading-wiki',dst/'trading-wiki',ledger,lambda p:p.parts[0]=='scripts' or p.name=='WIKI_SCHEMA.md')
        tree(SOURCE/'telegram-bots/research_archive',dst/'research-archive',ledger,
             lambda p:p.suffix in ('.py','.pine') and not any(s in p.parts for s in ('data','cloud_books_2026_10_26','cloud_books_2026_11_05')))
        copy_file(SOURCE/'r2d2-agents/AGENTS.md',dst/'r2d2-agents/AGENTS.md',ledger)
        private_study=dst/'telegram-bots/prompts/docs/operator_trade_study_2026-08-28.md'
        if private_study.exists():private_study.write_text('# Private study omitted\n\nThe original study contains personal trading examples and is excluded from this shareable source snapshot. Use public or synthetic examples for further research.\n')
        # The user watchlist is private runtime preference; only a blank template ships.
        (dst/'dashboard/watchlist.json').write_text('[]\n')
        # A monorepo clone has one .git at its root, rather than one per app.
        p=dst/'telegram-bots/shared/project_observability.py';t=p.read_text()
        t=t.replace("p.is_dir() and (p / '.git').exists()", "p.is_dir() and ((p / '.git').exists() or (p.name in ('telegram-bots','dashboard') and (BASE / '.git').exists()))")
        p.write_text(t)
        # Also record installed service definitions, including overrides newer than tracked examples.
        tree(SOURCE/'.config/systemd/user',dst/'installed-systemd-examples',ledger,
             lambda p:p.suffix in ('.service','.timer','.conf') and not p.name.startswith(('pz-','wifi-','openclaw')))
        (dst/'SETUP.md').write_text('''# Restore the integrated trading system

This snapshot keeps dashboard/ and telegram-bots/ together because the dashboard
imports the shared runtime. Agent/memory/token helpers are integration copies of
the reusable agent-workflow toolkit; install each project into its own environment.
No services or trading jobs start from cloning this repository.

The current runtime uses legacy <workspace> paths. On the original machine the
original folders stay authoritative. For an exact-layout restore put these folders
under <workspace> (back up existing work first). For another host review and configure
absolute paths before starting services. This is not a universal one-command installer.

1. Create separate Python virtual environments inside dashboard/ and telegram-bots/.
2. Install each requirements.txt. The runtime lock records the versions installed
   at export time; some packages require the original Python version/platform.
3. Copy .env.example to .env and supply YOUR credentials locally. Do not commit it.
4. Generate market caches and Lab panels with the documented producers. No account
   history, live paper books, caches, private memory or credentials are in this repo.
5. Review prompts/docs/trading_mandate.md, agent_contract.md and current schedule
   documentation. Installed systemd examples show the source host's configuration;
   never enable all timers blindly. Historical research is not active policy.
6. Start only the dashboard first and check health. Authenticate providers and
   configure Telegram separately. Activate paper schedules only when intended.

Focused tests can run without market data or external accounts by using their
provided stubs and temporary fixtures. See VERIFICATION.md in the catalogue.
''')
    elif kind=='agent':
        shared=dst/'telegram-bots/shared';shared.mkdir(parents=True,exist_ok=True)
        (shared/'__init__.py').write_text('')
        for name in AGENT:copy_file(SOURCE/f'telegram-bots/shared/{name}.py',shared/f'{name}.py',ledger)
        for agent in ('claude','codex','grok'):
            copy_file(SOURCE/f'telegram-bots/prompts/{agent}/system_prompt.md',dst/f'telegram-bots/prompts/{agent}/system_prompt.md',ledger)
        copy_file(SOURCE/'r2d2-agents/AGENTS.md',dst/'r2d2-agents/AGENTS.md',ledger)
        for name in ('agent_contract','agent_projects_setup','project_observability','telegram_runtime','grok_setup'):
            copy_file(SOURCE/f'telegram-bots/prompts/docs/{name}.md',dst/f'telegram-bots/prompts/docs/{name}.md',ledger)
        copy_file(SOURCE/'dashboard/agent_project_routes.py',dst/'agent_project_routes.py',ledger)
        for p in shared.glob('*.py'):portable_literals(p,dst)
        # Toolkit-specific prompts keep the exported runtime usable without a trading checkout.
        for agent in ('claude','codex','grok'):
            (dst/f'telegram-bots/prompts/{agent}/system_prompt.md').write_text(f'You are the independent {agent} assistant. Keep your own identity. Follow the current operator task and local AGENTS.md. No automatic cross-model review. Use on-demand memory and never expose secrets.\\n')
        # Isolate toolkit storage and make its own repository selectable without a trading clone.
        p=shared/'agent_projects.py';t=p.read_text()
        t=t.replace('STATE_DIR = Path.home() / ".config/r2d2/agent-projects"',
                    'STATE_DIR = Path(os.environ.get("R2D2_AGENT_STATE_DIR", ROOT.parent / ".state/agent-projects"))')
        t=t.replace('project="telegram-bots"', 'project=ROOT.parent.name')
        t=t.replace('if project else "telegram-bots"', 'if project else ROOT.parent.name')
        p.write_text(t)
        p=shared/'project_observability.py';t=p.read_text()
        t=t.replace('return {p.name: p.resolve() for p in sorted(BASE.iterdir())',
                    'return {p.name: p.resolve() for p in [BASE, *sorted(BASE.iterdir())]')
        t=t.replace("BASE / 'dashboard/AGENTS.md'", "BASE / 'AGENTS.md'")
        p.write_text(t)
        p=dst/'agent_project_routes.py';t=p.read_text().replace('body.get("project", "telegram-bots")',
                                         'body.get("project", agent_projects.ROOT.parent.name)');p.write_text(t)
        p=shared/'supervisor.py';t=p.read_text().replace('Path.home() / ".config" / "r2d2"',
                         'Path(__file__).resolve().parents[2] / ".state" / "provider-config"');p.write_text(t)
        generic_contract='# Agent toolkit contract\n\nIndependent provider sessions; no automatic cross-model review. Memory is read on demand. Never expose secrets. No automatic commits, pushes or account actions. Keep runtime state local.\n'
        for target in ('AGENTS.md','telegram-bots/AGENTS.md','r2d2-agents/AGENTS.md'):
            (dst/target).parent.mkdir(parents=True,exist_ok=True)
            (dst/target).write_text(generic_contract)
        (dst/'requirements.txt').write_text('fastapi\nuvicorn\npython-dotenv\nhttpx\npython-telegram-bot\n')
        (dst/'serve.py').write_text('''"""Optional minimal project-session API. Set R2D2_API_KEY locally; does not start providers itself."""
import os, sys, hmac
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'telegram-bots'))
from fastapi import FastAPI
from agent_project_routes import build_agent_project_router
app=FastAPI()
def auth(request):
    key=os.environ.get('R2D2_API_KEY','')
    return bool(key) and hmac.compare_digest(request.headers.get('x-api-key',''),key)
app.include_router(build_agent_project_router(auth))
''')
        (dst/'USAGE.md').write_text('''# Standalone use

Use an isolated virtual environment, then `pip install -r requirements.txt`.
`PYTHONPATH=telegram-bots python -m shared.token_usage --hours 24` reads usage.
Session memory is available from shared.session_memory; use R2D2_SESSION_MEMORY to
choose its private storage. `R2D2_WORKSPACE` overrides the exported workspace root.
Provider CLIs need their own login; no credentials or CLI executables are included.
Optional API: set R2D2_API_KEY to a local secret and run `uvicorn serve:app --host
localhost --port 8430`. It uses an x-api-key header. Never expose it unauthenticated.
Create an ordinary local Git repo under this workspace before choosing it as a
project. The source integration's telegram-bots fallback is only a compatibility
default; explicitly select the cloned repo/project you intend to operate on.
No trading engine, market data, Lab or order functions are imported by this toolkit.
''')
    elif kind=='browser':
        (dst/'shared').mkdir(exist_ok=True);(dst/'shared/__init__.py').write_text('')
        for name in BROWSER:copy_file(SOURCE/f'telegram-bots/shared/{name}.py',dst/f'shared/{name}.py',ledger)
        (dst/'systemd').mkdir(exist_ok=True)
        (dst/'systemd/agent-browser.service').write_text('[Unit]\nDescription=Dedicated Chrome browser for local automation\nAfter=graphical-session.target\n\n[Service]\nWorkingDirectory=%h/r2d2-browser-research-tools\nExecStart=%h/r2d2-browser-research-tools/.venv/bin/python -m shared.agent_browser\nRestart=on-failure\nRestartSec=3\n\n[Install]\nWantedBy=default.target\n')
        (dst/'requirements.txt').write_text('playwright\nscrapling\ntrafilatura\nbeautifulsoup4\nyt-dlp\n')
        (dst/'USAGE.md').write_text('''# Browser research helpers

Install requirements in a dedicated environment. Chrome/CDP normally listens on
localhost:9222. Configure the agent-browser service yourself; no browser profiles,
cookies or logins are included. shared.browser_client exposes async helpers (read,
fetch, goto, screenshot, click, fill, press). shared.clean_extract provides article
cleanup; shared.youtube_transcripts handles captions. Read each module's API.
Desktop helpers require Linux/X11; browser helpers require a running CDP browser.
Do not send messages, submit account changes or make purchases without an explicit
task authorizing them. This toolkit starts no model and contains no trading engine.
''')
    elif kind=='knowledge':
        tree(SOURCE/'.claude/skills/book-to-skill',dst/'book-to-skill',ledger)
        copy_file(SOURCE/'trading-wiki/scripts/wiki.py',dst/'wiki/wiki.py',ledger)
        copy_file(SOURCE/'trading-wiki/WIKI_SCHEMA.md',dst/'wiki/WIKI_SCHEMA.md',ledger)
        copy_file(SOURCE/'telegram-bots/shared/codegraph.py',dst/'codegraph/codegraph.py',ledger)
        p=dst/'wiki/wiki.py';text=p.read_text().replace(f'ROOT = "{SOURCE / "trading-wiki"}"','ROOT = os.environ.get("R2D2_WIKI_ROOT", os.path.dirname(os.path.abspath(__file__)))');p.write_text(text)
        (dst/'requirements.txt').write_text('# Python standard library; PDF extraction additionally needs pdftotext (poppler-utils).\n')
    elif kind=='skills':
        for name in SKILLS:tree((SOURCE/'.claude/skills'/name).resolve(),dst/'skills'/name,ledger)
        (dst/'UPSTREAMS.md').write_text('''# Provenance

This is a private snapshot of installed/adapted recipes, not a claim that every
skill was authored here. Preserve included licenses. Third-party sources include
leonxlnx/taste-skill (taste-skill), OpenAI/Anthropic frontend/debugging skill recipes,
morluto/rea (reverse-engineering adapter), Graphify-Labs/graphify (graphify adapter),
and locally adapted anatomy/diagram assets (see their LICENSE files). Browser,
trading-wiki, holistic-stock-analysis, forecast methods and book-to-skill include
local integrations. Installed packages and hosted plugins are listed as dependencies
in the workspace catalogue; their binaries, accounts and caches are not copied.
Review individual licenses before redistribution or making this repo public.
''')
    elif kind=='wifi':
        for name in ('wifi-guard','wifi-guard-ui','wifi-guard-notify'):copy_file(SOURCE/'.local/bin'/name,dst/'bin'/name,ledger)
        copy_file(SOURCE/'.config/systemd/user/wifi-guard.service',dst/'systemd/wifi-guard.service',ledger)
        copy_file(SOURCE/'.local/share/applications/com.r2d2.WifiGuard.desktop',dst/'desktop/com.r2d2.WifiGuard.desktop',ledger)
        p=dst/'bin/wifi-guard-notify';s=p.read_text().replace('#!<workspace>/telegram-bots/venv/bin/python','#!/usr/bin/env python3')
        a=s.index('sys.path.insert');b=s.index('\nSTATE_DIR',a)
        s=s[:a]+'''import urllib.request
import urllib.parse

class _Sender:
    async def send_message(self, target, text):
        token=os.environ.get('WIFI_GUARD_TELEGRAM_TOKEN','')
        chat=os.environ.get('WIFI_GUARD_TELEGRAM_CHAT_ID','')
        if not token or not chat:
            raise RuntimeError('Optional Telegram notifications are not configured')
        payload=urllib.parse.urlencode({'chat_id':chat,'text':text}).encode()
        def send():
            with urllib.request.urlopen('https://api.telegram.org/bot'+token+'/sendMessage',data=payload,timeout=20) as r:
                return r.read()
        return await asyncio.to_thread(send)
telegram_sender=_Sender()
''' +s[b:];p.write_text(s)
        (dst/'USAGE.md').write_text('''# Install only when intended

The core uses bash, NetworkManager/nmcli and standard Linux tools. The status UI
requires Python/Gtk (python3-gi, gir1.2-gtk-3.0). Configure WIFI_GUARD_IFACE for your
network device. Install bin files into ~/.local/bin only after reviewing them.
The optional notifier now uses WIFI_GUARD_TELEGRAM_TOKEN and
WIFI_GUARD_TELEGRAM_CHAT_ID from the environment, so it does not need the trading
repo or its .env. It never stores the Wi-Fi password. No service is auto-enabled.
''')
    elif kind=='linux':
        copy_file(SOURCE/'.local/bin/paseo-desktop',dst/'bin/paseo-desktop',ledger)
        for name in ('paseo.desktop','claude-code-url-handler.desktop'):
            copy_file(SOURCE/'.local/share/applications'/name,dst/'desktop'/name,ledger)
        for name in ('backup.sh','checkpoint.sh','desktop-control-setup.sh','desktop-control-setup2.sh','install-nvidia.sh','make_montage.py'):
            copy_file(SOURCE/name,dst/'scripts'/name,ledger)
        copy_file(SOURCE/'RESTORE.md',dst/'historical/RESTORE.md',ledger)
        copy_file(SOURCE/'telegram-bots/shared/sysinfo.py',dst/'sysinfo.py',ledger)
        (dst/'USAGE.md').write_text('''# Operational scripts

These preserve host-specific scripts; syntax checks do not run their effects.
Review absolute paths, package-manager and privilege requirements before use.
backup.sh intentionally captures local secrets/private data for OFFLINE recovery;
its archives must NEVER be committed or uploaded here. RESTORE.md is historical
and references retired models: use current trading docs for current deployment.
checkpoint.sh commits locally but does not push. None of these runs automatically.
''')
    elif kind=='productivity':
        for name in ('email_client','gtasks_sync'):
            copy_file(SOURCE/f'telegram-bots/shared/{name}.py',dst/f'{name}.py',ledger)
            portable_literals(dst/f'{name}.py',dst)
        copy_file(SOURCE/'telegram-bots/scripts/google_auth.py',dst/'google_auth.py',ledger)
        portable_literals(dst/'google_auth.py',dst)
        (dst/'requirements.txt').write_text('# Runtime helpers use the Python standard library. See OAuth setup source for optional setup dependencies.\n')
        (dst/'USAGE.md').write_text('# Optional account connectors\n\nRead module docstrings for environment variable names and APIs. Configure SMTP/IMAP\nor Google OAuth yourself. No credentials, access tokens or account data are included.\nRun each helper from its own environment and choose local credential storage paths.\nThese source modules expose explicit functions; importing/checking them does not\nsend email or edit tasks. Actual delivery, authentication and permissions were not\ntested during the source backup. No background sync is enabled by this repository.\n')
    elif kind=='indicator':
        tree(Path(os.environ.get('R2D2_INDICATOR_SOURCE') or next(SOURCE.glob('*/smart_candles_reconstruction.pine')).parent),dst,ledger,lambda p:p.suffix in ('.md','.pine'))
    active={str(Path(row['path']).relative_to(dst)) for row in ledger}
    for old in previous:
        relative=old['path']
        if relative in active:continue
        stale=(dst/relative).resolve()
        if dst.resolve() not in stale.parents:raise ValueError('Manifest path escaped export root')
        if not stale.is_file():continue
        if hashlib.sha256(stale.read_bytes()).hexdigest()!=old.get('export_sha256'):
            raise ValueError('Previously exported file has independent edits; preserve/reconcile it before export: '+relative)
        stale.unlink()
    # All files get independent checks; never import operational entry points here.
    write_check(dst,kind)
    readme=f"# {repo['name']}\n\n{repo['description']}\n\n{repo['purpose']}\n\n## Features\n\n"+'\n'.join('- '+f for f in repo['features'])
    readme+='\n\n## Use\n\n'+repo['run']+'\n\nRun `python3 check.py` for read-only source checks. These checks are not a claim\nthat external accounts, market feeds, hardware or a deployed service are configured.\n'
    readme+='\n## Snapshot and updates\n\nCreated on 2026-11-05 from the local R2D2 workspaces. This is a private source\nsnapshot; the original local workspaces remain the working copies. The catalogue\nrepo records every source and omission. Updates happen only on explicit operator\nrequest; there is no automatic sync, push, hook or publishing timer.\n\nCredentials, private chats/memory, live paper books, game saves, models, caches,\nvirtual environments and proprietary application binaries are not included.\nUse a separate environment for this repo. Read USAGE.md/SETUP.md or the original\nREADME where present. Existing integrations are documented rather than silently\nstarting account actions.\n'
    template=HERE/'docs/repositories'/f"{repo['name']}.md"
    (dst/'README.md').write_text(template.read_text() if template.exists() else readme)
    (dst/'.gitignore').write_text('''# Credentials and private runtime state
.env
.env.*
!.env.example
*.db
*.sqlite*
*.log
*.pyc
__pycache__/
.venv/
venv/
node_modules/
**/data/
**/runs/
**/models/
.state/
backups/
credentials.json
token.json
cookies.json
''')
    # Preserve the original broad ignore files under nested integrated roots.
    for row in ledger:
        row['path']=str(Path(row['path']).relative_to(dst))
        row['export_sha256']=hashlib.sha256((dst/row['path']).read_bytes()).hexdigest()
    (dst/'SOURCE_MANIFEST.json').write_text(json.dumps({'exported_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
           'source_home':str(SOURCE),'repo':repo['name'],'files':ledger,
           'adaptations':'Toolkit copies may adapt absolute paths or remove optional cross-repo notification dependencies; source and export hashes expose this.'},indent=2)+'\n')
    print(json.dumps({'repo':repo['name'],'source_files':len(ledger),'bytes':sum(p.stat().st_size for p in dst.rglob('*') if p.is_file() and '.git' not in p.parts)}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--repo',action='append',choices=['all']+[r['name'] for r in CONFIG['repos']])
    args=parser.parse_args()
    if args.list:
        for r in CONFIG['repos']:print(r['name']+' — '+r['description'])
        return
    if not args.repo:parser.error('Choose --repo explicitly; nothing is exported automatically')
    for r in CONFIG['repos']:
        if 'all' in args.repo or r['name'] in args.repo:build(r)

if __name__=='__main__':main()
