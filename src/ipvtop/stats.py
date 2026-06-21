from __future__ import annotations

from collections import Counter, deque

from ipvtop.models import IntervalStats, PacketInfo, PROTOCOL_NAMES, is_multicast


def format_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            if unit == "B":
                return f"{n:.0f} {unit}"
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def format_rate(n: float) -> str:
    return f"{format_bytes(n)}/s"


class TrafficStats:
    def __init__(self, packet_queue: deque, history_size: int = 60) -> None:
        self._packet_queue = packet_queue
        self.history_size = history_size

        self.ipv4_pps: deque[float] = deque(maxlen=history_size)
        self.ipv6_pps: deque[float] = deque(maxlen=history_size)
        self.ipv4_bps: deque[float] = deque(maxlen=history_size)
        self.ipv6_bps: deque[float] = deque(maxlen=history_size)
        self.total_pps: deque[float] = deque(maxlen=history_size)
        self.total_bps: deque[float] = deque(maxlen=history_size)

        self.total_ipv4_packets: int = 0
        self.total_ipv6_packets: int = 0
        self.total_other_packets: int = 0
        self.total_ipv4_bytes: int = 0
        self.total_ipv6_bytes: int = 0
        self.total_other_bytes: int = 0

        self._source_counter: Counter[str] = Counter()
        self._dest_counter: Counter[str] = Counter()
        self._source_bytes: Counter[str] = Counter()
        self._dest_bytes: Counter[str] = Counter()
        self._flow_counter: Counter[tuple[str, str]] = Counter()
        self._flow_bytes: Counter[tuple[str, str]] = Counter()
        self._proto_counter: Counter[str] = Counter()

        for _ in range(history_size):
            self.ipv4_pps.append(0)
            self.ipv6_pps.append(0)
            self.ipv4_bps.append(0)
            self.ipv6_bps.append(0)
            self.total_pps.append(0)
            self.total_bps.append(0)

    def tick(self) -> IntervalStats:
        packets: list[PacketInfo] = []
        while True:
            try:
                packets.append(self._packet_queue.popleft())
            except IndexError:
                break

        v4_pkts = v6_pkts = other_pkts = 0
        v4_bytes = v6_bytes = other_bytes = 0
        src_counter: Counter[str] = Counter()
        dst_counter: Counter[str] = Counter()
        src_bytes: Counter[str] = Counter()
        dst_bytes: Counter[str] = Counter()
        flow_counter: Counter[tuple[str, str]] = Counter()
        flow_bytes: Counter[tuple[str, str]] = Counter()
        proto_counter: Counter[str] = Counter()

        for pkt in packets:
            if pkt.ip_version == 4:
                v4_pkts += 1
                v4_bytes += pkt.size
            elif pkt.ip_version == 6:
                v6_pkts += 1
                v6_bytes += pkt.size
            else:
                other_pkts += 1
                other_bytes += pkt.size

            if pkt.src_ip:
                src_counter[pkt.src_ip] += 1
                src_bytes[pkt.src_ip] += pkt.size
            if pkt.dst_ip:
                dst_counter[pkt.dst_ip] += 1
                dst_bytes[pkt.dst_ip] += pkt.size
            if pkt.src_ip and pkt.dst_ip:
                flow = (pkt.src_ip, pkt.dst_ip)
                flow_counter[flow] += 1
                flow_bytes[flow] += pkt.size

            if is_multicast(pkt.ip_version, pkt.dst_ip):
                proto_name = "Multicast"
            else:
                proto_name = PROTOCOL_NAMES.get(pkt.protocol, f"Other({pkt.protocol})")
            proto_counter[proto_name] += 1

        self.ipv4_pps.append(v4_pkts)
        self.ipv6_pps.append(v6_pkts)
        self.ipv4_bps.append(v4_bytes)
        self.ipv6_bps.append(v6_bytes)
        self.total_pps.append(v4_pkts + v6_pkts + other_pkts)
        self.total_bps.append(v4_bytes + v6_bytes + other_bytes)

        self.total_ipv4_packets += v4_pkts
        self.total_ipv6_packets += v6_pkts
        self.total_other_packets += other_pkts
        self.total_ipv4_bytes += v4_bytes
        self.total_ipv6_bytes += v6_bytes
        self.total_other_bytes += other_bytes

        self._source_counter += src_counter
        self._dest_counter += dst_counter
        self._source_bytes += src_bytes
        self._dest_bytes += dst_bytes
        self._flow_counter += flow_counter
        self._flow_bytes += flow_bytes
        self._proto_counter += proto_counter

        top_sources = [
            (ip, src_counter[ip], src_bytes[ip])
            for ip in [ip for ip, _ in self._source_counter.most_common(15)]
        ]
        top_dests = [
            (ip, dst_counter[ip], dst_bytes[ip])
            for ip in [ip for ip, _ in self._dest_counter.most_common(15)]
        ]
        top_flows = [
            (
                src,
                dst,
                flow_counter[(src, dst)],
                flow_bytes[(src, dst)],
                self._flow_counter[(src, dst)],
                self._flow_bytes[(src, dst)],
            )
            for (src, dst), _ in self._flow_counter.most_common(15)
        ]

        return IntervalStats(
            ipv4_packets=v4_pkts,
            ipv6_packets=v6_pkts,
            other_packets=other_pkts,
            ipv4_bytes=v4_bytes,
            ipv6_bytes=v6_bytes,
            other_bytes=other_bytes,
            top_sources=top_sources,
            top_destinations=top_dests,
            top_flows=top_flows,
            protocol_counts=dict(self._proto_counter.most_common()),
        )

    def reset(self) -> None:
        self.ipv4_pps.clear()
        self.ipv6_pps.clear()
        self.ipv4_bps.clear()
        self.ipv6_bps.clear()
        self.total_pps.clear()
        self.total_bps.clear()
        for d in (self.ipv4_pps, self.ipv6_pps, self.ipv4_bps, self.ipv6_bps,
                  self.total_pps, self.total_bps):
            for _ in range(self.history_size):
                d.append(0)
        self.total_ipv4_packets = 0
        self.total_ipv6_packets = 0
        self.total_other_packets = 0
        self.total_ipv4_bytes = 0
        self.total_ipv6_bytes = 0
        self.total_other_bytes = 0
        self._source_counter.clear()
        self._dest_counter.clear()
        self._source_bytes.clear()
        self._dest_bytes.clear()
        self._flow_counter.clear()
        self._flow_bytes.clear()
        self._proto_counter.clear()
