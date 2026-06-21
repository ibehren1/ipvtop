from __future__ import annotations

from collections import deque
from time import monotonic

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView

from ipvtop import __version__
from ipvtop.capture import PacketCapture
from ipvtop.resolve import Resolver
from ipvtop.stats import TrafficStats
from ipvtop.widgets import (
    BandwidthChart,
    CpuPanel,
    ProtocolBreakdown,
    SparklinePanel,
    SummaryPanel,
    TopTalkersTable,
    TrafficSplit,
)


class IntervalScreen(ModalScreen[float | None]):

    DEFAULT_CSS = """
    IntervalScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #interval-dialog {
        width: 44;
        height: 9;
        border: round #50a0ff;
        background: #1a1a2e;
        padding: 1 2;
    }
    #interval-dialog Label {
        color: #c0c0d0;
        margin-bottom: 1;
    }
    #interval-dialog .hint {
        color: #606080;
        margin-top: 1;
    }
    #interval-dialog Input {
        width: 100%;
        background: #0e0e20;
        color: #ffffff;
        border: tall #303050;
    }
    #interval-dialog Input:focus {
        border: tall #50a0ff;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="interval-dialog"):
            yield Label("Refresh interval (seconds):")
            yield Input(placeholder="e.g. 0.5, 1, 2", id="interval-input")
            yield Label("Enter to apply, Escape to cancel", classes="hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            value = float(event.value)
            if 0.1 <= value <= 60.0:
                self.dismiss(value)
            else:
                self.dismiss(None)
        except ValueError:
            self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)


class InterfaceScreen(ModalScreen[str | None]):

    DEFAULT_CSS = """
    InterfaceScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    #interface-dialog {
        width: 50;
        height: auto;
        max-height: 80%;
        border: round #50a0ff;
        background: #1a1a2e;
        padding: 1 2;
    }
    #interface-dialog Label {
        color: #c0c0d0;
        margin-bottom: 1;
    }
    #interface-dialog .hint {
        color: #606080;
        margin-top: 1;
    }
    #interface-dialog ListView {
        height: auto;
        max-height: 14;
        background: #0e0e20;
        border: tall #303050;
    }
    #interface-dialog ListView:focus {
        border: tall #50a0ff;
    }
    #interface-dialog ListItem {
        background: #0e0e20;
        color: #c0c0d0;
        padding: 0 1;
    }
    #interface-dialog ListItem.-highlight {
        background: #ff50a0;
        color: #0e0e20;
        text-style: bold;
    }
    #interface-dialog ListView:focus > ListItem.-highlight {
        background: #ff50a0;
        color: #0e0e20;
        text-style: bold;
    }
    """

    def __init__(self, interfaces: list[str], current: str | None) -> None:
        super().__init__()
        self._interfaces = interfaces
        self._current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="interface-dialog"):
            yield Label("Select interface to monitor:")
            items = []
            for iface in self._interfaces:
                label = f"{iface}  (current)" if iface == self._current else iface
                items.append(ListItem(Label(label, markup=False)))
            yield ListView(*items, id="interface-list")
            yield Label("↑/↓ to move, Enter to apply, Escape to cancel", classes="hint")

    def on_mount(self) -> None:
        list_view = self.query_one("#interface-list", ListView)
        if self._current in self._interfaces:
            list_view.index = self._interfaces.index(self._current)
        list_view.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is None:
            self.dismiss(None)
        else:
            self.dismiss(self._interfaces[index])

    def key_escape(self) -> None:
        self.dismiss(None)


class IPvTopApp(App):
    CSS_PATH = "ipvtop.tcss"
    TITLE = f"ipvtop v{__version__}"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("p", "toggle_pause", "Pause"),
        Binding("r", "toggle_resolve", "Resolve"),
        Binding("R", "reset_stats", "Reset"),
        Binding("n", "change_interval", "Interval"),
        Binding("i", "change_interface", "Interface"),
    ]

    def __init__(self, interface: str | None = None, interval: float = 1.0, resolve: bool = False) -> None:
        super().__init__()
        self.interface = interface
        self.refresh_interval = interval
        self.packet_queue: deque = deque(maxlen=100_000)
        self.traffic_stats = TrafficStats(packet_queue=self.packet_queue)
        self.capture: PacketCapture | None = None
        self.resolver: Resolver | None = None
        self.resolve_enabled = resolve
        self.paused = False
        self._start_time = 0.0
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-row"):
            with Vertical(id="left-col"):
                yield SummaryPanel(id="summary")
                yield CpuPanel(id="cpu-panel")
                yield ProtocolBreakdown(id="protocol-breakdown")
            with Vertical(id="right-col"):
                yield BandwidthChart(id="bandwidth-chart")
                yield TrafficSplit(id="traffic-split")
                yield SparklinePanel(id="sparklines")
        yield Label("", id="status-label", markup=False)
        yield TopTalkersTable(id="top-talkers")
        yield Footer()

    def on_mount(self) -> None:
        if self.resolve_enabled:
            self.resolver = Resolver()
        self._update_subtitle()
        self._start_time = monotonic()

        self.query_one("#summary").border_title = "Summary"
        self.query_one("#bandwidth-chart").border_title = "Bandwidth"
        self.query_one("#traffic-split").border_title = "IPv4 / IPv6 Split"
        self.query_one("#sparklines").border_title = "Traffic History"
        self.query_one("#top-talkers").border_title = "Top Talkers"
        self.query_one("#cpu-panel").border_title = "CPU"
        self.query_one("#protocol-breakdown").border_title = "Protocols"

        self._timer = self.set_interval(self.refresh_interval, self._refresh_stats)

        if self.interface is None:
            # No interface given on the command line — prompt for one at startup.
            self.action_change_interface()
        else:
            self._start_capture(self.interface)

    def _start_capture(self, interface: str) -> None:
        self.interface = interface
        self.capture = PacketCapture(interface=interface, packet_queue=self.packet_queue)
        self.capture.start()
        self._update_subtitle()

    def _refresh_stats(self) -> None:
        try:
            status = self.query_one("#status-label", Label)
        except Exception:
            return
        if self.capture is None:
            status.update(" No interface selected — press 'i' to choose one")
            return
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
            self.resolver if self.resolve_enabled else None,
        )
        self.query_one("#cpu-panel", CpuPanel).poll()
        self.query_one("#protocol-breakdown", ProtocolBreakdown).update_stats(interval)

    def _update_subtitle(self) -> None:
        flags = []
        if self.resolve_enabled:
            flags.append("DNS")
        if self.paused:
            flags.append("PAUSED")
        suffix = f" [{' '.join(flags)}]" if flags else ""
        iface = self.interface if self.interface is not None else "no interface"
        self.sub_title = f"{iface} | {self.refresh_interval:.1f}s{suffix}"

    def action_toggle_pause(self) -> None:
        self.paused = not self.paused
        self._update_subtitle()

    def action_toggle_resolve(self) -> None:
        self.resolve_enabled = not self.resolve_enabled
        if self.resolve_enabled and self.resolver is None:
            self.resolver = Resolver()
        self._update_subtitle()

    def action_reset_stats(self) -> None:
        self.traffic_stats.reset()
        self._start_time = monotonic()

    def action_change_interval(self) -> None:
        self.push_screen(IntervalScreen(), self._on_interval_changed)

    def _on_interval_changed(self, value: float | None) -> None:
        if value is None:
            return
        self.refresh_interval = value
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(self.refresh_interval, self._refresh_stats)
        self._update_subtitle()

    def action_change_interface(self) -> None:
        interfaces = PacketCapture.list_interfaces()
        if not interfaces:
            return
        self.push_screen(
            InterfaceScreen(interfaces, self.interface),
            self._on_interface_changed,
        )

    def _on_interface_changed(self, interface: str | None) -> None:
        if interface is None or interface == self.interface:
            return
        if self.capture is not None:
            self.capture.stop()
        self.packet_queue.clear()
        self.traffic_stats.reset()
        self._start_time = monotonic()
        self._start_capture(interface)

    def on_unmount(self) -> None:
        if self.capture is not None:
            self.capture.stop()
        if self.resolver is not None:
            self.resolver.stop()
