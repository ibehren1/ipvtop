from __future__ import annotations

import argparse
import os
import sys


def main() -> None:
    from ipvtop import __version__

    parser = argparse.ArgumentParser(
        prog="ipvtop",
        description="Real-time network traffic monitor with IPv4/IPv6 breakdown",
    )
    parser.add_argument(
        "interface",
        nargs="?",
        help="Network interface to monitor (e.g., eth0, wlan0)",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version and exit",
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available network interfaces and exit",
    )
    parser.add_argument(
        "-n", "--interval",
        type=float,
        default=1.0,
        help="Screen refresh interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "-r", "--resolve",
        action="store_true",
        help="Reverse-DNS resolve source/dest IPs, showing hostnames when available",
    )
    args = parser.parse_args()

    if args.list:
        from ipvtop.capture import PacketCapture

        for iface in PacketCapture.list_interfaces():
            print(iface)
        sys.exit(0)

    if not args.interface:
        parser.error("interface is required (use -l to list available interfaces)")

    if os.geteuid() != 0:
        print(
            "Error: ipvtop requires root privileges for packet capture.\n"
            "Run with: sudo ipvtop <interface>",
            file=sys.stderr,
        )
        sys.exit(1)

    from ipvtop.app import IPvTopApp

    app = IPvTopApp(interface=args.interface, interval=args.interval, resolve=args.resolve)
    app.run()


if __name__ == "__main__":
    main()
