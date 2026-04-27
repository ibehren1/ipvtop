# ipvtop

A real-time network traffic monitor for the terminal with IPv4/IPv6 breakdown. Inspired by [btop](https://github.com/aristocratos/btop).

Built with [Textual](https://github.com/Textualize/textual), [Plotext](https://github.com/piccolomo/plotext), and [Scapy](https://scapy.net/).

## Build Status
[![Build binaries](https://github.com/ibehren1/ipvtop/actions/workflows/build.yml/badge.svg)](https://github.com/ibehren1/ipvtop/actions/workflows/build.yml)

## Features

- Live packet capture with per-second refresh
- IPv4 vs IPv6 traffic breakdown across all panels
- Rolling 60-second bandwidth chart (Mb/s) with braille-dot plotting
- Sparkline history for packets/s and Mb/s per protocol version
- Visual IPv4/IPv6 traffic split bar
- Top talkers table (sources and destinations) with tabbed view
- Protocol breakdown (TCP, UDP, ICMP, ICMPv6, GRE, ESP, AH, SCTP)
- btop-inspired dark theme with rounded borders and color-coded panels
- Runs on Linux and macOS

## Screenshot

```
╭─ Summary ────────────────╮╭─ Bandwidth ──────────────────────────────────╮
│  UPTIME 00:05:32         ││                                              │
│                          ││  ⡀⠀⠀⡀⣀⠀⠀⠀⡀⠀⠀⣀⠀⠀⡀⠀  IPv4 ─── IPv6   │
│  IPv4 ──────────────     ││  ⣧⣤⣰⣧⣿⣧⣆⣴⣿⣇⣠⣿⣧⣀⣿⣆  0.42 Mb/s       │
│    rate  1,234 pkt/s     ││                                              │
│    total  45,231 pkts    ││  -60s    -45s    -30s    -15s    now         │
│  IPv6 ──────────────     ││                                              │
│    rate    567 pkt/s     ││                                              │
│    total  12,045 pkts    ││                                              │
╰──────────────────────────╯╰──────────────────────────────────────────────╯
╭─ IPv4 / IPv6 Split ─────────────────────────────────────────────────────╮
│  ████████████████████ IPv4 78.3% ████████ IPv6 21.7% ████              │
╰─────────────────────────────────────────────────────────────────────────╯
╭─ Traffic History ────────────────────────────────────────────────────────╮
│  IPv4 Mb/s   ▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁▂▃▅  0.42 Mb/s         │
│  IPv6 Mb/s   ▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂  0.08 Mb/s         │
│  IPv4 pkt/s  ▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁▂▃▅▇█▇▅▃▂▁▂▃▅  1,234 pkt/s       │
│  IPv6 pkt/s  ▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂▃▂▁▁▂  567 pkt/s         │
╰──────────────────────────────────────────────────────────────────────────╯
╭─ Top Talkers ─────────────────────────╮╭─ Protocols ─────────────────────╮
│  Sources | Destinations               ││  TCP     ████████████░░  78.2%  │
│  # IP Address        Pkt/s  Bytes/s   ││  UDP     ███░░░░░░░░░░  15.1%  │
│  1 192.168.1.10      523    0.2 MB    ││  ICMP    █░░░░░░░░░░░░   4.2%  │
│  2 fe80::1           312    0.1 MB    ││  ICMPv6  ░░░░░░░░░░░░░   2.5%  │
│  3 10.0.0.1          198    85.2 KB   ││                                 │
╰───────────────────────────────────────╯╰─────────────────────────────────╯
```

## Installation

### Pre-built binaries

Download the latest binary for your platform from [GitHub Releases](../../releases):

| Platform | Architecture | Download |
|----------|-------------|----------|
| Linux    | x86_64      | `ipvtop-linux-x86_64` |
| Linux    | ARM64       | `ipvtop-linux-arm64` |
| macOS    | ARM64       | `ipvtop-macos-arm64` |

```bash
chmod +x ipvtop-*
sudo ./ipvtop-linux-x86_64 eth0
```

### From source with uv

```bash
git clone https://github.com/yourusername/ipvtop.git
cd ipvtop
uv sync
sudo uv run ipvtop eth0
```

### With pip

```bash
pip install .
sudo ipvtop eth0
```

## Usage

```
usage: ipvtop [-h] [-l] [interface]

Real-time network traffic monitor with IPv4/IPv6 breakdown

positional arguments:
  interface   Network interface to monitor (e.g., eth0, wlan0, en0)

options:
  -h, --help  show this help message and exit
  -l, --list  List available network interfaces and exit
```

### Examples

```bash
# List available interfaces
ipvtop -l

# Monitor a specific interface (requires root)
sudo ipvtop eth0        # Linux
sudo ipvtop en0         # macOS

# Run from source with uv
sudo uv run ipvtop eth0
```

### Keybindings

| Key | Action |
|-----|--------|
| `q` | Quit |
| `p` | Pause / resume display |
| `r` | Reset all statistics |

## Dashboard panels

### Summary

Displays running totals and per-second rates for IPv4 and IPv6 traffic (packets and bytes), the IPv4:IPv6 ratio, and session uptime.

### Bandwidth

A 60-second rolling line chart rendered with braille characters showing IPv4 and IPv6 throughput in Mb/s.

### IPv4 / IPv6 Split

A full-width stacked bar showing the cumulative byte ratio between IPv4 (blue) and IPv6 (green) with embedded percentage labels.

### Traffic History

Four sparkline rows showing rolling 60-second history:
- IPv4 Mb/s
- IPv6 Mb/s
- IPv4 packets/s
- IPv6 packets/s

### Top Talkers

A tabbed data table switching between top source and destination IPs. Shows per-second and cumulative packet/byte counts. IPs are color-coded blue (v4) or green (v6).

### Protocols

Horizontal bar chart showing the distribution of traffic across protocols (TCP, UDP, ICMP, ICMPv6, GRE, ESP, AH, SCTP).

## Color scheme

The interface uses a btop-inspired dark theme:

| Element | Color |
|---------|-------|
| IPv4    | Blue (`#50a0ff`) |
| IPv6    | Green (`#50ffa0`) |
| ICMP    | Orange (`#ffa050`) |
| ICMPv6  | Pink (`#ff50a0`) |
| Background | Dark blue-black (`#0a0a1a`) |
| Panel borders | Rounded, muted (`#303050`) |

## Building binaries

### Local build

```bash
uv sync --dev
uv run pyinstaller ipvtop.spec --clean --noconfirm
# Binary at dist/ipvtop
```

### CI/CD

The GitHub Actions workflow (`.github/workflows/build.yml`) builds binaries for all four platform/architecture combinations.

**Automatic release** on tag push:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers a build of all four binaries, generates SHA256 checksums, and creates a GitHub Release with the artifacts attached.

**Manual build** via the Actions tab using "Run workflow".

## Requirements

- Python >= 3.10
- Root privileges (for raw packet capture)
- A terminal emulator with 256-color support

### Dependencies

| Package | Purpose |
|---------|---------|
| [textual](https://github.com/Textualize/textual) | TUI framework |
| [textual-plotext](https://github.com/Textualize/textual-plotext) | Terminal charts |
| [scapy](https://scapy.net/) | Packet capture and parsing |

## Platform notes

### macOS

Promiscuous mode is not supported on most macOS interfaces. ipvtop automatically disables it and captures in normal mode, which sees all traffic to and from your machine.

### Linux

Works out of the box with `sudo`. Alternatively, grant the binary the `CAP_NET_RAW` capability to avoid running as root:

```bash
sudo setcap cap_net_raw+ep ./ipvtop
./ipvtop eth0
```

## License

MIT — Copyright © 2026 Isaac B. Behrens. All rights reserved.
