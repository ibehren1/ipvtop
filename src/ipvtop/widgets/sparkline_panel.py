from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label, Sparkline

from ipvtop.stats import TrafficStats

BYTES_TO_MBITS = 8 / 1_000_000


def _fmt_mbps(bps: float) -> str:
    return f"{bps * BYTES_TO_MBITS:.2f} Mb/s"


class SparklineRow(Widget):
    DEFAULT_CSS = """
    SparklineRow {
        height: 2;
        layout: horizontal;
    }
    SparklineRow Label.spark-label {
        width: 16;
        content-align: right middle;
        color: #808080;
    }
    SparklineRow Sparkline {
        width: 1fr;
    }
    SparklineRow Label.spark-value {
        width: 14;
        content-align: right middle;
    }
    """

    def __init__(
        self,
        label: str,
        color: str,
        row_id: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._color = color
        self._row_id = row_id

    def compose(self) -> ComposeResult:
        yield Label(f" {self._label} ", classes="spark-label")
        spark_classes = "v6-spark" if "v6" in self._row_id else "v4-spark"
        yield Sparkline(
            data=[0] * 60,
            id=f"spark-{self._row_id}",
            classes=spark_classes,
        )
        yield Label("0", classes="spark-value", id=f"val-{self._row_id}")


class SparklinePanel(Widget):
    DEFAULT_CSS = """
    SparklinePanel {
        height: 100%;
        layout: vertical;
    }
    """

    def compose(self) -> ComposeResult:
        yield SparklineRow("IPv4 Mb/s", "#50a0ff", "v4-bps")
        yield SparklineRow("IPv6 Mb/s", "#50ffa0", "v6-bps")
        yield SparklineRow("IPv4 pkt/s", "#50a0ff", "v4-pps")
        yield SparklineRow("IPv6 pkt/s", "#50ffa0", "v6-pps")

    def update_stats(self, stats: TrafficStats) -> None:
        v4_mbps = [v * BYTES_TO_MBITS for v in stats.ipv4_bps]
        v6_mbps = [v * BYTES_TO_MBITS for v in stats.ipv6_bps]
        self._update_row("v4-bps", v4_mbps, _fmt_mbps(stats.ipv4_bps[-1]))
        self._update_row("v6-bps", v6_mbps, _fmt_mbps(stats.ipv6_bps[-1]))
        self._update_row("v4-pps", list(stats.ipv4_pps), f"{int(stats.ipv4_pps[-1]):,} pkt/s")
        self._update_row("v6-pps", list(stats.ipv6_pps), f"{int(stats.ipv6_pps[-1]):,} pkt/s")

    def _update_row(self, row_id: str, data: list[float], value_text: str) -> None:
        try:
            spark = self.query_one(f"#spark-{row_id}", Sparkline)
            spark.data = data
            val = self.query_one(f"#val-{row_id}", Label)
            val.update(f" {value_text} ")
        except Exception:
            pass
