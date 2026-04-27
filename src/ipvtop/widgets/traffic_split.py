from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class TrafficSplit(Widget):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._v4_bytes: int = 0
        self._v6_bytes: int = 0

    def update_stats(self, total_v4_bytes: int, total_v6_bytes: int) -> None:
        self._v4_bytes = total_v4_bytes
        self._v6_bytes = total_v6_bytes
        self.refresh()

    def render(self) -> Text:
        total = self._v4_bytes + self._v6_bytes
        if total == 0:
            pct_v4 = 0.0
            pct_v6 = 0.0
        else:
            pct_v4 = self._v4_bytes / total * 100
            pct_v6 = self._v6_bytes / total * 100

        text = Text()

        bar_width = max(self.size.width - 4, 20)
        v4_fill = int(pct_v4 / 100 * bar_width)
        v6_fill = bar_width - v4_fill

        text.append("  ")

        v4_label = f" IPv4 {pct_v4:.1f}% "
        v6_label = f" IPv6 {pct_v6:.1f}% "

        v4_bar = "█" * v4_fill
        v6_bar = "█" * v6_fill

        if len(v4_label) <= v4_fill:
            before = (v4_fill - len(v4_label)) // 2
            after = v4_fill - len(v4_label) - before
            text.append("█" * before, style="#50a0ff")
            text.append(v4_label, style="bold white on #2050a0")
            text.append("█" * after, style="#50a0ff")
        else:
            text.append(v4_bar, style="#50a0ff")

        if len(v6_label) <= v6_fill:
            before = (v6_fill - len(v6_label)) // 2
            after = v6_fill - len(v6_label) - before
            text.append("█" * before, style="#50ffa0")
            text.append(v6_label, style="bold white on #20a050")
            text.append("█" * after, style="#50ffa0")
        else:
            text.append(v6_bar, style="#50ffa0")

        text.append("\n")

        if total == 0:
            text.append("  Waiting for traffic...", style="#606060")
        else:
            text.append(f"  IPv4 ", style="bold #50a0ff")
            text.append(f"{pct_v4:>5.1f}%", style="#50a0ff")
            text.append("  |  ", style="#404060")
            text.append(f"IPv6 ", style="bold #50ffa0")
            text.append(f"{pct_v6:>5.1f}%", style="#50ffa0")

        return text
