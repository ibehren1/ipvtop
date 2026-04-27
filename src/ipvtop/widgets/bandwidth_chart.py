from __future__ import annotations

from textual_plotext import PlotextPlot

from ipvtop.stats import TrafficStats

BYTES_TO_MBITS = 8 / 1_000_000


class BandwidthChart(PlotextPlot):

    def update_stats(self, stats: TrafficStats) -> None:
        plt = self.plt
        plt.clear_figure()
        plt.theme("dark")
        plt.title("Bandwidth (Mb/s)")
        plt.plot_size(None, None)

        v4_data = [v * BYTES_TO_MBITS for v in stats.ipv4_bps]
        v6_data = [v * BYTES_TO_MBITS for v in stats.ipv6_bps]
        xs = list(range(len(v4_data)))

        plt.plot(xs, v4_data, label="IPv4", color=(80, 160, 255), marker="braille")
        plt.plot(xs, v6_data, label="IPv6", color=(80, 255, 160), marker="braille")

        plt.xlabel("seconds ago")
        plt.ylabel("Mb/s")
        plt.xticks(
            [0, len(xs) // 4, len(xs) // 2, 3 * len(xs) // 4, len(xs) - 1],
            [f"-{len(xs)}s", f"-{3 * len(xs) // 4}s", f"-{len(xs) // 2}s", f"-{len(xs) // 4}s", "now"],
        )

        self.refresh()
