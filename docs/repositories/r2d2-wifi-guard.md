# R2D2 Wi-Fi Guard

A Linux workstation watchdog that notices a failed Wi-Fi connection and asks NetworkManager to reactivate an existing saved connection. It is intended for a workstation that should remain reachable but sometimes fails to reconnect after a router or link interruption.

The guard uses the connection already configured in NetworkManager. It does not collect or store a Wi-Fi password, and it does not require an AI model or the trading system.

## Components

- `bin/wifi-guard`: the Bash watchdog and its `run`, `status`, `reconnect`, `pause` and `resume` commands.
- `bin/wifi-guard-ui`: an optional Python/Gtk status window and tray interface.
- `bin/wifi-guard-notify`: an optional queue flusher for Telegram outage notices.
- `systemd/wifi-guard.service`: a user-service example.
- `desktop/`: a desktop launcher example.

The loop gives NetworkManager a grace period to recover naturally, tracks link/outage phases and records local event history. Notifications are queued while offline and attempted later. Closing the optional window does not stop a separately running watchdog service.

## Requirements

The core needs Linux, Bash, NetworkManager's `nmcli` and standard command-line utilities. The optional interface needs Python and Gtk/PyGObject. Telegram notices use Python's standard library and separately configured credentials.

## Setup

First confirm that the saved connection reconnects through NetworkManager on its own. Read [USAGE.md](USAGE.md), set `WIFI_GUARD_IFACE` for your interface and review the supported timing overrides in the script. Interface names are machine-specific; no actual network profile or router address is supplied here.

A source check does not change connectivity:

```bash
python3 check.py
bash -n bin/wifi-guard
```

After reviewing configuration, install the scripts in your chosen local executable directory and adapt the launcher/service paths. Run `wifi-guard status` before choosing to run the loop or enable a service. Installation and service activation are manual.

For optional notifications, supply `WIFI_GUARD_TELEGRAM_TOKEN` and `WIFI_GUARD_TELEGRAM_CHAT_ID` in the local process environment. No notifier credentials are included. Leave them unset if notifications are not wanted.

## Local state and boundaries

Configuration/pause state lives under the user's configuration directory; events, outages and queued notices live under the local state directory. Those files are not source and should remain private. The pause/resume controls are useful when the user intentionally wants Wi-Fi disabled.

The checks validate source syntax; they do not disconnect a network, test a real router or send a Telegram message. The guard is for NetworkManager-based Linux hosts, not a portable replacement for networking software on every operating system.

## Privacy, provenance and updates

This repository is a sanitized source export. No provider credentials, personal contact information, configured IP addresses, private conversations or runtime databases are included. Example hostnames and local environment variables are intentional. Keep newly generated account data and captures outside version control.

A source manifest records exported files. Local adaptations and third-party material retain their own provenance/notices; public visibility does not apply a new blanket license to every file. Related repositories and the manual update process are listed in the [workspace catalogue](https://github.com/r2d2broooo/r2d2-workspace-catalog).

Updates are made only on explicit request. Cloning does not enable an automatic sync, scheduled publication or Git push.
