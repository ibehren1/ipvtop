from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from ipvtop.models import IntervalStats
from ipvtop.stats import format_bytes


class TopTalkersTable(Widget):
    DEFAULT_CSS = """
    TopTalkersTable {
        height: 100%;
    }
    TopTalkersTable DataTable {
        height: 100%;
    }
    """

    # Fixed widths for the non-IP columns; Source/Destination split the remainder.
    _FIXED_WIDTHS = {
        "#": 4,
        "Pkt/s": 9,
        "Bytes/s": 11,
        "Total Pkts": 12,
        "Total Bytes": 12,
    }

    def compose(self) -> ComposeResult:
        yield DataTable(id="dt-talkers")

    def on_mount(self) -> None:
        dt = self.query_one("#dt-talkers", DataTable)
        dt.cursor_type = "row"
        dt.zebra_stripes = True
        self._col_keys = dt.add_columns(
            "#", "Source", "Destination", "Pkt/s", "Bytes/s", "Total Pkts", "Total Bytes"
        )
        self._resize_columns()

    def on_resize(self) -> None:
        self._resize_columns()

    def _resize_columns(self) -> None:
        try:
            dt = self.query_one("#dt-talkers", DataTable)
        except Exception:
            return
        # Each column is padded on both sides by cell_padding, so it consumes
        # width + 2 * cell_padding of horizontal space.
        padding_total = 2 * dt.cell_padding * len(self._col_keys)
        available = dt.size.width - padding_total
        fixed_total = sum(self._FIXED_WIDTHS.values())
        ip_space = max(available - fixed_total, 20)
        src_width = ip_space // 2
        dst_width = ip_space - src_width
        for col in dt.columns.values():
            name = col.label.plain
            if name == "Source":
                col.width = src_width
            elif name == "Destination":
                col.width = dst_width
            else:
                col.width = self._FIXED_WIDTHS.get(name, col.width)
            col.auto_width = False
        dt.refresh()

    def update_stats(self, interval: IntervalStats, source_counter, dest_counter, source_bytes, dest_bytes, resolver=None) -> None:
        try:
            dt = self.query_one("#dt-talkers", DataTable)
        except Exception:
            return

        dt.clear()
        for rank, (src, dst, pkts, bts, total_pkts, total_bts) in enumerate(interval.top_flows[:15], 1):
            dt.add_row(
                str(rank),
                self._endpoint(src, resolver),
                self._endpoint(dst, resolver),
                f"{pkts:,}",
                format_bytes(bts),
                f"{total_pkts:,}",
                format_bytes(total_bts),
            )

    @staticmethod
    def _endpoint(ip: str, resolver) -> Text:
        color = "#50ffa0" if ":" in ip else "#50a0ff"
        label = resolver.display(ip) if resolver is not None else ip
        return Text(label, style=color)
