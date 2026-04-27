from __future__ import annotations

from typing import NamedTuple

PROTOCOL_NAMES: dict[int, str] = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
    58: "ICMPv6",
    47: "GRE",
    50: "ESP",
    51: "AH",
    132: "SCTP",
}


class PacketInfo(NamedTuple):
    timestamp: float
    ip_version: int  # 4, 6, or 0
    src_ip: str
    dst_ip: str
    size: int
    protocol: int


class IntervalStats(NamedTuple):
    ipv4_packets: int
    ipv6_packets: int
    other_packets: int
    ipv4_bytes: int
    ipv6_bytes: int
    other_bytes: int
    top_sources: list[tuple[str, int, int]]  # (ip, packets, bytes)
    top_destinations: list[tuple[str, int, int]]
    protocol_counts: dict[str, int]
