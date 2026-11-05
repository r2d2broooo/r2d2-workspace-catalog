# External tools remain external

We preserve our source, adapters, recipes and notices. We do not republish installed
third-party executables, browser profiles, accounts or plugin caches as our projects.

Trading uses Python, NumPy/pandas, FastAPI/Uvicorn, plotting libraries, market-data
libraries and optional provider CLIs/Ollama. See its requirements and setup notes.
Browser research uses Chrome/CDP, Playwright, Scrapling, Trafilatura, captions and
optional X11 tools. Knowledge helpers use Python stdlib and optional pdftotext.
Agent providers require their own installations/login. Optional Telegram, mail and
Google Tasks integrations need local credentials. Wi-Fi uses Linux NetworkManager;
the optional status UI needs Gtk/PyGObject. Linux scripts require host-specific review.

Serena, Context7, REA, Graphify, hosted model services, Sites and other installed
plugins are upstream dependencies, not separately authored tools in this archive.
The agent-skills repo preserves relevant recipes and available upstream notices.
Review every individual license before redistributing third-party material publicly.
