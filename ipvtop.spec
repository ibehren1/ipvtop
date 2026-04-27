import os
import importlib

# Locate installed package paths for data file collection
textual_path = os.path.dirname(importlib.import_module("textual").__file__)
textual_plotext_path = os.path.dirname(importlib.import_module("textual_plotext").__file__)
ipvtop_path = os.path.dirname(importlib.import_module("ipvtop").__file__)

a = Analysis(
    ["src/ipvtop/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[
        # Textual ships CSS and default themes that must be bundled
        (textual_path, "textual"),
        (textual_plotext_path, "textual_plotext"),
        # Our own .tcss stylesheet
        (os.path.join(ipvtop_path, "ipvtop.tcss"), "ipvtop"),
    ],
    hiddenimports=[
        "ipvtop",
        "ipvtop.app",
        "ipvtop.capture",
        "ipvtop.models",
        "ipvtop.stats",
        "ipvtop.widgets",
        "ipvtop.widgets.summary_panel",
        "ipvtop.widgets.bandwidth_chart",
        "ipvtop.widgets.sparkline_panel",
        "ipvtop.widgets.top_talkers",
        "ipvtop.widgets.protocol_breakdown",
        "ipvtop.widgets.traffic_split",
        "ipvtop.widgets.cpu_panel",
        "psutil",
        "textual",
        "textual_plotext",
        "plotext",
        "scapy",
        "scapy.all",
        "scapy.layers.inet",
        "scapy.layers.inet6",
        "scapy.layers.l2",
        "scapy.layers.dns",
        "scapy.arch",
        "scapy.arch.bpf",
        "scapy.arch.unix",
        "scapy.arch.linux",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ipvtop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    target_arch=None,
)
