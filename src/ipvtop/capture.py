from __future__ import annotations

import traceback
import threading
from collections import deque
from time import time, sleep
from typing import Any


class PacketCapture:
    def __init__(self, interface: str, packet_queue: deque) -> None:
        self.interface = interface
        self.packet_queue = packet_queue
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._error: str | None = None
        self.raw_count: int = 0

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        sleep(1.0)

    def _run(self) -> None:
        try:
            from scapy.all import sniff, conf
            # Promiscuous mode fails on macOS — disable it
            conf.sniff_promisc = False

            sniff(
                iface=self.interface,
                prn=self._handle_packet,
                store=False,
                stop_filter=lambda _: self._stop_event.is_set(),
            )
        except Exception as exc:
            self._error = f"{type(exc).__name__}: {exc}"

    def _handle_packet(self, packet: Any) -> None:
        from scapy.layers.inet import IP
        from scapy.layers.inet6 import IPv6
        from ipvtop.models import PacketInfo

        self.raw_count += 1

        ts = time()
        size = len(packet)

        if packet.haslayer(IP):
            ip = packet[IP]
            self.packet_queue.append(PacketInfo(
                timestamp=ts,
                ip_version=4,
                src_ip=ip.src,
                dst_ip=ip.dst,
                size=size,
                protocol=ip.proto,
            ))
        elif packet.haslayer(IPv6):
            ip6 = packet[IPv6]
            self.packet_queue.append(PacketInfo(
                timestamp=ts,
                ip_version=6,
                src_ip=ip6.src,
                dst_ip=ip6.dst,
                size=size,
                protocol=ip6.nh,
            ))
        else:
            self.packet_queue.append(PacketInfo(
                timestamp=ts,
                ip_version=0,
                src_ip="",
                dst_ip="",
                size=size,
                protocol=0,
            ))

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3)

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def error(self) -> str | None:
        return self._error

    @staticmethod
    def list_interfaces() -> list[str]:
        from scapy.all import get_if_list
        return get_if_list()
