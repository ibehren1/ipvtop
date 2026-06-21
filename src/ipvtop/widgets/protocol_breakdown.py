from __future__ import annotations

from rich.text import Text
from textual.widget import Widget
from textual.reactive import reactive

from ipvtop.models import IntervalStats

PROTO_COLORS: dict[str, str] = {
    "TCP": "#50a0ff",
    "UDP": "#50ffa0",
    "ICMP": "#ffa050",
    "ICMPv6": "#ff50a0",
    "GRE": "#a050ff",
    "ESP": "#ffff50",
    "AH": "#50ffff",
    "SCTP": "#ff5050",
    "Multicast": "#ff9020",
}

# Display labels for protocols whose name is too long for the fixed-width column.
PROTO_LABELS: dict[str, str] = {
    "Multicast": "Mcast",
}


class ProtocolBreakdown(Widget):

    protocol_counts: reactive[dict[str, int]] = reactive(dict)

    def update_stats(self, interval: IntervalStats) -> None:
        self.protocol_counts = dict(interval.protocol_counts)
        self.refresh()

    def render(self) -> Text:
        text = Text()
        counts = self.protocol_counts
        total = sum(counts.values()) if counts else 0

        if total == 0:
            text.append("  Waiting for traffic...\n", style="#606060")
            return text

        bar_width = max(self.size.width - 24, 10)

        sorted_protos = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        for proto, count in sorted_protos:
            pct = count / total
            filled = int(pct * bar_width)
            color = PROTO_COLORS.get(proto, "#808080")
            label = PROTO_LABELS.get(proto, proto)

            text.append(f"  {label:<8}", style=f"bold {color}")
            text.append("█" * filled, style=color)
            text.append("░" * (bar_width - filled), style="#303030")
            text.append(f" {pct:>5.1%} ", style="#a0a0a0")
            text.append(f"{count:>6,}\n", style="#808080")

        return text
