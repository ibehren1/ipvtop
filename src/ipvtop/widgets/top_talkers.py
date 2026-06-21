from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, TabbedContent, TabPane

from ipvtop.models import IntervalStats
from ipvtop.stats import format_bytes


class TopTalkersTable(Widget):
    DEFAULT_CSS = """
    TopTalkersTable {
        height: 100%;
    }
    TopTalkersTable TabbedContent {
        height: 100%;
    }
    TopTalkersTable DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with TabbedContent("Sources", "Destinations"):
            with TabPane("Sources", id="tab-src"):
                yield DataTable(id="dt-sources")
            with TabPane("Destinations", id="tab-dst"):
                yield DataTable(id="dt-dests")

    def on_mount(self) -> None:
        for dt_id in ("dt-sources", "dt-dests"):
            dt = self.query_one(f"#{dt_id}", DataTable)
            dt.cursor_type = "row"
            dt.zebra_stripes = True
            dt.add_columns("#", "IP Address", "Ver", "Pkt/s", "Bytes/s", "Total Pkts", "Total Bytes")

    def update_stats(self, interval: IntervalStats, source_counter, dest_counter, source_bytes, dest_bytes, resolver=None) -> None:
        self._fill_table(
            "dt-sources",
            interval.top_sources,
            source_counter,
            source_bytes,
            resolver,
        )
        self._fill_table(
            "dt-dests",
            interval.top_destinations,
            dest_counter,
            dest_bytes,
            resolver,
        )

    def _fill_table(self, dt_id: str, current: list[tuple[str, int, int]], total_counter, total_bytes, resolver=None) -> None:
        try:
            dt = self.query_one(f"#{dt_id}", DataTable)
        except Exception:
            return

        dt.clear()
        for rank, (ip, pkts, bts) in enumerate(current[:15], 1):
            ver = "v6" if ":" in ip else "v4"
            color = "#50ffa0" if ver == "v6" else "#50a0ff"
            label = resolver.display(ip) if resolver is not None else ip
            dt.add_row(
                str(rank),
                Text(label, style=color),
                Text(ver, style=color),
                f"{pkts:,}",
                format_bytes(bts),
                f"{total_counter.get(ip, 0):,}",
                format_bytes(total_bytes.get(ip, 0)),
            )
