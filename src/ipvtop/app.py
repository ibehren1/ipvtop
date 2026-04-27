from __future__ import annotations

from collections import deque
from time import monotonic

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label

from ipvtop.capture import PacketCapture
from ipvtop.stats import TrafficStats
from ipvtop.widgets import (
    BandwidthChart,
    ProtocolBreakdown,
    SparklinePanel,
    SummaryPanel,
    TopTalkersTable,
    TrafficSplit,
)


class IPvTopApp(App):
    CSS_PATH = "ipvtop.tcss"
    TITLE = "ipvtop"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("p", "toggle_pause", "Pause"),
        Binding("r", "reset_stats", "Reset"),
    ]

    def __init__(self, interface: str) -> None:
        super().__init__()
        self.interface = interface
        self.packet_queue: deque = deque(maxlen=100_000)
        self.traffic_stats = TrafficStats(packet_queue=self.packet_queue)
        self.capture = PacketCapture(interface=self.interface, packet_queue=self.packet_queue)
        self.paused = False
        self._start_time = 0.0

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="top-row"):
            yield SummaryPanel(id="summary")
            yield BandwidthChart(id="bandwidth-chart")
        yield TrafficSplit(id="traffic-split")
        with Horizontal(id="mid-row"):
            yield SparklinePanel(id="sparklines")
        with Horizontal(id="bottom-row"):
            yield TopTalkersTable(id="top-talkers")
            with Vertical(id="right-col"):
                yield Label("", id="status-label", markup=False)
                yield ProtocolBreakdown(id="protocol-breakdown")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = f"{self.interface}"
        self._start_time = monotonic()

        self.query_one("#summary").border_title = "Summary"
        self.query_one("#bandwidth-chart").border_title = "Bandwidth"
        self.query_one("#traffic-split").border_title = "IPv4 / IPv6 Split"
        self.query_one("#sparklines").border_title = "Traffic History"
        self.query_one("#top-talkers").border_title = "Top Talkers"
        self.query_one("#protocol-breakdown").border_title = "Protocols"

        self.capture.start()
        self.set_interval(1.0, self._refresh_stats)

    def _refresh_stats(self) -> None:
        # Always update status line
        status = self.query_one("#status-label", Label)
        if self.capture.error:
            status.update(f" [ERROR] {self.capture.error}")
        elif not self.capture.is_running:
            status.update(f" [WARN] Sniffer not running — raw pkts seen: {self.capture.raw_count}")
        else:
            status.update(
                f" {self.interface} | "
                f"capture: {'paused' if self.paused else 'live'} | "
                f"raw pkts: {self.capture.raw_count:,} | "
                f"queue: {len(self.packet_queue):,}"
            )

        if self.paused:
            return

        interval = self.traffic_stats.tick()
        uptime = int(monotonic() - self._start_time)

        self.query_one("#summary", SummaryPanel).update_stats(
            interval=interval,
            total_v4_pkts=self.traffic_stats.total_ipv4_packets,
            total_v6_pkts=self.traffic_stats.total_ipv6_packets,
            total_v4_bytes=self.traffic_stats.total_ipv4_bytes,
            total_v6_bytes=self.traffic_stats.total_ipv6_bytes,
            uptime=uptime,
        )

        self.query_one("#traffic-split", TrafficSplit).update_stats(
            self.traffic_stats.total_ipv4_bytes,
            self.traffic_stats.total_ipv6_bytes,
        )
        self.query_one("#bandwidth-chart", BandwidthChart).update_stats(self.traffic_stats)
        self.query_one("#sparklines", SparklinePanel).update_stats(self.traffic_stats)
        self.query_one("#top-talkers", TopTalkersTable).update_stats(
            interval,
            self.traffic_stats._source_counter,
            self.traffic_stats._dest_counter,
            self.traffic_stats._source_bytes,
            self.traffic_stats._dest_bytes,
        )
        self.query_one("#protocol-breakdown", ProtocolBreakdown).update_stats(interval)

    def action_toggle_pause(self) -> None:
        self.paused = not self.paused
        self.sub_title = f"{self.interface} {'[PAUSED]' if self.paused else ''}"

    def action_reset_stats(self) -> None:
        self.traffic_stats.reset()
        self._start_time = monotonic()

    def on_unmount(self) -> None:
        self.capture.stop()
