# IDA ZoomAllViews 🔍

> **Ctrl+Scroll font zoom for every IDA view — not just the graph.**

[![Python 3](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![IDA Pro](https://img.shields.io/badge/IDA%20Pro-8.x%20%E2%80%94%209.3%2B-orange)](https://hex-rays.com/ida-pro/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A single-file IDA Pro plugin that adds **Ctrl+Scroll wheel zoom** (font resize) to all IDA views — Disassembly, Pseudocode, Hex View, Imports, Exports, Functions, Strings, Structures, Enums, Segments, Names, and every chooser window.

IDA's built-in Ctrl+Scroll zoom only works in the **graph view**. This plugin fills the gap for everything else.

> *"Ctrl+Scroll zoom should work everywhere out of the box. Now it does."*

---

## Compatibility

| IDA Version | Qt | Python Qt Bindings | Plugin Support |
|---|---|---|---|
| **8.x** | Qt5 | PyQt5 | **✅ Supported** |
| **9.0 — 9.1** | Qt5 | PyQt5 | **✅ Supported** |
| **9.2+** | Qt6 | PySide6 | **✅ Supported** |

IDA [switched from PyQt5 to PySide6 in version 9.2](https://docs.hex-rays.com/user-guide/plugins/migrating-pyqt5-code-to-pyside6). This plugin handles both Qt bindings automatically — a single file works across all supported versions.

---

## Demo

https://github.com/user-attachments/assets/907aef8a-a438-4fa4-8c45-2ff436775e30

*Ctrl+Scroll zooming across Disassembly, Pseudocode, Strings, Imports, and Functions views*

---

## How It Works

The plugin installs a single lightweight event filter on `QApplication` that intercepts `Ctrl+MouseWheel` events globally. When triggered, it:

1. Locates the `QAbstractScrollArea` under the cursor
2. Adjusts the font size via `setFont()` + `setStyleSheet()`
3. Updates row heights for tree/table views so text doesn't overlap

**Performance:** ~5 Qt calls per scroll tick. No child-walking, no paint hooks, no delegate patching.

---

## Supported Views

| View | Zoom | Row Height |
|---|:---:|:---:|
| Disassembly (text/linear mode) | ✅ | ✅ |
| Pseudocode (Hex-Rays decompiler) | ✅ | ✅ |
| Hex View | ✅ | ✅ |
| Imports | ✅ | ✅ |
| Exports | ✅ | ✅ |
| Functions | ✅ | ✅ |
| Strings | ✅ | ✅ |
| Structures / Enums | ✅ | ✅ |
| Segments / Names / Selectors | ✅ | ✅ |
| Chooser windows (general) | ✅ | ✅ |

### Views handled natively by IDA (not affected by this plugin)

| View | Detection Method |
|---|---|
| Graph view (disassembly) | `get_view_renderer_type() == TCCRT_GRAPH` |
| Proximity browser | `get_view_renderer_type() == TCCRT_PROXIMITY` |
| Xref graphs (from/to/calls) | `QOpenGLWidget` in widget hierarchy |

These views already have their own built-in Ctrl+Scroll zoom — this plugin detects and skips them so IDA's native zoom works without interference.

> A few views (e.g. the xref tree "Name" column) use IDA's internal C++ rendering with hardcoded fonts. These specific columns cannot be overridden from Python — use IDA's own font settings (`Options → Font`) for those.

---

## Installation

Copy the plugin file to your IDA plugins directory:

**Per-user (recommended — survives IDA reinstalls):**
```
%APPDATA%\Hex-Rays\IDA Pro\plugins\ZoomAllViews.py
```

**System-wide:**
```
<IDA_DIR>\plugins\ZoomAllViews.py
```

Restart IDA. The output window confirms:

```
[ZoomAllViews] v1.0.1 loaded  |  Ctrl-Shift-Z  |  Edit -> Plugins -> ZoomAllViews  |  Qt: pyside6
```

### IDA Plugin Manager (HCLI)

The plugin supports the [IDA Plugin Manager](https://hcli.docs.hex-rays.com/user-guide/plugin-manager/) via `ida-plugin.json` included in this repository. Once the plugin is published to [plugins.hex-rays.com](https://plugins.hex-rays.com/), it can be installed with:

```
hcli plugin install ZoomAllViews
```

---

## Usage

**Ctrl + Scroll Up** — increase font size (zoom in)
**Ctrl + Scroll Down** — decrease font size (zoom out)

Hover over any supported view and scroll. Each view maintains its own independent zoom level.

---

## Enable / Disable

The plugin is **active by default** after installation. It can be toggled on and off at any time:

**Menu:** `Edit → Plugins → ZoomAllViews`
**Hotkey:** `Ctrl-Shift-Z`

| State | Output Window |
|---|---|
| Active | `[ZoomAllViews] ✔ Activated` |
| Inactive | `[ZoomAllViews] ✘ Deactivated` |

When deactivated, the event filter is fully removed from `QApplication` — zero overhead. Reactivating reinstalls it.

---

## Configuration

Edit the constants at the top of the plugin file:

```python
MIN_FONT_SIZE = 6       # smallest allowed font (points)
MAX_FONT_SIZE = 40      # largest allowed font (points)
ZOOM_STEP = 1           # points per scroll notch
DEFAULT_FONT_SIZE = 10  # fallback if font size can't be read
```

---

## Repository Structure

```
ZoomAllViews/
│   ZoomAllViews.py             ← plugin (drop into IDA plugins directory)
│   ida-plugin.json             ← IDA Plugin Manager metadata
│   LICENSE
│   README.md
│
└───Media/
        demo.mp4                ← usage demo video
```

---

## License

Licensed under the **MIT License** — see the [LICENSE](LICENSE) file for the full text.

---

## Credits

**Author:** Jiří Vinopal
&nbsp;&nbsp;&nbsp;&nbsp;X / Twitter: [@vinopaljiri](https://x.com/vinopaljiri)
&nbsp;&nbsp;&nbsp;&nbsp;GitHub: [Dump-GUY](https://github.com/Dump-GUY)
