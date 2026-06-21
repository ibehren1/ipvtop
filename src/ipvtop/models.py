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


def is_multicast(ip_version: int, dst_ip: str) -> bool:
    """Return True if the destination address is multicast.

    IPv4 multicast is 224.0.0.0/4 (first octet 224-239); IPv6 multicast is
    ff00::/8 (address starts with "ff").
    """
    if not dst_ip:
        return False
    if ip_version == 4:
        first = dst_ip.split(".", 1)[0]
        return first.isdigit() and 224 <= int(first) <= 239
    if ip_version == 6:
        return dst_ip.lower().startswith("ff")
    return False


class IntervalStats(NamedTuple):
    ipv4_packets: int
    ipv6_packets: int
    other_packets: int
    ipv4_bytes: int
    ipv6_bytes: int
    other_bytes: int
    top_sources: list[tuple[str, int, int]]  # (ip, packets, bytes)
    top_destinations: list[tuple[str, int, int]]
    # (src_ip, dst_ip, packets, bytes, total_packets, total_bytes)
    top_flows: list[tuple[str, str, int, int, int, int]]
    protocol_counts: dict[str, int]
