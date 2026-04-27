from __future__ import annotations

from rich.text import Text
from textual.widget import Widget
from textual.reactive import reactive

from ipvtop.models import IntervalStats
from ipvtop.stats import format_bytes, format_rate


class SummaryPanel(Widget):

    interval: reactive[IntervalStats | None] = reactive(None)
    total_v4_pkts: reactive[int] = reactive(0)
    total_v6_pkts: reactive[int] = reactive(0)
    total_v4_bytes: reactive[int] = reactive(0)
    total_v6_bytes: reactive[int] = reactive(0)
    uptime_seconds: reactive[int] = reactive(0)

    def update_stats(
        self,
        interval: IntervalStats,
        total_v4_pkts: int,
        total_v6_pkts: int,
        total_v4_bytes: int,
        total_v6_bytes: int,
        uptime: int,
    ) -> None:
        self.interval = interval
        self.total_v4_pkts = total_v4_pkts
        self.total_v6_pkts = total_v6_pkts
        self.total_v4_bytes = total_v4_bytes
        self.total_v6_bytes = total_v6_bytes
        self.uptime_seconds = uptime
        self.refresh()

    def render(self) -> Text:
        iv = self.interval
        text = Text()

        v4_pps = iv.ipv4_packets if iv else 0
        v6_pps = iv.ipv6_packets if iv else 0
        v4_bps = iv.ipv4_bytes if iv else 0
        v6_bps = iv.ipv6_bytes if iv else 0

        total_pkts = self.total_v4_pkts + self.total_v6_pkts
        pct_v4 = (self.total_v4_pkts / total_pkts * 100) if total_pkts else 0
        pct_v6 = (self.total_v6_pkts / total_pkts * 100) if total_pkts else 0

        mins, secs = divmod(self.uptime_seconds, 60)
        hrs, mins = divmod(mins, 60)
        uptime_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        text.append("  UPTIME ", style="bold #a0a0a0")
        text.append(f"{uptime_str}\n", style="bold white")
        text.append("\n")

        text.append("  IPv4 ", style="bold #50a0ff")
        text.append(f"{'─' * 22}\n", style="#404060")

        text.append("    rate   ", style="#808080")
        text.append(f"{v4_pps:>6,} pkt/s ", style="#50a0ff")
        text.append(f"{format_rate(v4_bps):>10}\n", style="#50a0ff")

        text.append("    total  ", style="#808080")
        text.append(f"{self.total_v4_pkts:>10,} pkts ", style="#6080b0")
        text.append(f"{format_bytes(self.total_v4_bytes):>8}\n", style="#6080b0")

        text.append("    share  ", style="#808080")
        text.append(f"{pct_v4:>5.1f}%\n", style="#50a0ff")

        text.append("\n")

        text.append("  IPv6 ", style="bold #50ffa0")
        text.append(f"{'─' * 22}\n", style="#406040")

        text.append("    rate   ", style="#808080")
        text.append(f"{v6_pps:>6,} pkt/s ", style="#50ffa0")
        text.append(f"{format_rate(v6_bps):>10}\n", style="#50ffa0")

        text.append("    total  ", style="#808080")
        text.append(f"{self.total_v6_pkts:>10,} pkts ", style="#60b080")
        text.append(f"{format_bytes(self.total_v6_bytes):>8}\n", style="#60b080")

        text.append("    share  ", style="#808080")
        text.append(f"{pct_v6:>5.1f}%\n", style="#50ffa0")

        return text
