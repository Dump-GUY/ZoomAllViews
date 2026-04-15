"""
ZoomAllViews — Ctrl+Scroll font zoom for every IDA view.

Compatibility : IDA 8.x — 9.3+ (PyQt5 / PySide6)
Installation  : Copy to <IDA_DIR>/plugins/
Usage         : Ctrl + Scroll Up/Down
Toggle        : Edit -> Plugins -> ZoomAllViews  |  Ctrl-Shift-Z
"""

__author__ = "Jiri Vinopal (@Dump-GUY)"
__version__ = "1.0.1"

import ida_idaapi
import ida_kernwin

# -----------------------------------------------------------------------
# Qt compatibility layer — PyQt5 (IDA ≤ 9.1) / PySide6 (IDA ≥ 9.2)
# -----------------------------------------------------------------------

try:
    from PySide6.QtWidgets import (QApplication, QWidget, QAbstractScrollArea,
                                    QTableView, QTreeView)
    from PySide6.QtCore import QObject, QEvent, Qt
    from PySide6.QtGui import QFontMetrics
    QT_MODULE = "pyside6"

    WHEEL_EVENT = QEvent.Type.Wheel
    CTRL_MODIFIER = Qt.KeyboardModifier.ControlModifier

    def _global_pos(event):
        return event.globalPosition().toPoint()

except ImportError:
    from PyQt5.QtWidgets import (QApplication, QWidget, QAbstractScrollArea,
                                  QTableView, QTreeView)
    from PyQt5.QtCore import QObject, QEvent, Qt
    from PyQt5.QtGui import QFontMetrics
    QT_MODULE = "pyqt5"

    WHEEL_EVENT = QEvent.Wheel
    CTRL_MODIFIER = Qt.ControlModifier

    def _global_pos(event):
        return event.globalPos()


# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------

MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 40
ZOOM_STEP = 1
DEFAULT_FONT_SIZE = 10
SIZE_PROP = "_zav_size"

PLUGIN_NAME = "ZoomAllViews"
PLUGIN_HOTKEY = "Ctrl-Shift-Z"


# -----------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------

def _find_scroll_area(widget):
    """Walk up to the nearest QAbstractScrollArea parent."""
    w = widget
    while w is not None:
        if isinstance(w, QAbstractScrollArea):
            return w
        p = w.parent()
        if not isinstance(p, QWidget):
            return widget
        w = p
    return widget


def _is_graph_view(target, container):
    """Detect graph-based views that handle their own Ctrl+Scroll zoom:
    - IDA View in graph mode (TCCRT_GRAPH)
    - IDA View in proximity mode (TCCRT_PROXIMITY)
    - Xref/call graph windows (QOpenGLWidget renderer)
    """
    try:
        twidget = ida_kernwin.get_current_widget()
        if twidget and ida_kernwin.is_idaview(twidget):
            rt = ida_kernwin.get_view_renderer_type(twidget)
            if rt != ida_kernwin.TCCRT_FLAT:
                return True

        w = target
        while w is not None:
            if w.metaObject().className() == "QOpenGLWidget":
                return True
            p = w.parent()
            if not isinstance(p, QWidget):
                break
            w = p
    except Exception:
        pass
    return False


def _apply_zoom(widget, size):
    """Apply font size via setFont + setStyleSheet + row-height fixups."""
    font = widget.font()
    font.setPointSize(size)
    row_h = QFontMetrics(font).height() + 6

    widget.setFont(font)
    vp = widget.viewport()
    if vp:
        vp.setFont(font)

    widget.setStyleSheet(
        f"* {{ font-size: {size}pt; }} "
        f"QTreeView::item  {{ height: {row_h}px; }} "
        f"QTableView::item {{ height: {row_h}px; }} "
        f"QListView::item  {{ height: {row_h}px; }}"
    )

    if isinstance(widget, QTableView):
        try:
            vh = widget.verticalHeader()
            if vh:
                vh.setDefaultSectionSize(row_h)
                vh.setMinimumSectionSize(row_h)
        except Exception:
            pass

    if isinstance(widget, QTreeView):
        try:
            widget.setUniformRowHeights(False)
        except Exception:
            pass


class WheelZoomFilter(QObject):
    """Application-level event filter — intercepts Ctrl+Wheel globally."""

    def eventFilter(self, obj, event):
        if event.type() != WHEEL_EVENT:
            return False
        if not (event.modifiers() & CTRL_MODIFIER):
            return False

        delta = event.angleDelta().y()
        if delta == 0:
            return False

        target = QApplication.widgetAt(_global_pos(event))
        if target is None:
            return False

        view = _find_scroll_area(target)
        if not isinstance(view, QAbstractScrollArea):
            return False

        if _is_graph_view(target, view):
            return False

        cur = view.property(SIZE_PROP)
        if not isinstance(cur, int) or cur <= 0:
            ps = view.font().pointSize()
            cur = ps if ps > 0 else DEFAULT_FONT_SIZE

        new = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE,
                  cur + (ZOOM_STEP if delta > 0 else -ZOOM_STEP)))
        if new == cur:
            return True

        view.setProperty(SIZE_PROP, new)
        _apply_zoom(view, new)
        return True


# -----------------------------------------------------------------------
# Plugin
# -----------------------------------------------------------------------

class ZoomAllViewsPlugin(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_KEEP
    comment = "Ctrl+Scroll font zoom in all views"
    help = "Ctrl+MouseWheel to zoom text in any IDA view"
    wanted_name = PLUGIN_NAME
    wanted_hotkey = PLUGIN_HOTKEY

    def init(self):
        self._filter = None
        self._active = False

        try:
            app = QApplication.instance()
            if app is None:
                return ida_idaapi.PLUGIN_SKIP
        except Exception:
            return ida_idaapi.PLUGIN_SKIP

        self._activate()

        ida_kernwin.msg(
            f"[{PLUGIN_NAME}] v{__version__} loaded  |  "
            f"{PLUGIN_HOTKEY}  |  Edit -> Plugins -> {PLUGIN_NAME}  |  "
            f"Qt: {QT_MODULE}\n"
        )
        return ida_idaapi.PLUGIN_KEEP

    def run(self, arg):
        """Called by IDA when menu item or hotkey is triggered."""
        if self._active:
            self._deactivate()
        else:
            self._activate()

    def term(self):
        self._deactivate()

    def _activate(self):
        if self._active:
            return
        app = QApplication.instance()
        if not app:
            return
        self._filter = WheelZoomFilter()
        app.installEventFilter(self._filter)
        self._active = True
        ida_kernwin.msg(f"[{PLUGIN_NAME}] \u2714 Activated  |  Ctrl+Scroll to zoom\n")

    def _deactivate(self):
        if not self._active:
            return
        try:
            app = QApplication.instance()
            if app and self._filter:
                app.removeEventFilter(self._filter)
        except Exception:
            pass
        self._filter = None
        self._active = False
        ida_kernwin.msg(f"[{PLUGIN_NAME}] \u2718 Deactivated\n")


def PLUGIN_ENTRY():
    return ZoomAllViewsPlugin()
