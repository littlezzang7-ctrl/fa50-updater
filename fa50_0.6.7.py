# -*- coding: utf-8 -*-
"""
FA-50 Desktop 3D Step Simulator (PySide6 + pyqtgraph.opengl)

Run:
  pip install pyside6 pyqtgraph PyOpenGL numpy
  python fa50.py
"""

import math
import os
import re
import sys
import time
import csv
import atexit
import json
import hashlib
import tempfile
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

import numpy as np
from PySide6.QtCore import QEvent, QPoint, Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics, QKeySequence, QShortcut, QVector3D
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap, QPolygon
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGraphicsOpacityEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSplitter,
    QStyle,
    QSizePolicy,
    QTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
import pyqtgraph as pg

LOCAL_PYOPENGL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyopengl-3.1.10")
if os.path.isdir(os.path.join(LOCAL_PYOPENGL_DIR, "OpenGL")) and LOCAL_PYOPENGL_DIR not in sys.path:
    sys.path.insert(0, LOCAL_PYOPENGL_DIR)

try:
    import pyqtgraph.opengl as gl
except Exception as e:
    gl = None
    OPENGL_IMPORT_ERROR = e
else:
    OPENGL_IMPORT_ERROR = None


def patch_openpyxl_named_style_none():
    # Some workbooks contain a named style entry with missing name.
    # openpyxl can raise TypeError on that; coerce None to empty string.
    try:
        from openpyxl.styles.named_styles import _NamedCellStyle
    except Exception:
        return
    original_init = _NamedCellStyle.__init__
    if getattr(original_init, "_fa50_patched", False):
        return

    def _patched_init(self, name=None, xfId=None, builtinId=None, iLevel=None, hidden=None, customBuiltin=None, extLst=None):
        if name is None:
            name = ""
        return original_init(self, name=name, xfId=xfId, builtinId=builtinId, iLevel=iLevel, hidden=hidden, customBuiltin=customBuiltin, extLst=extLst)

    _patched_init._fa50_patched = True
    _NamedCellStyle.__init__ = _patched_init


G0 = 32.174
KT_TO_FTPS = 1.68781
NM_TO_FT = 6076.12
APP_VERSION = "0.6.7"
UPDATE_META_URL = "https://raw.githubusercontent.com/littlezzang7-ctrl/fa50-updater/main/version.json"
_SINGLE_INSTANCE_LOCK_FD = None
_SINGLE_INSTANCE_LOCK_PATH = os.path.join(tempfile.gettempdir(), "fa50_single_instance.lock")


def acquire_single_instance_lock() -> bool:
    global _SINGLE_INSTANCE_LOCK_FD
    try:
        fd = os.open(_SINGLE_INSTANCE_LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
        _SINGLE_INSTANCE_LOCK_FD = fd

        def _release():
            global _SINGLE_INSTANCE_LOCK_FD
            try:
                if _SINGLE_INSTANCE_LOCK_FD is not None:
                    os.close(_SINGLE_INSTANCE_LOCK_FD)
            except Exception:
                pass
            _SINGLE_INSTANCE_LOCK_FD = None
            try:
                if os.path.exists(_SINGLE_INSTANCE_LOCK_PATH):
                    os.remove(_SINGLE_INSTANCE_LOCK_PATH)
            except Exception:
                pass

        atexit.register(_release)
        return True
    except FileExistsError:
        return False
    except Exception:
        # If lock setup fails unexpectedly, do not block startup.
        return True
GROUND_MIN_EXTENT_FT = 50.0 * NM_TO_FT  # 100nm x 100nm default grid (half-extent 50nm)
GRID_VERTICAL_MAX_FT = 40000.0
ARROW_BASE_GAP_FT = 500.0
ARROW_MIN_GAP_FT = 150.0
ARROW_MAX_GAP_FT = 800.0
ARROW_MIN_SHAFT_LEN_FT = 120.0
ARROW_DYNAMIC_SAFETY_FT = 200.0
AIRCRAFT_IDS = [f"#{i}" for i in range(1, 9)]
COLOR_ORDER = ["BLACK", "BLUE", "CYAN", "GREEN", "RED", "ORANGE", "PINK", "PURPLE"]
COLOR_PRESETS = {
    "BLACK": {
        "label": "Black",
        "rgba": (0.05, 0.05, 0.05, 1.0),
        "ui": {"border": "#9a9a9a", "title": "#111111", "label": "#111111", "bg": "#ebebeb", "spin_fg": "#111111", "spin_bg": "#ffffff", "combo_fg": "#111111", "combo_bg": "#ffffff"},
    },
    "BLUE": {
        "label": "Blue",
        "rgba": (0.10, 0.25, 0.95, 1.0),
        "ui": {"border": "#6f90d8", "title": "#2f5fb8", "label": "#365a9a", "bg": "#f8fbff", "spin_fg": "#1f3f7a", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "CYAN": {
        "label": "Cyan",
        "rgba": (0.00, 0.68, 0.82, 1.0),
        "ui": {"border": "#63bccc", "title": "#007a8a", "label": "#006674", "bg": "#f2fdff", "spin_fg": "#005c67", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "GREEN": {
        "label": "Green",
        "rgba": (0.08, 0.62, 0.22, 1.0),
        "ui": {"border": "#75bf7a", "title": "#1f7b30", "label": "#236d30", "bg": "#f5fff5", "spin_fg": "#1e5d29", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "RED": {
        "label": "Red",
        "rgba": (0.90, 0.10, 0.10, 1.0),
        "ui": {"border": "#d88b8b", "title": "#b83c3c", "label": "#9d3f3f", "bg": "#fff9f9", "spin_fg": "#7f2a2a", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "ORANGE": {
        "label": "Orange",
        "rgba": (0.95, 0.55, 0.10, 1.0),
        "ui": {"border": "#e5a15b", "title": "#d46f00", "label": "#9b5600", "bg": "#fff8ef", "spin_fg": "#8a4a00", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "PINK": {
        "label": "Pink",
        "rgba": (0.95, 0.35, 0.70, 1.0),
        "ui": {"border": "#d997b7", "title": "#b14a7f", "label": "#923f69", "bg": "#fff6fb", "spin_fg": "#7a3457", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
    "PURPLE": {
        "label": "Purple",
        "rgba": (0.58, 0.28, 0.88, 1.0),
        "ui": {"border": "#ad92d9", "title": "#6d3bb0", "label": "#5a3790", "bg": "#f9f6ff", "spin_fg": "#4a2f75", "spin_bg": "#ffffff", "combo_fg": "#202020", "combo_bg": "#ffffff"},
    },
}
DEFAULT_COLOR_BY_AID = {aid: COLOR_ORDER[i % len(COLOR_ORDER)] for i, aid in enumerate(AIRCRAFT_IDS)}
COLORS = {aid: COLOR_PRESETS[DEFAULT_COLOR_BY_AID[aid]]["rgba"] for aid in AIRCRAFT_IDS}
TEAM_A = {"#1", "#2"}
TEAM_B = set(AIRCRAFT_IDS) - TEAM_A

MODE_KEYS = ["1vs1", "2vs1", "2vs2", "4vs2", "4vs4"]
MODE_ACTIVE_IDS = {
    "1vs1": ["#1", "#2"],
    "2vs1": ["#1", "#2", "#3"],
    "2vs2": ["#1", "#2", "#3", "#4"],
    "4vs2": ["#1", "#2", "#3", "#4", "#5", "#6"],
    "4vs4": ["#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8"],
}
# DCA BA/RA definition:
# 2vs1 -> BA: #1,#2 / RA: #3
# 2vs2 -> BA: #1,#2 / RA: #3,#4
# 4vs2 -> BA: #1,#2,#3,#4 / RA: #5,#6
# 4vs4 -> BA: #1,#2,#3,#4 / RA: #5,#6,#7,#8
DCA_BA_IDS_BY_MODE = {
    "2vs1": ["#1", "#2"],
    "2vs2": ["#1", "#2"],
    "4vs2": ["#1", "#2", "#3", "#4"],
    "4vs4": ["#1", "#2", "#3", "#4"],
}
MODE_COLOR_KEYS = {
    "1vs1": ["BLACK", "RED"],
    "2vs1": ["BLACK", "BLUE", "RED"],
    "2vs2": ["BLACK", "BLUE", "RED", "ORANGE"],
    "4vs2": ["BLACK", "BLUE", "CYAN", "GREEN", "RED", "ORANGE"],
    "4vs4": ["BLACK", "BLUE", "CYAN", "GREEN", "RED", "ORANGE", "PINK", "PURPLE"],
}
MODE_SETUP_OPTIONS = {
    "1vs1": ["TI SETUP", "BFM 3K", "BFM 9K"],
    "2vs1": ["TI SETUP", "OACM SETUP", "DACM SETUP"],
    "2vs2": [
        "2vs2 RANGE",
        "2vs2 LAB",
        "2vs2 ECHELON",
    ],
    "4vs2": [
        "4vs2 BA OFFSET BOX + RA RANGE",
        "4vs2 BA OFFSET BOX + RA LAB",
        "4vs2 BA OFFSET BOX + RA ECHELON",
        "4vs2 BA FLUID FOUR + RA RANGE",
        "4vs2 BA FLUID FOUR + RA LAB",
        "4vs2 BA FLUID FOUR + RA ECHELON",
    ],
    "4vs4": [
        "4vs4 BA OFFSET BOX + RA OFFSET BOX",
        "4vs4 BA OFFSET BOX + RA FLUID FOUR",
        "4vs4 BA FLUID FOUR + RA OFFSET BOX",
        "4vs4 BA FLUID FOUR + RA FLUID FOUR",
    ],
}


class StartupScenarioDialog(QDialog):
    def __init__(self, parent=None, initial_mode: str = "2vs1", initial_setup: str = "TI SETUP"):
        super().__init__(parent)
        self.setWindowTitle("Select Scenario")
        self.resize(1464, 936)
        self.setMinimumSize(1296, 840)
        self.setStyleSheet(
            "QDialog { font-size: 13pt; }"
            "QLabel { font-size: 13pt; }"
            "QGroupBox { font-size: 14pt; font-weight: 600; }"
            "QGroupBox::title {"
            " subcontrol-origin: margin;"
            " subcontrol-position: top center;"
            " padding: 0 6px;"
            "}"
            "QPushButton { font-size: 13pt; }"
            "QDoubleSpinBox { font-size: 13pt; }"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(12)

        btn_open_saved_top = QPushButton("Open Saved Data")
        btn_open_saved_top.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_saved_top.setFixedSize(260, 52)
        btn_open_saved_top.setStyleSheet(
            "QPushButton {"
            " border: 2px solid #2b6de9;"
            " border-radius: 8px;"
            " background: #dbeafe;"
            " color: #0f172a;"
            " font-weight: 700;"
            " padding: 6px 10px;"
            "}"
            "QPushButton:hover { background: #cfe5ff; border-color: #1d4ed8; }"
            "QPushButton:pressed { background: #bfdcff; }"
        )
        btn_open_saved_top.clicked.connect(self._choose_open_saved_data)
        lay.addWidget(btn_open_saved_top, alignment=Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("Select Scenario")
        title.setStyleSheet("font-size: 20pt; font-weight: 700;")
        lay.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        hint = QLabel("선택 박스를 누르면 즉시 적용됩니다.")
        hint.setStyleSheet("font-size: 12pt; color: #555;")
        lay.addWidget(hint, alignment=Qt.AlignmentFlag.AlignHCenter)

        default_mode = str(initial_mode).strip() if str(initial_mode).strip() in MODE_KEYS else "2vs1"
        default_setup = str(initial_setup).strip()
        self._selected_mode = default_mode
        self._selected_setup = default_setup if default_setup else "TI SETUP"
        self._selected_dist_nm: Optional[float] = None
        self._open_saved_data_requested = False
        self._selected_4vs2_ba_setup: Optional[str] = None
        self._selected_4vs2_ra_setup: Optional[str] = None
        self._selected_4vs4_ba_setup: Optional[str] = None
        self._selected_4vs4_ra_setup: Optional[str] = None

        self._grp_dist_spins: Dict[str, NoWheelDoubleSpinBox] = {}
        self._4vs2_ba_buttons: Dict[str, QPushButton] = {}
        self._4vs2_ra_buttons: Dict[str, QPushButton] = {}
        self._4vs4_ba_buttons: Dict[str, QPushButton] = {}
        self._4vs4_ra_buttons: Dict[str, QPushButton] = {}

        grid_wrap = QWidget()
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # 6-column grid:
        # top row: 3 cards (each spans 2 cols), bottom row: 2 cards (each spans 3 cols).
        mode_grid_pos = {
            "1vs1": (0, 0, 2),
            "2vs1": (0, 2, 2),
            "2vs2": (0, 4, 2),
            "4vs2": (1, 0, 3),
            "4vs4": (1, 3, 3),
        }
        for i, mode in enumerate(MODE_KEYS):
            gb = QGroupBox(mode)
            gb_lay = QVBoxLayout(gb)
            gb_lay.setContentsMargins(10, 10, 10, 10)
            gb_lay.setSpacing(8)
            gb_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            if mode == "2vs2":
                box = QGroupBox("RA FORMATION")
                self._apply_ra_box_style(box)
                bl = QVBoxLayout(box)
                bl.setContentsMargins(10, 22, 10, 10)
                bl.setSpacing(12)
                for setup in MODE_SETUP_OPTIONS.get("2vs2", []):
                    form_name = setup.split()[-1]
                    row = QHBoxLayout()
                    row.setContentsMargins(0, 0, 0, 0)
                    row.setSpacing(12)
                    btn = self._make_setup_box(form_name)
                    spin = NoWheelDoubleSpinBox()
                    spin.setDecimals(1)
                    spin.setRange(0.1, 50.0)
                    spin.setSingleStep(0.1)
                    spin.setValue(2.0)
                    spin.setFixedWidth(132)
                    spin.setToolTip(f"{form_name} 거리(nm)")
                    self._grp_dist_spins[setup] = spin
                    btn.clicked.connect(lambda _=False, s=setup, sp=spin: self._choose_setup("2vs2", s, sp))
                    row.addStretch(1)
                    row.addWidget(btn, 0)
                    row.addWidget(spin, 0)
                    row.addWidget(QLabel("nm"), 0)
                    row.addStretch(1)
                    bl.addLayout(row)
                bl.addStretch(1)
                gb_lay.addWidget(box)
            elif mode == "4vs2":
                wrap = QWidget()
                hg = QGridLayout(wrap)
                hg.setContentsMargins(0, 0, 0, 0)
                hg.setHorizontalSpacing(12)
                hg.setVerticalSpacing(8)

                ba_box = QGroupBox("BA FORMATION")
                self._apply_ba_box_style(ba_box)
                ba_lay = QVBoxLayout(ba_box)
                ba_lay.setContentsMargins(10, 22, 10, 10)
                ba_lay.setSpacing(10)
                for setup in ["4vs2 BA OFFSET BOX", "4vs2 BA FLUID FOUR"]:
                    btn = self._make_setup_box(setup.replace("4vs2 BA ", ""))
                    self._4vs2_ba_buttons[setup] = btn
                    btn.clicked.connect(lambda _=False, s=setup: self._choose_4vs2_ba(s))
                    ba_lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
                ba_lay.addStretch(1)

                ra_box = QGroupBox("RA FORMATION")
                self._apply_ra_box_style(ra_box)
                ra_lay = QVBoxLayout(ra_box)
                ra_lay.setContentsMargins(10, 22, 10, 10)
                ra_lay.setSpacing(10)
                for suffix in ["RANGE", "LAB", "ECHELON"]:
                    setup = f"4vs2 RA {suffix}"
                    row = QHBoxLayout()
                    row.setContentsMargins(0, 0, 0, 0)
                    row.setSpacing(12)
                    btn = self._make_setup_box(suffix)
                    self._4vs2_ra_buttons[setup] = btn
                    spin = NoWheelDoubleSpinBox()
                    spin.setDecimals(1)
                    spin.setRange(0.1, 50.0)
                    spin.setSingleStep(0.1)
                    spin.setValue(2.0)
                    spin.setFixedWidth(132)
                    spin.setToolTip(f"RA {suffix} 거리(nm)")
                    self._grp_dist_spins[setup] = spin
                    btn.clicked.connect(lambda _=False, s=setup, sp=spin: self._choose_4vs2_ra(s, sp))
                    row.addStretch(1)
                    row.addWidget(btn, 0)
                    row.addWidget(spin, 0)
                    row.addWidget(QLabel("nm"), 0)
                    row.addStretch(1)
                    ra_lay.addLayout(row)
                ra_lay.addStretch(1)

                hg.addWidget(ba_box, 0, 0)
                hg.addWidget(ra_box, 0, 1)
                gb_lay.addWidget(wrap)
                guide = QLabel("4vs2는 BA와 RA를 각각 선택해야 적용됩니다.")
                guide.setStyleSheet("font-size: 11pt; color: #555;")
                gb_lay.addWidget(guide, alignment=Qt.AlignmentFlag.AlignHCenter)
                self._refresh_4vs2_selection_styles()
            elif mode == "4vs4":
                wrap = QWidget()
                hg = QGridLayout(wrap)
                hg.setContentsMargins(0, 0, 0, 0)
                hg.setHorizontalSpacing(12)
                hg.setVerticalSpacing(8)

                ba_box = QGroupBox("BA FORMATION")
                self._apply_ba_box_style(ba_box)
                ba_lay = QVBoxLayout(ba_box)
                ba_lay.setContentsMargins(10, 22, 10, 10)
                ba_lay.setSpacing(10)
                for setup in ["4vs4 BA OFFSET BOX", "4vs4 BA FLUID FOUR"]:
                    btn = self._make_setup_box(setup.replace("4vs4 BA ", ""))
                    self._4vs4_ba_buttons[setup] = btn
                    btn.clicked.connect(lambda _=False, s=setup: self._choose_4vs4_ba(s))
                    ba_lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
                ba_lay.addStretch(1)

                ra_box = QGroupBox("RA FORMATION")
                self._apply_ra_box_style(ra_box)
                ra_lay = QVBoxLayout(ra_box)
                ra_lay.setContentsMargins(10, 22, 10, 10)
                ra_lay.setSpacing(10)
                for setup in ["4vs4 RA OFFSET BOX", "4vs4 RA FLUID FOUR"]:
                    btn = self._make_setup_box(setup.replace("4vs4 RA ", ""))
                    self._4vs4_ra_buttons[setup] = btn
                    btn.clicked.connect(lambda _=False, s=setup: self._choose_4vs4_ra(s))
                    ra_lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
                ra_lay.addStretch(1)

                hg.addWidget(ba_box, 0, 0)
                hg.addWidget(ra_box, 0, 1)
                gb_lay.addWidget(wrap)
                guide = QLabel("4vs4는 BA와 RA를 각각 선택해야 적용됩니다.")
                guide.setStyleSheet("font-size: 11pt; color: #555;")
                gb_lay.addWidget(guide, alignment=Qt.AlignmentFlag.AlignHCenter)
                self._refresh_4vs4_selection_styles()
            else:
                for setup in MODE_SETUP_OPTIONS.get(mode, ["DEFAULT"]):
                    btn = self._make_setup_box(setup)
                    btn.clicked.connect(lambda _=False, m=mode, s=setup: self._choose_setup(m, s, None))
                    gb_lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            gb_lay.addStretch(1)
            r, c, cs = mode_grid_pos.get(mode, (i // 3, (i % 3) * 2, 2))
            grid.addWidget(gb, r, c, 1, cs)

        lay.addWidget(grid_wrap, 1, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _make_setup_box(self, text: str) -> QPushButton:
        btn = QPushButton(str(text))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(230, 60)
        self._apply_setup_box_style(btn, selected=False)
        return btn

    def _apply_ba_box_style(self, box: QGroupBox):
        box.setStyleSheet(
            "QGroupBox { border: 2px solid #2b6de9; border-radius: 8px; margin-top: 10px; }"
            "QGroupBox::title { color: #1d4ed8; font-weight: 700; padding: 0 8px; }"
        )

    def _apply_ra_box_style(self, box: QGroupBox):
        box.setStyleSheet(
            "QGroupBox { border: 2px solid #dc2626; border-radius: 8px; margin-top: 10px; }"
            "QGroupBox::title { color: #b91c1c; font-weight: 700; padding: 0 8px; }"
        )

    def _setup_box_style(self, selected: bool = False) -> str:
        if selected:
            return (
                "QPushButton {"
                " border: 2px solid #2b6de9;"
                " border-radius: 8px;"
                " background: #dbeafe;"
                " color: #0f172a;"
                " font-weight: 700;"
                " padding: 6px 10px;"
                "}"
                "QPushButton:hover { background: #cfe5ff; border-color: #1d4ed8; }"
                "QPushButton:pressed { background: #bfdcff; }"
            )
        return (
            "QPushButton {"
            " border: 1px solid #9aa4b2;"
            " border-radius: 8px;"
            " background: #f7f9fc;"
            " color: #111;"
            " font-weight: 600;"
            " padding: 6px 10px;"
            "}"
            "QPushButton:hover { background: #e8f0ff; border-color: #5b8def; }"
            "QPushButton:pressed { background: #dce9ff; }"
        )

    def _apply_setup_box_style(self, btn: Optional[QPushButton], selected: bool = False):
        if btn is None:
            return
        btn.setStyleSheet(self._setup_box_style(selected=bool(selected)))

    def _refresh_4vs2_selection_styles(self):
        for setup, btn in self._4vs2_ba_buttons.items():
            self._apply_setup_box_style(btn, selected=(setup == self._selected_4vs2_ba_setup))
        for setup, btn in self._4vs2_ra_buttons.items():
            self._apply_setup_box_style(btn, selected=(setup == self._selected_4vs2_ra_setup))

    def _refresh_4vs4_selection_styles(self):
        for setup, btn in self._4vs4_ba_buttons.items():
            self._apply_setup_box_style(btn, selected=(setup == self._selected_4vs4_ba_setup))
        for setup, btn in self._4vs4_ra_buttons.items():
            self._apply_setup_box_style(btn, selected=(setup == self._selected_4vs4_ra_setup))

    def _choose_setup(self, mode: str, setup: str, dist_spin: Optional[NoWheelDoubleSpinBox]):
        self._open_saved_data_requested = False
        self._selected_mode = str(mode)
        self._selected_setup = str(setup)
        self._selected_dist_nm = float(dist_spin.value()) if dist_spin is not None else None
        self.accept()

    def _choose_open_saved_data(self):
        self._open_saved_data_requested = True
        self.accept()

    def open_saved_requested(self) -> bool:
        return bool(self._open_saved_data_requested)

    def _choose_4vs2_ba(self, ba_setup: str):
        self._selected_mode = "4vs2"
        self._selected_4vs2_ba_setup = str(ba_setup)
        self._refresh_4vs2_selection_styles()
        self._try_accept_4vs2()

    def _choose_4vs2_ra(self, ra_setup: str, dist_spin: Optional[NoWheelDoubleSpinBox]):
        self._selected_mode = "4vs2"
        self._selected_4vs2_ra_setup = str(ra_setup)
        self._selected_dist_nm = float(dist_spin.value()) if dist_spin is not None else 2.0
        self._refresh_4vs2_selection_styles()
        self._try_accept_4vs2()

    def _try_accept_4vs2(self):
        if not self._selected_4vs2_ba_setup or not self._selected_4vs2_ra_setup:
            return
        ba = self._selected_4vs2_ba_setup.replace("4vs2 BA ", "").strip()
        ra = self._selected_4vs2_ra_setup.replace("4vs2 RA ", "").strip()
        self._selected_setup = f"4vs2 BA {ba} + RA {ra}"
        self.accept()

    def _choose_4vs4_ba(self, ba_setup: str):
        self._selected_mode = "4vs4"
        self._selected_4vs4_ba_setup = str(ba_setup)
        self._refresh_4vs4_selection_styles()
        self._try_accept_4vs4()

    def _choose_4vs4_ra(self, ra_setup: str):
        self._selected_mode = "4vs4"
        self._selected_4vs4_ra_setup = str(ra_setup)
        self._refresh_4vs4_selection_styles()
        self._try_accept_4vs4()

    def _try_accept_4vs4(self):
        if not self._selected_4vs4_ba_setup or not self._selected_4vs4_ra_setup:
            return
        ba = self._selected_4vs4_ba_setup.replace("4vs4 BA ", "").strip()
        ra = self._selected_4vs4_ra_setup.replace("4vs4 RA ", "").strip()
        self._selected_setup = f"4vs4 BA {ba} + RA {ra}"
        self.accept()

    def selection(self) -> Tuple[str, str, Optional[float]]:
        mode = str(self._selected_mode or "2vs1")
        setup = str(self._selected_setup or "TI SETUP")
        if mode in {"2vs2", "4vs2"} and any(k in setup.upper() for k in ("RANGE", "LAB", "ECHELON")):
            if self._selected_dist_nm is not None:
                return mode, setup, float(self._selected_dist_nm)
            sp = self._grp_dist_spins.get(setup)
            if sp is not None:
                return mode, setup, float(sp.value())
        return mode, setup, None


class DcaSetupDialog(QDialog):
    def __init__(
        self,
        parent=None,
        *,
        be_bearing_deg: float = 180.0,
        be_range_nm: float = 10.0,
        asset_bearing_from_be_deg: float = 360.0,
        asset_range_from_be_nm: float = 5.0,
        asset_same_as_be: bool = False,
        ra_zone_radius_nm: float = 5.0,
        ra_line_forward_nm: float = 5.0,
        ra_zone_mode: str = "radius",
        mission_width_nm: float = 25.0,
        mission_height_nm: float = 65.0,
        cap_front_nm: float = 13.0,
        cap_rear_nm: float = 5.0,
        cap_pair_enabled: bool = False,
        cap_pair_half_sep_nm: float = 0.0,
        hmrl_nm: float = 5.0,
        ldez_nm: float = 25.0,
        hdez_nm: float = 45.0,
        commit_nm: float = 55.0,
        ba_from_asset_nm: float = 20.0,
        ra_from_asset_nm: float = 25.0,
        ba_heading_deg: float = 360.0,
        ra_heading_deg: float = 180.0,
        mode_key: str = "2vs1",
        ba_ids_preview: Optional[List[str]] = None,
        ra_ids_preview: Optional[List[str]] = None,
        ba_member_offsets_nm: Optional[Dict[str, Tuple[float, float]]] = None,
        ra_member_offsets_nm: Optional[Dict[str, Tuple[float, float]]] = None,
        ra_shape_preview: str = "RANGE",
    ):
        super().__init__(parent)
        self.setWindowTitle("DCA / B.E / Asset Setup")
        self.setModal(True)
        self.resize(1920, 1080)
        self.setMinimumSize(1920, 960)
        self.setStyleSheet(
            "QDialog { font-size: 14pt; }"
            "QLabel, QCheckBox, QRadioButton, QPushButton { font-size: 14pt; }"
            "QGroupBox { font-size: 15pt; font-weight: 700; }"
            "QDoubleSpinBox { font-size: 14pt; }"
        )
        self._be_bearing_deg_value = float(be_bearing_deg)
        self._be_range_nm_value = float(be_range_nm)
        self._ba_ids_preview = list(ba_ids_preview or [])
        self._ra_ids_preview = list(ra_ids_preview or [])
        self._ba_member_offsets_nm = dict(ba_member_offsets_nm or {})
        self._ra_member_offsets_nm = dict(ra_member_offsets_nm or {})
        self._ra_shape_preview = str(ra_shape_preview).strip().upper() or "RANGE"
        self._preview_points_nm: Dict[str, np.ndarray] = {}
        self._preview_map_cache: Dict[str, float] = {}
        self._preview_line_screen: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]] = {}
        self._preview_corner_screen: List[Tuple[float, float]] = []
        self._preview_point_screen: Dict[str, Tuple[float, float]] = {}
        self._drag_aircraft_id: Optional[str] = None
        self._preview_drag_mode: Optional[str] = None
        self._preview_drag_key: Optional[str] = None
        self._preview_drag_corner: Optional[int] = None
        self._preview_corner_drag_ctx: Optional[Dict[str, float]] = None
        self._preview_drag_hint_text: str = ""
        self._preview_drag_hint_pos: Optional[Tuple[float, float]] = None
        self._preview_view_lock: Dict[str, float] = {}
        self._preview_manual_zoom = False
        self._preview_pan_active = False
        self._preview_pan_last_px: Optional[Tuple[float, float]] = None
        self._cap_front_pair_enabled = bool(cap_pair_enabled)
        self._cap_front_pair_half_sep_nm = max(0.0, float(cap_pair_half_sep_nm))
        self._selected_ba_squad: List[str] = []
        self._ba_heading_override_deg: Dict[str, float] = {}
        self._selected_ba_squad_center_nm: Optional[np.ndarray] = None
        self._drag_changed = False
        self.preview_colors = {
            "bg": QColor("#e9f7e9"),
            "mission": QColor("#facc15"),
            "asset": QColor("#ff0000"),
            "be": QColor("#2563eb"),
            "cap": QColor("#111111"),
            "hmrl": QColor("#ff3b30"),
            "dez": QColor("#00e5ff"),
            "commit": QColor("#ff3b30"),
            "ra_touch": QColor("#a855f7"),
            "ba": QColor("#3b82f6"),
            "ra": QColor("#ef4444"),
        }
        suggested_ba_init = float(cap_front_nm)
        suggested_ra_init = float(commit_nm) + (0.5 * (float(mission_height_nm) - float(commit_nm)))
        self._ba_user_modified = abs(float(ba_from_asset_nm) - suggested_ba_init) > 1e-9
        self._ra_user_modified = abs(float(ra_from_asset_nm) - suggested_ra_init) > 1e-9
        self._auto_sync_guard = False

        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        left_wrap = QWidget()
        left_root = QVBoxLayout(left_wrap)
        left_root.setContentsMargins(0, 0, 0, 0)
        left_root.setSpacing(6)

        # 1) MISSION AREA + ASSET
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(6)

        mission_group = QGroupBox("MISSION AREA")
        mission_form = QFormLayout(mission_group)
        self._compact_form(mission_form)
        self.mission_width_nm = QDoubleSpinBox()
        self.mission_width_nm.setDecimals(1)
        self.mission_width_nm.setRange(0.1, 500.0)
        self.mission_width_nm.setSingleStep(0.1)
        self.mission_width_nm.setValue(float(mission_width_nm))
        self.mission_height_nm = QDoubleSpinBox()
        self.mission_height_nm.setDecimals(1)
        self.mission_height_nm.setRange(0.1, 500.0)
        self.mission_height_nm.setSingleStep(0.1)
        self.mission_height_nm.setValue(float(mission_height_nm))
        mission_form.addRow("Width (nm)", self.mission_width_nm)
        mission_form.addRow("Height (nm)", self.mission_height_nm)
        self._style_group_box(mission_group, "#facc15")
        top_row.addWidget(mission_group, 1)

        asset_group = QGroupBox("ASSET (B.E 기준)")
        asset_form = QFormLayout(asset_group)
        self._compact_form(asset_form)
        self.asset_bearing_deg = QDoubleSpinBox()
        self.asset_bearing_deg.setDecimals(0)
        self.asset_bearing_deg.setRange(0.0, 360.0)
        self.asset_bearing_deg.setSingleStep(1.0)
        self.asset_bearing_deg.setValue(float(asset_bearing_from_be_deg))
        self.asset_range_nm = QDoubleSpinBox()
        self.asset_range_nm.setDecimals(1)
        self.asset_range_nm.setRange(0.0, 200.0)
        self.asset_range_nm.setSingleStep(0.1)
        self.asset_range_nm.setValue(float(asset_range_from_be_nm))
        self.chk_asset_same_as_be = QCheckBox("B.E와 동일 위치로 설정")
        self.chk_asset_same_as_be.setChecked(bool(asset_same_as_be))
        self.chk_asset_same_as_be.toggled.connect(self._on_asset_same_toggled)
        asset_form.addRow("Bearing (deg)", self.asset_bearing_deg)
        asset_form.addRow("Range (nm)", self.asset_range_nm)
        asset_form.addRow("", self.chk_asset_same_as_be)
        self._style_group_box(asset_group, "#ff0000")
        top_row.addWidget(asset_group, 1)
        left_root.addLayout(top_row)

        # 2) DEZ + COMMIT + HMRL
        lines_row = QHBoxLayout()
        lines_row.setContentsMargins(0, 0, 0, 0)
        lines_row.setSpacing(6)

        dez_group = QGroupBox("DEZ (ASSET 기준)")
        dez_form = QFormLayout(dez_group)
        self._compact_form(dez_form)
        self.ldez_nm = QDoubleSpinBox()
        self.ldez_nm.setDecimals(1)
        self.ldez_nm.setRange(0.0, 500.0)
        self.ldez_nm.setSingleStep(0.1)
        self.ldez_nm.setValue(float(ldez_nm))
        self.hdez_nm = QDoubleSpinBox()
        self.hdez_nm.setDecimals(1)
        self.hdez_nm.setRange(0.0, 500.0)
        self.hdez_nm.setSingleStep(0.1)
        self.hdez_nm.setValue(float(hdez_nm))
        dez_form.addRow("INNER DEZ (nm)", self.ldez_nm)
        dez_form.addRow("OUTER DEZ (nm)", self.hdez_nm)
        self._style_group_box(dez_group, "#00e5ff")
        lines_row.addWidget(dez_group, 1)

        commit_group = QGroupBox("COMMIT LINE (ASSET 기준)")
        commit_form = QFormLayout(commit_group)
        self._compact_form(commit_form)
        self.commit_nm = QDoubleSpinBox()
        self.commit_nm.setDecimals(1)
        self.commit_nm.setRange(0.0, 500.0)
        self.commit_nm.setSingleStep(0.1)
        self.commit_nm.setValue(float(commit_nm))
        commit_form.addRow("COMMIT (nm)", self.commit_nm)
        self._style_group_box(commit_group, "#ff3b30")
        lines_row.addWidget(commit_group, 1)

        hmrl_group = QGroupBox("HMRL (ASSET 기준)")
        hmrl_form = QFormLayout(hmrl_group)
        self._compact_form(hmrl_form)
        self.hmrl_nm = QDoubleSpinBox()
        self.hmrl_nm.setDecimals(1)
        self.hmrl_nm.setRange(0.0, 500.0)
        self.hmrl_nm.setSingleStep(0.1)
        self.hmrl_nm.setValue(float(hmrl_nm))
        hmrl_form.addRow("HMRL (nm)", self.hmrl_nm)
        self._style_group_box(hmrl_group, "#ff3b30")
        lines_row.addWidget(hmrl_group, 1)
        left_root.addLayout(lines_row)

        # 3) CAP FRONT/REAR + BA POSITION
        ba_ids_text = "#1,#2" if str(mode_key).strip() in {"2vs1", "2vs2"} else "#1,#2,#3,#4"
        cap_ba_row = QHBoxLayout()
        cap_ba_row.setContentsMargins(0, 0, 0, 0)
        cap_ba_row.setSpacing(6)

        cap_group = QGroupBox("CAP FRONT / REAR POSITION (ASSET 기준)")
        cap_form = QFormLayout(cap_group)
        self._compact_form(cap_form)
        self.cap_front_nm = QDoubleSpinBox()
        self.cap_front_nm.setDecimals(1)
        self.cap_front_nm.setRange(0.0, 500.0)
        self.cap_front_nm.setSingleStep(0.1)
        self.cap_front_nm.setValue(float(cap_front_nm))
        self.cap_rear_nm = QDoubleSpinBox()
        self.cap_rear_nm.setDecimals(1)
        self.cap_rear_nm.setRange(0.0, 500.0)
        self.cap_rear_nm.setSingleStep(0.1)
        self.cap_rear_nm.setValue(float(cap_rear_nm))
        cap_form.addRow("CAP FRONT (nm)", self.cap_front_nm)
        cap_form.addRow("CAP REAR (nm)", self.cap_rear_nm)
        self._style_group_box(cap_group, "#111111", "#ffffff")
        cap_ba_row.addWidget(cap_group, 1)

        ba_group = QGroupBox("BA POSITION (ASSET 기준)")
        ba_form = QFormLayout(ba_group)
        self._compact_form(ba_form)
        self.ba_from_asset_nm = QDoubleSpinBox()
        self.ba_from_asset_nm.setDecimals(1)
        self.ba_from_asset_nm.setRange(0.0, 500.0)
        self.ba_from_asset_nm.setSingleStep(0.1)
        self.ba_from_asset_nm.setValue(float(ba_from_asset_nm))
        self.ba_heading_deg = QDoubleSpinBox()
        self.ba_heading_deg.setDecimals(0)
        self.ba_heading_deg.setRange(0.0, 360.0)
        self.ba_heading_deg.setSingleStep(1.0)
        self.ba_heading_deg.setValue(float(ba_heading_deg))
        ba_form.addRow("BA IDs", QLabel(ba_ids_text))
        ba_form.addRow("BA 거리 (nm)", self.ba_from_asset_nm)
        ba_form.addRow("BA Heading (deg)", self.ba_heading_deg)
        self._style_group_box(ba_group, "#3b82f6")
        cap_ba_row.addWidget(ba_group, 1)
        left_root.addLayout(cap_ba_row)

        # 4) RA POSITION + RA TOUCHDOWN ZONE
        ra_row = QHBoxLayout()
        ra_row.setContentsMargins(0, 0, 0, 0)
        ra_row.setSpacing(6)

        ra_pos_group = QGroupBox("RA POSITION (ASSET 기준)")
        ra_pos_form = QFormLayout(ra_pos_group)
        self._compact_form(ra_pos_form)
        self.ra_from_asset_nm = QDoubleSpinBox()
        self.ra_from_asset_nm.setDecimals(1)
        self.ra_from_asset_nm.setRange(0.0, 500.0)
        self.ra_from_asset_nm.setSingleStep(0.1)
        self.ra_from_asset_nm.setValue(float(ra_from_asset_nm))
        self.ra_heading_deg = QDoubleSpinBox()
        self.ra_heading_deg.setDecimals(0)
        self.ra_heading_deg.setRange(0.0, 360.0)
        self.ra_heading_deg.setSingleStep(1.0)
        self.ra_heading_deg.setValue(float(ra_heading_deg))
        ra_pos_form.addRow("RA 거리 (nm)", self.ra_from_asset_nm)
        ra_pos_form.addRow("RA Heading (deg)", self.ra_heading_deg)
        self._style_group_box(ra_pos_group, "#ff0000")
        ra_row.addWidget(ra_pos_group, 1)

        ra_group = QGroupBox("RA TOUCHDOWN ZONE (ASSET 기준)")
        ra_form = QFormLayout(ra_group)
        self._compact_form(ra_form)
        self.ra_zone_radius_nm = QDoubleSpinBox()
        self.ra_zone_radius_nm.setDecimals(1)
        self.ra_zone_radius_nm.setRange(0.1, 200.0)
        self.ra_zone_radius_nm.setSingleStep(0.1)
        self.ra_zone_radius_nm.setValue(float(ra_zone_radius_nm))
        self.ra_line_forward_nm = QDoubleSpinBox()
        self.ra_line_forward_nm.setDecimals(1)
        self.ra_line_forward_nm.setRange(0.0, 200.0)
        self.ra_line_forward_nm.setSingleStep(0.1)
        self.ra_line_forward_nm.setValue(float(ra_line_forward_nm))
        ra_form.addRow("Radius (nm)", self.ra_zone_radius_nm)
        ra_form.addRow("Forward (nm)", self.ra_line_forward_nm)
        self.ra_mode_radius = QRadioButton("Radius Circle")
        self.ra_mode_line = QRadioButton("Forward Line")
        use_line = str(ra_zone_mode).strip().lower() == "line"
        self.ra_mode_line.setChecked(use_line)
        self.ra_mode_radius.setChecked(not use_line)
        self.ra_mode_radius.toggled.connect(self._on_ra_mode_changed)
        self.ra_mode_line.toggled.connect(self._on_ra_mode_changed)
        ra_mode_row = QHBoxLayout()
        ra_mode_row.setContentsMargins(0, 0, 0, 0)
        ra_mode_row.setSpacing(8)
        ra_mode_row.addWidget(self.ra_mode_line)
        ra_mode_row.addWidget(self.ra_mode_radius)
        ra_mode_row.addStretch(1)
        ra_form.addRow("Zone Type", ra_mode_row)
        self._style_group_box(ra_group, "#a855f7")
        ra_row.addWidget(ra_group, 1)
        left_root.addLayout(ra_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_ok = QPushButton("Apply")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        left_root.addLayout(btn_row)
        left_root.addStretch(1)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setWidget(left_wrap)
        left_scroll.setMinimumWidth(560)
        root.addWidget(left_scroll, 1)

        preview_group = QGroupBox("DCA Preview")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        preview_layout.setSpacing(6)
        preview_mode_row = QHBoxLayout()
        preview_mode_row.setContentsMargins(6, 4, 6, 4)
        preview_mode_row.setSpacing(8)
        self.chk_enable_individual_drag = QCheckBox()
        self.chk_enable_individual_drag.setText("개별 이동")
        self.chk_enable_individual_drag.setChecked(False)
        preview_mode_row.addStretch(1)
        preview_mode_row.addWidget(self.chk_enable_individual_drag, 0)
        preview_mode_row.addStretch(1)
        preview_layout.addLayout(preview_mode_row)
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(480, 800)
        self.preview_label.setStyleSheet("background:#e9f7e9; border:1px solid #7fbf7f; border-radius:6px;")
        self.preview_label.setMouseTracking(True)
        self.preview_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.preview_label.installEventFilter(self)
        self.btn_flip_squad = QPushButton("↻", self.preview_label)
        self.btn_flip_squad.setFixedSize(34, 34)
        self.btn_flip_squad.setToolTip("선택 분대 Heading 180deg 회전")
        self.btn_flip_squad.setStyleSheet("QPushButton { color: #000000; background: transparent; border: none; font-size: 20px; font-weight: 700; }")
        self.btn_flip_squad.setVisible(False)
        self.btn_flip_squad.raise_()
        preview_layout.addWidget(self.preview_label, 1)
        preview_bottom_row = QHBoxLayout()
        preview_bottom_row.setContentsMargins(6, 0, 6, 4)
        preview_bottom_row.setSpacing(8)
        preview_bottom_row.addStretch(1)
        self.btn_cap_front_pair = QPushButton("CAP 추가")
        self.btn_cap_front_pair.setCheckable(True)
        self.btn_cap_front_pair.setChecked(bool(self._cap_front_pair_enabled))
        preview_bottom_row.addWidget(self.btn_cap_front_pair, 0)
        preview_layout.addLayout(preview_bottom_row)
        root.addWidget(preview_group, 1)
        root.setStretch(0, 1)
        root.setStretch(1, 1)

        self._shrink_widget_font(left_wrap, steps=3)
        self._shrink_value_boxes(ratio=1.04)
        self._connect_live_updates()
        self.chk_enable_individual_drag.toggled.connect(self._on_individual_drag_toggled)
        self._set_position_controls_locked(False)
        self._on_asset_same_toggled(bool(self.chk_asset_same_as_be.isChecked()))
        self._on_ra_mode_changed()
        self._sync_ba_ra_defaults_from_mission_and_cap(force=False)
        self._update_preview()

    def _connect_live_updates(self):
        self.cap_front_nm.valueChanged.connect(self._on_cap_or_mission_changed)
        self.cap_rear_nm.valueChanged.connect(self._on_cap_or_mission_changed)
        self.commit_nm.valueChanged.connect(self._on_cap_or_mission_changed)
        self.mission_height_nm.valueChanged.connect(self._on_cap_or_mission_changed)
        self.mission_width_nm.valueChanged.connect(self._update_preview)
        self.hmrl_nm.valueChanged.connect(self._update_preview)
        self.ldez_nm.valueChanged.connect(self._update_preview)
        self.hdez_nm.valueChanged.connect(self._update_preview)
        self.asset_bearing_deg.valueChanged.connect(self._update_preview)
        self.asset_range_nm.valueChanged.connect(self._update_preview)
        self.ra_zone_radius_nm.valueChanged.connect(self._update_preview)
        self.ra_line_forward_nm.valueChanged.connect(self._update_preview)
        self.ba_heading_deg.valueChanged.connect(self._update_preview)
        self.ra_heading_deg.valueChanged.connect(self._update_preview)
        self.ba_from_asset_nm.valueChanged.connect(self._on_ba_spin_changed)
        self.ra_from_asset_nm.valueChanged.connect(self._on_ra_spin_changed)
        self.btn_cap_front_pair.toggled.connect(self._on_cap_front_pair_toggled)
        self.btn_flip_squad.clicked.connect(self._on_flip_selected_squad)

    def _style_group_box(self, box: QGroupBox, color_hex: str, title_color_hex: Optional[str] = None):
        c = str(color_hex).strip()
        tc = str(title_color_hex).strip() if title_color_hex is not None else c
        box.setStyleSheet(
            "QGroupBox {"
            f" border: 2px solid {c};"
            " border-radius: 8px;"
            " margin-top: 36px;"
            "}"
            "QGroupBox::title {"
            f" color: {tc};"
            " font-weight: 700;"
            " padding: 0 8px 14px 8px;"
            "}"
        )

    def _compact_form(self, form: QFormLayout):
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(12)
        form.setContentsMargins(12, 34, 12, 12)

    def _shrink_value_boxes(self, ratio: float = 0.8):
        r = max(0.2, min(3.0, float(ratio)))
        for w in self.findChildren(QDoubleSpinBox):
            target = int(round(float(w.sizeHint().width()) * r))
            w.setFixedWidth(max(56, target))

    def _shrink_widget_font(self, widget: QWidget, steps: int = 2):
        f = widget.font()
        ps = float(f.pointSizeF())
        if ps <= 0.0:
            ps = float(max(9, QApplication.font().pointSize()))
        f.setPointSizeF(max(7.0, ps - float(max(0, int(steps)))))
        widget.setFont(f)

    def _on_ba_spin_changed(self, _v: float):
        if self._auto_sync_guard:
            return
        self._ba_user_modified = True
        self._update_preview()

    def _on_ra_spin_changed(self, _v: float):
        if self._auto_sync_guard:
            return
        self._ra_user_modified = True
        self._update_preview()

    def _on_cap_or_mission_changed(self, _v: float):
        self._sync_ba_ra_defaults_from_mission_and_cap(force=False)
        self._update_preview()

    def _on_cap_front_pair_toggled(self, checked: bool):
        self._cap_front_pair_enabled = bool(checked)
        if hasattr(self, "btn_cap_front_pair") and self.btn_cap_front_pair is not None:
            self.btn_cap_front_pair.setText("CAP 추가됨" if self._cap_front_pair_enabled else "CAP 추가")
        if self._cap_front_pair_enabled:
            # Place CAP pair at quarter points from center:
            # if width=40nm => +-10nm (10nm from each side boundary).
            if float(self._cap_front_pair_half_sep_nm) <= 0.0:
                self._cap_front_pair_half_sep_nm = 0.25 * float(self.mission_width_nm.value())
        else:
            self._selected_ba_squad = []
            self._selected_ba_squad_center_nm = None
            self._ba_heading_override_deg = {}
            if hasattr(self, "btn_flip_squad"):
                self.btn_flip_squad.setVisible(False)
        if self._cap_front_pair_enabled:
            self._align_ba_to_cap_pair_once()
            self._apply_cap_pair_default_headings()
            self._sync_position_spins_from_preview(target="ba")
        self._update_preview()

    def _apply_cap_pair_default_headings(self):
        # CAP split default: keep #1 squad heading as-is, set other BA squad(s) to 180deg.
        ba_ids = [str(x) for x in self._ba_ids_preview]
        if not ba_ids:
            return
        if len(ba_ids) == 2:
            target_ids = [x for x in ["#2"] if x in ba_ids]
        else:
            target_ids = [x for x in ["#3", "#4"] if x in ba_ids]
        for sid in target_ids:
            self._ba_heading_override_deg[str(sid)] = 180.0

    def _move_ba_members_by_delta_nm(self, member_ids: Set[str], delta_nm: np.ndarray):
        if (not member_ids) or (not self._ba_ids_preview):
            return
        geo = self._build_preview_geometry_nm()
        lead = str(self._ba_ids_preview[0])
        base = np.array(geo["ba"], dtype=float)
        cur_map: Dict[str, np.ndarray] = {str(pid): np.array(pp, dtype=float) for pid, pp in geo["ba_points"]}
        moved_map: Dict[str, np.ndarray] = {k: np.array(v, dtype=float) for k, v in cur_map.items()}
        dn = np.array(delta_nm, dtype=float)
        for sid in member_ids:
            if sid in moved_map:
                moved_map[sid] = np.array(moved_map[sid], dtype=float) + dn
        moved_lead = np.array(moved_map.get(lead, cur_map.get(lead, base)), dtype=float)
        self._ba_member_offsets_nm[lead] = (float((moved_lead - base)[0]), float((moved_lead - base)[1]))
        for sid, mp in moved_map.items():
            if str(sid) == lead:
                continue
            rel = np.array(mp, dtype=float) - moved_lead
            self._ba_member_offsets_nm[str(sid)] = (float(rel[0]), float(rel[1]))

    def _shift_ba_split_groups_nm(self, left_delta_nm: np.ndarray, right_delta_nm: np.ndarray):
        ids = [str(x) for x in self._ba_ids_preview]
        if not ids:
            return
        if len(ids) == 2:
            # 2vs2 CAP split: #1 on left CAP lane, #2 on right CAP lane.
            if "#1" in ids:
                self._move_ba_members_by_delta_nm({"#1"}, np.array(left_delta_nm, dtype=float))
            if "#2" in ids:
                self._move_ba_members_by_delta_nm({"#2"}, np.array(right_delta_nm, dtype=float))
            return
        left_grp = {x for x in ["#1", "#2"] if x in ids}
        right_grp = {x for x in ["#3", "#4"] if x in ids}
        if left_grp:
            self._move_ba_members_by_delta_nm(left_grp, np.array(left_delta_nm, dtype=float))
        if right_grp:
            self._move_ba_members_by_delta_nm(right_grp, np.array(right_delta_nm, dtype=float))

    def _align_ba_to_cap_pair_once(self):
        if not bool(self._cap_front_pair_enabled):
            return
        geo = self._build_preview_geometry_nm()
        cap_pair = geo.get("cap_f_pair")
        if cap_pair is None:
            return
        by_id: Dict[str, np.ndarray] = {str(a): np.array(p, dtype=float) for a, p in geo["ba_points"]}
        left_target = np.array(cap_pair[0], dtype=float)
        right_target_f = np.array(cap_pair[1], dtype=float)
        cap_r_pair = geo.get("cap_r_pair")
        right_target_r = np.array(cap_r_pair[1], dtype=float) if cap_r_pair is not None else np.array(right_target_f, dtype=float)
        ids = [str(x) for x in self._ba_ids_preview]
        if len(ids) == 2:
            # 2vs2: #1 -> left CAP FRONT, #2 -> right CAP REAR.
            left_delta = np.zeros(2, dtype=float)
            right_delta = np.zeros(2, dtype=float)
            if "#1" in by_id:
                left_delta = left_target - np.array(by_id["#1"], dtype=float)
            if "#2" in by_id:
                right_delta = right_target_r - np.array(by_id["#2"], dtype=float)
            self._shift_ba_split_groups_nm(left_delta, right_delta)
            return
        left_anchor_id = "#1" if "#1" in by_id else None
        right_anchor_id = "#3" if "#3" in by_id else None
        left_delta = np.zeros(2, dtype=float)
        right_delta = np.zeros(2, dtype=float)
        if left_anchor_id is not None:
            left_delta = left_target - np.array(by_id[left_anchor_id], dtype=float)
        if right_anchor_id is not None:
            # Non-#1 squad anchors to CAP REAR lane.
            right_delta = right_target_r - np.array(by_id[right_anchor_id], dtype=float)
        self._shift_ba_split_groups_nm(left_delta, right_delta)

    def _pick_ba_squad_for_aid(self, aid: str) -> List[str]:
        sid = str(aid)
        ba_ids = [str(x) for x in self._ba_ids_preview]
        if sid not in ba_ids:
            return []
        if not bool(self._cap_front_pair_enabled):
            return []
        if len(ba_ids) == 2:
            # In 2vs2 CAP-split, #1 and #2 are independent squads.
            return [sid]
        if len(ba_ids) >= 4:
            if sid in {"#1", "#2"}:
                return [x for x in ["#1", "#2"] if x in ba_ids]
            if sid in {"#3", "#4"}:
                return [x for x in ["#3", "#4"] if x in ba_ids]
        return [sid]

    def _on_preview_aircraft_clicked(self, aid: str):
        squad = self._pick_ba_squad_for_aid(str(aid))
        self._selected_ba_squad = list(squad)
        if hasattr(self, "btn_flip_squad") and self.btn_flip_squad is not None:
            if squad:
                self.btn_flip_squad.setVisible(True)
                self.btn_flip_squad.setText("↻")
                pts = []
                for sid in squad:
                    p = self._preview_points_nm.get(str(sid))
                    if p is not None:
                        pts.append(np.array(p, dtype=float))
                if pts:
                    self._selected_ba_squad_center_nm = np.mean(np.vstack(pts), axis=0)
                else:
                    self._selected_ba_squad_center_nm = None
            else:
                self.btn_flip_squad.setVisible(False)
                self._selected_ba_squad_center_nm = None

    def _on_flip_selected_squad(self):
        if not self._selected_ba_squad:
            return
        for sid in self._selected_ba_squad:
            base = float(self._ba_heading_override_deg.get(str(sid), float(self.ba_heading_deg.value())))
            self._ba_heading_override_deg[str(sid)] = self._wrap_heading(base + 180.0)
        self._update_preview()

    def _on_individual_drag_toggled(self, checked: bool):
        self._set_position_controls_locked(bool(checked))
        self._update_preview()

    def _set_position_controls_locked(self, locked: bool):
        # In individual-aircraft drag mode, lock BA/RA position controls to avoid
        # conflicting group-anchor edits while members are moved independently.
        en = not bool(locked)
        for w in [self.ba_from_asset_nm, self.ba_heading_deg, self.ra_from_asset_nm, self.ra_heading_deg]:
            try:
                w.setEnabled(en)
            except Exception:
                pass

    def _is_individual_drag_enabled(self) -> bool:
        if (not hasattr(self, "chk_enable_individual_drag")) or (self.chk_enable_individual_drag is None):
            return False
        return bool(self.chk_enable_individual_drag.isChecked())

    def _sync_ba_ra_defaults_from_mission_and_cap(self, force: bool = False):
        suggested_ra = float(self.commit_nm.value()) + (0.5 * (float(self.mission_height_nm.value()) - float(self.commit_nm.value())))
        if suggested_ra < 0.0:
            suggested_ra = 0.0
        self._auto_sync_guard = True
        try:
            if force or (not self._ra_user_modified):
                self.ra_from_asset_nm.setValue(float(suggested_ra))
        finally:
            self._auto_sync_guard = False

    def _draw_line_nm(self, painter: QPainter, map_fn, p0: np.ndarray, p1: np.ndarray, color: QColor, width: int = 2):
        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(max(1, int(width)))
        painter.setPen(pen)
        a = map_fn(float(p0[0]), float(p0[1]))
        b = map_fn(float(p1[0]), float(p1[1]))
        painter.drawLine(a[0], a[1], b[0], b[1])

    def _draw_point_nm(self, painter: QPainter, map_fn, p: np.ndarray, color: QColor, radius_px: int = 5, label: Optional[str] = None):
        xy = map_fn(float(p[0]), float(p[1]))
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawEllipse(xy[0] - radius_px, xy[1] - radius_px, radius_px * 2, radius_px * 2)
        if label:
            painter.drawText(xy[0] + 6, xy[1] - 6, str(label))

    def _draw_aircraft_arrow_nm(
        self,
        painter: QPainter,
        map_fn,
        p: np.ndarray,
        color: QColor,
        heading_deg: float,
        label: Optional[str] = None,
    ):
        center = map_fn(float(p[0]), float(p[1]))
        hdg = math.radians(float(heading_deg))
        dir_px = np.array([math.sin(hdg), -math.cos(hdg)], dtype=float)
        right_px = np.array([dir_px[1], -dir_px[0]], dtype=float)
        nose = np.array([float(center[0]), float(center[1])], dtype=float) + (dir_px * 9.0)
        tail = np.array([float(center[0]), float(center[1])], dtype=float) - (dir_px * 7.0)
        left = tail + (right_px * 4.5)
        right = tail - (right_px * 4.5)
        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawPolygon(
            QPolygon(
                [
                    QPoint(int(round(float(nose[0]))), int(round(float(nose[1])))),
                    QPoint(int(round(float(left[0]))), int(round(float(left[1])))),
                    QPoint(int(round(float(right[0]))), int(round(float(right[1])))),
                ]
            )
        )
        if label:
            painter.setPen(QColor("#111111"))
            painter.drawText(int(round(float(center[0]) + 7.0)), int(round(float(center[1]) - 7.0)), str(label))

    def _preview_px_to_nm(self, px: float, py: float) -> np.ndarray:
        if not self._preview_map_cache:
            return np.zeros(2, dtype=float)
        w = float(self._preview_map_cache.get("w", 1.0))
        h = float(self._preview_map_cache.get("h", 1.0))
        cx = float(self._preview_map_cache.get("cx", 0.0))
        cy = float(self._preview_map_cache.get("cy", 0.0))
        scale = max(1e-9, float(self._preview_map_cache.get("scale", 1.0)))
        x_nm = cx + ((float(px) - (0.5 * w)) / scale)
        y_nm = cy - ((float(py) - (0.5 * h)) / scale)
        return np.array([x_nm, y_nm], dtype=float)

    def _wrap_heading(self, deg: float) -> float:
        return float((float(deg) + 360.0) % 360.0)

    def _pick_aircraft_at_px(self, px: float, py: float, radius_px: float = 20.0) -> Optional[str]:
        if not self._preview_points_nm or not self._preview_map_cache:
            return None
        w = float(self._preview_map_cache.get("w", 1.0))
        h = float(self._preview_map_cache.get("h", 1.0))
        cx = float(self._preview_map_cache.get("cx", 0.0))
        cy = float(self._preview_map_cache.get("cy", 0.0))
        scale = max(1e-9, float(self._preview_map_cache.get("scale", 1.0)))
        best_id = None
        best_d = float(radius_px)
        for aid, p in self._preview_points_nm.items():
            sx = (0.5 * w) + ((float(p[0]) - cx) * scale)
            sy = (0.5 * h) - ((float(p[1]) - cy) * scale)
            d = math.hypot(float(px) - sx, float(py) - sy)
            if d <= best_d:
                best_d = d
                best_id = str(aid)
        return best_id

    def _group_for_aircraft(self, aid: str) -> Tuple[Optional[str], Optional[str]]:
        sid = str(aid)
        if sid in self._ba_ids_preview and self._ba_ids_preview:
            return "ba", str(self._ba_ids_preview[0])
        if sid in self._ra_ids_preview and self._ra_ids_preview:
            return "ra", str(self._ra_ids_preview[0])
        return None, None

    def _apply_drag_position_nm(self, aid: str, new_pos_nm: np.ndarray):
        geo = self._build_preview_geometry_nm()
        group, lead = self._group_for_aircraft(str(aid))
        if not group or not lead:
            return
        if group == "ba":
            base = np.array(geo["ba"], dtype=float)
            offsets = self._ba_member_offsets_nm
            lead_off = np.array(offsets.get(lead, (0.0, 0.0)), dtype=float)
        else:
            base = np.array(geo["ra"], dtype=float)
            offsets = self._ra_member_offsets_nm
            lead_off = np.array(offsets.get(lead, (0.0, 0.0)), dtype=float)
        lead_pos = base + lead_off
        sid = str(aid)
        use_group_drag = (not self._is_individual_drag_enabled()) or (group == "ba" and bool(self._cap_front_pair_enabled))
        if use_group_drag:
            # Default behavior: move BA/RA as group, except CAP-split BA control rules.
            group_points = geo["ba_points"] if group == "ba" else geo["ra_points"]
            cur = None
            cur_map: Dict[str, np.ndarray] = {}
            for pid, pp in group_points:
                ps = str(pid)
                pv = np.array(pp, dtype=float)
                cur_map[ps] = pv
                if ps == sid:
                    cur = pv
            if cur is None:
                cur = np.array(lead_pos, dtype=float)
            delta = np.array(new_pos_nm, dtype=float) - cur
            moved_map: Dict[str, np.ndarray] = {ms: np.array(pv, dtype=float) for ms, pv in cur_map.items()}
            move_members: Set[str] = set(cur_map.keys())
            if group == "ba" and bool(self._cap_front_pair_enabled):
                ba_ids = [str(x) for x in self._ba_ids_preview]
                if len(ba_ids) == 2:
                    # 2vs2 CAP split: #1 and #2 are independent squads.
                    move_members = {sid}
                elif len(ba_ids) >= 4:
                    # 4vs2/4vs4 split: #1,#2 together and #3,#4 together.
                    if sid in {"#1", "#2"}:
                        move_members = {x for x in ["#1", "#2"] if x in cur_map}
                    elif sid in {"#3", "#4"}:
                        move_members = {x for x in ["#3", "#4"] if x in cur_map}
                    else:
                        move_members = {sid}
            for ms in move_members:
                if ms in moved_map:
                    moved_map[ms] = np.array(moved_map[ms], dtype=float) + delta
            moved_lead = np.array(moved_map.get(lead, np.array(lead_pos, dtype=float) + delta), dtype=float)
            # Offset semantics in this dialog:
            # - lead: base-relative
            # - non-lead: lead-relative
            lead_off = moved_lead - base
            offsets[lead] = (float(lead_off[0]), float(lead_off[1]))
            for ms, moved in moved_map.items():
                if str(ms) == lead:
                    continue
                rel = np.array(moved, dtype=float) - moved_lead
                offsets[str(ms)] = (float(rel[0]), float(rel[1]))
        else:
            # Individual adjust mode: aircraft can be moved independently.
            if sid == lead:
                delta = np.array(new_pos_nm, dtype=float) - lead_pos
                off = np.array(new_pos_nm, dtype=float) - base
                offsets[lead] = (float(off[0]), float(off[1]))
                group_ids = self._ba_ids_preview if group == "ba" else self._ra_ids_preview
                for mid in group_ids:
                    ms = str(mid)
                    if ms == lead:
                        continue
                    prev = np.array(offsets.get(ms, (0.0, 0.0)), dtype=float)
                    nxt = prev - delta
                    offsets[ms] = (float(nxt[0]), float(nxt[1]))
            else:
                off = np.array(new_pos_nm, dtype=float) - lead_pos
                offsets[sid] = (float(off[0]), float(off[1]))
        self._drag_changed = True
        self._sync_position_spins_from_preview(target=group)
        self._update_preview()

    def _sync_position_spins_from_preview(self, target: str = "both"):
        if self._is_individual_drag_enabled():
            return
        t = str(target).strip().lower()
        sync_ba = t in {"ba", "both", "all"}
        sync_ra = t in {"ra", "both", "all"}
        geo = self._build_preview_geometry_nm()
        asset = np.array(geo.get("asset", np.zeros(2, dtype=float)), dtype=float)
        _, fwd, _ = self._current_preview_axes()

        ba_ids = [str(x) for x in self._ba_ids_preview]
        ra_ids = [str(x) for x in self._ra_ids_preview]
        ba_lead = ba_ids[0] if ba_ids else None
        ra_lead = ra_ids[0] if ra_ids else None

        ba_map = {str(pid): np.array(pp, dtype=float) for pid, pp in geo.get("ba_points", [])}
        ra_map = {str(pid): np.array(pp, dtype=float) for pid, pp in geo.get("ra_points", [])}

        self._auto_sync_guard = True
        try:
            if sync_ba and ba_lead and (ba_lead in ba_map):
                rel = np.array(ba_map[ba_lead], dtype=float) - asset
                ba_dist = max(0.0, float(np.dot(rel, fwd)))
                self._set_spin_clamped(self.ba_from_asset_nm, ba_dist)
                self._ba_user_modified = True
            if sync_ra and ra_lead and (ra_lead in ra_map):
                rel = np.array(ra_map[ra_lead], dtype=float) - asset
                ra_dist = max(0.0, float(np.dot(rel, fwd)))
                self._set_spin_clamped(self.ra_from_asset_nm, ra_dist)
                self._ra_user_modified = True
        finally:
            self._auto_sync_guard = False

    def _draw_preview_metric_boxes(self, painter: QPainter, h_px: int):
        metric_pairs = [("#2", "#1"), ("#3", "#1"), ("#4", "#3"), ("#6", "#5"), ("#7", "#5"), ("#8", "#7")]
        ba_lines: List[str] = []
        ra_lines: List[str] = []
        for a, b in metric_pairs:
            pa = self._preview_points_nm.get(str(a))
            pb = self._preview_points_nm.get(str(b))
            if pa is None or pb is None:
                continue
            dv = np.array(pb, dtype=float) - np.array(pa, dtype=float)
            dist_nm = math.hypot(float(dv[0]), float(dv[1]))
            bearing_deg = self._wrap_heading(math.degrees(math.atan2(float(dv[0]), float(dv[1]))))
            label = f"{a}->{b}: {dist_nm:.2f}nm / {bearing_deg:03.0f}deg"
            if str(a) in self._ba_ids_preview:
                ba_lines.append(label)
            else:
                ra_lines.append(label)
        fm = painter.fontMetrics()
        line_h = fm.height()

        if ra_lines:
            box_w = max(fm.horizontalAdvance(t) for t in ra_lines)
            box_h = line_h * len(ra_lines)
            x0 = 12
            y0 = 12
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.drawRect(x0 - 6, y0 - 6, box_w + 12, box_h + 12)
            painter.setPen(QColor("#111111"))
            for i, t in enumerate(ra_lines):
                painter.drawText(x0, y0 + ((i + 1) * line_h) - fm.descent(), t)

        if ba_lines:
            box_w = max(fm.horizontalAdvance(t) for t in ba_lines)
            box_h = line_h * len(ba_lines)
            x0 = 12
            y0 = max(12, int(h_px - box_h - 18))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.drawRect(x0 - 6, y0 - 6, box_w + 12, box_h + 12)
            painter.setPen(QColor("#111111"))
            for i, t in enumerate(ba_lines):
                painter.drawText(x0, y0 + ((i + 1) * line_h) - fm.descent(), t)

    def eventFilter(self, obj, event):
        if obj is self.preview_label:
            et = event.type()
            if et == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
                p = event.position()
                self.preview_label.setFocus()
                self._preview_pan_active = True
                self._preview_pan_last_px = (float(p.x()), float(p.y()))
                return True
            if et == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                p = event.position()
                self.preview_label.setFocus()
                px = float(p.x())
                py = float(p.y())
                corner_idx = self._pick_mission_corner_at_px(px, py)
                if corner_idx is not None:
                    self._preview_drag_mode = "mission_corner"
                    self._preview_drag_corner = int(corner_idx)
                    nm = self._preview_px_to_nm(px, py)
                    _, fwd, right = self._current_preview_axes()
                    rel = np.array(nm, dtype=float)
                    self._preview_corner_drag_ctx = {
                        "corner_idx": float(corner_idx),
                        "start_w": float(self.mission_width_nm.value()),
                        "start_h": float(self.mission_height_nm.value()),
                        "start_r": float(np.dot(rel, right)),
                        "start_f": float(np.dot(rel, fwd)),
                    }
                    return True
                line_key = self._pick_preview_line_at_px(px, py)
                picked = self._pick_aircraft_at_px(px, py)
                if picked:
                    self._on_preview_aircraft_clicked(str(picked))
                    self._preview_drag_mode = "aircraft"
                    self._drag_aircraft_id = str(picked)
                    return True
                if line_key:
                    self._preview_drag_mode = "line"
                    self._preview_drag_key = str(line_key)
                    return True
                point_key = self._pick_preview_point_at_px(px, py)
                if point_key:
                    self._preview_drag_mode = "point"
                    self._preview_drag_key = str(point_key)
                    return True
            elif et == QEvent.Type.MouseMove:
                p = event.position()
                px = float(p.x())
                py = float(p.y())
                if self._preview_pan_active and self._preview_pan_last_px is not None:
                    lx, ly = self._preview_pan_last_px
                    self._pan_preview_by_pixels(float(px - lx), float(py - ly))
                    self._preview_pan_last_px = (px, py)
                    return True
                if self._preview_drag_mode == "line" and self._preview_drag_key:
                    self._preview_drag_hint_pos = (px, py)
                    nm = self._preview_px_to_nm(px, py)
                    self._apply_drag_line_nm(self._preview_drag_key, nm)
                    return True
                if self._preview_drag_mode == "mission_corner" and self._preview_drag_corner is not None:
                    self._preview_drag_hint_pos = (px, py)
                    nm = self._preview_px_to_nm(px, py)
                    self._apply_drag_mission_corner_nm(int(self._preview_drag_corner), nm)
                    return True
                if self._preview_drag_mode == "point" and self._preview_drag_key:
                    self._preview_drag_hint_pos = (px, py)
                    nm = self._preview_px_to_nm(px, py)
                    self._apply_drag_preview_point_nm(self._preview_drag_key, nm)
                    return True
                if self._preview_drag_mode == "aircraft" and self._drag_aircraft_id:
                    p = event.position()
                    nm = self._preview_px_to_nm(float(p.x()), float(p.y()))
                    self._apply_drag_position_nm(self._drag_aircraft_id, nm)
                    return True
            elif et == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                if self._preview_drag_mode or self._drag_aircraft_id:
                    self._drag_aircraft_id = None
                    self._preview_drag_mode = None
                    self._preview_drag_key = None
                    self._preview_drag_corner = None
                    self._preview_corner_drag_ctx = None
                    self._preview_drag_hint_pos = None
                    self._preview_drag_hint_text = ""
                    self._update_preview()
                    return True
            elif et == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.RightButton:
                self._preview_pan_active = False
                self._preview_pan_last_px = None
                return True
            elif et == QEvent.Type.Wheel:
                p = event.position()
                self._apply_preview_wheel_zoom(float(p.x()), float(p.y()), float(event.angleDelta().y()))
                return True
            elif et == QEvent.Type.KeyPress:
                k = int(event.key())
                step_px = 36.0
                if bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    step_px = 72.0
                if k == int(Qt.Key.Key_Left):
                    self._pan_preview_by_pixels(-step_px, 0.0)
                    return True
                if k == int(Qt.Key.Key_Right):
                    self._pan_preview_by_pixels(step_px, 0.0)
                    return True
                if k == int(Qt.Key.Key_Up):
                    self._pan_preview_by_pixels(0.0, -step_px)
                    return True
                if k == int(Qt.Key.Key_Down):
                    self._pan_preview_by_pixels(0.0, step_px)
                    return True
        return super().eventFilter(obj, event)

    def _pan_preview_by_pixels(self, dx_px: float, dy_px: float):
        if not self._preview_map_cache:
            return
        sc = max(1e-9, float(self._preview_view_lock.get("scale", self._preview_map_cache.get("scale", 1.0))))
        cx = float(self._preview_view_lock.get("cx", self._preview_map_cache.get("cx", 0.0)))
        cy = float(self._preview_view_lock.get("cy", self._preview_map_cache.get("cy", 0.0)))
        w = float(self._preview_map_cache.get("w", 1.0))
        h = float(self._preview_map_cache.get("h", 1.0))
        cx = cx - (float(dx_px) / sc)
        cy = cy + (float(dy_px) / sc)
        self._preview_view_lock["scale"] = float(sc)
        self._preview_view_lock["cx"] = float(cx)
        self._preview_view_lock["cy"] = float(cy)
        self._preview_view_lock["w"] = float(w)
        self._preview_view_lock["h"] = float(h)
        self._preview_manual_zoom = True
        self._update_preview()

    def _apply_preview_wheel_zoom(self, px: float, py: float, delta_y: float):
        if not self._preview_map_cache:
            return
        w = float(self._preview_map_cache.get("w", 1.0))
        h = float(self._preview_map_cache.get("h", 1.0))
        cx = float(self._preview_view_lock.get("cx", self._preview_map_cache.get("cx", 0.0)))
        cy = float(self._preview_view_lock.get("cy", self._preview_map_cache.get("cy", 0.0)))
        sc = max(1e-6, float(self._preview_view_lock.get("scale", self._preview_map_cache.get("scale", 1.0))))
        zoom = 1.12 if float(delta_y) > 0.0 else (1.0 / 1.12)
        new_sc = max(0.25, min(5000.0, sc * zoom))
        # Keep cursor-anchored world point stable during zoom.
        x_nm = cx + ((float(px) - (0.5 * w)) / sc)
        y_nm = cy - ((float(py) - (0.5 * h)) / sc)
        new_cx = x_nm - ((float(px) - (0.5 * w)) / new_sc)
        new_cy = y_nm + ((float(py) - (0.5 * h)) / new_sc)
        self._preview_view_lock["scale"] = float(new_sc)
        self._preview_view_lock["cx"] = float(new_cx)
        self._preview_view_lock["cy"] = float(new_cy)
        self._preview_view_lock["w"] = float(w)
        self._preview_view_lock["h"] = float(h)
        self._preview_manual_zoom = True
        self._update_preview()

    @staticmethod
    def _point_to_segment_dist_px(
        px: float,
        py: float,
        a: Tuple[float, float],
        b: Tuple[float, float],
    ) -> float:
        ax, ay = float(a[0]), float(a[1])
        bx, by = float(b[0]), float(b[1])
        vx = bx - ax
        vy = by - ay
        wx = px - ax
        wy = py - ay
        vv = (vx * vx) + (vy * vy)
        if vv <= 1e-9:
            return math.hypot(px - ax, py - ay)
        t = ((wx * vx) + (wy * vy)) / vv
        t = max(0.0, min(1.0, t))
        qx = ax + (t * vx)
        qy = ay + (t * vy)
        return math.hypot(px - qx, py - qy)

    def _pick_preview_line_at_px(self, px: float, py: float) -> Optional[str]:
        best_key = None
        best_d = 1e9
        for key, line in self._preview_line_screen.items():
            d = self._point_to_segment_dist_px(px, py, line[0], line[1])
            if d < best_d:
                best_d = d
                best_key = str(key)
        if best_key and best_d <= 14.0:
            return best_key
        return None

    def _pick_mission_corner_at_px(self, px: float, py: float) -> Optional[int]:
        if not self._preview_corner_screen:
            return None
        best_idx = None
        best_d2 = 1e18
        for i, c in enumerate(self._preview_corner_screen):
            dx = px - float(c[0])
            dy = py - float(c[1])
            d2 = (dx * dx) + (dy * dy)
            if d2 < best_d2:
                best_d2 = d2
                best_idx = i
        if best_idx is not None and best_d2 <= (14.0 * 14.0):
            return int(best_idx)
        return None

    def _pick_preview_point_at_px(self, px: float, py: float) -> Optional[str]:
        best_key = None
        best_d2 = 1e18
        for key, c in self._preview_point_screen.items():
            dx = px - float(c[0])
            dy = py - float(c[1])
            d2 = (dx * dx) + (dy * dy)
            if d2 < best_d2:
                best_d2 = d2
                best_key = str(key)
        if best_key is not None and best_d2 <= (14.0 * 14.0):
            return best_key
        return None

    def _current_preview_axes(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        asset = np.array([0.0, 0.0], dtype=float)
        fwd_rad = math.radians(float(self.asset_bearing_deg.value()))
        fwd = np.array([math.sin(fwd_rad), math.cos(fwd_rad)], dtype=float)
        right = np.array([math.cos(fwd_rad), -math.sin(fwd_rad)], dtype=float)
        return asset, fwd, right

    def _current_be_point_nm(self, asset: np.ndarray) -> np.ndarray:
        if bool(self.chk_asset_same_as_be.isChecked()):
            return np.array(asset, dtype=float)
        be_to_asset_rad = math.radians(float(self.asset_bearing_deg.value()))
        be_to_asset = np.array([math.sin(be_to_asset_rad), math.cos(be_to_asset_rad)], dtype=float) * float(self.asset_range_nm.value())
        return np.array(asset, dtype=float) - be_to_asset

    def _set_spin_clamped(self, spin: QDoubleSpinBox, value: float):
        lo = float(spin.minimum())
        hi = float(spin.maximum())
        spin.setValue(float(min(hi, max(lo, float(value)))))

    def _apply_drag_line_nm(self, line_key: str, nm: np.ndarray):
        asset, fwd, _ = self._current_preview_axes()
        rel = np.array(nm, dtype=float) - np.array(asset, dtype=float)
        dist_nm = float(np.dot(rel, fwd))
        key = str(line_key).lower().strip()
        if key in {"cap_left", "cap_right"} and bool(self._cap_front_pair_enabled):
            _, _, right = self._current_preview_axes()
            rel2 = np.array(nm, dtype=float) - np.array(asset, dtype=float)
            lat = abs(float(np.dot(rel2, right)))
            half_w = 0.5 * float(self.mission_width_nm.value())
            old_sep = float(self._cap_front_pair_half_sep_nm)
            new_sep = float(min(half_w, max(0.0, lat)))
            dsep = float(new_sep - old_sep)
            self._cap_front_pair_half_sep_nm = float(new_sep)
            left_delta = (-right) * dsep
            right_delta = (right) * dsep
            self._shift_ba_split_groups_nm(left_delta, right_delta)
            self._sync_position_spins_from_preview(target="ba")
            self._preview_drag_hint_text = f"CAP pair slide: {float(self._cap_front_pair_half_sep_nm):.1f} nm"
            self._update_preview()
            return
        line_dist_for_hint = dist_nm
        if key == "hmrl":
            self._set_spin_clamped(self.hmrl_nm, dist_nm)
            line_dist_for_hint = float(self.hmrl_nm.value())
            self._preview_drag_hint_text = f"HMRL: {line_dist_for_hint:.1f} nm"
        elif key == "ldez":
            self._set_spin_clamped(self.ldez_nm, dist_nm)
            if float(self.ldez_nm.value()) > float(self.hdez_nm.value()):
                self._set_spin_clamped(self.hdez_nm, float(self.ldez_nm.value()))
            line_dist_for_hint = float(self.ldez_nm.value())
            self._preview_drag_hint_text = f"INNER DEZ: {line_dist_for_hint:.1f} nm"
        elif key == "hdez":
            self._set_spin_clamped(self.hdez_nm, dist_nm)
            if float(self.hdez_nm.value()) < float(self.ldez_nm.value()):
                self._set_spin_clamped(self.ldez_nm, float(self.hdez_nm.value()))
            line_dist_for_hint = float(self.hdez_nm.value())
            self._preview_drag_hint_text = f"OUTER DEZ: {line_dist_for_hint:.1f} nm"
        elif key == "commit":
            self._set_spin_clamped(self.commit_nm, dist_nm)
            line_dist_for_hint = float(self.commit_nm.value())
            self._preview_drag_hint_text = f"COMMIT LINE: {line_dist_for_hint:.1f} nm"
        else:
            return
        be = self._current_be_point_nm(asset)
        c = np.array(asset, dtype=float) + (fwd * line_dist_for_hint)
        d_be = math.hypot(float(c[0] - be[0]), float(c[1] - be[1]))
        self._preview_drag_hint_text = f"{self._preview_drag_hint_text}  |  B.E: {d_be:.1f} nm"
        self._update_preview()

    def _apply_drag_mission_corner_nm(self, corner_idx: int, nm: np.ndarray):
        _, fwd, right = self._current_preview_axes()
        rel = np.array(nm, dtype=float)
        r_now = float(np.dot(rel, right))
        f_now = float(np.dot(rel, fwd))
        ctx = self._preview_corner_drag_ctx or {}
        base_w = float(ctx.get("start_w", float(self.mission_width_nm.value())))
        base_h = float(ctx.get("start_h", float(self.mission_height_nm.value())))
        r0 = float(ctx.get("start_r", r_now))
        f0 = float(ctx.get("start_f", f_now))
        idx = int(corner_idx)

        dr = r_now - r0
        df = f_now - f0
        # Corner behavior tuned for mission rectangle anchored at ASSET rear-center:
        # - Rear corners: adjust width only (prevents sudden height collapse).
        # - Front corners: adjust both width and height.
        if idx in (1, 2):  # right side
            width_nm = base_w + (2.0 * dr)
        else:  # left side
            width_nm = base_w - (2.0 * dr)
        if idx in (2, 3):  # front corners
            height_nm = base_h + df
        else:
            height_nm = base_h
        width_nm = max(0.1, width_nm)
        height_nm = max(0.1, height_nm)
        self._set_spin_clamped(self.mission_width_nm, width_nm)
        self._set_spin_clamped(self.mission_height_nm, height_nm)
        self._preview_drag_hint_text = f"MISSION W/H: {float(self.mission_width_nm.value()):.1f} / {float(self.mission_height_nm.value()):.1f} nm"
        self._update_preview()

    def _apply_drag_preview_point_nm(self, point_key: str, nm: np.ndarray):
        key = str(point_key).lower().strip()
        asset, fwd, right = self._current_preview_axes()
        if key in {"cap_l", "cap_r", "cap_lf", "cap_rf", "cap_lr", "cap_rr", "cap_left", "cap_right"} and bool(self._cap_front_pair_enabled):
            rel = np.array(nm, dtype=float) - np.array(asset, dtype=float)
            lat = abs(float(np.dot(rel, right)))
            half_w = 0.5 * float(self.mission_width_nm.value())
            old_sep = float(self._cap_front_pair_half_sep_nm)
            new_sep = float(min(half_w, max(0.0, lat)))
            dsep = float(new_sep - old_sep)
            self._cap_front_pair_half_sep_nm = float(new_sep)
            left_delta = (-right) * dsep
            right_delta = (right) * dsep
            self._shift_ba_split_groups_nm(left_delta, right_delta)
            self._sync_position_spins_from_preview(target="ba")
            self._preview_drag_hint_text = f"CAP pair slide: {float(self._cap_front_pair_half_sep_nm):.1f} nm"
            self._update_preview()
            return
        if key in {"cf", "cr"}:
            rel = np.array(nm, dtype=float) - np.array(asset, dtype=float)
            dist_nm = float(np.dot(rel, fwd))
            if key == "cf":
                self._set_spin_clamped(self.cap_front_nm, dist_nm)
                if float(self.cap_front_nm.value()) < float(self.cap_rear_nm.value()):
                    self._set_spin_clamped(self.cap_rear_nm, float(self.cap_front_nm.value()))
                self._preview_drag_hint_text = f"C.F: {float(self.cap_front_nm.value()):.1f} nm"
            else:
                self._set_spin_clamped(self.cap_rear_nm, dist_nm)
                if float(self.cap_rear_nm.value()) > float(self.cap_front_nm.value()):
                    self._set_spin_clamped(self.cap_front_nm, float(self.cap_rear_nm.value()))
                self._preview_drag_hint_text = f"C.R: {float(self.cap_rear_nm.value()):.1f} nm"
            self._update_preview()
            return
        if key == "be":
            if bool(self.chk_asset_same_as_be.isChecked()):
                self.chk_asset_same_as_be.setChecked(False)
            be_now = self._current_be_point_nm(asset)
            # B.E drag constraint: vertical-only move on preview (keep X fixed).
            be = np.array([float(be_now[0]), float(nm[1])], dtype=float)
            vec = np.array(asset, dtype=float) - be
            rng = math.hypot(float(vec[0]), float(vec[1]))
            brg = self._wrap_heading(math.degrees(math.atan2(float(vec[0]), float(vec[1]))))
            self._set_spin_clamped(self.asset_range_nm, rng)
            self._set_spin_clamped(self.asset_bearing_deg, brg)
            self._preview_drag_hint_text = f"B.E: {float(rng):.1f} nm / {float(brg):.0f} deg"
            self._update_preview()

    def _build_preview_geometry_nm(self):
        asset = np.array([0.0, 0.0], dtype=float)
        fwd_rad = math.radians(float(self.asset_bearing_deg.value()))
        fwd = np.array([math.sin(fwd_rad), math.cos(fwd_rad)], dtype=float)
        right = np.array([math.cos(fwd_rad), -math.sin(fwd_rad)], dtype=float)
        width_nm = float(self.mission_width_nm.value())
        height_nm = float(self.mission_height_nm.value())
        half_w = 0.5 * width_nm
        p0 = asset - (right * half_w)
        p1 = asset + (right * half_w)
        p2 = p1 + (fwd * height_nm)
        p3 = p0 + (fwd * height_nm)
        mission_poly = [p0, p1, p2, p3]
        if bool(self.chk_asset_same_as_be.isChecked()):
            be = np.array(asset, dtype=float)
        else:
            be_to_asset_rad = math.radians(float(self.asset_bearing_deg.value()))
            be_to_asset = np.array([math.sin(be_to_asset_rad), math.cos(be_to_asset_rad)], dtype=float) * float(self.asset_range_nm.value())
            be = asset - be_to_asset

        def width_line_at(dist_nm: float):
            c = asset + (fwd * float(dist_nm))
            return c - (right * half_w), c + (right * half_w)

        ba = asset + (fwd * float(self.ba_from_asset_nm.value()))
        ra = asset + (fwd * float(self.ra_from_asset_nm.value()))
        cap_f = width_line_at(float(self.cap_front_nm.value()))
        cap_r = width_line_at(float(self.cap_rear_nm.value()))
        hmrl = width_line_at(float(self.hmrl_nm.value()))
        ldez = width_line_at(float(self.ldez_nm.value()))
        hdez = width_line_at(float(self.hdez_nm.value()))
        commit = width_line_at(float(self.commit_nm.value()))
        line_center = asset + (fwd * float(self.ra_line_forward_nm.value()))
        ra_line = (line_center - (right * half_w), line_center + (right * half_w))
        cap_f_center = asset + (fwd * float(self.cap_front_nm.value()))
        cap_r_center = asset + (fwd * float(self.cap_rear_nm.value()))
        cap_f_pair = None
        cap_r_pair = None
        if bool(self._cap_front_pair_enabled):
            half_w = 0.5 * float(width_nm)
            sep = float(min(half_w, max(0.0, float(self._cap_front_pair_half_sep_nm))))
            cap_f_pair = (
                np.array(cap_f_center, dtype=float) - (right * sep),
                np.array(cap_f_center, dtype=float) + (right * sep),
            )
            cap_r_pair = (
                np.array(cap_r_center, dtype=float) - (right * sep),
                np.array(cap_r_center, dtype=float) + (right * sep),
            )
        ba_points: List[Tuple[str, np.ndarray]] = []
        ra_points: List[Tuple[str, np.ndarray]] = []
        if self._ba_ids_preview:
            lead = self._ba_ids_preview[0]
            lead_off = np.array(self._ba_member_offsets_nm.get(str(lead), (0.0, 0.0)), dtype=float)
            lead_pos = np.array(ba, dtype=float) + lead_off
            ba_points.append((str(lead), lead_pos))
            for aid in self._ba_ids_preview[1:]:
                off = self._ba_member_offsets_nm.get(str(aid), (0.0, 0.0))
                p = np.array(lead_pos, dtype=float) + np.array([float(off[0]), float(off[1])], dtype=float)
                ba_points.append((str(aid), p))
        else:
            ba_points.append(("BA", np.array(ba, dtype=float)))
        if self._ra_ids_preview:
            ra_shape = str(self._ra_shape_preview).upper()
            # Mirror runtime DCA placement for two-ship RA LAB/ECHELON in preview.
            if (not bool(self._drag_changed)) and (len(self._ra_ids_preview) >= 2) and (ra_shape in {"LAB", "ECHELON"}):
                lead = str(self._ra_ids_preview[0])
                wing = str(self._ra_ids_preview[1])
                lead_off = np.array(self._ra_member_offsets_nm.get(lead, (0.0, 0.0)), dtype=float)
                wing_rel = np.array(self._ra_member_offsets_nm.get(wing, (2.0, 0.0)), dtype=float)
                pair_dist_nm = float(math.hypot(float(wing_rel[0]), float(wing_rel[1])))
                if (not np.isfinite(pair_dist_nm)) or (pair_dist_nm <= 0.0):
                    pair_dist_nm = 2.0
                half_nm = 0.5 * float(pair_dist_nm)
                left = -right
                if ra_shape == "LAB":
                    d_lead = left
                    d_wing = right
                else:
                    # ECHELON: lead = left-forward, wing = right-aft
                    d_lead = left + fwd
                    d_wing = right - fwd
                    n1 = max(float(np.linalg.norm(d_lead)), 1e-9)
                    n2 = max(float(np.linalg.norm(d_wing)), 1e-9)
                    d_lead = d_lead / n1
                    d_wing = d_wing / n2
                ra_center = np.array(ra, dtype=float) + lead_off
                p_lead = np.array(ra_center, dtype=float) + (d_lead * half_nm)
                p_wing = np.array(ra_center, dtype=float) + (d_wing * half_nm)
                ra_points.append((lead, p_lead))
                ra_points.append((wing, p_wing))
                for aid in self._ra_ids_preview[2:]:
                    off = self._ra_member_offsets_nm.get(str(aid), (0.0, 0.0))
                    p = np.array(ra_center, dtype=float) + np.array([float(off[0]), float(off[1])], dtype=float)
                    ra_points.append((str(aid), p))
            else:
                lead = self._ra_ids_preview[0]
                lead_off = np.array(self._ra_member_offsets_nm.get(str(lead), (0.0, 0.0)), dtype=float)
                lead_pos = np.array(ra, dtype=float) + lead_off
                ra_points.append((str(lead), lead_pos))
                for aid in self._ra_ids_preview[1:]:
                    off = self._ra_member_offsets_nm.get(str(aid), (0.0, 0.0))
                    p = np.array(lead_pos, dtype=float) + np.array([float(off[0]), float(off[1])], dtype=float)
                    ra_points.append((str(aid), p))
        else:
            ra_points.append(("RA", np.array(ra, dtype=float)))

        return {
            "asset": asset,
            "be": be,
            "ba": ba,
            "ra": ra,
            "ba_points": ba_points,
            "ra_points": ra_points,
            "mission": mission_poly,
            "cap_f": cap_f,
            "cap_r": cap_r,
            "cap_f_center": cap_f_center,
            "cap_r_center": cap_r_center,
            "cap_f_pair": cap_f_pair,
            "cap_r_pair": cap_r_pair,
            "hmrl": hmrl,
            "ldez": ldez,
            "hdez": hdez,
            "commit": commit,
            "ra_line": ra_line,
            "ra_radius_nm": float(self.ra_zone_radius_nm.value()),
        }

    def _update_preview(self):
        if not hasattr(self, "preview_label") or self.preview_label is None:
            return
        w = max(360, int(self.preview_label.width()))
        h = max(800, int(self.preview_label.height()))
        pix = QPixmap(w, h)
        pix.fill(self.preview_colors["bg"])
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QColor("#1f2937"))

        geo = self._build_preview_geometry_nm()
        bounds = []
        # Keep battlefield framing fixed to static DCA geometry.
        # Do not include draggable BA/RA aircraft points in auto-fit bounds.
        for p in geo["mission"]:
            bounds.append(np.array(p, dtype=float))
        bounds.extend([np.array(geo["asset"]), np.array(geo["be"]), np.array(geo["cap_f_center"]), np.array(geo["cap_r_center"])])
        if geo.get("cap_f_pair") is not None:
            bounds.append(np.array(geo["cap_f_pair"][0], dtype=float))
            bounds.append(np.array(geo["cap_f_pair"][1], dtype=float))
        if geo.get("cap_r_pair") is not None:
            bounds.append(np.array(geo["cap_r_pair"][0], dtype=float))
            bounds.append(np.array(geo["cap_r_pair"][1], dtype=float))
        for k in ("hmrl", "ldez", "hdez", "commit", "ra_line"):
            bounds.append(np.array(geo[k][0], dtype=float))
            bounds.append(np.array(geo[k][1], dtype=float))
        rr = float(geo["ra_radius_nm"])
        bounds.append(np.array(geo["asset"]) + np.array([rr, rr], dtype=float))
        bounds.append(np.array(geo["asset"]) + np.array([-rr, -rr], dtype=float))

        be_x = float(np.array(geo["be"], dtype=float)[0])
        xs = [float(p[0]) for p in bounds]
        ys = [float(p[1]) for p in bounds]
        max_dx = max([abs(float(x) - be_x) for x in xs] + [1.0])
        min_y = min(ys)
        max_y = max(ys)
        span_x = max(1.0, 2.0 * max_dx)
        span_y = max(1.0, max_y - min_y)
        pad_px = 28.0
        scale = min((w - (2.0 * pad_px)) / span_x, (h - (2.0 * pad_px)) / span_y)
        scale = max(1.0, scale)
        cx = float(be_x)
        cy = 0.5 * (min_y + max_y)
        lock_w = int(self._preview_view_lock.get("w", -1))
        lock_h = int(self._preview_view_lock.get("h", -1))
        if (not self._preview_view_lock) or (lock_w != w) or (lock_h != h):
            self._preview_view_lock = {
                "scale": float(scale),
                "cx": float(cx),
                "cy": float(cy),
                "w": float(w),
                "h": float(h),
            }
        lock_scale = float(self._preview_view_lock.get("scale", scale))
        lock_cx = float(self._preview_view_lock.get("cx", cx))
        lock_cy = float(self._preview_view_lock.get("cy", cy))
        fit_scale = float(scale)
        fit_cy = float(cy)
        avail_span_y = max(1e-6, (h - (2.0 * pad_px)) / max(1e-9, lock_scale))
        # Keep fixed zoom feel; only recenter/zoom out when clipping would occur.
        # If user manually zoomed with wheel, preserve user zoom/center.
        if not bool(self._preview_manual_zoom):
            if span_y <= avail_span_y:
                lock_cy = float(fit_cy)
            else:
                lock_scale = float(min(lock_scale, fit_scale))
                lock_cy = float(fit_cy)
        self._preview_view_lock["scale"] = float(lock_scale)
        self._preview_view_lock["cx"] = float(lock_cx)
        self._preview_view_lock["cy"] = float(lock_cy)
        scale = float(lock_scale)
        cx = float(lock_cx)
        cy = float(lock_cy)

        def map_nm(x_nm: float, y_nm: float):
            px = (0.5 * w) + ((x_nm - cx) * scale)
            py = (0.5 * h) - ((y_nm - cy) * scale)
            return int(round(px)), int(round(py))
        self._preview_map_cache = {"w": float(w), "h": float(h), "cx": float(cx), "cy": float(cy), "scale": float(scale)}
        self._preview_line_screen = {}
        self._preview_corner_screen = []
        self._preview_point_screen = {}

        def _annotate_line(line_pts: Tuple[np.ndarray, np.ndarray], title: str):
            p0 = np.array(line_pts[0], dtype=float)
            p1 = np.array(line_pts[1], dtype=float)
            left = p0 if float(p0[0]) <= float(p1[0]) else p1
            right_p = p1 if left is p0 else p0
            left_s = map_nm(float(left[0]), float(left[1]))
            right_s = map_nm(float(right_p[0]), float(right_p[1]))
            c = 0.5 * (p0 + p1)
            be = np.array(geo["be"], dtype=float)
            d_nm = math.hypot(float(c[0] - be[0]), float(c[1] - be[1]))
            left_txt = f"{d_nm:.1f}NM(B.E)"
            fm = painter.fontMetrics()
            painter.setPen(QColor("#1f2937"))
            painter.drawText(left_s[0] - fm.horizontalAdvance(left_txt) - 8, left_s[1] - 4, left_txt)
            painter.drawText(right_s[0] + 8, right_s[1] - 4, title)

        mission = geo["mission"]
        mission_pts = [map_nm(float(p[0]), float(p[1])) for p in mission]
        painter.setPen(self.preview_colors["mission"])
        for i in range(4):
            a = mission_pts[i]
            b = mission_pts[(i + 1) % 4]
            painter.drawLine(a[0], a[1], b[0], b[1])
            self._preview_corner_screen.append((float(a[0]), float(a[1])))
        painter.setPen(QColor("#111111"))
        painter.setBrush(QColor("#ffffff"))
        for c in self._preview_corner_screen:
            cx_px = int(round(float(c[0])))
            cy_px = int(round(float(c[1])))
            painter.drawRect(cx_px - 4, cy_px - 4, 8, 8)

        def _draw_nose_cone(center_nm: np.ndarray, heading_deg: float):
            hdg = float(heading_deg)
            radius_nm = 40.0
            seg = 40
            cone_pts: List[QPoint] = []
            cpx = map_nm(float(center_nm[0]), float(center_nm[1]))
            cone_pts.append(QPoint(int(cpx[0]), int(cpx[1])))
            for i in range(seg + 1):
                ang = hdg - 60.0 + (120.0 * (float(i) / float(seg)))
                ar = math.radians(float(ang))
                tip = np.array(center_nm, dtype=float) + (np.array([math.sin(ar), math.cos(ar)], dtype=float) * radius_nm)
                tp = map_nm(float(tip[0]), float(tip[1]))
                cone_pts.append(QPoint(int(tp[0]), int(tp[1])))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(135, 206, 250, 77))
            painter.drawPolygon(QPolygon(cone_pts))
        ba_map: Dict[str, np.ndarray] = {str(a): np.array(p, dtype=float) for a, p in geo["ba_points"]}
        cone_ids: List[str] = ["#1"]
        if len(self._ba_ids_preview) == 2:
            cone_ids.append("#2")
        if len(self._ba_ids_preview) >= 4:
            cone_ids.append("#3")
        for cid in cone_ids:
            p = ba_map.get(str(cid))
            if p is not None:
                hdg_i = float(self._ba_heading_override_deg.get(str(cid), float(self.ba_heading_deg.value())))
                _draw_nose_cone(p, hdg_i)

        pair_enabled = (geo.get("cap_f_pair") is not None) and (geo.get("cap_r_pair") is not None)
        pen_cfcr = painter.pen()
        pen_cfcr.setColor(QColor("#111111"))
        pen_cfcr.setWidth(2)
        pen_cfcr.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen_cfcr)
        if not pair_enabled:
            cf_s = map_nm(float(geo["cap_f_center"][0]), float(geo["cap_f_center"][1]))
            cr_s = map_nm(float(geo["cap_r_center"][0]), float(geo["cap_r_center"][1]))
            self._draw_point_nm(painter, map_nm, geo["cap_f_center"], self.preview_colors["cap"], 4, "C.F")
            self._draw_point_nm(painter, map_nm, geo["cap_r_center"], self.preview_colors["cap"], 4, "C.R")
            self._preview_point_screen["cf"] = (float(cf_s[0]), float(cf_s[1]))
            self._preview_point_screen["cr"] = (float(cr_s[0]), float(cr_s[1]))
            cf_nm = np.array(geo["cap_f_center"], dtype=float)
            cr_nm = np.array(geo["cap_r_center"], dtype=float)
            cf_cr_dist_nm = math.hypot(float(cf_nm[0] - cr_nm[0]), float(cf_nm[1] - cr_nm[1]))
            painter.drawLine(int(cf_s[0]), int(cf_s[1]), int(cr_s[0]), int(cr_s[1]))
            mid_x = int(round((float(cf_s[0]) + float(cr_s[0])) * 0.5))
            mid_y = int(round((float(cf_s[1]) + float(cr_s[1])) * 0.5))
            cfcr_txt = f"C.F-C.R: {cf_cr_dist_nm:.1f} nm"
            fm_cfcr = painter.fontMetrics()
            tw = fm_cfcr.horizontalAdvance(cfcr_txt)
            th = fm_cfcr.height()
            bx = mid_x - (tw // 2) - 6
            by = mid_y - th - 10
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 225))
            painter.drawRoundedRect(bx, by, tw + 12, th + 8, 5, 5)
            painter.setPen(QColor("#111111"))
            painter.drawText(bx + 6, by + th, cfcr_txt)
        else:
            cap_lf = np.array(geo["cap_f_pair"][0], dtype=float)
            cap_rf = np.array(geo["cap_f_pair"][1], dtype=float)
            cap_lr = np.array(geo["cap_r_pair"][0], dtype=float)
            cap_rr = np.array(geo["cap_r_pair"][1], dtype=float)
            lf_s = map_nm(float(cap_lf[0]), float(cap_lf[1]))
            rf_s = map_nm(float(cap_rf[0]), float(cap_rf[1]))
            lr_s = map_nm(float(cap_lr[0]), float(cap_lr[1]))
            rr_s = map_nm(float(cap_rr[0]), float(cap_rr[1]))
            self._draw_point_nm(painter, map_nm, cap_lf, self.preview_colors["cap"], 4, "C.F")
            self._draw_point_nm(painter, map_nm, cap_rf, self.preview_colors["cap"], 4, "C.F")
            self._draw_point_nm(painter, map_nm, cap_lr, self.preview_colors["cap"], 4, "C.R")
            self._draw_point_nm(painter, map_nm, cap_rr, self.preview_colors["cap"], 4, "C.R")
            self._preview_point_screen["cap_lf"] = (float(lf_s[0]), float(lf_s[1]))
            self._preview_point_screen["cap_rf"] = (float(rf_s[0]), float(rf_s[1]))
            self._preview_point_screen["cap_lr"] = (float(lr_s[0]), float(lr_s[1]))
            self._preview_point_screen["cap_rr"] = (float(rr_s[0]), float(rr_s[1]))
            # Backward-compatible pick keys
            self._preview_point_screen["cap_l"] = (float(lf_s[0]), float(lf_s[1]))
            self._preview_point_screen["cap_r"] = (float(rf_s[0]), float(rf_s[1]))
            cf_cr_dist_nm = math.hypot(float(cap_lf[0] - cap_lr[0]), float(cap_lf[1] - cap_lr[1]))
            painter.drawLine(int(lf_s[0]), int(lf_s[1]), int(lr_s[0]), int(lr_s[1]))
            painter.drawLine(int(rf_s[0]), int(rf_s[1]), int(rr_s[0]), int(rr_s[1]))
            self._preview_line_screen["cap_left"] = ((float(lf_s[0]), float(lf_s[1])), (float(lr_s[0]), float(lr_s[1])))
            self._preview_line_screen["cap_right"] = ((float(rf_s[0]), float(rf_s[1])), (float(rr_s[0]), float(rr_s[1])))
            cfcr_txt = f"C.F-C.R: {cf_cr_dist_nm:.1f} nm"
            fm_cfcr = painter.fontMetrics()
            tw = fm_cfcr.horizontalAdvance(cfcr_txt)
            th = fm_cfcr.height()
            mid_x = int(round((float(lf_s[0]) + float(rf_s[0]) + float(lr_s[0]) + float(rr_s[0])) * 0.25))
            mid_y = int(round((float(lf_s[1]) + float(lr_s[1])) * 0.5))
            bx = mid_x - (tw // 2) - 6
            by = mid_y - th - 10
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 225))
            painter.drawRoundedRect(bx, by, tw + 12, th + 8, 5, 5)
            painter.setPen(QColor("#111111"))
            painter.drawText(bx + 6, by + th, cfcr_txt)
        self._draw_line_nm(painter, map_nm, geo["hmrl"][0], geo["hmrl"][1], self.preview_colors["hmrl"], 2)
        hmrl_s = (map_nm(float(geo["hmrl"][0][0]), float(geo["hmrl"][0][1])), map_nm(float(geo["hmrl"][1][0]), float(geo["hmrl"][1][1])))
        self._preview_line_screen["hmrl"] = ((float(hmrl_s[0][0]), float(hmrl_s[0][1])), (float(hmrl_s[1][0]), float(hmrl_s[1][1])))
        _annotate_line(geo["hmrl"], "HMRL")
        self._draw_line_nm(painter, map_nm, geo["ldez"][0], geo["ldez"][1], self.preview_colors["dez"], 2)
        ldez_s = (map_nm(float(geo["ldez"][0][0]), float(geo["ldez"][0][1])), map_nm(float(geo["ldez"][1][0]), float(geo["ldez"][1][1])))
        self._preview_line_screen["ldez"] = ((float(ldez_s[0][0]), float(ldez_s[0][1])), (float(ldez_s[1][0]), float(ldez_s[1][1])))
        _annotate_line(geo["ldez"], "INNER DEZ")
        self._draw_line_nm(painter, map_nm, geo["hdez"][0], geo["hdez"][1], self.preview_colors["dez"], 2)
        hdez_s = (map_nm(float(geo["hdez"][0][0]), float(geo["hdez"][0][1])), map_nm(float(geo["hdez"][1][0]), float(geo["hdez"][1][1])))
        self._preview_line_screen["hdez"] = ((float(hdez_s[0][0]), float(hdez_s[0][1])), (float(hdez_s[1][0]), float(hdez_s[1][1])))
        _annotate_line(geo["hdez"], "OUTER DEZ")
        self._draw_line_nm(painter, map_nm, geo["commit"][0], geo["commit"][1], self.preview_colors["commit"], 2)
        commit_s = (
            map_nm(float(geo["commit"][0][0]), float(geo["commit"][0][1])),
            map_nm(float(geo["commit"][1][0]), float(geo["commit"][1][1])),
        )
        self._preview_line_screen["commit"] = ((float(commit_s[0][0]), float(commit_s[0][1])), (float(commit_s[1][0]), float(commit_s[1][1])))
        _annotate_line(geo["commit"], "COMMIT LINE")

        if bool(self.ra_mode_radius.isChecked()):
            center = map_nm(float(geo["asset"][0]), float(geo["asset"][1]))
            rr_px = max(2, int(round(float(geo["ra_radius_nm"]) * scale)))
            painter.setPen(self.preview_colors["ra_touch"])
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center[0] - rr_px, center[1] - rr_px, rr_px * 2, rr_px * 2)
        else:
            self._draw_line_nm(painter, map_nm, geo["ra_line"][0], geo["ra_line"][1], self.preview_colors["ra_touch"], 2)

        self._draw_point_nm(painter, map_nm, geo["be"], self.preview_colors["be"], 5, "B.E")
        be_s = map_nm(float(geo["be"][0]), float(geo["be"][1]))
        self._preview_point_screen["be"] = (float(be_s[0]), float(be_s[1]))
        self._draw_point_nm(painter, map_nm, geo["asset"], self.preview_colors["asset"], 5, "ASSET")
        self._preview_points_nm = {}
        for aid, p in geo["ba_points"]:
            self._preview_points_nm[str(aid)] = np.array(p, dtype=float)
            hdg = float(self._ba_heading_override_deg.get(str(aid), float(self.ba_heading_deg.value())))
            self._draw_aircraft_arrow_nm(painter, map_nm, p, self.preview_colors["ba"], hdg, str(aid))
        for aid, p in geo["ra_points"]:
            self._preview_points_nm[str(aid)] = np.array(p, dtype=float)
            self._draw_aircraft_arrow_nm(painter, map_nm, p, self.preview_colors["ra"], float(self.ra_heading_deg.value()), str(aid))

        if hasattr(self, "btn_flip_squad") and (self.btn_flip_squad is not None):
            if self._selected_ba_squad:
                pts2 = []
                for sid in self._selected_ba_squad:
                    p = self._preview_points_nm.get(str(sid))
                    if p is not None:
                        pts2.append(np.array(p, dtype=float))
                self._selected_ba_squad_center_nm = np.mean(np.vstack(pts2), axis=0) if pts2 else None
            if self._selected_ba_squad and (self._selected_ba_squad_center_nm is not None):
                cs = map_nm(float(self._selected_ba_squad_center_nm[0]), float(self._selected_ba_squad_center_nm[1]))
                bx = int(round(float(cs[0]) + 18.0))
                by = int(round(float(cs[1]) - 28.0))
                bx = max(4, min(w - self.btn_flip_squad.width() - 4, bx))
                by = max(4, min(h - self.btn_flip_squad.height() - 4, by))
                self.btn_flip_squad.move(bx, by)
                self.btn_flip_squad.show()
                self.btn_flip_squad.raise_()
            else:
                self.btn_flip_squad.hide()

        if self._is_individual_drag_enabled():
            self._draw_preview_metric_boxes(painter, h)
        if self._preview_drag_hint_text:
            fm_hint = painter.fontMetrics()
            tw = fm_hint.horizontalAdvance(self._preview_drag_hint_text)
            th = fm_hint.height()
            hx = 12
            hy = 12
            if self._preview_drag_hint_pos is not None:
                hx = int(round(float(self._preview_drag_hint_pos[0]) + 14.0))
                hy = int(round(float(self._preview_drag_hint_pos[1]) + 14.0))
            hx = max(8, min(w - tw - 18, hx))
            hy = max(th + 8, min(h - 8, hy))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 225))
            painter.drawRoundedRect(hx - 8, hy - th, tw + 16, th + 8, 6, 6)
            painter.setPen(QColor("#111111"))
            painter.drawText(hx, hy, self._preview_drag_hint_text)
        painter.end()
        self.preview_label.setPixmap(pix)

    def _on_asset_same_toggled(self, checked: bool):
        en = not bool(checked)
        self.asset_bearing_deg.setEnabled(en)
        self.asset_range_nm.setEnabled(en)
        self._update_preview()

    def _on_ra_mode_changed(self):
        use_radius = bool(self.ra_mode_radius.isChecked())
        self.ra_zone_radius_nm.setEnabled(use_radius)
        self.ra_line_forward_nm.setEnabled(not use_radius)
        self._update_preview()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_preview()
        QTimer.singleShot(0, self._update_preview)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_preview()

    def selection(self):
        ra_zone_mode = "radius" if bool(self.ra_mode_radius.isChecked()) else "line"
        return (
            float(self._be_bearing_deg_value),
            float(self._be_range_nm_value),
            float(self.asset_bearing_deg.value()),
            float(self.asset_range_nm.value()),
            bool(self.chk_asset_same_as_be.isChecked()),
            float(self.ba_from_asset_nm.value()),
            float(self.ra_from_asset_nm.value()),
            float(self.ba_heading_deg.value()),
            float(self.ra_heading_deg.value()),
            float(self.ra_zone_radius_nm.value()),
            float(self.ra_line_forward_nm.value()),
            ra_zone_mode,
            float(self.mission_width_nm.value()),
            float(self.mission_height_nm.value()),
            float(self.cap_front_nm.value()),
            float(self.cap_rear_nm.value()),
            float(self.hmrl_nm.value()),
            float(self.ldez_nm.value()),
            float(self.hdez_nm.value()),
            float(self.commit_nm.value()),
            bool(self._cap_front_pair_enabled),
            float(self._cap_front_pair_half_sep_nm),
            dict(self._ba_member_offsets_nm),
            dict(self._ra_member_offsets_nm),
            bool(self._drag_changed),
            dict(self._ba_heading_override_deg),
        )


G_CLAMP_STEP = 0.1


def quantize_g_01(g_cmd: float, min_g: float = 1.0, max_g: float = 9.0) -> float:
    g = float(min(max_g, max(min_g, float(g_cmd))))
    return float(round(g, 1))


def quantize_bank_deg(bank_cmd: float, min_bank: float = 0.0, max_bank: float = 180.0) -> float:
    b = float(min(max_bank, max(min_bank, float(bank_cmd))))
    return float(round(b, 1))


def g_candidates_01(g_cmd: float, min_g: float = 1.0):
    gi0 = int(round(quantize_g_01(g_cmd, min_g=min_g) * 10))
    gi_min = int(round(min_g * 10))
    for gi in range(gi0, gi_min - 1, -1):
        yield gi / 10.0


def find_max_feasible_g(ps_db, power, cas_kt, alt_ft, g_cmd, pitch_deg, turn_dir):
    # Canonical max-feasible G search: downward 0.1g scan at fixed CAS/ALT/POWER.
    # pitch/turn_dir are part of the API contract for call-site consistency.
    _ = pitch_deg
    _ = turn_dir
    g_cmd_c = quantize_g_01(g_cmd, min_g=1.0, max_g=9.0)
    attempts = []
    for g_try in g_candidates_01(g_cmd_c, 1.0):
        ps = ps_db.lookup_ps(power, cas_kt, g_try, alt_ft)
        dbg = ps_db.last_lookup_debug() if hasattr(ps_db, "last_lookup_debug") else None
        if isinstance(dbg, dict) and len(attempts) < 5:
            attempts.append(
                {
                    "g_try": float(g_try),
                    "ps_final": float(ps) if not np.isnan(ps) else np.nan,
                    "g_left_10": float(dbg.get("10k", {}).get("g_left", np.nan)),
                    "g_right_10": float(dbg.get("10k", {}).get("g_right", np.nan)),
                    "ps_left_10": float(dbg.get("10k", {}).get("ps_left", np.nan)),
                    "ps_right_10": float(dbg.get("10k", {}).get("ps_right", np.nan)),
                    "g_left_20": float(dbg.get("20k", {}).get("g_left", np.nan)),
                    "g_right_20": float(dbg.get("20k", {}).get("g_right", np.nan)),
                    "ps_left_20": float(dbg.get("20k", {}).get("ps_left", np.nan)),
                    "ps_right_20": float(dbg.get("20k", {}).get("ps_right", np.nan)),
                }
            )
        if not np.isnan(ps):
            clamped = g_try < (g_cmd_c - 1e-9)
            reason = "ok" if not clamped else f"G limited: {g_cmd_c:.1f} -> {g_try:.1f}"
            return float(g_try), float(ps), bool(clamped), reason, attempts
    return None, np.nan, True, "No feasible turn G at this CAS/ALT/POWER", attempts

EMBEDDED_KR_FONT_B64 = ""


def compute_turn_radius_nm_from_tas_tanbank(tas_kt: float, tan_bank: float) -> float:
    if abs(tan_bank) < 1e-12:
        return float("inf")
    return (1.475e-5 * tas_kt * tas_kt) / tan_bank


def compute_turn_radius_ft_from_tas_n(tas_kt: float, n_load: float) -> float:
    n = max(float(n_load), 1.0)
    tan_bank = math.sqrt(max(n * n - 1.0, 0.0))
    r_nm = compute_turn_radius_nm_from_tas_tanbank(tas_kt, tan_bank)
    return r_nm * NM_TO_FT


def run_sanity_tests():
    tas = 350.0
    n = 2.0
    r_ft = compute_turn_radius_ft_from_tas_n(tas, n)
    ok = abs(r_ft - 6257.0) <= 150.0
    print(f"RADIUS TEST (TAS=350, n=2): R_ft={r_ft:.1f} expected~6257 : {'PASS' if ok else 'FAIL'}")
    got = [float(v) for _, v in zip(range(12), g_candidates_01(7.0, 1.0))]
    expected = [7.0, 6.9, 6.8, 6.7, 6.6, 6.5, 6.4, 6.3, 6.2, 6.1, 6.0, 5.9]
    if len(got) != len(expected) or any(abs(a - b) > 1e-9 for a, b in zip(got, expected)):
        raise RuntimeError(f"G clamp generator test failed: {got}")
    print("G clamp generator test: PASS")


def excel_round(value: float, digits: int = 0) -> float:
    factor = 10 ** digits
    scaled = value * factor
    if scaled >= 0:
        return math.floor(scaled + 0.5) / factor
    return math.ceil(scaled - 0.5) / factor


def to_float(v) -> float:
    if v is None:
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    s = str(v).strip()
    if s == "" or s.lower() in {"nan", "none"}:
        return np.nan
    s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


def clean_text(v) -> str:
    if v is None:
        return ""
    return str(v).strip().lower()


class PsDBNPZ:
    def __init__(self, npz_path: str):
        self._last_lookup_debug = None
        blob = np.load(npz_path, allow_pickle=False)
        self.cas_keys = np.asarray(blob["cas_keys"], dtype=np.int32)
        self.g_keys = np.asarray(blob["g_keys_0p1"], dtype=np.float32)
        self.ps_layers = {
            "A": {10000: np.asarray(blob["ps_A_10k_0p1"], dtype=np.float32), 20000: np.asarray(blob["ps_A_20k_0p1"], dtype=np.float32)},
            "M": {10000: np.asarray(blob["ps_M_10k_0p1"], dtype=np.float32), 20000: np.asarray(blob["ps_M_20k_0p1"], dtype=np.float32)},
            "I": {10000: np.asarray(blob["ps_I_10k_0p1"], dtype=np.float32), 20000: np.asarray(blob["ps_I_20k_0p1"], dtype=np.float32)},
        }
        self._cas_to_idx = {int(c): i for i, c in enumerate(self.cas_keys.tolist())}
        self._g10_to_idx = {int(round(float(g) * 10)): i for i, g in enumerate(self.g_keys.tolist())}

    def _interp_layer_by_cas(self, layer: np.ndarray, g_idx: int, cas_kt: float) -> Tuple[float, Dict]:
        cas_arr = self.cas_keys.astype(np.float64)
        col = layer[:, g_idx].astype(np.float64)
        valid = ~np.isnan(col)
        if not np.any(valid):
            return np.nan, {"ok": False, "reason": "no_valid_cas"}

        v_cas = cas_arr[valid]
        v_ps = col[valid]
        cas_f = float(cas_kt)

        left_mask = v_cas <= (cas_f + 1e-9)
        right_mask = v_cas >= (cas_f - 1e-9)
        if not np.any(left_mask) and not np.any(right_mask):
            return np.nan, {"ok": False, "reason": "cas_outside_valid_range"}
        # Local one-sided hold near a valid edge (prevents 1 kt cliff like 300->299).
        # This is limited to <=10 kt to avoid broad envelope expansion.
        if not np.any(left_mask):
            ri = int(np.where(right_mask)[0][0])
            cas_r = float(v_cas[ri])
            ps_r = float(v_ps[ri])
            if abs(cas_r - cas_f) <= 10.0 + 1e-9:
                return ps_r, {"ok": True, "cas_left": cas_r, "cas_right": cas_r, "ps_left": ps_r, "ps_right": ps_r, "reason": "one_sided_right_hold"}
            return np.nan, {"ok": False, "reason": "cas_extrapolation_blocked_right"}
        if not np.any(right_mask):
            li = int(np.where(left_mask)[0][-1])
            cas_l = float(v_cas[li])
            ps_l = float(v_ps[li])
            if abs(cas_f - cas_l) <= 10.0 + 1e-9:
                return ps_l, {"ok": True, "cas_left": cas_l, "cas_right": cas_l, "ps_left": ps_l, "ps_right": ps_l, "reason": "one_sided_left_hold"}
            return np.nan, {"ok": False, "reason": "cas_extrapolation_blocked_left"}

        li = int(np.where(left_mask)[0][-1])
        ri = int(np.where(right_mask)[0][0])
        cas_l = float(v_cas[li])
        cas_r = float(v_cas[ri])
        ps_l = float(v_ps[li])
        ps_r = float(v_ps[ri])
        if ri < li:
            return np.nan, {"ok": False, "reason": "invalid_bracket_order"}
        if abs(cas_r - cas_l) <= 1e-9:
            return ps_l, {"ok": True, "cas_left": cas_l, "cas_right": cas_r, "ps_left": ps_l, "ps_right": ps_r}

        t = (cas_f - cas_l) / (cas_r - cas_l)
        if t < -1e-9 or t > 1.0 + 1e-9:
            return np.nan, {"ok": False, "reason": "cas_extrapolation_blocked"}
        ps = ps_l * (1.0 - t) + ps_r * t
        return float(ps), {"ok": True, "cas_left": cas_l, "cas_right": cas_r, "ps_left": ps_l, "ps_right": ps_r, "t": float(t)}

    def _estimate_alt_delta_from_neighbor_g(self, power_mode: str, cas_kt: float, g_idx: int) -> Optional[float]:
        """
        Estimate (ps20 - ps10) at this CAS using nearest g columns where both layers are valid.
        """
        layer10 = self.ps_layers[power_mode][10000]
        layer20 = self.ps_layers[power_mode][20000]
        n_g = layer10.shape[1]
        for d in range(1, n_g):
            for cand in (g_idx - d, g_idx + d):
                if cand < 0 or cand >= n_g:
                    continue
                p10, dbg10 = self._interp_layer_by_cas(layer10, cand, cas_kt)
                p20, dbg20 = self._interp_layer_by_cas(layer20, cand, cas_kt)
                if not np.isnan(p10) and not np.isnan(p20):
                    return float(p20 - p10)
                _ = dbg10
                _ = dbg20
        return None

    def lookup_ps(self, power_mode: str, cas_kt: float, g_val: float, alt_ft: float) -> float:
        if power_mode not in self.ps_layers:
            return np.nan
        g10 = int(round(float(g_val) * 10))
        g_idx = self._g10_to_idx.get(g10)
        if g_idx is None:
            return np.nan

        ps10, dbg10 = self._interp_layer_by_cas(self.ps_layers[power_mode][10000], g_idx, cas_kt)
        ps20, dbg20 = self._interp_layer_by_cas(self.ps_layers[power_mode][20000], g_idx, cas_kt)
        self._last_lookup_debug = {
            "cas_kt": float(cas_kt),
            "g_try": float(g10 / 10.0),
            "alt_ft": float(alt_ft),
            "10k": {"ok": not np.isnan(ps10), "g_idx": int(g_idx), "ps": ps10, **dbg10},
            "20k": {"ok": not np.isnan(ps20), "g_idx": int(g_idx), "ps": ps20, **dbg20},
        }

        # Excel-style altitude relation:
        #   ps(alt)=ps20 + (alt-20000)*(ps20-ps10)/10000
        # If one layer is missing, infer it from nearest g where both 10k/20k are valid.
        inferred = None
        if np.isnan(ps10) and np.isnan(ps20):
            return np.nan
        if np.isnan(ps10) ^ np.isnan(ps20):
            delta = self._estimate_alt_delta_from_neighbor_g(power_mode, cas_kt, g_idx)
            if delta is None:
                # Last-resort fallback: no gradient info, keep constant with altitude.
                if np.isnan(ps10):
                    ps10 = ps20
                    inferred = "ps10_from_ps20_hold"
                else:
                    ps20 = ps10
                    inferred = "ps20_from_ps10_hold"
            else:
                if np.isnan(ps10):
                    ps10 = float(ps20 - delta)
                    inferred = "ps10_from_neighbor_delta"
                else:
                    ps20 = float(ps10 + delta)
                    inferred = "ps20_from_neighbor_delta"
            self._last_lookup_debug["inferred"] = inferred

        ps = ps20 + (alt_ft - 20000.0) * (ps20 - ps10) / 10000.0
        self._last_lookup_debug["ps"] = float(ps)
        return float(ps)

    def last_lookup_debug(self):
        return self._last_lookup_debug

    def cas_in_supported_range(self, power_mode: str, cas_kt: float) -> bool:
        if power_mode not in self.ps_layers:
            return False
        if len(self.cas_keys) == 0:
            return False
        c = float(cas_kt)
        return (c >= float(np.min(self.cas_keys))) and (c <= float(np.max(self.cas_keys)))


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class PivotGLViewWidget(gl.GLViewWidget if gl is not None else object):
    TOP_ELEV_MAX = 89.5
    def __init__(
        self,
        pivot_points_provider: Callable[[], Dict[str, np.ndarray]],
        pivot_setter: Callable[[np.ndarray], None],
        click_handler: Optional[Callable[[float, float], bool]] = None,
        right_click_handler: Optional[Callable[[float, float], bool]] = None,
        right_press_handler: Optional[Callable[[float, float], bool]] = None,
        right_move_handler: Optional[Callable[[float, float], bool]] = None,
        right_release_handler: Optional[Callable[[float, float], bool]] = None,
        resize_handler: Optional[Callable[[], None]] = None,
        view_changed_handler: Optional[Callable[[], None]] = None,
        overlay_paint_handler: Optional[Callable[[QPainter], None]] = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self._pivot_points_provider = pivot_points_provider
        self._pivot_setter = pivot_setter
        self._click_handler = click_handler
        self._right_click_handler = right_click_handler
        self._right_press_handler = right_press_handler
        self._right_move_handler = right_move_handler
        self._right_release_handler = right_release_handler
        self._resize_handler = resize_handler
        self._view_changed_handler = view_changed_handler
        self._overlay_paint_handler = overlay_paint_handler
        self._right_drag_active = False
        self._right_custom_active = False
        self._right_press_pos = None
        self._right_dragged = False
        self._left_press_pos = None
        self._left_dragged = False
        # Keep only horizontal inversion; vertical follows natural drag direction.
        # (Upward drag raises view, downward drag lowers view.)
        self._orbit_x_sign = 1.0
        self._orbit_y_sign = 1.0

    def _notify_view_changed(self):
        if self._view_changed_handler is not None:
            try:
                self._view_changed_handler()
            except Exception:
                pass

    @staticmethod
    def _vec3_to_np(v: QVector3D) -> np.ndarray:
        return np.array([float(v.x()), float(v.y()), float(v.z())], dtype=float)

    def _camera_basis(self):
        cam = self._vec3_to_np(self.cameraPosition())
        center = self._vec3_to_np(self.opts["center"])
        forward = center - cam
        n = np.linalg.norm(forward)
        if n < 1e-9:
            forward = np.array([0.0, 1.0, 0.0], dtype=float)
        else:
            forward = forward / n
        up_world = np.array([0.0, 0.0, 1.0], dtype=float)
        right = np.cross(forward, up_world)
        rn = np.linalg.norm(right)
        if rn < 1e-9:
            up_world = np.array([0.0, 1.0, 0.0], dtype=float)
            right = np.cross(forward, up_world)
            rn = np.linalg.norm(right)
        right = right / max(rn, 1e-9)
        up = np.cross(right, forward)
        up = up / max(np.linalg.norm(up), 1e-9)
        return cam, forward, right, up

    def _project_point(self, p_world: np.ndarray):
        w = max(1, int(self.width()))
        h = max(1, int(self.height()))
        cam, forward, right, up = self._camera_basis()
        rel = p_world - cam
        zc = float(np.dot(rel, forward))
        if zc <= 1e-6:
            return None
        xc = float(np.dot(rel, right))
        yc = float(np.dot(rel, up))
        fov = float(self.opts.get("fov", 60.0))
        s = (h * 0.5) / max(math.tan(math.radians(fov) * 0.5), 1e-9)
        sx = (w * 0.5) + (xc * s / zc)
        sy = (h * 0.5) - (yc * s / zc)
        return np.array([sx, sy], dtype=float)

    def _ray_from_screen(self, sx: float, sy: float):
        w = max(1, int(self.width()))
        h = max(1, int(self.height()))
        cam, forward, right, up = self._camera_basis()
        nx = (float(sx) - (w * 0.5)) / (w * 0.5)
        ny = ((h * 0.5) - float(sy)) / (h * 0.5)
        fov = float(self.opts.get("fov", 60.0))
        tan_half = math.tan(math.radians(fov) * 0.5)
        aspect = float(w) / float(max(h, 1))
        ray = forward + right * (nx * tan_half * aspect) + up * (ny * tan_half)
        ray = ray / max(np.linalg.norm(ray), 1e-9)
        return cam, ray

    def _set_pivot_from_click(self, sx: float, sy: float):
        pts = self._pivot_points_provider() if self._pivot_points_provider else {}
        chosen = None
        best = float("inf")
        for _aid, p in pts.items():
            scr = self._project_point(p)
            if scr is None:
                continue
            d = float(np.linalg.norm(scr - np.array([sx, sy], dtype=float)))
            if d < best:
                best = d
                chosen = p
        if chosen is not None and best <= 45.0:
            pivot = chosen
        else:
            cam, ray = self._ray_from_screen(sx, sy)
            if abs(ray[2]) > 1e-9:
                t = (0.0 - cam[2]) / ray[2]
                pivot = cam + ray * t if t > 0.0 else self._vec3_to_np(self.opts["center"])
            else:
                pivot = self._vec3_to_np(self.opts["center"])
        self.opts["center"] = QVector3D(float(pivot[0]), float(pivot[1]), float(pivot[2]))
        if self._pivot_setter:
            self._pivot_setter(pivot)
        self.update()
        self._notify_view_changed()

    def mousePressEvent(self, ev):
        p = ev.position() if hasattr(ev, "position") else ev.localPos()
        if ev.button() == Qt.MouseButton.RightButton:
            if self._right_press_handler is not None:
                try:
                    if bool(self._right_press_handler(float(p.x()), float(p.y()))):
                        self._right_custom_active = True
                        self._right_drag_active = False
                        self._right_press_pos = p
                        self._right_dragged = False
                        ev.accept()
                        return
                except Exception:
                    pass
            self._right_custom_active = False
            self._right_drag_active = True
            self._right_press_pos = p
            self._right_dragged = False
            self.mousePos = p
            ev.accept()
            return
        if ev.button() == Qt.MouseButton.LeftButton:
            self._left_press_pos = p
            self._left_dragged = False
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        p = ev.position() if hasattr(ev, "position") else ev.localPos()
        if self._right_custom_active and (ev.buttons() & Qt.MouseButton.RightButton):
            handled = False
            if self._right_move_handler is not None:
                try:
                    handled = bool(self._right_move_handler(float(p.x()), float(p.y())))
                except Exception:
                    handled = False
            if self._right_press_pos is not None and (p - self._right_press_pos).manhattanLength() > 3:
                self._right_dragged = True
            if handled:
                ev.accept()
                return
        if self._right_drag_active and (ev.buttons() & Qt.MouseButton.RightButton):
            if not hasattr(self, "mousePos"):
                self.mousePos = p
            diff = p - self.mousePos
            self.mousePos = p
            cam = self._vec3_to_np(self.cameraPosition())
            center_np = self._vec3_to_np(self.opts["center"])
            _, _, right, up = self._camera_basis()
            view_h = max(1.0, float(self.height()))
            fov = float(self.opts.get("fov", 60.0))
            cam_dist = float(np.linalg.norm(center_np - cam))
            world_per_px = (2.0 * cam_dist * math.tan(math.radians(fov) * 0.5)) / view_h
            delta_world = (-float(diff.x()) * world_per_px) * right + (float(diff.y()) * world_per_px) * up
            new_center = center_np + delta_world
            self.opts["center"] = QVector3D(float(new_center[0]), float(new_center[1]), float(new_center[2]))
            self.update()
            self._notify_view_changed()
            if self._right_press_pos is not None and (p - self._right_press_pos).manhattanLength() > 3:
                self._right_dragged = True
            ev.accept()
            return
        if ev.buttons() & Qt.MouseButton.LeftButton:
            if not hasattr(self, "mousePos"):
                self.mousePos = p
            diff = p - self.mousePos
            self.mousePos = p
            if ev.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.pan(float(diff.x()), float(diff.y()), 0.0, relative="view")
            else:
                # Left drag orbit: horizontal inverted, vertical normal.
                self.orbit(self._orbit_x_sign * float(diff.x()), self._orbit_y_sign * float(diff.y()))
            if self._left_press_pos is not None and (p - self._left_press_pos).manhattanLength() > 3:
                self._left_dragged = True
            self._clamp_elevation()
            self._notify_view_changed()
            ev.accept()
            return
        if self._left_press_pos is not None:
            if (p - self._left_press_pos).manhattanLength() > 3:
                self._left_dragged = True
        super().mouseMoveEvent(ev)
        self._clamp_elevation()
        self._notify_view_changed()

    def wheelEvent(self, ev):
        super().wheelEvent(ev)
        self._clamp_elevation()
        self._notify_view_changed()

    def keyPressEvent(self, ev):
        if ev.modifiers() == Qt.KeyboardModifier.NoModifier:
            k = ev.key()
            if k in (
                Qt.Key.Key_Left,
                Qt.Key.Key_Right,
                Qt.Key.Key_Up,
                Qt.Key.Key_Down,
            ):
                cam = self._vec3_to_np(self.cameraPosition())
                center_np = self._vec3_to_np(self.opts["center"])
                forward = center_np - cam
                forward[2] = 0.0
                _, _, right, _ = self._camera_basis()
                right_h = np.array(right, dtype=float)
                right_h[2] = 0.0
                f_norm = float(np.linalg.norm(forward))
                r_norm = float(np.linalg.norm(right_h))
                if f_norm <= 1e-6:
                    forward = np.array([0.0, 1.0, 0.0], dtype=float)
                else:
                    forward = forward / f_norm
                if r_norm <= 1e-6:
                    right_h = np.array([1.0, 0.0, 0.0], dtype=float)
                else:
                    right_h = right_h / r_norm
                cam_dist = float(np.linalg.norm(center_np - cam))
                step_ft = max(800.0, cam_dist * 0.06)
                delta = np.zeros(3, dtype=float)
                if k == Qt.Key.Key_Left:
                    delta = -right_h * step_ft
                elif k == Qt.Key.Key_Right:
                    delta = right_h * step_ft
                elif k == Qt.Key.Key_Up:
                    delta = forward * step_ft
                elif k == Qt.Key.Key_Down:
                    delta = -forward * step_ft
                new_center = center_np + delta
                self.opts["center"] = QVector3D(float(new_center[0]), float(new_center[1]), float(new_center[2]))
                self.update()
                self._notify_view_changed()
                ev.accept()
                return
        super().keyPressEvent(ev)

    def paintEvent(self, ev):
        super().paintEvent(ev)
        if self._overlay_paint_handler is None:
            return
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            self._overlay_paint_handler(painter)
            painter.end()
        except Exception:
            pass

    def resizeEvent(self, ev):
        try:
            super().resizeEvent(ev)
        except Exception:
            # Some drivers can raise transient GL errors during early resize.
            pass
        if self._resize_handler is not None:
            try:
                self._resize_handler()
            except Exception:
                pass

    def mouseReleaseEvent(self, ev):
        p = ev.position() if hasattr(ev, "position") else ev.localPos()
        if ev.button() == Qt.MouseButton.RightButton:
            if self._right_custom_active:
                handled = False
                if self._right_release_handler is not None:
                    try:
                        handled = bool(self._right_release_handler(float(p.x()), float(p.y())))
                    except Exception:
                        handled = False
                self._right_custom_active = False
                self._right_drag_active = False
                self._right_press_pos = None
                self._right_dragged = False
                if handled:
                    ev.accept()
                    return
            self._right_drag_active = False
            do_right_click = (self._right_press_pos is not None) and (not self._right_dragged)
            self._right_press_pos = None
            self._right_dragged = False
            if do_right_click and self._right_click_handler is not None:
                try:
                    if bool(self._right_click_handler(float(p.x()), float(p.y()))):
                        ev.accept()
                        return
                except Exception:
                    pass
            ev.accept()
            return
        if ev.button() == Qt.MouseButton.LeftButton:
            do_pick = (self._left_press_pos is not None) and (not self._left_dragged)
            self._left_press_pos = None
            self._left_dragged = False
            super().mouseReleaseEvent(ev)
            if do_pick:
                if self._click_handler is not None:
                    try:
                        if bool(self._click_handler(float(p.x()), float(p.y()))):
                            return
                    except Exception:
                        pass
                self._set_pivot_from_click(float(p.x()), float(p.y()))
            return
        super().mouseReleaseEvent(ev)

    def _clamp_elevation(self):
        elev = float(self.opts.get("elevation", 0.0))
        if elev > self.TOP_ELEV_MAX:
            self.setCameraPosition(elevation=self.TOP_ELEV_MAX)


class LosRelationMapWidget(QWidget):
    def __init__(self, on_pair_drawn: Callable[[str, str], None], parent=None):
        super().__init__(parent)
        self._on_pair_drawn = on_pair_drawn
        self._mode_key = "2vs1"
        self._active_ids: List[str] = []
        self._nodes: Dict[str, QPoint] = {}
        self._links: List[Tuple[str, str]] = []
        self._color_by_aid: Dict[str, Tuple[int, int, int]] = {}
        self._drag_src: Optional[str] = None
        self._drag_pos: Optional[QPoint] = None
        self.setMouseTracking(True)
        self.setMinimumSize(220, 180)
        self.setStyleSheet("background: rgba(255,255,255,200); border: 1px solid rgba(40,40,40,120); border-radius: 6px;")

    def set_mode_and_active(self, mode_key: str, active_ids: Iterable[str]):
        self._mode_key = str(mode_key)
        self._active_ids = [str(a) for a in active_ids]
        self._nodes = self._compute_node_positions(self._mode_key, self._active_ids, self.width(), self.height())
        self.update()

    def set_links(self, links: List[Tuple[str, str]]):
        self._links = [(str(a), str(b)) for a, b in links]
        self.update()

    def set_node_colors(self, color_by_aid: Dict[str, Tuple[int, int, int]]):
        self._color_by_aid = {str(k): (int(v[0]), int(v[1]), int(v[2])) for k, v in color_by_aid.items()}
        self.update()

    @staticmethod
    def _compute_node_positions(mode_key: str, active_ids: List[str], w: int, h: int) -> Dict[str, QPoint]:
        w = max(140, int(w))
        h = max(120, int(h))
        lcol = int(w * 0.24)
        rcol = int(w * 0.76)
        top = int(h * 0.24)
        low = int(h * 0.86)
        nodes: Dict[str, QPoint] = {}
        mk = str(mode_key).strip()
        if mk == "1vs1":
            layout = {"#1": QPoint(lcol, top), "#2": QPoint(rcol, low)}
        elif mk == "2vs1":
            c = int(w * 0.50)
            layout = {"#1": QPoint(c, top), "#2": QPoint(lcol, low), "#3": QPoint(rcol, low)}
        elif mk == "2vs2":
            layout = {"#1": QPoint(lcol, top), "#2": QPoint(lcol, low), "#3": QPoint(rcol, top), "#4": QPoint(rcol, low)}
        elif mk == "4vs2":
            ys_l = [int(h * 0.20), int(h * 0.42), int(h * 0.64), int(h * 0.86)]
            # BA left column as "(" shape.
            xl = [int(w * 0.34), int(w * 0.18), int(w * 0.18), int(w * 0.34)]
            # RA right side as ")" tendency (top/bottom slightly inward).
            ys_r = [int(h * 0.20), int(h * 0.86)]
            xr = [int(w * 0.66), int(w * 0.66)]
            layout = {
                "#1": QPoint(xl[0], ys_l[0]), "#2": QPoint(xl[1], ys_l[1]), "#3": QPoint(xl[2], ys_l[2]), "#4": QPoint(xl[3], ys_l[3]),
                "#5": QPoint(xr[0], ys_r[0]), "#6": QPoint(xr[1], ys_r[1]),
            }
        else:
            ys = [int(h * 0.20), int(h * 0.42), int(h * 0.64), int(h * 0.86)]
            # BA "(" and RA ")" shapes to reduce overlap of cross-links.
            xl = [int(w * 0.34), int(w * 0.18), int(w * 0.18), int(w * 0.34)]
            xr = [int(w * 0.66), int(w * 0.82), int(w * 0.82), int(w * 0.66)]
            layout = {
                "#1": QPoint(xl[0], ys[0]), "#2": QPoint(xl[1], ys[1]), "#3": QPoint(xl[2], ys[2]), "#4": QPoint(xl[3], ys[3]),
                "#5": QPoint(xr[0], ys[0]), "#6": QPoint(xr[1], ys[1]), "#7": QPoint(xr[2], ys[2]), "#8": QPoint(xr[3], ys[3]),
            }
        for aid in active_ids:
            if aid in layout:
                nodes[aid] = layout[aid]
        return nodes

    def _hit_node(self, p: QPoint) -> Optional[str]:
        for aid, c in self._nodes.items():
            if (p - c).manhattanLength() <= 16:
                return aid
        return None

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._nodes = self._compute_node_positions(self._mode_key, self._active_ids, self.width(), self.height())

    def mousePressEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            ev.accept()
            return
        p = ev.position().toPoint() if hasattr(ev, "position") else ev.pos()
        self._drag_src = self._hit_node(p)
        self._drag_pos = p
        self.update()
        ev.accept()

    def mouseMoveEvent(self, ev):
        p = ev.position().toPoint() if hasattr(ev, "position") else ev.pos()
        self._drag_pos = p
        if self._drag_src is not None:
            self.update()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            ev.accept()
            return
        p = ev.position().toPoint() if hasattr(ev, "position") else ev.pos()
        dst = self._hit_node(p)
        src = self._drag_src
        self._drag_src = None
        self._drag_pos = None
        self.update()
        if (src is not None) and (dst is not None) and (src != dst):
            try:
                self._on_pair_drawn(str(src), str(dst))
            except Exception:
                pass
        ev.accept()

    def paintEvent(self, ev):
        super().paintEvent(ev)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        qp.setPen(QColor(35, 35, 35, 130))
        for a, b in self._links:
            if (a not in self._nodes) or (b not in self._nodes):
                continue
            qp.drawLine(self._nodes[a], self._nodes[b])
        if (self._drag_src is not None) and (self._drag_pos is not None) and (self._drag_src in self._nodes):
            qp.setPen(QColor(20, 20, 20, 150))
            qp.drawLine(self._nodes[self._drag_src], self._drag_pos)
        for aid, c in self._nodes.items():
            qp.setPen(QColor(20, 20, 20, 200))
            rgb = self._color_by_aid.get(str(aid), (255, 255, 255))
            qp.setBrush(QColor(int(rgb[0]), int(rgb[1]), int(rgb[2]), 235))
            qp.drawEllipse(c, 10, 10)
            qp.drawText(c.x() - 12, c.y() - 14, aid)
        qp.end()

    def wheelEvent(self, ev):
        # Prevent parent 3D view zoom while interacting over relation map.
        ev.accept()


class CompassRoseWidget(QWidget):
    _compass_img_cache: Optional[QPixmap] = None
    _compass_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1.JPG")
    _compass_img_mtime: Optional[float] = None

    def __init__(self, on_cardinal_clicked: Callable[[str], None], parent=None):
        super().__init__(parent)
        self._on_cardinal_clicked = on_cardinal_clicked
        self._up_azimuth_deg = 0.0
        self.setMinimumSize(132, 132)
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent; border: none;")
        self._ensure_compass_image_loaded()

    @classmethod
    def _ensure_compass_image_loaded(cls):
        try:
            mtime = float(os.path.getmtime(cls._compass_img_path))
            if (
                isinstance(cls._compass_img_cache, QPixmap)
                and (not cls._compass_img_cache.isNull())
                and (cls._compass_img_mtime is not None)
                and abs(float(cls._compass_img_mtime) - mtime) < 1e-9
            ):
                return
            pm = QPixmap(cls._compass_img_path)
            if pm.isNull():
                cls._compass_img_cache = None
                cls._compass_img_mtime = None
                return
            cls._compass_img_cache = cls._make_white_transparent(pm)
            cls._compass_img_mtime = mtime
        except Exception:
            cls._compass_img_cache = None
            cls._compass_img_mtime = None

    @staticmethod
    def _make_white_transparent(pm: QPixmap) -> QPixmap:
        img = pm.toImage().convertToFormat(QImage.Format.Format_ARGB32)
        w = int(img.width())
        h = int(img.height())
        for y in range(h):
            for x in range(w):
                c = img.pixelColor(x, y)
                r = int(c.red())
                g = int(c.green())
                b = int(c.blue())
                # White/near-white background becomes transparent.
                if r >= 244 and g >= 244 and b >= 244:
                    c.setAlpha(0)
                elif r >= 228 and g >= 228 and b >= 228:
                    # Soften anti-aliased edge pixels.
                    c.setAlpha(max(0, 255 - ((max(r, g, b) - 228) * 10)))
                img.setPixelColor(x, y, c)
        return QPixmap.fromImage(img)

    def set_up_azimuth(self, az_deg: float):
        # World bearing currently shown at screen 12 o'clock.
        self._up_azimuth_deg = float(az_deg) % 360.0
        self.update()

    def _pick_cardinal(self, p: QPoint) -> Optional[str]:
        w = max(1, self.width())
        h = max(1, self.height())
        cx = 0.5 * float(w)
        cy = 0.5 * float(h)
        dx = float(p.x()) - cx
        dy = float(p.y()) - cy
        r = math.hypot(dx, dy)
        outer = 0.5 * min(w, h) - 10.0
        if r < max(16.0, outer * 0.35):
            return None
        ang = (math.degrees(math.atan2(dx, -dy)) + 360.0) % 360.0
        world_bearing = (float(self._up_azimuth_deg) + float(ang)) % 360.0
        cards = [("N", 0.0), ("E", 90.0), ("S", 180.0), ("W", 270.0)]
        best = min(cards, key=lambda it: min(abs(world_bearing - float(it[1])), 360.0 - abs(world_bearing - float(it[1]))))
        return str(best[0])

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            p = ev.position().toPoint() if hasattr(ev, "position") else ev.pos()
            c = self._pick_cardinal(p)
            if c is not None:
                try:
                    self._on_cardinal_clicked(c)
                except Exception:
                    pass
        ev.accept()

    def mouseMoveEvent(self, ev):
        ev.accept()

    def wheelEvent(self, ev):
        ev.accept()

    def paintEvent(self, ev):
        super().paintEvent(ev)
        self._ensure_compass_image_loaded()
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        qp.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        w = max(1, self.width())
        h = max(1, self.height())
        cx = 0.5 * float(w)
        cy = 0.5 * float(h)
        r = 0.5 * min(w, h) - 12.0

        pm = self._compass_img_cache
        if isinstance(pm, QPixmap) and (not pm.isNull()):
            side = int(max(24, min(w, h) - 40))
            qp.save()
            qp.translate(cx, cy)
            # Compass must counter-rotate against camera yaw so it behaves like a real rose.
            qp.rotate(float(-self._up_azimuth_deg))
            qp.drawPixmap(int(round(-0.5 * side)), int(round(-0.5 * side)), side, side, pm)
            qp.restore()
            # Draw upright labels outside the compass image.
            font = qp.font()
            font.setBold(True)
            font.setPointSize(max(18, int(round((font.pointSizeF() if font.pointSizeF() > 0 else 10) * 2.1))))
            qp.setFont(font)
            fm = qp.fontMetrics()

            def _draw_upright_label(card_text: str, world_bearing_deg: float):
                ang = math.radians(float(world_bearing_deg) - float(self._up_azimuth_deg))
                rad = (0.5 * float(side)) + 10.0
                lx = cx + (math.sin(ang) * rad)
                ly = cy - (math.cos(ang) * rad)
                tw = fm.horizontalAdvance(card_text)
                th = fm.height()
                x = int(round(lx - (0.5 * tw)))
                y = int(round(ly + (0.35 * th)))
                # Transparent background: stroke/shadow text only.
                qp.setPen(QColor(255, 255, 255, 230))
                qp.drawText(x + 1, y + 1, card_text)
                qp.setPen(QColor(15, 15, 15, 250))
                qp.drawText(x, y, card_text)

            _draw_upright_label("N", 0.0)
            _draw_upright_label("E", 90.0)
            _draw_upright_label("S", 180.0)
            _draw_upright_label("W", 270.0)
            qp.end()
            return

        qp.setPen(QColor(25, 25, 25, 170))
        qp.setBrush(QColor(255, 255, 255, 180))
        qp.drawEllipse(QPoint(int(round(cx)), int(round(cy))), int(round(r)), int(round(r)))

        # Cross and minor ticks for a familiar compass look.
        for deg in range(0, 360, 30):
            a = math.radians(float(deg))
            ux = math.sin(a)
            uy = -math.cos(a)
            r0 = r * (0.78 if (deg % 90 == 0) else 0.86)
            r1 = r * 0.96
            qp.setPen(QColor(35, 35, 35, 170 if (deg % 90 == 0) else 120))
            qp.drawLine(
                int(round(cx + (ux * r0))),
                int(round(cy + (uy * r0))),
                int(round(cx + (ux * r1))),
                int(round(cy + (uy * r1))),
            )

        # Cardinal labels
        qp.setPen(QColor(20, 20, 20, 230))
        font = qp.font()
        font.setBold(True)
        font.setPointSize(max(8, int(round(font.pointSizeF() or 8))))
        qp.setFont(font)
        off = r * 0.72
        qp.drawText(int(round(cx - 5)), int(round(cy - off + 4)), "N")
        qp.drawText(int(round(cx + off - 4)), int(round(cy + 4)), "E")
        qp.drawText(int(round(cx - 4)), int(round(cy + off + 4)), "S")
        qp.drawText(int(round(cx - off - 4)), int(round(cy + 4)), "W")

        # Heading needle: indicates what world direction is currently UP on screen.
        a_up = math.radians(float(self._up_azimuth_deg))
        ux = math.sin(a_up)
        uy = -math.cos(a_up)
        tip = QPoint(int(round(cx + (ux * r * 0.68))), int(round(cy + (uy * r * 0.68))))
        tail = QPoint(int(round(cx - (ux * r * 0.24))), int(round(cy - (uy * r * 0.24))))
        qp.setPen(QColor(12, 88, 200, 235))
        qp.drawLine(tail, tip)
        qp.setBrush(QColor(12, 88, 200, 235))
        qp.drawEllipse(tip, 3, 3)
        qp.setBrush(QColor(25, 25, 25, 220))
        qp.setPen(QColor(25, 25, 25, 220))
        qp.drawEllipse(QPoint(int(round(cx)), int(round(cy))), 2, 2)

        qp.end()


class AircraftControl:
    @staticmethod
    def _turn_to_code(v: str) -> str:
        s = str(v).strip().upper()
        if s in ("R/H", "RH", "R", "RIGHT", "CW"):
            return "CW"
        if s in ("L/H", "LH", "L", "LEFT", "CCW"):
            return "CCW"
        return "S"

    @staticmethod
    def _power_to_code(v: str) -> str:
        s = str(v).strip().upper()
        if s in ("IDLE", "I"):
            return "I"
        if s in ("MIL", "M"):
            return "M"
        if s in ("AB", "A"):
            return "A"
        return "M"

    def __init__(self, aid: str):
        self.aid = aid
        self.group = QGroupBox("")
        self.offset_anchor_label = "#3" if aid == "#4" else "#1"
        self.color_key_default = DEFAULT_COLOR_BY_AID.get(aid, "BLACK")
        p = COLOR_PRESETS.get(self.color_key_default, COLOR_PRESETS["BLACK"])["ui"]
        self.base_group_style = (
            "QGroupBox {"
            f" border: 1px solid {p['border']};"
            " border-radius: 5px;"
            " margin-top: 3px;"
            f" background: {p['bg']};"
            "}"
            "QGroupBox::title {"
            f" color: {p['title']};"
            " font-weight: bold;"
            " subcontrol-origin: margin;"
            " left: 8px;"
            " padding: 1px 4px;"
            "}"
            f"QLabel {{ color: {p['label']}; padding-top: 1px; padding-bottom: 1px; }}"
            f"QDoubleSpinBox {{ color: {p['spin_fg']}; background: {p['spin_bg']}; }}"
            f"QComboBox {{ color: {p['combo_fg']}; background: {p['combo_bg']}; }}"
            f"QCheckBox {{ color: {p['title']}; font-weight: bold; }}"
        )
        self.disabled_group_style = (
            "QGroupBox { border: 2px dashed #7a7a7a; border-radius: 5px; margin-top: 3px; background: #d6d6d6; }"
            "QGroupBox::title { color: #4a4a4a; font-weight: bold; subcontrol-origin: margin; left: 8px; padding: 1px 4px; }"
            "QLabel { color: #5f5f5f; padding-top: 1px; padding-bottom: 1px; }"
            "QDoubleSpinBox { color: #6a6a6a; background: #cfcfcf; }"
            "QComboBox { color: #6a6a6a; background: #cfcfcf; }"
            "QCheckBox { color: #2f2f2f; font-weight: bold; }"
        )
        self.group.setStyleSheet(self.base_group_style)
        v = QVBoxLayout(self.group)
        v.setContentsMargins(2, 2, 2, 2)
        v.setSpacing(3)

        self.color_combo = QComboBox()
        for ck in COLOR_ORDER:
            self.color_combo.addItem(str(COLOR_PRESETS[ck]["label"]), ck)
        idx_color = self.color_combo.findData(self.color_key_default)
        if idx_color >= 0:
            self.color_combo.setCurrentIndex(idx_color)
        self.header_label = QLabel(f"AIRCRAFT {aid}")
        self.header_label.setStyleSheet("font-size: 9pt; font-weight: 700;")
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(4)
        self.header_row = header_row
        header_row.addWidget(self.header_label, 0, Qt.AlignmentFlag.AlignLeft)
        header_row.addStretch(1)
        header_row.addWidget(QLabel("COLOR"), 0, Qt.AlignmentFlag.AlignRight)
        header_row.addWidget(self.color_combo, 0, Qt.AlignmentFlag.AlignRight)
        v.addLayout(header_row)
        self.color_combo.currentIndexChanged.connect(self._on_color_changed)

        self.lock_note = QLabel("")
        self.lock_note.setStyleSheet("font-size: 8pt; color: #888;")
        self.lock_note.setVisible(False)
        self.offset_lock_note = QLabel("")
        self.offset_lock_note.setStyleSheet("font-size: 8pt; color: #888;")
        self.offset_lock_note.setVisible(False)

        self.init_state_group = QGroupBox("Initial State (Step 0 only)")
        init_state_grid = QGridLayout(self.init_state_group)
        self.init_state_grid = init_state_grid
        init_state_grid.setContentsMargins(4, 16, 4, 4)
        init_state_grid.setHorizontalSpacing(1)
        init_state_grid.setVerticalSpacing(4)
        init_state_grid.setColumnStretch(0, 0)
        init_state_grid.setColumnStretch(1, 0)

        self.offset_group = None
        self.offset_widgets: List[QDoubleSpinBox] = []

        self.range_nm = NoWheelDoubleSpinBox()
        self.range_nm.setDecimals(1)
        self.range_nm.setRange(0.0, 200.0)
        default_range_nm = {"#1": 0.0, "#2": 2.0, "#3": 20.0, "#4": 2.0, "#5": 2.0, "#6": 2.0, "#7": 2.0, "#8": 2.0}
        self.range_nm.setValue(float(default_range_nm.get(aid, 2.0)))
        self.range_nm.setSingleStep(0.1)

        self.bearing_deg = NoWheelDoubleSpinBox()
        self.bearing_deg.setDecimals(0)
        self.bearing_deg.setRange(0.0, 360.0)
        default_bearing_deg = {"#1": 0.0, "#2": 90.0, "#3": 360.0, "#4": 270.0, "#5": 45.0, "#6": 135.0, "#7": 225.0, "#8": 315.0}
        self.bearing_deg.setValue(float(default_bearing_deg.get(aid, 90.0)))
        self.bearing_deg.setSingleStep(1.0)

        self.alt_ft = NoWheelDoubleSpinBox()
        self.alt_ft.setDecimals(0)
        self.alt_ft.setRange(0.0, 60000.0)
        self.alt_ft.setValue(22000.0 if aid in ("#1", "#2") else 18000.0)
        self.alt_ft.setSingleStep(100.0)

        self.hdg_deg = NoWheelDoubleSpinBox()
        self.hdg_deg.setDecimals(0)
        self.hdg_deg.setRange(0.0, 360.0)
        self.hdg_deg.setValue(180.0 if aid == "#3" else 0.0)
        self.hdg_deg.setSingleStep(1.0)

        self.cas_kt = NoWheelDoubleSpinBox()
        self.cas_kt.setDecimals(0)
        self.cas_kt.setRange(50.0, 700.0)
        self.cas_kt.setValue(400.0 if aid in ("#1", "#2") else 350.0)
        self.cas_kt.setSingleStep(10.0)
        self.mach = NoWheelDoubleSpinBox()
        self.mach.setDecimals(2)
        self.mach.setRange(0.10, 2.00)
        self.mach.setValue(0.80)
        self.mach.setSingleStep(0.01)

        for w in [self.range_nm, self.bearing_deg, self.alt_ft, self.hdg_deg, self.cas_kt, self.mach]:
            w.setButtonSymbols(QAbstractSpinBox.PlusMinus)

        if aid == "#1":
            self.init_state_group.setToolTip("#1 초기 상태는 Step 0에서만 수정할 수 있습니다.")
            init_state_grid.addWidget(QLabel("Altitude (ft)"), 0, 0)
            init_state_grid.addWidget(self.alt_ft, 0, 1)
            init_state_grid.addWidget(QLabel("HDG (deg)"), 1, 0)
            init_state_grid.addWidget(self.hdg_deg, 1, 1)
            init_state_grid.addWidget(QLabel("Airspeed (kt)"), 2, 0)
            init_state_grid.addWidget(self.cas_kt, 2, 1)
            init_state_grid.addWidget(QLabel("Mach"), 3, 0)
            init_state_grid.addWidget(self.mach, 3, 1)
        else:
            self.offset_group = QGroupBox(f"Offset from {self.offset_anchor_label} (Step 0 only)")
            offset_grid = QGridLayout(self.offset_group)
            offset_grid.setContentsMargins(4, 16, 4, 4)
            offset_grid.setHorizontalSpacing(1)
            offset_grid.setVerticalSpacing(4)
            offset_grid.setColumnStretch(0, 0)
            offset_grid.setColumnStretch(1, 0)
            if aid == "#4":
                self.offset_group.setToolTip("#4 오프셋: #3 기준 초기 위치를 설정합니다 (0=앞, 90=오른쪽, 180=뒤, 270=왼쪽).")
            else:
                self.offset_group.setToolTip("#2/#3/#5~#8 오프셋: #1 기준 초기 위치를 설정합니다 (0=북쪽, 90=동쪽).")
            offset_grid.addWidget(QLabel("Offset (NM)"), 0, 0)
            offset_grid.addWidget(self.range_nm, 0, 1)
            offset_grid.addWidget(QLabel("Rel Bearing (deg)" if aid == "#4" else "Bearing (deg)"), 1, 0)
            offset_grid.addWidget(self.bearing_deg, 1, 1)
            self.offset_widgets = [self.range_nm, self.bearing_deg]

            self.init_state_group.setToolTip("#2~#8 초기 상태는 Step 0에서만 수정할 수 있습니다 (고도/방위/속도).")
            init_state_grid.addWidget(QLabel("Altitude (ft)"), 0, 0)
            init_state_grid.addWidget(self.alt_ft, 0, 1)
            init_state_grid.addWidget(QLabel("HDG (deg)"), 1, 0)
            init_state_grid.addWidget(self.hdg_deg, 1, 1)
            init_state_grid.addWidget(QLabel("Airspeed (kt)"), 2, 0)
            init_state_grid.addWidget(self.cas_kt, 2, 1)
            init_state_grid.addWidget(QLabel("Mach"), 3, 0)
            init_state_grid.addWidget(self.mach, 3, 1)

        self.hold_speed_chk = QCheckBox("Hold Speed")
        self.hold_speed_chk.setStyleSheet("font-size: 8pt;")
        self.hold_speed_chk.setToolTip("Step 진행 중 이 항공기의 CAS를 고정합니다.")
        init_state_grid.addWidget(self.hold_speed_chk, 4, 0, 1, 2)

        self.cmd_group = QGroupBox("Command (Current step)")
        cmd_grid = QGridLayout(self.cmd_group)
        cmd_grid.setContentsMargins(4, 16, 4, 4)
        cmd_grid.setHorizontalSpacing(2)
        cmd_grid.setVerticalSpacing(4)
        cmd_grid.setColumnStretch(0, 0)
        cmd_grid.setColumnStretch(1, 1)
        cmd_grid.setColumnStretch(2, 0)
        cmd_grid.setColumnStretch(3, 1)
        cmd_grid.setColumnStretch(4, 0)
        cmd_grid.setColumnStretch(5, 1)

        self.turn = QComboBox()
        self.turn.addItem("S", "S")
        self.turn.addItem("R/H", "CW")
        self.turn.addItem("L/H", "CCW")
        self.turn.setCurrentIndex(0)

        self.power = QComboBox()
        self.power.addItem("IDLE", "I")
        self.power.addItem("MIL", "M")
        self.power.addItem("AB", "A")
        self.power.setCurrentIndex(1)

        self.g_cmd = NoWheelDoubleSpinBox()
        self.g_cmd.setObjectName(f"cmd_g_spin_{aid.replace('#', '')}")
        self.g_cmd.setDecimals(1)
        self.g_cmd.setSingleStep(0.1)
        self.g_cmd.setRange(0.5, 9.0)
        self.g_cmd.setValue(1.0)
        self.g_cmd.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.g_cmd.setToolTip("PS 한계를 넘는 기동이면 가용 G로 자동 조절됩니다.")
        self.g_cmd.editingFinished.connect(self._snap_g_cmd_to_01)
        self.g_max_chk = QCheckBox("MAX G")
        self.g_max_chk.setChecked(False)
        self.g_max_chk.setToolTip("현재 속도/고도/출력 기준 PS 가용 최대 G를 자동 적용합니다.")

        self.pitch_deg = NoWheelDoubleSpinBox()
        self.pitch_deg.setDecimals(1)
        self.pitch_deg.setSingleStep(1.0)
        self.pitch_deg.setRange(-9999.0, 9999.0)
        self.pitch_deg.setValue(0.0)
        self.pitch_deg.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.pitch_deg.setReadOnly(False)
        self.pitch_deg.setToolTip("Pull Up에서 직접 Pitch를 입력하면 Bank와 자동 연동됩니다.")
        self._pitch_user_set = False
        self._pitch_auto_updating = False
        self.pitch_deg.valueChanged.connect(self._on_pitch_value_changed)
        self.pitch_hold_chk = QCheckBox("Pitch Hold")
        self.pitch_hold_chk.setChecked(False)
        self.pitch_hold_chk.setToolTip("체크 시 입력한 Pitch(상승/강하각)를 고정하고 G에 맞춰 Bank를 자동 계산합니다.")

        self.bank_deg = NoWheelDoubleSpinBox()
        self.bank_deg.setDecimals(0)
        self.bank_deg.setSingleStep(1.0)
        self.bank_deg.setRange(0.0, 180.0)
        self.bank_deg.setValue(0.0)
        self.bank_deg.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self._bank_user_set = False
        self._bank_auto_updating = False
        self.bank_deg.valueChanged.connect(self._on_bank_value_changed)
        self.pull_up_chk = QCheckBox("Pull Up")
        self.pull_down_chk = QCheckBox("Pull Down")
        self.level_chk = QCheckBox("Level")
        self.level_chk.setChecked(True)
        self.pull_up_chk.setToolTip("상승 기동을 위해 양의 수직 하중을 사용하여 pitch를 증가시킵니다.")
        self.pull_down_chk.setToolTip("강하 기동을 위해 음의 수직 하중을 사용하여 pitch를 감소시킵니다.")
        self.level_chk.setToolTip("현재 pitch를 0도로 회복하도록 bank와 g를 자동 보정합니다.")
        self.pull_up_chk.toggled.connect(self._on_pull_up_toggled)
        self.pull_down_chk.toggled.connect(self._on_pull_down_toggled)
        self.level_chk.toggled.connect(self._on_level_toggled)

        cmd_grid.addWidget(QLabel("Turn"), 0, 0)
        cmd_grid.addWidget(self.turn, 0, 1)
        cmd_grid.addWidget(QLabel("Power"), 0, 2)
        cmd_grid.addWidget(self.power, 0, 3)
        self.bank_lbl = QLabel("Bank (deg)")
        cmd_grid.addWidget(self.bank_lbl, 2, 0)
        cmd_grid.addWidget(self.bank_deg, 2, 1)
        cmd_grid.addWidget(QLabel("G"), 1, 0)
        cmd_grid.addWidget(self.g_cmd, 1, 1)
        cmd_grid.addWidget(self.g_max_chk, 1, 2, 1, 2)
        cmd_grid.addWidget(QLabel("Pitch (deg)"), 3, 0)
        cmd_grid.addWidget(self.pitch_deg, 3, 1)
        cmd_grid.addWidget(self.pitch_hold_chk, 3, 2, 1, 2)
        self.applied_g_lbl = QLabel("Applied G: -")
        self.applied_g_lbl.setStyleSheet("font-size: 8pt; color: #555;")
        self.applied_g_lbl.setVisible(False)
        self.g_limit_lbl = QLabel("")
        self.g_limit_lbl.setStyleSheet("font-size: 8pt; color: #777;")
        self.g_limit_lbl.setVisible(False)
        cmd_grid.addWidget(self.g_limit_lbl, 4, 3, 1, 3)
        cmd_grid.addWidget(self.pull_up_chk, 5, 0)
        cmd_grid.addWidget(self.pull_down_chk, 5, 1)
        cmd_grid.addWidget(self.level_chk, 5, 2)

        self.status = QLabel("")
        self.status.setStyleSheet("font-size: 8pt; color: #666;")
        self.status.setVisible(False)
        if self.offset_group is not None:
            v.addWidget(self.offset_group)
        v.addWidget(self.init_state_group)
        v.addWidget(self.cmd_group)
        v.addWidget(self.status)
        self.use_checkbox = None
        self.use_hint_label = None
        self.disabled_badge = None

        self.initial_state_widgets = [self.alt_ft, self.hdg_deg, self.cas_kt, self.mach]
        self.initial_widgets = self.initial_state_widgets + self.offset_widgets
        self._initial_editable = True
        self._syncing_speed = False
        self.cas_kt.valueChanged.connect(self._sync_mach_from_cas)
        self.alt_ft.valueChanged.connect(self._sync_mach_from_cas)
        self.mach.valueChanged.connect(self._sync_cas_from_mach)
        self._sync_mach_from_cas()
        self._on_color_changed()

    def read_command(self) -> Dict:
        turn_code = self._turn_to_code(str(self.turn.currentData() if self.turn.currentData() is not None else self.turn.currentText()))
        power_code = self._power_to_code(str(self.power.currentData() if self.power.currentData() is not None else self.power.currentText()))
        pull_mode = self.read_pull_mode()
        pitch_hold = bool(self.pitch_hold_chk.isChecked())
        # Avoid treating display-only current pitch as command unless user explicitly uses pitch modes.
        pitch_cmd = float(self.pitch_deg.value()) if (pitch_hold or (pull_mode in {"UP", "DOWN"})) else 0.0
        return {
            "turn": turn_code,
            "power": power_code,
            "g_cmd": quantize_g_01(float(self.g_cmd.value()), min_g=1.0, max_g=9.0),
            "g_use_max": bool(self.g_max_chk.isChecked()),
            "pitch_deg": pitch_cmd,
            "pitch_hold": pitch_hold,
            "pitch_user_set": bool(self._pitch_user_set),
            "bank_deg": quantize_bank_deg(float(self.bank_deg.value()), min_bank=0.0, max_bank=180.0),
            "bank_user_set": bool(self._bank_user_set),
            "pull_mode": pull_mode,
            "level_hold": bool(self.level_chk.isChecked()),
        }

    def read_hold_speed(self) -> bool:
        return bool(self.hold_speed_chk.isChecked())

    def set_hold_speed(self, checked: bool):
        self.hold_speed_chk.blockSignals(True)
        self.hold_speed_chk.setChecked(bool(checked))
        self.hold_speed_chk.blockSignals(False)

    def set_command(self, cmd: Dict):
        self.turn.blockSignals(True)
        self.power.blockSignals(True)
        self.g_cmd.blockSignals(True)
        self.g_max_chk.blockSignals(True)
        self.pitch_deg.blockSignals(True)
        self.pitch_hold_chk.blockSignals(True)
        self.bank_deg.blockSignals(True)
        self.pull_up_chk.blockSignals(True)
        self.pull_down_chk.blockSignals(True)
        self.level_chk.blockSignals(True)
        try:
            turn_code = self._turn_to_code(str(cmd.get("turn", "S")))
            power_code = self._power_to_code(str(cmd.get("power", "M")))
            idx_turn = self.turn.findData(turn_code)
            if idx_turn >= 0:
                self.turn.setCurrentIndex(idx_turn)
            idx_power = self.power.findData(power_code)
            if idx_power >= 0:
                self.power.setCurrentIndex(idx_power)
            # Reset stale per-step G cap before loading saved command value.
            # (Without this, previous-step max range may silently clip incoming g_cmd.)
            self.g_cmd.setRange(0.5, 9.0)
            self.g_cmd.setValue(quantize_g_01(float(cmd.get("g_cmd", self.g_cmd.value())), min_g=1.0, max_g=9.0))
            self.g_max_chk.setChecked(bool(cmd.get("g_use_max", False)))
            self.pitch_deg.setValue(float(self._display_pitch_deg(cmd.get("pitch_deg", self.pitch_deg.value()))))
            self._pitch_user_set = bool(cmd.get("pitch_user_set", False))
            self.pitch_hold_chk.setChecked(bool(cmd.get("pitch_hold", False)))
            bank_v = quantize_bank_deg(float(cmd.get("bank_deg", self.bank_deg.value())), min_bank=0.0, max_bank=180.0)
            self.bank_deg.setValue(bank_v)
            self._bank_user_set = bool(cmd.get("bank_user_set", abs(bank_v) > 1e-9))
            pm = str(cmd.get("pull_mode", "NONE")).upper()
            self.pull_up_chk.setChecked(pm == "UP")
            self.pull_down_chk.setChecked(pm == "DOWN")
            self.level_chk.setChecked(bool(cmd.get("level_hold", True)))
        finally:
            self.turn.blockSignals(False)
            self.power.blockSignals(False)
            self.g_cmd.blockSignals(False)
            self.g_max_chk.blockSignals(False)
            self.pitch_deg.blockSignals(False)
            self.pitch_hold_chk.blockSignals(False)
            self.bank_deg.blockSignals(False)
            self.pull_up_chk.blockSignals(False)
            self.pull_down_chk.blockSignals(False)
            self.level_chk.blockSignals(False)

    def _snap_g_cmd_to_01(self):
        q = quantize_g_01(float(self.g_cmd.value()), min_g=1.0, max_g=9.0)
        self.g_cmd.blockSignals(True)
        self.g_cmd.setValue(q)
        self.g_cmd.blockSignals(False)

    def _on_bank_value_changed(self, _v: float):
        if bool(self._bank_auto_updating):
            return
        self._bank_user_set = True
        # Bank is user-authored; pitch should be derived automatically from bank.
        self._pitch_user_set = False

    def _on_pitch_value_changed(self, _v: float):
        if bool(self._pitch_auto_updating):
            return
        self._pitch_user_set = True
        # Pitch is user-authored; bank should be derived automatically from pitch.
        self._bank_user_set = False

    def set_bank_from_auto(self, bank_deg: float):
        b = quantize_bank_deg(float(bank_deg), min_bank=0.0, max_bank=180.0)
        self._bank_auto_updating = True
        self.bank_deg.blockSignals(True)
        try:
            self.bank_deg.setValue(b)
            self._bank_user_set = False
        finally:
            self.bank_deg.blockSignals(False)
            self._bank_auto_updating = False

    def set_pitch_from_auto(self, pitch_deg: float):
        p = float(pitch_deg)
        if np.isnan(p) or np.isinf(p):
            p = 0.0
        self._pitch_auto_updating = True
        self.pitch_deg.blockSignals(True)
        try:
            self.pitch_deg.setValue(p)
            self._pitch_user_set = False
        finally:
            self.pitch_deg.blockSignals(False)
            self._pitch_auto_updating = False

    def has_user_bank_input(self) -> bool:
        return bool(self._bank_user_set)

    def has_user_pitch_input(self) -> bool:
        return bool(self._pitch_user_set)

    def set_bank_input_highlight(self, enabled: bool):
        if bool(enabled):
            self.bank_lbl.setStyleSheet("font-size: 8pt; color: #9a3a00; font-weight: 700;")
            self.bank_deg.setStyleSheet("border: 2px solid #d46f00; background: #fff4e6;")
        else:
            self.bank_lbl.setStyleSheet("")
            self.bank_deg.setStyleSheet("")

    def read_pull_mode(self) -> str:
        if bool(self.pull_up_chk.isChecked()):
            return "UP"
        if bool(self.pull_down_chk.isChecked()):
            return "DOWN"
        return "NONE"

    def _on_pull_up_toggled(self, checked: bool):
        if bool(checked):
            self.pull_down_chk.blockSignals(True)
            self.level_chk.blockSignals(True)
            self.pull_down_chk.setChecked(False)
            self.level_chk.setChecked(False)
            self.pull_down_chk.blockSignals(False)
            self.level_chk.blockSignals(False)

    def _on_pull_down_toggled(self, checked: bool):
        if bool(checked):
            self.pull_up_chk.blockSignals(True)
            self.level_chk.blockSignals(True)
            self.pull_up_chk.setChecked(False)
            self.level_chk.setChecked(False)
            self.pull_up_chk.blockSignals(False)
            self.level_chk.blockSignals(False)

    def _on_level_toggled(self, checked: bool):
        if bool(checked):
            self.pull_up_chk.blockSignals(True)
            self.pull_down_chk.blockSignals(True)
            self.pull_up_chk.setChecked(False)
            self.pull_down_chk.setChecked(False)
            self.pull_up_chk.blockSignals(False)
            self.pull_down_chk.blockSignals(False)
            # Reset manual-bank intent when user explicitly selects LEVEL.
            # If user edits bank again after this, intent will be re-armed.
            self._bank_user_set = False

    def set_pitch_display(self, pitch_deg: float):
        self.set_pitch_from_auto(float(self._display_pitch_deg(pitch_deg)))

    @staticmethod
    def _display_pitch_deg(pitch_deg: float) -> float:
        # Fold loop pitch to pilot-friendly display range [-90, +90].
        p = float(pitch_deg)
        if np.isnan(p) or np.isinf(p):
            return 0.0
        disp = math.degrees(math.asin(math.sin(math.radians(p))))
        if abs(disp) < 1e-9:
            disp = 0.0
        return float(disp)

    @staticmethod
    def _tas_from_cas(cas_kt: float, alt_ft: float) -> float:
        return float(cas_kt) * (1.0 + 0.0142 * (float(alt_ft) / 1000.0))

    @staticmethod
    def _mach_from_tas_alt(tas_kt: float, alt_ft: float) -> float:
        tas_mps = float(tas_kt) * 0.514444
        h = max(0.0, float(alt_ft) * 0.3048)
        if h < 11000.0:
            t_k = 288.15 - 0.0065 * h
        else:
            t_k = 216.65
        a = math.sqrt(1.4 * 287.05 * max(t_k, 1.0))
        return tas_mps / max(a, 1e-6)

    @classmethod
    def _mach_from_cas_alt(cls, cas_kt: float, alt_ft: float) -> float:
        return float(cls._mach_from_tas_alt(cls._tas_from_cas(cas_kt, alt_ft), alt_ft))

    @classmethod
    def _cas_from_mach_alt(cls, mach: float, alt_ft: float) -> float:
        h = max(0.0, float(alt_ft) * 0.3048)
        if h < 11000.0:
            t_k = 288.15 - 0.0065 * h
        else:
            t_k = 216.65
        a_mps = math.sqrt(1.4 * 287.05 * max(t_k, 1.0))
        tas_kt = float(mach) * float(a_mps) / 0.514444
        scale = 1.0 + 0.0142 * (float(alt_ft) / 1000.0)
        return tas_kt / max(scale, 1e-6)

    def _sync_mach_from_cas(self, *_args):
        if self._syncing_speed:
            return
        self._syncing_speed = True
        try:
            m = float(self._mach_from_cas_alt(float(self.cas_kt.value()), float(self.alt_ft.value())))
            self.mach.setValue(max(self.mach.minimum(), min(self.mach.maximum(), m)))
        finally:
            self._syncing_speed = False

    def _sync_cas_from_mach(self, *_args):
        if self._syncing_speed:
            return
        self._syncing_speed = True
        try:
            c = float(self._cas_from_mach_alt(float(self.mach.value()), float(self.alt_ft.value())))
            self.cas_kt.setValue(max(self.cas_kt.minimum(), min(self.cas_kt.maximum(), c)))
        finally:
            self._syncing_speed = False

    def current_color_key(self) -> str:
        data = self.color_combo.currentData()
        return str(data if data is not None else self.color_key_default)

    def current_color_rgba(self) -> Tuple[float, float, float, float]:
        key = self.current_color_key()
        return tuple(COLOR_PRESETS.get(key, COLOR_PRESETS["BLACK"])["rgba"])

    def set_color_key(self, color_key: str):
        key = str(color_key).strip().upper()
        idx = self.color_combo.findData(key)
        if idx >= 0:
            self.color_combo.blockSignals(True)
            self.color_combo.setCurrentIndex(idx)
            self.color_combo.blockSignals(False)
        self._on_color_changed()

    def _on_color_changed(self, *_args):
        key = self.current_color_key()
        p = COLOR_PRESETS.get(key, COLOR_PRESETS["BLACK"])["ui"]
        self.base_group_style = (
            "QGroupBox {"
            f" border: 1px solid {p['border']};"
            " border-radius: 5px;"
            " margin-top: 3px;"
            f" background: {p['bg']};"
            "}"
            "QGroupBox::title {"
            f" color: {p['title']};"
            " font-weight: bold;"
            " subcontrol-origin: margin;"
            " left: 8px;"
            " padding: 1px 4px;"
            "}"
            f"QLabel {{ color: {p['label']}; padding-top: 1px; padding-bottom: 1px; }}"
            f"QDoubleSpinBox {{ color: {p['spin_fg']}; background: {p['spin_bg']}; }}"
            f"QComboBox {{ color: {p['combo_fg']}; background: {p['combo_bg']}; }}"
            f"QCheckBox {{ color: {p['title']}; font-weight: bold; }}"
        )
        if not (self.disabled_badge is not None and self.disabled_badge.isVisible()):
            self.group.setStyleSheet(self.base_group_style)

    def set_initial_editable(self, editable: bool):
        self._initial_editable = bool(editable)
        if self.offset_group is not None:
            self.offset_group.setVisible(bool(editable))
        for w in self.initial_widgets:
            w.setEnabled(editable)
            if editable:
                w.setStyleSheet("")
            else:
                w.setStyleSheet("color: #888; background: #f0f0f0;")
        if editable:
            self.lock_note.setVisible(False)
            self.offset_lock_note.setVisible(False)
            self.init_state_group.setTitle("Initial State (Step 0 only)")
            if self.offset_group is not None:
                self.offset_group.setTitle(f"Offset from {self.offset_anchor_label} (Step 0 only)")
        else:
            self.lock_note.setVisible(False)
            self.init_state_group.setTitle("Current State (Step > 0 Read-only)")
            if self.offset_group is not None:
                self.offset_group.setTitle(f"Offset from {self.offset_anchor_label} (Step 0 only)")

    def set_offset_anchor_label(self, anchor_aid: str):
        self.offset_anchor_label = str(anchor_aid)
        if self.offset_group is not None:
            if self._initial_editable:
                self.offset_group.setTitle(f"Offset from {self.offset_anchor_label} (Step 0 only)")
            else:
                self.offset_group.setTitle(f"Offset from {self.offset_anchor_label} (Step 0 only)")

    def set_current_state(self, cas_kt: float, alt_ft: float, hdg_deg: float):
        if self._initial_editable:
            return
        hdg_v = float(int(round(hdg_deg)) % 360)
        self.alt_ft.blockSignals(True)
        self.hdg_deg.blockSignals(True)
        self.cas_kt.blockSignals(True)
        self.mach.blockSignals(True)
        try:
            self.alt_ft.setValue(float(alt_ft))
            self.hdg_deg.setValue(hdg_v)
            self.cas_kt.setValue(float(cas_kt))
            self._sync_mach_from_cas()
        finally:
            self.alt_ft.blockSignals(False)
            self.hdg_deg.blockSignals(False)
            self.cas_kt.blockSignals(False)
            self.mach.blockSignals(False)

    def set_g_limit_indicator(self, g_user: float, g_used: float):
        self.g_limit_lbl.setText(f"LIMIT {g_user:.1f}->{g_used:.1f}")
        self.g_limit_lbl.setVisible(True)

    def clear_g_limit_indicator(self):
        self.g_limit_lbl.setText("")
        self.g_limit_lbl.setVisible(False)

    def set_applied_g(self, g_used: float):
        if np.isnan(float(g_used)):
            self.applied_g_lbl.setText("Applied G: -")
        else:
            self.applied_g_lbl.setText(f"Applied G: {float(g_used):.1f}")

    def set_participation_enabled(self, enabled: bool):
        if enabled:
            self.group.setStyleSheet(self.base_group_style)
            self.cmd_group.setEnabled(True)
            self.init_state_group.setEnabled(True)
            if self.offset_group is not None:
                self.offset_group.setEnabled(True)
        else:
            self.group.setStyleSheet(self.disabled_group_style)
            self.cmd_group.setEnabled(False)
            self.init_state_group.setEnabled(False)
            if self.offset_group is not None:
                self.offset_group.setEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self, npz_path: str, startup_mode: str = "2vs1", startup_setup: str = "DEFAULT"):
        super().__init__()
        self.setWindowTitle(f"FA-50 3D Step Simulator v{APP_VERSION}")
        self.resize(1360, 820)

        self.db = PsDBNPZ(npz_path)
        print(
            f"[PS-NPZ-0.1] loaded n_cas={len(self.db.cas_keys)} n_g={len(self.db.g_keys)} "
            f"cas=[{int(self.db.cas_keys.min())},{int(self.db.cas_keys.max())}] "
            f"g=[{float(self.db.g_keys.min()):.1f},{float(self.db.g_keys.max()):.1f}]"
        )
        try:
            g_probe, _ps_probe, _clamp_probe, _reason_probe, _attempts_probe = find_max_feasible_g(
                self.db, "M", 350.0, 15000.0, 9.0, 0.0, "CW"
            )
            print(f"[PS-NPZ] probe power=M cas=350 alt=15000 g_cmd=9.0 -> g_max={g_probe}")
        except Exception as e:
            print(f"[PS-NPZ] probe skipped: {e}")

        self.step_cmds: Dict[int, Dict] = {}
        self.hold_state_by_step: Dict[int, Dict[str, bool]] = {}
        self.state_history: List[Dict[str, Dict]] = []
        self.transition_history: List[Dict[str, Dict]] = []
        self.current_step = 0
        self.fixed_dt: Optional[float] = None

        self.top_view_enabled = False
        self.saved_camera = None
        self.camera_mode = "free"  # free | top | plan
        self.plan_view_axis_idx = 0  # 0: E->W, 1: S->N
        self.speed_lock_initial_cas = {aid: np.nan for aid in AIRCRAFT_IDS}
        self.speed_lock_initial_ps = {aid: 0.0 for aid in AIRCRAFT_IDS}
        self.lock_speed_value_by_step: Dict[int, Dict[str, float]] = {}
        self.lock_ps_value_by_step: Dict[int, Dict[str, float]] = {}
        self.warning_shown = {"impl": False, "mach": False}
        self._splitter_ratio_initialized = False
        self.aircraft_line_width_scale = 1.05
        self._left_panel_hidden = False
        self._status_panel_hidden = False
        self._left_panel_last_width = 0
        self._splitter_anim_state: Optional[Dict[str, float]] = None
        self._startup_min_left_applied = False
        self.current_mode_key = str(startup_mode)
        self.current_setup_key = str(startup_setup)
        self.hide_los_in_step_view = self.current_mode_key in {"4vs2", "4vs4"}
        self._suppress_dca_prompt = False
        self._camera_refresh_guard = False
        self.step_tail_limit = 10  # 3 | 10 | -1(infinite)
        self.step_bookmarks: Dict[int, Dict[str, object]] = {}
        self.bookmark_selected_step: Optional[int] = None
        self._panel_detach_recommend_shown: Dict[str, bool] = {"4vs2": False, "4vs4": False}
        self._auto_cmd_limit_guard = False
        self._bulk_initial_update = False
        self._left_ui_pop_dialog: Optional[QDialog] = None
        self._left_ui_popped = False
        self._left_panel_placeholder: Optional[QWidget] = None
        self.dca_ra_ui_locked = False
        self.dca_be_center_ft: Optional[np.ndarray] = None
        self.dca_be_outer_diam_ft = 6000.0
        self.dca_be_inner_diam_ft = 3000.0
        self.dca_be_default_bearing_deg = 180.0
        self.dca_be_default_range_nm = 25.0
        self.dca_asset_center_ft: Optional[np.ndarray] = None
        self.dca_asset_diam_ft = 3000.0
        self.dca_asset_default_bearing_from_be_deg = 360.0
        self.dca_asset_default_range_from_be_nm = 5.0
        self.dca_asset_same_as_be_default = False
        self.dca_ba_from_asset_nm_default = 13.0
        self.dca_ra_from_asset_nm_default = 60.0
        self.dca_ba_from_asset_user_set = False
        self.dca_ra_from_asset_user_set = False
        self.dca_ba_heading_deg_default = 360.0
        self.dca_ra_heading_deg_default = 180.0
        self.dca_ra_zone_radius_nm_default = 5.0
        self.dca_ra_line_forward_nm_default = 5.0
        self.dca_ra_zone_mode_default = "radius"
        self.dca_ra_zone_radius_nm = float(self.dca_ra_zone_radius_nm_default)
        self.dca_ra_line_forward_nm = float(self.dca_ra_line_forward_nm_default)
        self.dca_ra_zone_mode = str(self.dca_ra_zone_mode_default)
        self.dca_ra_zone_center_ft: Optional[np.ndarray] = None
        self.dca_ra_line_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_width_nm_default = 25.0
        self.dca_mission_height_nm_default = 65.0
        self.dca_mission_width_nm = float(self.dca_mission_width_nm_default)
        self.dca_mission_height_nm = float(self.dca_mission_height_nm_default)
        self.dca_mission_rect_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_diag1_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_diag2_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_front_nm_default = 13.0
        self.dca_cap_rear_nm_default = 5.0
        self.dca_cap_pair_enabled_default = False
        self.dca_cap_pair_half_sep_nm_default = 0.0
        self.dca_hmrl_nm_default = 5.0
        self.dca_ldez_nm_default = 25.0
        self.dca_hdez_nm_default = 45.0
        self.dca_commit_nm_default = 55.0
        self.dca_cap_front_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_rear_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_front_center_ft: Optional[np.ndarray] = None
        self.dca_cap_rear_center_ft: Optional[np.ndarray] = None
        self.dca_cap_front_split_centers_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_rear_split_centers_ft = np.zeros((0, 3), dtype=float)
        self.dca_hmrl_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_ldez_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_hdez_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_commit_pts_ft = np.zeros((0, 3), dtype=float)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        self.main_splitter = splitter
        root.addWidget(splitter)

        left = QScrollArea()
        self.left_scroll = left
        left.setWidgetResizable(True)
        left.setFrameShape(QFrame.Shape.NoFrame)
        left_content = QWidget()
        left.setWidget(left_content)
        self.left_panel = left_content
        fm = QFontMetrics(self.font())
        self._left_min_width = max(250, fm.horizontalAdvance("Fwd 10 Back 10 Reset Step Playback 2.0x") + 64)
        left.setMinimumWidth(self._left_min_width)
        left_content.setMinimumWidth(self._left_min_width - 8)
        left_layout = QVBoxLayout(left_content)
        self.left_layout = left_layout
        left_layout.setContentsMargins(2, 2, 2, 2)
        left_layout.setSpacing(2)
        global_group = QGroupBox("Global")
        self.global_group = global_group
        g_layout = QGridLayout(global_group)
        self.global_layout = g_layout
        g_layout.setContentsMargins(3, 3, 3, 3)
        g_layout.setHorizontalSpacing(3)
        g_layout.setVerticalSpacing(2)
        g_layout.setColumnStretch(0, 0)
        g_layout.setColumnStretch(1, 1)
        g_layout.setColumnStretch(2, 0)
        g_layout.setColumnStretch(3, 0)
        g_layout.setColumnStretch(4, 0)
        g_layout.setColumnStretch(5, 0)
        g_layout.setColumnStretch(6, 0)

        self.step_label = QLabel("step: 0")
        self.step_label.setVisible(False)

        self.btn_guide = QPushButton("GUIDE")
        self.btn_guide.setStyleSheet("font-size: 8pt; background:#f2f2f2; color:#111;")
        self.btn_guide.setFixedHeight(20)
        self.btn_guide.setToolTip("사용자 가이드를 엽니다.")
        g_layout.addWidget(self.btn_guide, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_setup_popup = QPushButton("Setup")
        self.btn_setup_popup.setStyleSheet("font-size: 8pt; background:#f2f2f2; color:#111;")
        self.btn_setup_popup.setFixedHeight(20)
        self.btn_setup_popup.setToolTip("편대/초기 setup을 다시 선택합니다.")
        g_layout.addWidget(self.btn_setup_popup, 0, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        self.btn_global_popout = QPushButton("패널 분리")
        self.btn_global_popout.setStyleSheet("font-size: 8pt; background:#f2f2f2; color:#111;")
        self.btn_global_popout.setFixedHeight(20)
        self.btn_global_popout.setToolTip("좌측 전체 UI 패널을 별도 창으로 분리/복귀합니다.")

        self.step_big_label = QLabel("STEP: 0")
        self.step_big_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.step_big_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_big_label.setToolTip("현재 step 번호입니다.")
        g_layout.addWidget(self.step_big_label, 0, 2, 1, 4)
        g_layout.addWidget(self.btn_global_popout, 0, 6, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        self.dt_sec = NoWheelDoubleSpinBox()
        self.dt_sec.setStyleSheet("font-size: 8pt;")
        self.dt_sec.setDecimals(0)
        self.dt_sec.setRange(1.0, 5.0)
        self.dt_sec.setValue(3.0)
        self.dt_sec.setSingleStep(1.0)
        self.dt_sec.setButtonSymbols(QAbstractSpinBox.PlusMinus)
        self.dt_sec.setToolTip("한 step의 시간(초)입니다.")
        g_layout.addWidget(QLabel("Step (sec)"), 1, 0)
        g_layout.addWidget(self.dt_sec, 1, 1)

        self.view_mode = QComboBox()
        self.view_mode.setStyleSheet(
            "QComboBox { font-size: 8pt; background: #ffffff; color: #111111; }"
            "QComboBox QAbstractItemView { background: #ffffff; color: #111111; selection-background-color: #dbeafe; selection-color: #111111; }"
        )
        self.view_mode.addItems(["Step View", "Overview View"])
        self.view_mode.setToolTip("Step View 또는 Overview View를 선택합니다.")
        g_layout.addWidget(QLabel("View"), 1, 3)
        g_layout.addWidget(self.view_mode, 1, 4)

        self.chk_speed_lock = QCheckBox("HOLD SPEED (lock the selected speed while stepping)")
        self.chk_speed_lock.setObjectName("chkHoldSpeedLock")
        self.chk_speed_lock.setToolTip("체크하면 step 진행 중 속도를 고정합니다.")
        self.chk_speed_lock.setStyleSheet("font-size: 8pt;")
        self.chk_speed_lock.setToolTip("체크하면 step 진행 중 속도를 고정합니다.")

        self.chk_show_los = QCheckBox("Show LOS")
        self.chk_show_los.setObjectName("chkShowLos")
        self.chk_show_los.setStyleSheet("font-size: 8pt;")
        self.chk_show_los.setChecked(True)
        self.chk_show_los.setToolTip("LOS 선과 라벨을 표시합니다.")
        g_layout.addWidget(self.chk_show_los, 1, 2)
        self.chk_show_steps = QCheckBox("Show Steps")
        self.chk_show_steps.setStyleSheet("font-size: 8pt;")
        self.chk_show_steps.setChecked(False)
        self.chk_show_steps.setToolTip("항공기 옆에 step 번호를 표시합니다.")
        g_layout.addWidget(self.chk_show_steps, 1, 5)
        self.btn_clear_los = QPushButton("Clear LOS")
        self.btn_clear_los.setStyleSheet("font-size: 8pt; background:#f2f2f2; color:#111;")
        self.btn_clear_los.setFixedHeight(22)
        self.btn_clear_los.setToolTip("사용자 생성 LOS를 모두 삭제합니다.")
        g_layout.addWidget(self.btn_clear_los, 1, 6)

        self.btn_adv1 = QPushButton("Fwd 1  ]")
        self.btn_adv5 = QPushButton("Fwd 5")
        self.btn_adv10 = QPushButton("Fwd 10")
        self.btn_back1 = QPushButton("Back 1  [")
        self.btn_back5 = QPushButton("Back 5")
        self.btn_back10 = QPushButton("Back 10")
        self.btn_reset_step = QPushButton("Reset Step")
        self.btn_reset = QPushButton("Reset All")
        self.btn_save = QPushButton("")
        self.btn_import_scn = QPushButton("")
        self.btn_play_back = QPushButton("")
        self.btn_play = QPushButton("")
        self.btn_stop = QPushButton("")
        ui_style = self.style()
        save_icon = ui_style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        if save_icon.isNull():
            save_icon = ui_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.btn_save.setIcon(save_icon)
        self.btn_save.setToolTip("저장")
        self.btn_import_scn.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_DirOpenIcon, QColor(230, 180, 60)))
        self.btn_import_scn.setToolTip("불러오기")
        self.btn_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaSeekBackward, QColor("#1e9e3e")))
        self.btn_play_back.setToolTip("역방향 재생")
        self.btn_play.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPlay, QColor("#1e9e3e")))
        self.btn_play.setToolTip("재생")
        self.btn_stop.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaStop, QColor("#cf2f2f")))
        self.btn_stop.setToolTip("정지")
        self.btn_adv1.setToolTip("다음 1 step (단축키: ])")
        self.btn_back1.setToolTip("이전 1 step (단축키: [)")
        for b in [self.btn_save, self.btn_import_scn, self.btn_play_back, self.btn_play, self.btn_stop]:
            b.setFixedWidth(28)
            b.setFixedHeight(24)
            b.setStyleSheet("padding: 0px;")
        self.play_speed = QComboBox()
        self.play_speed.setStyleSheet("font-size: 8pt;")
        self.play_speed.addItems(["x1", "x2", "x4"])
        self.play_speed.setCurrentText("x1")
        self.play_speed.setObjectName("cmbPlaySpeed")
        self.play_speed.setToolTip("재생 배속을 선택합니다.")

        common_h = 27
        for b in [self.btn_adv1, self.btn_adv5, self.btn_adv10]:
            b.setStyleSheet("font-size: 8pt; background:#cfeccf; color:#111;")
            b.setFixedHeight(common_h)
        for b in [self.btn_back1, self.btn_back5, self.btn_back10]:
            b.setStyleSheet("font-size: 8pt; background:#f3d0d0; color:#111;")
            b.setFixedHeight(common_h)
        self.btn_reset_step.setStyleSheet("font-size: 8pt; background:#e6e6e6; color:#111;")
        self.btn_reset_step.setFixedHeight(common_h)
        self.btn_reset_step.setToolTip("현재 step 명령을 초기화합니다.")
        self.btn_reset.setStyleSheet("font-size: 8pt; background:#dcdcdc; color:#111;")
        self.btn_reset.setFixedHeight(common_h)
        self.btn_reset.setToolTip("전체 step과 기록을 초기화합니다.")
        self.btn_save.setStyleSheet("font-size: 8pt; background:#d4e1f7; color:#111;")
        self.btn_save.setFixedHeight(common_h)
        self.btn_import_scn.setFixedHeight(common_h)
        self.btn_play_back.setFixedHeight(common_h)
        self.btn_play.setFixedHeight(common_h)
        self.btn_stop.setFixedHeight(common_h)
        self.play_speed.setFixedHeight(common_h)

        # 4-row button layout (Forward / Back / Resets / File+Playback).
        btn_rows = QVBoxLayout()
        btn_rows.setContentsMargins(0, 0, 0, 0)
        btn_rows.setSpacing(2)

        row_fwd = QHBoxLayout()
        row_fwd.setContentsMargins(0, 0, 0, 0)
        row_fwd.setSpacing(2)
        row_fwd.addWidget(self.btn_adv1)
        row_fwd.addWidget(self.btn_adv5)
        row_fwd.addWidget(self.btn_adv10)
        btn_rows.addLayout(row_fwd)

        row_back = QHBoxLayout()
        row_back.setContentsMargins(0, 0, 0, 0)
        row_back.setSpacing(2)
        row_back.addWidget(self.btn_back1)
        row_back.addWidget(self.btn_back5)
        row_back.addWidget(self.btn_back10)
        btn_rows.addLayout(row_back)

        row_reset = QHBoxLayout()
        row_reset.setContentsMargins(0, 0, 0, 0)
        row_reset.setSpacing(2)
        row_reset.addWidget(self.btn_reset_step)
        row_reset.addWidget(self.btn_reset)
        row_reset.addStretch(1)
        row_reset.addWidget(self.btn_save)
        row_reset.addWidget(self.btn_import_scn)
        row_reset.addWidget(self.btn_play_back)
        row_reset.addWidget(self.btn_play)
        row_reset.addWidget(self.btn_stop)
        row_reset.addWidget(self.play_speed)
        btn_rows.addLayout(row_reset)

        g_layout.addLayout(btn_rows, 3, 0, 2, 7)

        left_layout.addWidget(global_group)

        aircraft_row = QWidget()
        self.aircraft_row = aircraft_row
        aircraft_layout = QGridLayout(aircraft_row)
        self.aircraft_row_layout = aircraft_layout
        aircraft_layout.setContentsMargins(0, 0, 0, 0)
        aircraft_layout.setSpacing(2)

        self.controls = {}
        panel_pos = {aid: (i // 2, i % 2) for i, aid in enumerate(AIRCRAFT_IDS)}
        for aid in AIRCRAFT_IDS:
            ac = AircraftControl(aid)
            self.controls[aid] = ac
            r, c = panel_pos.get(aid, (0, 0))
            aircraft_layout.addWidget(ac.group, r, c)
        self.aircraft_enable_checks: Dict[str, QCheckBox] = {}
        self.aircraft_colors: Dict[str, Tuple[float, float, float, float]] = {
            aid: tuple(self.controls[aid].current_color_rgba()) for aid in AIRCRAFT_IDS
        }
        aircraft_layout.setColumnStretch(0, 1)
        aircraft_layout.setColumnStretch(1, 1)
        self._refresh_offset_anchor_labels_for_mode(self.current_mode_key)
        self._arrange_aircraft_panels_for_mode(self.current_mode_key)
        # Place global hold-speed toggle below AIRCRAFT #1 panel.
        if "#1" in self.controls and hasattr(self.controls["#1"], "group"):
            self.chk_speed_lock.setParent(self.controls["#1"].group)
            self.chk_speed_lock.setText("HOLD SPEED")
            self.chk_speed_lock.setStyleSheet("font-size: 8pt; font-weight: 700;")
            try:
                self.controls["#1"].group.layout().addWidget(self.chk_speed_lock)
            except Exception:
                pass
        self.cmd_g_spin: Dict[str, QDoubleSpinBox] = {aid: self.controls[aid].g_cmd for aid in AIRCRAFT_IDS}
        self.applied_g_label: Dict[str, QLabel] = {aid: self.controls[aid].applied_g_lbl for aid in AIRCRAFT_IDS}
        self._g_binding_logged = False
        self._bank_prompt_shown: Dict[str, bool] = {aid: False for aid in AIRCRAFT_IDS}
        left_layout.addWidget(aircraft_row)
        self.default_cmds = self._default_step_cmds()
        self._configure_left_panel_text_policies()

        ui_font = QApplication.instance().font()
        self.setFont(ui_font)
        left.setFont(ui_font)
        global_group.setFont(ui_font)
        for ac in self.controls.values():
            ac.group.setFont(ui_font)
            for w in [ac.alt_ft, ac.hdg_deg, ac.cas_kt, ac.mach, ac.range_nm, ac.bearing_deg, ac.g_cmd, ac.pitch_deg, ac.bank_deg]:
                w.setMaximumWidth(104)
            ac.alt_ft.setMaximumWidth(116)
            ac.turn.setMaximumWidth(96)
            ac.power.setMaximumWidth(96)
            if ac.offset_group is not None:
                ac.offset_group.setMinimumHeight(ac.offset_group.sizeHint().height())
            ac.init_state_group.setMinimumHeight(ac.init_state_group.sizeHint().height())
            ac.cmd_group.setMinimumHeight(ac.cmd_group.sizeHint().height())
            ac.group.setMinimumHeight(ac.group.sizeHint().height())

        left_layout.addStretch(1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.view = PivotGLViewWidget(
            self._current_positions_for_pivot,
            self._set_pivot_marker,
            click_handler=self._on_view_click,
            right_click_handler=None,
            right_press_handler=self._on_view_right_press,
            right_move_handler=self._on_view_right_move,
            right_release_handler=self._on_view_right_release,
            resize_handler=self._position_view_overlays,
            view_changed_handler=self._on_view_camera_changed,
            overlay_paint_handler=self._paint_step_number_overlay,
        )
        self.view.setBackgroundColor((220, 235, 255))
        self.view.setCameraPosition(distance=40000, elevation=22, azimuth=45)
        self.view.opts["center"] = QVector3D(0, 0, 12000)
        self.grid_enabled = True
        self.grid_spacing_ft = 6000.0
        self.pivot_marker = gl.GLScatterPlotItem(
            pos=np.array([[0.0, 0.0, 12000.0]], dtype=float),
            color=(0.2, 0.6, 0.2, 0.45),
            size=12.0,
            pxMode=True,
        )
        self.view.addItem(self.pivot_marker)
        self.ground_plane_items: List[gl.GLMeshItem] = []
        self.grid_items: List[gl.GLLinePlotItem] = []
        self.grid_items_by_plane: Dict[str, gl.GLLinePlotItem] = {}
        self.grid_extent_ft = 0.0
        self._build_or_update_dashed_grids(force=True)
        self.selected_orbit_aid: Optional[str] = None
        self.current_arrow_pick: Dict[str, Dict[str, np.ndarray]] = {}
        self.selected_ring = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(1.0, 0.92, 0.20, 0.92),
            width=2.6,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.selected_ring)
        self.dca_be_outer_ring = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.10, 0.45, 0.98, 0.95),
            width=2.2,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_be_outer_ring)
        self.dca_be_inner_ring = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.10, 0.45, 0.98, 0.95),
            width=2.2,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_be_inner_ring)
        self.dca_asset_disc = gl.GLScatterPlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(1.0, 0.0, 0.0, 1.0),
            size=0.0,
            pxMode=False,
        )
        self.dca_asset_disc.setGLOptions("opaque")
        self.view.addItem(self.dca_asset_disc)
        self.dca_ra_zone_ring = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.95, 0.12, 0.12, 0.95),
            width=1.8,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_ra_zone_ring)
        self.dca_ra_line = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.95, 0.12, 0.12, 0.95),
            width=2.1,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_ra_line)
        self.dca_mission_rect = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(1.0, 0.92, 0.10, 0.95),
            width=2.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_mission_rect)
        self.dca_mission_diag1 = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(1.0, 0.92, 0.10, 0.95),
            width=1.4,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_mission_diag1)
        self.dca_mission_diag2 = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(1.0, 0.92, 0.10, 0.95),
            width=1.4,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_mission_diag2)
        self.dca_cap_front_dot = gl.GLScatterPlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.0, 0.0, 0.0, 1.0),
            size=0.0,
            pxMode=False,
        )
        self.dca_cap_front_dot.setGLOptions("opaque")
        self.view.addItem(self.dca_cap_front_dot)
        self.dca_cap_rear_dot = gl.GLScatterPlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.0, 0.0, 0.0, 1.0),
            size=0.0,
            pxMode=False,
        )
        self.dca_cap_rear_dot.setGLOptions("opaque")
        self.view.addItem(self.dca_cap_rear_dot)
        self.dca_cap_split_dots = gl.GLScatterPlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.0, 0.0, 0.0, 1.0),
            size=0.0,
            pxMode=False,
        )
        self.dca_cap_split_dots.setGLOptions("opaque")
        self.view.addItem(self.dca_cap_split_dots)
        self.dca_hmrl_line = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.95, 0.12, 0.12, 0.95),
            width=2.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_hmrl_line)
        self.dca_ldez_line = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.0, 0.95, 0.95, 0.95),
            width=2.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_ldez_line)
        self.dca_hdez_line = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.0, 0.95, 0.95, 0.95),
            width=2.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_hdez_line)
        self.dca_commit_line = gl.GLLinePlotItem(
            pos=np.zeros((0, 3), dtype=float),
            color=(0.95, 0.12, 0.12, 0.95),
            width=2.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.dca_commit_line)
        self.dca_be_label = QLabel("B.E", self.view)
        self.dca_be_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.dca_be_label.setStyleSheet(
            "QLabel { color: #0b54f2; font-size: 10pt; font-weight: 700; "
            "background: rgba(255,255,255,165); border-radius: 3px; padding: 1px 4px; }"
        )
        self.dca_be_label.hide()
        self.dca_be_label.raise_()
        self.dca_asset_label = QLabel("ASSET", self.view)
        self.dca_asset_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.dca_asset_label.setStyleSheet(
            "QLabel { color: #d11919; font-size: 10pt; font-weight: 700; "
            "background: rgba(255,255,255,165); border-radius: 3px; padding: 1px 4px; }"
        )
        self.dca_asset_label.hide()
        self.dca_asset_label.raise_()
        self.grid_spacing_combo = QComboBox(self.view)
        self.grid_spacing_combo.addItems(["Grid OFF", "Grid 1000 ft", "Grid 3000 ft", "Grid 6000 ft"])
        self.grid_spacing_combo.setCurrentText("Grid 6000 ft")
        self.grid_spacing_combo.setStyleSheet(
            "QComboBox { background: rgba(255,255,255,210); color: #111; border: 1px solid #888; padding: 2px 6px; font-size: 9pt; }"
        )
        self.grid_spacing_combo.currentIndexChanged.connect(self._on_grid_spacing_changed)
        self.grid_spacing_combo.raise_()
        self.brand_stamp = QLabel("produced by 103SQ, GOODSHOT", self.view)
        self.brand_stamp.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.brand_stamp.setStyleSheet(
            "QLabel {"
            " font-size: 8pt;"
            " color: rgba(20, 20, 20, 170);"
            " background: rgba(255, 255, 255, 120);"
            " border-radius: 4px;"
            " padding: 2px 6px;"
            "}"
        )
        self.brand_stamp.show()
        self.brand_stamp.raise_()
        self.elapsed_stamp = QLabel("TIME 00:00", self.view)
        self.elapsed_stamp.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.elapsed_stamp.setStyleSheet(
            "QLabel {"
            " font-size: 16pt;"
            " font-weight: 900;"
            " color: rgba(20, 20, 20, 220);"
            " background: rgba(255, 255, 255, 120);"
            " border-radius: 8px;"
            " padding: 4px 10px;"
            "}"
        )
        self.elapsed_stamp.show()
        self.elapsed_stamp.raise_()
        self.step_center_stamp = QLabel("STEP 0", self.view)
        self.step_center_stamp.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.step_center_stamp.setStyleSheet(
            "QLabel {"
            " font-size: 16pt;"
            " font-weight: 900;"
            " color: rgba(20, 20, 20, 210);"
            " background: rgba(255, 255, 255, 120);"
            " border-radius: 8px;"
            " padding: 4px 10px;"
            "}"
        )
        self.step_center_stamp.show()
        self.step_center_stamp.raise_()
        self.chk_top_view_overlay = QCheckBox("TOP VIEW (T)", self.view)
        self.chk_top_view_overlay.setStyleSheet(
            "QCheckBox {"
            " font-size: 9pt;"
            " color: rgba(20, 20, 20, 220);"
            " background: rgba(255, 255, 255, 160);"
            " border-radius: 4px;"
            " padding: 2px 6px;"
            "}"
        )
        self.chk_top_view_overlay.setChecked(False)
        self.chk_top_view_overlay.show()
        self.chk_top_view_overlay.raise_()
        self.chk_plan_view_overlay = QCheckBox("PLAN VIEW (P)", self.view)
        self.chk_plan_view_overlay.setStyleSheet(
            "QCheckBox {"
            " font-size: 9pt;"
            " color: rgba(20, 20, 20, 220);"
            " background: rgba(255, 255, 255, 160);"
            " border-radius: 4px;"
            " padding: 2px 6px;"
            "}"
        )
        self.chk_plan_view_overlay.setChecked(False)
        self.chk_plan_view_overlay.show()
        self.chk_plan_view_overlay.raise_()
        self.btn_view_back = QPushButton("BACK", self.view)
        self.btn_view_back.setStyleSheet(
            "QPushButton {"
            " font-size: 10pt;"
            " font-weight: 700;"
            " color: #ffffff;"
            " background: rgba(24, 24, 24, 220);"
            " border: 1px solid rgba(255, 255, 255, 120);"
            " border-radius: 5px;"
            " padding: 3px 8px;"
            "}"
            "QPushButton:hover { background: rgba(44, 44, 44, 230); }"
        )
        self.btn_view_back.show()
        self.btn_view_back.raise_()
        self.btn_view_fwd = QPushButton("FWD", self.view)
        self.btn_view_fwd.setStyleSheet(self.btn_view_back.styleSheet())
        self.btn_view_fwd.show()
        self.btn_view_fwd.raise_()
        self.btn_view_zoom_in = QPushButton("+", self.view)
        self.btn_view_zoom_in.setStyleSheet(self.btn_view_back.styleSheet())
        self.btn_view_zoom_in.show()
        self.btn_view_zoom_in.raise_()
        self.btn_view_zoom_out = QPushButton("-", self.view)
        self.btn_view_zoom_out.setStyleSheet(self.btn_view_back.styleSheet())
        self.btn_view_zoom_out.show()
        self.btn_view_zoom_out.raise_()
        self.btn_view_bookmark = QPushButton("★", self.view)
        self.btn_view_bookmark.setStyleSheet(
            "QPushButton {"
            " font-size: 12pt;"
            " font-weight: 800;"
            " color: #7a5200;"
            " background: rgba(255, 236, 140, 235);"
            " border: 1px solid rgba(160, 120, 20, 170);"
            " border-radius: 5px;"
            " padding: 1px 8px;"
            "}"
            "QPushButton:hover { background: rgba(255, 243, 175, 242); }"
        )
        self.btn_view_bookmark.setToolTip("현재 step 북마크 추가")
        self.btn_view_bookmark.show()
        self.btn_view_bookmark.raise_()
        self.btn_view_play_back = QPushButton("", self.view)
        self.btn_view_play_back.setStyleSheet("padding: 0px;")
        self.btn_view_play_back.setFixedWidth(28)
        self.btn_view_play_back.setFixedHeight(24)
        self.btn_view_play_back.show()
        self.btn_view_play_back.raise_()
        self.btn_view_play_pause = QPushButton("", self.view)
        self.btn_view_play_pause.setStyleSheet("padding: 0px;")
        self.btn_view_play_pause.setFixedWidth(28)
        self.btn_view_play_pause.setFixedHeight(24)
        self.btn_view_play_pause.show()
        self.btn_view_play_pause.raise_()
        self.btn_view_stop = QPushButton("", self.view)
        self.btn_view_stop.setStyleSheet("padding: 0px;")
        self.btn_view_stop.setFixedWidth(28)
        self.btn_view_stop.setFixedHeight(24)
        self.btn_view_stop.show()
        self.btn_view_stop.raise_()
        self.btn_view_speed_x1 = QPushButton("x1", self.view)
        self.btn_view_speed_x2 = QPushButton("x2", self.view)
        self.btn_view_speed_x4 = QPushButton("x4", self.view)
        speed_btn_style = (
            "QPushButton {"
            " font-size: 9pt;"
            " font-weight: 700;"
            " color: #111111;"
            " background: rgba(255, 255, 255, 220);"
            " border: 1px solid rgba(30, 30, 30, 130);"
            " border-radius: 4px;"
            " padding: 1px 6px;"
            "}"
            "QPushButton:hover { background: rgba(240, 248, 255, 235); }"
        )
        for _b in (self.btn_view_speed_x1, self.btn_view_speed_x2, self.btn_view_speed_x4):
            _b.setStyleSheet(speed_btn_style)
            _b.show()
            _b.raise_()
        self.btn_view_mode_step = QPushButton("stepview", self.view)
        self.btn_view_mode_overview = QPushButton("overview", self.view)
        self.btn_view_show_steps = QPushButton("show steps", self.view)
        for _b in (self.btn_view_mode_step, self.btn_view_mode_overview, self.btn_view_show_steps):
            _b.setCheckable(True)
            _b.setStyleSheet(speed_btn_style)
            _b.show()
            _b.raise_()
        self.lbl_view_tail = QLabel("TAIL", self.view)
        self.lbl_view_tail.setStyleSheet("QLabel { font-size: 8pt; font-weight: 700; color: #111111; background: rgba(255,255,255,190); border-radius: 4px; padding: 1px 6px; }")
        self.btn_view_tail_3 = QPushButton("3", self.view)
        self.btn_view_tail_10 = QPushButton("10", self.view)
        self.btn_view_tail_inf = QPushButton("\u221e", self.view)
        for _b in (self.btn_view_tail_3, self.btn_view_tail_10, self.btn_view_tail_inf):
            _b.setCheckable(True)
            _b.setStyleSheet(speed_btn_style)
            _b.show()
            _b.raise_()
        self.compass_rose = CompassRoseWidget(self._set_top_view_cardinal, self.view)
        self.compass_rose.show()
        self.compass_rose.raise_()
        QTimer.singleShot(0, self._position_view_overlays)
        right_layout.addWidget(self.view)
        self.los_map_panel = QWidget(self.view)
        self.los_map_panel.setStyleSheet("QWidget { background: rgba(255,255,255,210); border: 1px solid rgba(20,20,20,120); border-radius: 6px; }")
        self.los_map_layout = QVBoxLayout(self.los_map_panel)
        self.los_map_layout.setContentsMargins(6, 8, 6, 8)
        self.los_map_layout.setSpacing(6)
        step_row = QHBoxLayout()
        step_row.setContentsMargins(0, 0, 0, 0)
        step_row.setSpacing(4)
        self.lbl_los_step = QLabel("LOS step")
        self.lbl_los_step.setStyleSheet("QLabel { color: #111111; font-size: 8pt; }")
        self.edt_los_step = QLineEdit(self.los_map_panel)
        self.edt_los_step.setPlaceholderText("blank = current")
        self.edt_los_step.setFixedWidth(98)
        self.edt_los_step.setStyleSheet("QLineEdit { background: rgba(255,255,255,245); color:#111; font-size:8pt; border:1px solid rgba(20,20,20,110); border-radius:3px; padding:1px 4px; }")
        step_row.addWidget(self.lbl_los_step)
        step_row.addWidget(self.edt_los_step)
        step_row.addStretch(1)
        self.los_map_layout.addLayout(step_row)
        self.lbl_los_help = QLabel("점 두 개를 이어 그리면 LOS 선이 생깁니다.", self.los_map_panel)
        self.lbl_los_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_los_help.setStyleSheet("QLabel { color:#111111; font-size:8pt; background: rgba(255,255,255,160); border-radius:3px; padding:3px 6px; }")
        self.los_map_layout.addWidget(self.lbl_los_help)
        self.los_relation_map = LosRelationMapWidget(self._on_relation_map_pair_drawn, self.los_map_panel)
        self.los_relation_map.setMinimumSize(220, 160)
        self.los_map_layout.addWidget(self.los_relation_map, 1)
        self.los_map_panel.hide()
        self.bookmark_panel = QWidget(self.view)
        self.bookmark_panel.setStyleSheet("QWidget#bookmarkPanel { background: rgba(0,0,0,0); border: none; }")
        self.bookmark_panel.setObjectName("bookmarkPanel")
        self.bookmark_layout = QVBoxLayout(self.bookmark_panel)
        self.bookmark_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmark_layout.setSpacing(0)
        self.bookmark_scroll = QScrollArea(self.bookmark_panel)
        self.bookmark_scroll.setWidgetResizable(True)
        self.bookmark_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bookmark_scroll.setStyleSheet(
            "QScrollArea {"
            " background: rgba(0,0,0,0);"
            " border: none;"
            "}"
        )
        self.bookmark_cards = QWidget(self.bookmark_scroll)
        self.bookmark_cards.setStyleSheet("QWidget { background: rgba(0,0,0,0); border: none; }")
        self.bookmark_cards_layout = QVBoxLayout(self.bookmark_cards)
        self.bookmark_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.bookmark_cards_layout.setSpacing(5)
        self.bookmark_cards_layout.addStretch(1)
        self.bookmark_scroll.setWidget(self.bookmark_cards)
        self.bookmark_layout.addWidget(self.bookmark_scroll, 1)
        self.bookmark_panel.show()
        self.bookmark_panel.raise_()
        self._refresh_bookmark_panel()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)
        splitter.setChildrenCollapsible(False)
        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, False)
        self.btn_left_panel_toggle = QPushButton("\u25b6", self)
        self.btn_left_panel_toggle.setStyleSheet(
            "QPushButton {"
            " font-size: 14pt;"
            " font-weight: bold;"
            " color: rgba(255, 255, 255, 235);"
            " background: rgba(70, 70, 70, 220);"
            " border: 1px solid rgba(30, 30, 30, 220);"
            " border-radius: 5px;"
            " padding: 0px;"
            "}"
        )
        # Left-panel collapse feature is disabled; keep only panel popout workflow.
        self.btn_left_panel_toggle.hide()
        self.global_overlay = QWidget(self.view)
        self.global_overlay.setStyleSheet(
            "QWidget { background: rgba(0, 0, 0, 0); border: none; }"
        )
        self.global_overlay_layout = QVBoxLayout(self.global_overlay)
        self.global_overlay_layout.setContentsMargins(2, 2, 2, 2)
        self.global_overlay_layout.setSpacing(0)
        self.global_overlay_opacity = QGraphicsOpacityEffect(self.global_group)
        self.global_overlay_opacity.setOpacity(0.50)
        self._global_overlay_text_style = (
            "QGroupBox {"
            " color: #ffffff;"
            " border: 1px solid rgba(255,255,255,120);"
            " border-radius: 6px;"
            " margin-top: 8px;"
            " background: rgba(0,0,0,220);"
            "}"
            "QGroupBox::title { color: #ffffff; subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
            "QLabel { color: #ffffff; }"
            "QCheckBox { color: #ffffff; }"
            "QCheckBox#chkShowLos, QCheckBox#chkHoldSpeedLock {"
            " background: rgba(255,255,255,235);"
            " color: #111111;"
            " border-radius: 3px;"
            " padding: 1px 4px;"
            "}"
            "QPushButton { color: #ffffff; }"
            "QComboBox { color: #ffffff; }"
            "QComboBox#cmbPlaySpeed {"
            " background: rgba(255,255,255,245);"
            " color: #111111;"
            " border: 1px solid rgba(0,0,0,80);"
            "}"
            "QComboBox#cmbPlaySpeed QAbstractItemView { background: #ffffff; color: #111111; }"
            "QDoubleSpinBox { color: #ffffff; }"
        )
        self._global_overlay_fold_text_style = (
            "QGroupBox {"
            " color: #111111;"
            " border: 1px solid rgba(0,0,0,80);"
            " border-radius: 6px;"
            " margin-top: 8px;"
            " background: rgba(255,255,255,0);"
            "}"
            "QGroupBox::title { color: #111111; subcontrol-origin: margin; left: 8px; padding: 0 3px; }"
            "QLabel { color: #111111; }"
            "QCheckBox { color: #111111; }"
            "QCheckBox#chkShowLos, QCheckBox#chkHoldSpeedLock {"
            " background: rgba(255,255,255,245);"
            " color: #111111;"
            " border-radius: 3px;"
            " padding: 1px 4px;"
            "}"
            "QPushButton { color: #111111; }"
            "QComboBox { color: #111111; }"
            "QComboBox#cmbPlaySpeed {"
            " background: rgba(255,255,255,250);"
            " color: #111111;"
            " border: 1px solid rgba(0,0,0,80);"
            "}"
            "QComboBox#cmbPlaySpeed QAbstractItemView { background: #ffffff; color: #111111; }"
            "QDoubleSpinBox { color: #111111; }"
        )
        self.global_overlay.hide()
        self.global_overlay.raise_()

        self.plot_items = {}
        self.step_arrow_items: Dict[str, List[gl.GLLinePlotItem]] = {aid: [] for aid in AIRCRAFT_IDS}
        for aid in AIRCRAFT_IDS:
            color = self.aircraft_colors.get(aid, COLORS.get(aid, (0.0, 0.0, 0.0, 1.0)))
            trail_dashed = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(2.52), antialias=True, mode="lines")
            trail_recent = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(4.62), antialias=True, mode="lines")
            arrows_dashed = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(3.36), antialias=True, mode="lines")
            arrow_current = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(5.04), antialias=True, mode="lines")
            vertical_markers = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(1.4), antialias=True, mode="lines")
            overview_line = gl.GLLinePlotItem(pos=np.zeros((2, 3)), color=color, width=self._lw(2.1), antialias=True)
            overview_scatter = gl.GLScatterPlotItem(pos=np.zeros((1, 3)), color=color, size=7.5, pxMode=True)

            for item in [trail_dashed, trail_recent, arrows_dashed, arrow_current, vertical_markers, overview_line, overview_scatter]:
                self.view.addItem(item)
            self.plot_items[aid] = {
                "trail_dashed": trail_dashed,
                "trail_recent": trail_recent,
                "arrows_dashed": arrows_dashed,
                "arrow_current": arrow_current,
                "vertical_markers": vertical_markers,
                "overview_line": overview_line,
                "overview_scatter": overview_scatter,
            }

        self.los_pairs = [(AIRCRAFT_IDS[i], AIRCRAFT_IDS[j]) for i in range(len(AIRCRAFT_IDS)) for j in range(i + 1, len(AIRCRAFT_IDS))]
        self.los_styles = {}
        for pair in self.los_pairs:
            if pair == ("#1", "#2"):
                self.los_styles[pair] = {"color": (0.0, 0.0, 0.0, 0.35), "text_color": "#111111"}
            elif pair == ("#1", "#3"):
                self.los_styles[pair] = {"color": (0.0, 0.0, 0.0, 0.35), "text_color": "#111111"}
            elif pair == ("#2", "#3"):
                self.los_styles[pair] = {"color": (0.10, 0.35, 0.95, 0.35), "text_color": "#1f4fd0"}
            else:
                self.los_styles[pair] = {"color": (0.90, 0.10, 0.10, 0.30), "text_color": "#b22222"}
        self.los_items = {}
        for pair in self.los_pairs:
            los_line = gl.GLLinePlotItem(
                pos=np.zeros((2, 3), dtype=float),
                color=self.los_styles[pair]["color"],
                width=1.0,
                antialias=True,
                mode="lines",
            )
            self.view.addItem(los_line)
            self.los_items[pair] = los_line
        self.custom_los_links: List[Dict[str, object]] = []
        self.custom_los_line_items: List[gl.GLLinePlotItem] = []
        self.custom_los_link_labels: List[QLabel] = []
        self.custom_link_drag_src: Optional[Dict[str, object]] = None
        self.default_step_los_hidden: Dict[Tuple[str, int], Set[Tuple[str, str]]] = {}
        self.custom_los_drag_line = gl.GLLinePlotItem(
            pos=np.zeros((2, 3), dtype=float),
            color=(0.0, 0.0, 0.0, 0.35),
            width=1.0,
            antialias=True,
            mode="lines",
        )
        self.view.addItem(self.custom_los_drag_line)
        self.custom_los_drag_line.setVisible(False)
        self.ata_labels = {}
        for pair in self.los_pairs:
            self.ata_labels[pair] = QLabel(self.view)
        for pair, label in self.ata_labels.items():
            label.setText("")
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            tcolor = self.los_styles[pair]["text_color"]
            label.setStyleSheet(
                "QLabel {"
                " font-size: 10pt;"
                f" color: {tcolor};"
                " background-color: rgba(255, 255, 255, 0);"
                " border: none;"
                " padding: 0px;"
                "}"
            )
            label.hide()
        self.step_num_labels: Dict[str, List[QLabel]] = {aid: [] for aid in AIRCRAFT_IDS}

        self.btn_adv1.clicked.connect(lambda: self.advance_steps(1))
        self.btn_adv5.clicked.connect(lambda: self.advance_steps(5))
        self.btn_adv10.clicked.connect(lambda: self.advance_steps(10))
        self.btn_back1.clicked.connect(lambda: self.back_steps(1))
        self.btn_back5.clicked.connect(lambda: self.back_steps(5))
        self.btn_back10.clicked.connect(lambda: self.back_steps(10))
        self.btn_reset_step.clicked.connect(self.reset_current_step_cmds)
        self.btn_reset.clicked.connect(self.on_reset_scenario_clicked)
        self.btn_guide.clicked.connect(self._show_guide_dialog)
        self.btn_setup_popup.clicked.connect(self._on_setup_popup_clicked)
        self.btn_global_popout.clicked.connect(self._toggle_left_ui_popout)
        self.btn_save.clicked.connect(self.export_scenario_csv)
        self.btn_import_scn.clicked.connect(self.import_scenario_csv)
        self.btn_play_back.clicked.connect(self.toggle_playback_backward)
        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_stop.clicked.connect(self.stop_playback)
        self.btn_view_back.clicked.connect(lambda: self.back_steps(1))
        self.btn_view_fwd.clicked.connect(lambda: self.advance_steps(1))
        self.btn_view_zoom_in.clicked.connect(lambda: self._adjust_view_zoom(0.85))
        self.btn_view_zoom_out.clicked.connect(lambda: self._adjust_view_zoom(1.0 / 0.85))
        self.btn_view_bookmark.clicked.connect(self._on_add_bookmark_clicked)
        self.btn_view_play_back.clicked.connect(self.toggle_playback_backward)
        self.btn_view_play_pause.clicked.connect(self.toggle_playback)
        self.btn_view_stop.clicked.connect(self.stop_playback)
        self.btn_view_speed_x1.clicked.connect(lambda: self._set_play_speed_preset("x1"))
        self.btn_view_speed_x2.clicked.connect(lambda: self._set_play_speed_preset("x2"))
        self.btn_view_speed_x4.clicked.connect(lambda: self._set_play_speed_preset("x4"))
        self.btn_view_mode_step.clicked.connect(self._on_view_overlay_step_clicked)
        self.btn_view_mode_overview.clicked.connect(self._on_view_overlay_overview_clicked)
        self.btn_view_show_steps.clicked.connect(self._on_view_overlay_show_steps_clicked)
        self.btn_view_tail_3.clicked.connect(lambda: self._set_step_tail_limit(3))
        self.btn_view_tail_10.clicked.connect(lambda: self._set_step_tail_limit(10))
        self.btn_view_tail_inf.clicked.connect(lambda: self._set_step_tail_limit(-1))
        self.btn_clear_los.clicked.connect(self._on_clear_los_clicked)
        self.btn_left_panel_toggle.clicked.connect(self._on_toggle_left_panel_clicked)
        self.view_mode.currentIndexChanged.connect(self.refresh_ui)
        self.play_speed.currentIndexChanged.connect(lambda _i: self._sync_view_speed_buttons())
        self.dt_sec.valueChanged.connect(self._on_dt_sec_changed)
        self.chk_speed_lock.toggled.connect(self._on_speed_lock_toggled)
        self.chk_show_los.toggled.connect(self.refresh_ui)
        self.chk_show_steps.toggled.connect(self.refresh_ui)
        for aid in AIRCRAFT_IDS:
            self.controls[aid].hold_speed_chk.toggled.connect(lambda checked, a=aid: self._on_aircraft_hold_toggled(a, checked))
            self.controls[aid].color_combo.currentIndexChanged.connect(lambda _idx, a=aid: self._on_aircraft_color_changed(a))
            self.controls[aid].g_cmd.valueChanged.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].g_cmd.editingFinished.connect(lambda a=aid: self._on_cmd_input_finalize(a))
            self.controls[aid].g_max_chk.toggled.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].pitch_deg.valueChanged.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].pitch_deg.editingFinished.connect(lambda a=aid: self._on_cmd_input_finalize(a))
            self.controls[aid].pitch_hold_chk.toggled.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].bank_deg.valueChanged.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].pull_up_chk.toggled.connect(lambda _v, a=aid: self._on_pull_mode_toggled(a))
            self.controls[aid].pull_down_chk.toggled.connect(lambda _v, a=aid: self._on_pull_mode_toggled(a))
            self.controls[aid].level_chk.toggled.connect(lambda _v, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].turn.currentIndexChanged.connect(lambda _i, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].power.currentIndexChanged.connect(lambda _i, a=aid: self._on_cmd_input_changed(a))
            self.controls[aid].alt_ft.valueChanged.connect(self._on_step0_initial_state_changed)
            self.controls[aid].hdg_deg.valueChanged.connect(self._on_step0_initial_state_changed)
            self.controls[aid].cas_kt.valueChanged.connect(self._on_step0_initial_state_changed)
            self.controls[aid].range_nm.valueChanged.connect(self._on_step0_initial_state_changed)
            self.controls[aid].bearing_deg.valueChanged.connect(self._on_step0_initial_state_changed)
        self.chk_top_view_overlay.toggled.connect(self._on_top_view_checkbox_toggled)
        self.chk_plan_view_overlay.toggled.connect(self._on_plan_view_checkbox_toggled)

        self.shortcut_top = QShortcut(QKeySequence("T"), self)
        self.shortcut_top.activated.connect(self.toggle_top_view)
        self.shortcut_plan = QShortcut(QKeySequence("P"), self)
        self.shortcut_plan.activated.connect(self.toggle_plan_view)
        self.shortcut_fwd1 = QShortcut(QKeySequence("]"), self)
        self.shortcut_fwd1.activated.connect(lambda: self.advance_steps(1))
        self.shortcut_back1 = QShortcut(QKeySequence("["), self)
        self.shortcut_back1.activated.connect(lambda: self.back_steps(1))
        self.shortcut_zoom_in_plus = QShortcut(QKeySequence("+"), self)
        self.shortcut_zoom_in_plus.activated.connect(lambda: self._adjust_view_zoom(0.85))
        self.shortcut_zoom_in_equal = QShortcut(QKeySequence("="), self)
        self.shortcut_zoom_in_equal.activated.connect(lambda: self._adjust_view_zoom(0.85))
        self.shortcut_zoom_in_numpad = QShortcut(QKeySequence("Num+"), self)
        self.shortcut_zoom_in_numpad.activated.connect(lambda: self._adjust_view_zoom(0.85))
        self.shortcut_zoom_in_pageup = QShortcut(QKeySequence("PgUp"), self)
        self.shortcut_zoom_in_pageup.activated.connect(lambda: self._adjust_view_zoom(0.85))
        self.shortcut_zoom_out_minus = QShortcut(QKeySequence("-"), self)
        self.shortcut_zoom_out_minus.activated.connect(lambda: self._adjust_view_zoom(1.0 / 0.85))
        self.shortcut_zoom_out_underscore = QShortcut(QKeySequence("_"), self)
        self.shortcut_zoom_out_underscore.activated.connect(lambda: self._adjust_view_zoom(1.0 / 0.85))
        self.shortcut_zoom_out_numpad = QShortcut(QKeySequence("Num-"), self)
        self.shortcut_zoom_out_numpad.activated.connect(lambda: self._adjust_view_zoom(1.0 / 0.85))
        self.shortcut_zoom_out_pagedown = QShortcut(QKeySequence("PgDown"), self)
        self.shortcut_zoom_out_pagedown.activated.connect(lambda: self._adjust_view_zoom(1.0 / 0.85))
        self.ata_label_timer = QTimer(self)
        self.ata_label_timer.setInterval(120)
        self.ata_label_timer.timeout.connect(self._on_ata_label_timer_tick)
        self.ata_label_timer.start()
        self._splitter_anim_timer = QTimer(self)
        self._splitter_anim_timer.setInterval(16)
        self._splitter_anim_timer.timeout.connect(self._on_splitter_anim_tick)
        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(33)
        self.playback_timer.timeout.connect(self._on_playback_tick)
        self.playback_running = False
        self.playback_active = False
        self.playback_direction = 1
        self.playback_step_float = 0.0
        self.playback_origin_step = 0
        self._last_playback_wall = None
        self._sync_play_button_icon()
        self._sync_view_speed_buttons()
        self._sync_view_mode_overlay_buttons()
        self._capture_boot_init_values()

        QTimer.singleShot(0, self._init_splitter_ratio)
        self.reset_sim()

    @staticmethod
    def _version_tuple(ver: str) -> Tuple[int, int, int]:
        nums = [int(x) for x in re.findall(r"\d+", str(ver))]
        while len(nums) < 3:
            nums.append(0)
        return int(nums[0]), int(nums[1]), int(nums[2])

    @staticmethod
    def _is_remote_newer(remote_ver: str, local_ver: str = APP_VERSION) -> bool:
        return MainWindow._version_tuple(str(remote_ver)) > MainWindow._version_tuple(str(local_ver))

    @staticmethod
    def _sha256_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest().upper()

    def _fetch_update_meta(self, timeout_sec: float = 4.0) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        try:
            req = urllib.request.Request(UPDATE_META_URL, headers={"User-Agent": f"FA50/{APP_VERSION}"})
            with urllib.request.urlopen(req, timeout=float(timeout_sec)) as resp:
                raw = resp.read().decode("utf-8-sig", errors="replace")
            data = json.loads(raw)
            if not isinstance(data, dict):
                return None, "Invalid update metadata format"
            return data, None
        except Exception as e:
            return None, str(e)

    def check_updates_on_startup(self):
        meta, _err = self._fetch_update_meta(timeout_sec=4.0)
        if not isinstance(meta, dict):
            return
        remote_ver = str(meta.get("latest_version", "")).strip()
        if not remote_ver or (not self._is_remote_newer(remote_ver, APP_VERSION)):
            return
        msg = (
            f"업데이트가 있습니다.\n\n"
            f"현재 버전: {APP_VERSION}\n"
            f"최신 버전: {remote_ver}\n\n"
            f"지금 다운로드 후 적용하시겠습니까?"
        )
        ans = QMessageBox.question(self, "Update Available", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ans != QMessageBox.Yes:
            return
        self._download_and_apply_update(meta)

    def _download_and_apply_update(self, meta: Dict[str, str]):
        url = str(meta.get("download_url", "")).strip()
        sha_expected = str(meta.get("sha256", "")).strip().upper()
        asset_name = str(meta.get("asset_name", "FA50.exe")).strip() or "FA50.exe"
        if not url:
            QMessageBox.warning(self, "Update Error", "download_url이 비어 있습니다.")
            return
        safe_name = re.sub(r"[^A-Za-z0-9._ -]", "_", asset_name)
        temp_dir = os.path.join(tempfile.gettempdir(), "fa50_updater")
        os.makedirs(temp_dir, exist_ok=True)
        target_path = os.path.join(temp_dir, safe_name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"FA50/{APP_VERSION}"})
            with urllib.request.urlopen(req, timeout=30.0) as src, open(target_path, "wb") as dst:
                while True:
                    buf = src.read(1024 * 1024)
                    if not buf:
                        break
                    dst.write(buf)
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"다운로드 실패: {e}")
            return

        if sha_expected:
            try:
                sha_got = self._sha256_file(target_path)
                if sha_got != sha_expected:
                    QMessageBox.warning(
                        self,
                        "Update Error",
                        f"SHA256 불일치\nexpected: {sha_expected}\nactual:   {sha_got}",
                    )
                    return
            except Exception as e:
                QMessageBox.warning(self, "Update Error", f"해시 검증 실패: {e}")
                return

        if not getattr(sys, "frozen", False):
            QMessageBox.information(
                self,
                "Update Downloaded",
                f"업데이트 파일 다운로드 완료:\n{target_path}\n\n"
                f"현재는 Python 실행 모드라 자동 교체를 수행하지 않습니다.",
            )
            return

        cur_exe = os.path.abspath(sys.executable)
        bat_path = os.path.join(temp_dir, "fa50_apply_update.cmd")
        pid = int(os.getpid())
        bat = (
            "@echo off\r\n"
            "setlocal\r\n"
            f"set \"PID={pid}\"\r\n"
            f"set \"SRC={target_path}\"\r\n"
            f"set \"DST={cur_exe}\"\r\n"
            "for /L %%I in (1,1,120) do (\r\n"
            "  tasklist /FI \"PID eq %PID%\" | find \"%PID%\" >nul\r\n"
            "  if errorlevel 1 goto :copy\r\n"
            "  timeout /t 1 /nobreak >nul\r\n"
            ")\r\n"
            ":copy\r\n"
            "copy /Y \"%SRC%\" \"%DST%\" >nul\r\n"
            "if errorlevel 1 (\r\n"
            "  start \"\" \"%SRC%\"\r\n"
            ") else (\r\n"
            "  start \"\" \"%DST%\"\r\n"
            ")\r\n"
            "del \"%SRC%\" >nul 2>nul\r\n"
            "del \"%~f0\" >nul 2>nul\r\n"
            "endlocal\r\n"
        )
        try:
            with open(bat_path, "w", encoding="utf-8", newline="") as f:
                f.write(bat)
            cflags = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
            subprocess.Popen(["cmd", "/c", bat_path], close_fds=True, creationflags=cflags)
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"업데이트 적용 준비 실패: {e}")
            return

        QMessageBox.information(self, "Update", "업데이트를 적용하기 위해 프로그램을 종료합니다.")
        QTimer.singleShot(100, QApplication.instance().quit)

    @staticmethod
    def _wrap_hdg(hdg: float) -> float:
        v = hdg % 360.0
        if v < 0:
            v += 360.0
        return v

    @staticmethod
    def _wrap_hdg_excel(hdg: float) -> float:
        # Excel rule:
        # =IF(Y<(-360),Y+720,IF(Y<0,Y+360,IF(Y<360,Y,IF(Y>=360,Y-360,Y))))
        if hdg < -360.0:
            return hdg + 720.0
        if hdg < 0.0:
            return hdg + 360.0
        if hdg < 360.0:
            return hdg
        if hdg >= 360.0:
            return hdg - 360.0
        return hdg

    @staticmethod
    def _tas_from_cas(cas_kt: float, alt_ft: float) -> float:
        return cas_kt * (1.0 + 0.0142 * (alt_ft / 1000.0))

    @staticmethod
    def _wrap_to_pm180(angle_deg: float) -> float:
        wrapped = (angle_deg + 180.0) % 360.0 - 180.0
        if wrapped <= -180.0:
            return wrapped + 360.0
        return wrapped

    def _active_aircraft_ids(self) -> List[str]:
        mk = str(getattr(self, "current_mode_key", "")).strip()
        mode_ids = MODE_ACTIVE_IDS.get(mk, MODE_ACTIVE_IDS["2vs1"])
        return [aid for aid in mode_ids if aid in AIRCRAFT_IDS]

    def _enabled_aircraft_ids_for_save(self) -> List[str]:
        mk = str(getattr(self, "current_mode_key", "")).strip()
        mode_ids = [aid for aid in MODE_ACTIVE_IDS.get(mk, MODE_ACTIVE_IDS["2vs1"]) if aid in AIRCRAFT_IDS]
        if bool(getattr(self, "aircraft_enable_checks", {})):
            out: List[str] = []
            for aid in mode_ids:
                cb = self.aircraft_enable_checks.get(aid)
                if (cb is None) or bool(cb.isChecked()):
                    out.append(aid)
            return out
        return list(mode_ids)

    def _ba_ids_for_mode(self) -> set:
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if mk in {"4vs2", "4vs4"}:
            return {"#1", "#2", "#3", "#4"}
        return {"#1", "#2"}

    def _ba_ra_sets_for_current_mode(self) -> Tuple[set, set]:
        active = set(self._active_aircraft_ids())
        ba = self._ba_ids_for_mode() & active
        ra = active - ba
        return ba, ra

    @staticmethod
    def _hex_from_rgb01(rgb: Tuple[float, float, float]) -> str:
        r = int(max(0, min(255, round(float(rgb[0]) * 255.0))))
        g = int(max(0, min(255, round(float(rgb[1]) * 255.0))))
        b = int(max(0, min(255, round(float(rgb[2]) * 255.0))))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _los_style_for_pair(self, a: str, b: str) -> Dict[str, object]:
        # LOS line color follows the source aircraft color (a -> b) across all modes.
        c = self._aircraft_color(a)
        return {"color": (c[0], c[1], c[2], 0.35), "text_color": self._hex_from_rgb01((c[0], c[1], c[2]))}

    def _active_los_pairs(self) -> List[Tuple[str, str]]:
        active = set(self._active_aircraft_ids())
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if mk == "4vs2":
            wanted = [
                ("#1", "#2"),  # #2-#1
                ("#3", "#4"),  # #4-#3
                ("#1", "#3"),  # #3-#1
                ("#1", "#5"),
                ("#1", "#6"),
                ("#3", "#5"),
                ("#3", "#6"),
                ("#5", "#6"),  # RA-RA
            ]
            out: List[Tuple[str, str]] = []
            for a, b in wanted:
                if (a in active) and (b in active):
                    out.append((a, b))
            return out
        if mk in {"2vs2", "4vs2", "4vs4"}:
            ba = self._ba_ids_for_mode()
            ra = active - ba
            out: List[Tuple[str, str]] = []
            if mk == "2vs2" and ("#1" in active and "#2" in active):
                out.append(("#1", "#2"))
            for a in AIRCRAFT_IDS:
                if a not in active or a not in ba:
                    continue
                for b in AIRCRAFT_IDS:
                    if b not in active or b not in ra:
                        continue
                    out.append((a, b))
            if mk == "2vs2" and ("#3" in active and "#4" in active):
                out.append(("#3", "#4"))
            return out
        return [pair for pair in self.los_pairs if pair[0] in active and pair[1] in active]

    def _on_aircraft_color_changed(self, aid: str):
        if aid in self.controls:
            self.aircraft_colors[aid] = tuple(self.controls[aid].current_color_rgba())
        self.refresh_ui()

    def _capture_boot_init_values(self):
        boot = {}
        for aid in AIRCRAFT_IDS:
            ac = self.controls[aid]
            boot[aid] = {
                "alt_ft": float(ac.alt_ft.value()),
                "hdg_deg": float(ac.hdg_deg.value()),
                "cas_kt": float(ac.cas_kt.value()),
                "range_nm": float(ac.range_nm.value()),
                "bearing_deg": float(ac.bearing_deg.value()),
            }
        self._boot_init_values = {
            "aircraft": boot,
            "colors": {aid: str(self.controls[aid].current_color_key()) for aid in AIRCRAFT_IDS},
        }

    def _restore_boot_init_values(self):
        if not hasattr(self, "_boot_init_values"):
            return
        boot = self._boot_init_values.get("aircraft", {})
        for aid in AIRCRAFT_IDS:
            ac = self.controls[aid]
            vals = boot.get(aid, {})
            ac.alt_ft.setValue(float(vals.get("alt_ft", ac.alt_ft.value())))
            ac.hdg_deg.setValue(float(vals.get("hdg_deg", ac.hdg_deg.value())))
            ac.cas_kt.setValue(float(vals.get("cas_kt", ac.cas_kt.value())))
            ac.range_nm.setValue(float(vals.get("range_nm", ac.range_nm.value())))
            ac.bearing_deg.setValue(float(vals.get("bearing_deg", ac.bearing_deg.value())))
            ac.set_color_key(str(self._boot_init_values.get("colors", {}).get(aid, ac.current_color_key())))
            ac._sync_mach_from_cas()
        self.aircraft_colors = {aid: tuple(self.controls[aid].current_color_rgba()) for aid in AIRCRAFT_IDS}

    def _init_splitter_ratio(self):
        if self._splitter_ratio_initialized:
            return
        self._recompute_left_min_width()
        self._apply_main_minimum_size()
        self._apply_splitter_start_min_left()
        self._update_aircraft_group_widths()
        self._splitter_ratio_initialized = True
        self._debug_check_left_panel_clipping()

    def _apply_splitter_collapsed_start(self):
        sizes = self.main_splitter.sizes()
        total_width = int(sum(sizes)) if sizes else int(self.main_splitter.width())
        if total_width <= 0:
            total_width = int(self.width())
        # Startup preference: begin with the left panel minimized.
        self._set_left_panel_collapsed_limits(True)
        self.main_splitter.setSizes([0, max(1, total_width)])
        self._left_panel_hidden = True
        self._left_panel_last_width = max(1, int(getattr(self, "_left_min_width", 300)))
        self._set_global_overlay_mode(True)
        self._update_left_panel_toggle_text()
        self._position_left_panel_toggle()

    def _update_left_panel_toggle_text(self):
        if not hasattr(self, "btn_left_panel_toggle") or self.btn_left_panel_toggle is None:
            return
        hidden = bool(getattr(self, "_status_panel_hidden", False))
        if hidden:
            self.btn_left_panel_toggle.setText("\u25b6")
            self.btn_left_panel_toggle.setToolTip("항공기 상태 패널 펼치기")
        else:
            self.btn_left_panel_toggle.setText("\u25c0")
            self.btn_left_panel_toggle.setToolTip("항공기 상태 패널 접기")

    def _set_left_panel_collapsed_limits(self, collapsed: bool):
        if (not hasattr(self, "left_scroll")) or (self.left_scroll is None):
            return
        if collapsed:
            self.left_scroll.setMinimumWidth(0)
            self.left_scroll.setMaximumWidth(0)
            if hasattr(self, "left_panel") and (self.left_panel is not None):
                self.left_panel.setMinimumWidth(0)
        else:
            min_left = int(getattr(self, "_left_min_width", 300))
            self.left_scroll.setMaximumWidth(16777215)
            self.left_scroll.setMinimumWidth(min_left)
            if hasattr(self, "left_panel") and (self.left_panel is not None):
                self.left_panel.setMinimumWidth(max(0, min_left - 8))

    def _position_left_panel_toggle(self):
        # Left-panel collapse feature is disabled.
        if hasattr(self, "btn_left_panel_toggle") and self.btn_left_panel_toggle is not None:
            self.btn_left_panel_toggle.hide()
        return
        if not hasattr(self, "btn_left_panel_toggle") or self.btn_left_panel_toggle is None:
            return
        if bool(getattr(self, "_left_ui_popped", False)):
            self.btn_left_panel_toggle.hide()
            return
        sg = self.main_splitter.geometry()
        if sg.width() <= 0 or sg.height() <= 0:
            return
        sizes = self.main_splitter.sizes()
        left_w = int(sizes[0]) if sizes else 0
        bw = 22
        bh = max(56, int(round(float(sg.height()) * 0.20)))
        if bool(getattr(self, "_status_panel_hidden", False)):
            x = 0
        else:
            x = int(sg.x() + left_w - bw // 2)
        x = max(0, min(x, max(0, self.width() - bw)))
        y = int(sg.y() + max(0, (sg.height() - bh) // 2))
        self.btn_left_panel_toggle.setGeometry(x, y, bw, bh)
        self.btn_left_panel_toggle.raise_()

    def _is_left_panel_effectively_hidden(self) -> bool:
        if bool(getattr(self, "_left_ui_popped", False)):
            return False
        if not hasattr(self, "main_splitter") or self.main_splitter is None:
            return bool(getattr(self, "_left_panel_hidden", False))
        sizes = self.main_splitter.sizes()
        left_w = int(sizes[0]) if sizes else 0
        return left_w <= 1

    def _left_compact_width_for_global(self) -> int:
        if not hasattr(self, "global_group") or self.global_group is None:
            return 220
        self.global_group.adjustSize()
        return int(max(220, self.global_group.sizeHint().width() + 20))

    def _set_global_overlay_mode(self, use_overlay: bool):
        if not hasattr(self, "global_group") or self.global_group is None:
            return
        if not hasattr(self, "global_overlay") or self.global_overlay is None:
            return
        if use_overlay:
            try:
                if hasattr(self, "left_layout") and self.left_layout is not None:
                    self.left_layout.removeWidget(self.global_group)
            except Exception:
                pass
            try:
                self.global_overlay_layout.removeWidget(self.global_group)
            except Exception:
                pass
            if self.global_group.parent() is not self.global_overlay:
                self.global_group.setParent(self.global_overlay)
            if self.global_overlay_layout.indexOf(self.global_group) < 0:
                self.global_overlay_layout.addWidget(self.global_group)
            if bool(getattr(self, "_status_panel_hidden", False)):
                # In status-fold mode, keep GLOBAL in original look (no gray popup styling).
                self.global_group.setGraphicsEffect(None)
                self.global_group.setStyleSheet(self._global_overlay_fold_text_style)
            else:
                self.global_group.setGraphicsEffect(self.global_overlay_opacity)
                self.global_group.setStyleSheet(self._global_overlay_text_style)
            self.global_group.show()
            self.global_group.adjustSize()
            self.global_overlay.adjustSize()
            self.global_overlay.show()
            self.global_group.raise_()
            self._position_global_overlay()
        else:
            if self.global_group.parent() is not self.left_panel:
                try:
                    self.global_overlay_layout.removeWidget(self.global_group)
                except Exception:
                    pass
                self.global_group.setParent(self.left_panel)
                if hasattr(self, "left_layout") and self.left_layout is not None:
                    self.left_layout.insertWidget(0, self.global_group)
            self.global_group.setGraphicsEffect(None)
            self.global_group.setStyleSheet("")
            self.global_overlay.hide()

    def _position_global_overlay(self):
        if not hasattr(self, "global_overlay") or self.global_overlay is None:
            return
        if not self.global_overlay.isVisible():
            return
        m = 10
        self.global_group.adjustSize()
        self.global_overlay.adjustSize()
        gh = self.global_group.sizeHint()
        gw = int(max(gh.width(), self.global_group.size().width()))
        ghh = int(max(gh.height(), self.global_group.size().height()))
        ow = int(self.global_overlay.sizeHint().width())
        oh = int(self.global_overlay.sizeHint().height())
        w = int(max(gw, ow))
        h = int(max(ghh, oh))
        if w <= 0 or h <= 0:
            return
        self.global_overlay.setGeometry(m, m, w, h)
        self.global_overlay.raise_()

    def _ensure_global_overlay_alive(self):
        if not bool(self._is_left_panel_effectively_hidden()):
            return
        if self.global_group.parent() is not self.global_overlay:
            self._set_global_overlay_mode(True)
        if not self.global_group.isVisible():
            self.global_group.show()
        if not self.global_overlay.isVisible():
            self.global_overlay.show()
        self.global_group.adjustSize()
        self.global_overlay.adjustSize()
        gh = self.global_group.sizeHint()
        w = int(max(220, gh.width(), self.global_group.minimumSizeHint().width(), self.global_overlay.sizeHint().width()))
        h = int(max(80, gh.height(), self.global_group.minimumSizeHint().height(), self.global_overlay.sizeHint().height()))
        self.global_overlay.setGeometry(10, 10, w, h)
        self.global_group.raise_()
        self.global_overlay.raise_()

    def _on_toggle_left_panel_clicked(self):
        # Left-panel collapse feature is disabled.
        return

    def _animate_left_panel(self, show: bool):
        sizes = self.main_splitter.sizes()
        total = int(sum(sizes)) if sizes else int(self.main_splitter.width())
        if total <= 1:
            return
        start_left = int(sizes[0]) if sizes else 1
        if not bool(self._left_panel_hidden):
            self._left_panel_last_width = max(1, start_left)
        min_left = int(getattr(self, "_left_min_width", 300))
        if show:
            self._set_left_panel_collapsed_limits(False)
            target_left = max(min_left, int(self._left_panel_last_width or min_left))
        else:
            target_left = 0
        target_left = max(0, min(target_left, total - 1))
        self._splitter_anim_state = {
            "step": 0,
            "steps": 12,
            "start_left": float(start_left),
            "target_left": float(target_left),
            "total": float(total),
            "show": 1.0 if show else 0.0,
        }
        self.main_splitter.setCollapsible(0, True)
        self._splitter_anim_timer.start()

    def _on_splitter_anim_tick(self):
        st = self._splitter_anim_state
        if not isinstance(st, dict):
            self._splitter_anim_timer.stop()
            return
        step = int(st.get("step", 0)) + 1
        steps = max(1, int(st.get("steps", 12)))
        a = min(1.0, float(step) / float(steps))
        ease = a * a * (3.0 - 2.0 * a)
        left = float(st.get("start_left", 1.0)) + (float(st.get("target_left", 1.0)) - float(st.get("start_left", 1.0))) * ease
        total = max(2.0, float(st.get("total", 2.0)))
        left_i = max(0, min(int(round(left)), int(total) - 1))
        right_i = max(1, int(total) - left_i)
        self.main_splitter.setSizes([left_i, right_i])
        self._position_left_panel_toggle()
        st["step"] = step
        if step >= steps:
            self._splitter_anim_timer.stop()
            show = bool(int(st.get("show", 0.0)))
            self._left_panel_hidden = not show
            if show:
                self._left_panel_last_width = left_i
                self._set_left_panel_collapsed_limits(False)
                self._set_global_overlay_mode(False)
            else:
                self._set_left_panel_collapsed_limits(True)
                self._set_global_overlay_mode(True)
            self._update_left_panel_toggle_text()
            self._position_left_panel_toggle()
            self._position_view_overlays()

    def _apply_splitter_ratio_15_85(self):
        sizes = self.main_splitter.sizes()
        total_width = int(sum(sizes)) if sizes else int(self.main_splitter.width())
        if total_width <= 0:
            total_width = int(self.width())
        min_left = int(getattr(self, "_left_min_width", 280))
        # Start as narrow as possible without clipping: left uses computed minimum width.
        left_w = max(min_left, int(total_width * 0.15))
        left_w = min_left if total_width > (min_left + 1) else left_w
        left_w = min(left_w, max(min_left, total_width - 1))
        right_w = max(1, total_width - left_w)
        self.main_splitter.setSizes([left_w, right_w])
        self._left_panel_hidden = False
        self._left_panel_last_width = int(left_w)
        self._set_left_panel_collapsed_limits(False)
        self._set_global_overlay_mode(False)
        self._update_left_panel_toggle_text()
        self._position_left_panel_toggle()

    def _apply_splitter_start_min_left(self):
        sizes = self.main_splitter.sizes()
        total_width = int(sum(sizes)) if sizes else int(self.main_splitter.width())
        if total_width <= 0:
            total_width = int(self.width())
        min_left = int(getattr(self, "_left_min_width", 300))
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if mk in {"4vs2", "4vs4"}:
            # In 4-ship BA modes, start with wide UI panel to avoid text clipping.
            left_target = int(round(total_width * 0.70))
            left_w = max(min_left, left_target)
            left_w = max(1, min(left_w, max(1, total_width - 1)))
        else:
            left_w = max(1, min(min_left, max(1, total_width - 1)))
        right_w = max(1, total_width - left_w)
        self.main_splitter.setSizes([left_w, right_w])
        self._left_panel_hidden = False
        self._left_panel_last_width = int(left_w)
        self._set_left_panel_collapsed_limits(False)
        self._set_global_overlay_mode(False)
        self._update_left_panel_toggle_text()
        self._position_left_panel_toggle()

    def _configure_left_panel_text_policies(self):
        if not hasattr(self, "left_panel"):
            return
        min_lbl_h = QFontMetrics(self.font()).height() + 1
        for lbl in self.left_panel.findChildren(QLabel):
            lbl.setWordWrap(False)
            lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            lbl.setMinimumHeight(min_lbl_h)
            base = lbl.styleSheet().strip()
            pad = "padding-top: 1px; padding-bottom: 1px;"
            if pad not in base:
                lbl.setStyleSheet((base + ("; " if base else "")) + pad)

    def _recompute_left_min_width(self):
        if not hasattr(self, "left_panel"):
            return
        if bool(getattr(self, "_status_panel_hidden", False)) and hasattr(self, "global_group"):
            # When aircraft status panel is hidden, reclaim width for the 3D view.
            self.global_group.adjustSize()
            global_need = int(self.global_group.sizeHint().width()) + 20
            min_left_width = max(220, global_need)
            self._left_min_width = int(min_left_width)
            self.left_panel.setMinimumWidth(max(180, self._left_min_width - 8))
            if hasattr(self, "left_scroll"):
                self.left_scroll.setMinimumWidth(self._left_min_width)
            return
        fm = QFontMetrics(self.font())
        labels = [lbl for lbl in self.left_panel.findChildren(QLabel) if lbl.text()]
        widest_label_text = max([fm.horizontalAdvance(lbl.text()) for lbl in labels], default=0)
        group_titles = [gb.title() for gb in self.left_panel.findChildren(QGroupBox)]
        widest_group_title = max([fm.horizontalAdvance(t) for t in group_titles if t], default=0) + 30
        spin_hints = [w.sizeHint().width() for w in self.left_panel.findChildren(QDoubleSpinBox)]
        combo_hints = [w.sizeHint().width() for w in self.left_panel.findChildren(QComboBox)]
        widest_input = max(spin_hints + combo_hints + [90])
        label_row_need = widest_label_text + widest_input + 54

        row_buttons_1 = [self.btn_adv1, self.btn_adv5, self.btn_adv10, self.btn_back1, self.btn_back5, self.btn_back10]
        row_buttons_2 = [self.btn_reset_step, self.btn_reset, self.btn_save, self.btn_import_scn, self.btn_play_back, self.btn_play, self.btn_stop, self.play_speed]
        spacing = int(getattr(self.global_layout, "horizontalSpacing", lambda: 2)())
        btn_row1_need = sum(b.sizeHint().width() for b in row_buttons_1) + spacing * (len(row_buttons_1) - 1) + 12
        btn_row2_need = sum(b.sizeHint().width() for b in row_buttons_2) + spacing * (len(row_buttons_2) - 1) + 12

        group_hints = [self.controls[aid].group.sizeHint().width() for aid in AIRCRAFT_IDS] if hasattr(self, "controls") else [0]
        pair_need = 0
        if group_hints:
            s = sorted(group_hints, reverse=True)
            pair_need = (s[0] + (s[1] if len(s) > 1 else 0) + 12)
        aircraft_row_need = max(260, pair_need)
        min_left_width = max(250, widest_group_title, label_row_need, btn_row1_need, btn_row2_need, aircraft_row_need)
        self._left_min_width = int(min_left_width)
        self.left_panel.setMinimumWidth(max(220, self._left_min_width - 8))
        if hasattr(self, "left_scroll"):
            self.left_scroll.setMinimumWidth(self._left_min_width)

    def _apply_main_minimum_size(self):
        min_left = int(getattr(self, "_left_min_width", 300))
        min_view = 900
        min_w = min_left + min_view
        min_h = 760
        self.setMinimumSize(min_w, min_h)

    def _debug_check_left_panel_clipping(self):
        if os.environ.get("FA50_UI_DEBUG", "0") != "1":
            return
        if not hasattr(self, "left_panel"):
            return
        for w in self.left_panel.findChildren(QWidget):
            if not w.isVisible():
                continue
            hint = w.sizeHint()
            if hint.isValid() and w.width() > 0 and w.width() < hint.width():
                print(f"[UI-CLIP-WARN] {w.__class__.__name__}: width={w.width()} < sizeHint={hint.width()}")
            if hint.isValid() and w.height() > 0 and w.height() < hint.height():
                print(f"[UI-CLIP-WARN] {w.__class__.__name__}: height={w.height()} < sizeHint={hint.height()}")
        for gb in self.left_panel.findChildren(QGroupBox):
            gh = gb.sizeHint().height()
            if gb.height() > 0 and gb.height() < gh:
                print(f"[UI-CLIP-WARN] QGroupBox({gb.title()}): height={gb.height()} < sizeHint={gh}")

    def _update_aircraft_group_widths(self):
        if not hasattr(self, "aircraft_row") or not hasattr(self, "controls"):
            return
        panel_w = int(self.left_panel.width())
        if hasattr(self, "left_scroll") and self.left_scroll is not None:
            panel_w = max(panel_w, int(self.left_scroll.viewport().width()))
        avail = max(300, panel_w - 8)
        col_w = max(220, avail // 2)
        for aid in AIRCRAFT_IDS:
            self.controls[aid].group.setMaximumWidth(col_w)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if bool(getattr(self, "_status_panel_hidden", False)):
            sizes = self.main_splitter.sizes()
            total = int(sum(sizes)) if sizes else int(self.main_splitter.width())
            if total <= 0:
                total = int(self.width())
            self.main_splitter.setSizes([0, max(1, total)])
            self._left_panel_hidden = True
            self._set_left_panel_collapsed_limits(True)
            self._set_global_overlay_mode(True)
            self._ensure_global_overlay_alive()
            self._update_aircraft_group_widths()
            self._position_left_panel_toggle()
            self._position_view_overlays()
            return
        if (
            bool(getattr(self, "_splitter_ratio_initialized", False))
            and (not bool(getattr(self, "_left_panel_hidden", False)))
            and (not bool(getattr(self, "_startup_min_left_applied", False)))
            and (self.width() > 640)
        ):
            self._apply_splitter_start_min_left()
            self._startup_min_left_applied = True
        self._update_aircraft_group_widths()
        self._position_left_panel_toggle()
        self._ensure_global_overlay_alive()
        self._position_view_overlays()

    @staticmethod
    def _safe_heading_pitch_velocity_unit(hdg_deg: float, pitch_deg: float) -> np.ndarray:
        hdg = 0.0 if np.isnan(hdg_deg) else float(hdg_deg)
        pitch = 0.0 if np.isnan(pitch_deg) else float(pitch_deg)
        pitch_rad = math.radians(pitch)
        hdg_rad = math.radians(hdg)
        return np.array(
            [
                math.sin(hdg_rad) * math.cos(pitch_rad),
                math.cos(hdg_rad) * math.cos(pitch_rad),
                math.sin(pitch_rad),
            ],
            dtype=float,
        )

    def _state_velocity_vector_ftps(self, st: Dict) -> np.ndarray:
        tas_kt = float(st.get("tas_kt", np.nan))
        if np.isnan(tas_kt):
            tas_kt = self._tas_from_cas(float(st.get("cas_kt", 0.0)), float(st.get("z_ft", 0.0)))
        tas_ftps = tas_kt * KT_TO_FTPS
        u_v = self._safe_heading_pitch_velocity_unit(float(st.get("hdg_deg", 0.0)), float(st.get("pitch_deg", 0.0)))
        return tas_ftps * u_v

    def _compute_relative_geometry(self, own: Dict, tgt: Dict) -> Dict[str, float]:
        dx = float(tgt["x_ft"]) - float(own["x_ft"])
        dy = float(tgt["y_ft"]) - float(own["y_ft"])
        dz = float(tgt["z_ft"]) - float(own["z_ft"])
        rh_ft = math.hypot(dx, dy)
        r_ft = math.sqrt(dx * dx + dy * dy + dz * dz)
        rng_nm = r_ft / NM_TO_FT

        brg_deg = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0
        rb_deg = self._wrap_to_pm180(brg_deg - float(own["hdg_deg"]))

        if rh_ft < 1e-6:
            if dz > 0.0:
                el_deg = 90.0
            elif dz < 0.0:
                el_deg = -90.0
            else:
                el_deg = 0.0
        else:
            el_deg = math.degrees(math.atan2(dz, max(rh_ft, 1e-6)))

        u_los = np.array([dx, dy, dz], dtype=float) / max(r_ft, 1e-6)
        u_v_own = self._safe_heading_pitch_velocity_unit(float(own["hdg_deg"]), float(own.get("pitch_deg", 0.0)))
        dot_v_los = float(np.clip(np.dot(u_v_own, u_los), -1.0, 1.0))
        ata_deg = math.degrees(math.acos(dot_v_los))

        # Signed ATA in horizontal plane, right side is positive.
        los_h_norm = math.hypot(dx, dy)
        if los_h_norm < 1e-9:
            ata_signed_deg = 0.0
        else:
            hdg_rad = math.radians(float(own["hdg_deg"]))
            fwd_h = np.array([math.sin(hdg_rad), math.cos(hdg_rad)], dtype=float)
            los_h = np.array([dx, dy], dtype=float) / los_h_norm
            dot_h = float(np.clip(np.dot(fwd_h, los_h), -1.0, 1.0))
            cross_z = float(fwd_h[0] * los_h[1] - fwd_h[1] * los_h[0])
            ata_signed_deg = -math.degrees(math.atan2(cross_z, dot_h))

        v_rel = self._state_velocity_vector_ftps(tgt) - self._state_velocity_vector_ftps(own)
        closure_ftps = -float(np.dot(v_rel, u_los))
        closure_kt = closure_ftps / KT_TO_FTPS

        return {
            "brg_deg": brg_deg,
            "rb_deg": rb_deg,
            "rng_nm": rng_nm,
            "el_deg": el_deg,
            "ata_deg": ata_deg,
            "ata_signed_deg": ata_signed_deg,
            "closure_kt": closure_kt,
        }

    def _format_relative_lines(self, aid: str, cur_states: Dict[str, Dict]) -> List[str]:
        lines = []
        own = cur_states[aid]
        for tgt_id in AIRCRAFT_IDS:
            if tgt_id == aid:
                continue
            rel = self._compute_relative_geometry(own, cur_states[tgt_id])
            lines.append(f"To {tgt_id}: {self._format_los_short(rel)}")
        return lines

    def _build_los_summary_lines(self, cur_states: Dict[str, Dict]) -> List[str]:
        lines = []
        for a, b in self.los_pairs:
            rel = self._compute_relative_geometry(cur_states[a], cur_states[b])
            lines.append(f"{a.replace('#', '')}-{b.replace('#', '')}: {self._format_los_short(rel)}")
        return lines

    @staticmethod
    def _format_los_short(rel: Dict[str, float]) -> str:
        ata_signed = float(rel.get("ata_signed_deg", 0.0))
        ata_abs = int(round(abs(ata_signed)))
        if ata_abs == 0:
            ata_txt = "0"
        else:
            ata_txt = f"{ata_abs}{'R' if ata_signed >= 0.0 else 'L'}"
        rng_nm = float(rel.get("rng_nm", 0.0))
        el_signed = float(rel.get("el_deg", 0.0))
        el_i = int(round(el_signed))
        if el_i == 0:
            pitch_txt = "0°"
        else:
            pitch_txt = f"{el_i:+d}°"
        return f"{ata_txt}/{rng_nm:.1f}nm/{pitch_txt}"

    @staticmethod
    def _signed_deg_label_rounded10(v_deg: float, use_lr: bool = True, width: int = 2) -> str:
        v = float(v_deg)
        mag = int(round(abs(v) / 10.0) * 10)
        mag = max(0, min(180, mag))
        if mag == 0:
            return "0".rjust(width, "0")
        if not use_lr:
            return str(mag).rjust(width, "0")
        side = "R" if v >= 0.0 else "L"
        return f"{str(mag).rjust(width, '0')}{side}"

    @staticmethod
    def _signed_deg_label_1deg(v_deg: float, use_lr: bool = True, width: int = 2) -> str:
        v = float(v_deg)
        mag = int(abs(v))  # 1-degree unit (truncate)
        mag = max(0, min(180, mag))
        if mag == 0:
            return "0".rjust(width, "0")
        if not use_lr:
            return str(mag).rjust(width, "0")
        side = "R" if v >= 0.0 else "L"
        return f"{str(mag).rjust(width, '0')}{side}"

    def _aa_label_from_target_tail(self, own: Dict, tgt: Dict) -> str:
        dx = float(own["x_ft"]) - float(tgt["x_ft"])
        dy = float(own["y_ft"]) - float(tgt["y_ft"])
        brg_tgt_to_own = self._wrap_hdg(math.degrees(math.atan2(dx, dy)))
        tail_hdg = self._wrap_hdg(float(tgt.get("hdg_deg", 0.0)) + 180.0)
        delta = self._wrap_to_pm180(brg_tgt_to_own - tail_hdg)
        # Requirement: clockwise from target tail -> L, counterclockwise -> R.
        bins = int(round(abs(delta) / 10.0))
        bins = max(0, min(18, bins))
        if bins == 0:
            return "00"
        side = "L" if delta > 0.0 else "R"
        return f"{bins:02d}{side}"

    def _format_los_label_for_pair(self, a: str, b: str, cur_states: Dict[str, Dict]) -> str:
        if {a, b} == {"#1", "#2"}:
            # Always show ATA on #1-#2 LOS as seen from #2 toward #1.
            rel_21 = self._compute_relative_geometry(cur_states["#2"], cur_states["#1"])
            return self._format_los_short(rel_21)
        rel = self._compute_relative_geometry(cur_states[a], cur_states[b])
        ba, ra = self._ba_ra_sets_for_current_mode()
        if ((a in ba and b in ra) or (a in ra and b in ba)):
            own_id = a if a in ba else b
            tgt_id = b if own_id == a else a
            own = cur_states[own_id]
            tgt = cur_states[tgt_id]
            aa_txt = self._aa_label_from_target_tail(own, tgt)
            top = f"{aa_txt}/{float(rel.get('rng_nm', 0.0)):.1f}nm"
            rb_txt = self._signed_deg_label_1deg(float(rel.get("rb_deg", 0.0)), use_lr=True, width=3)
            el = float(rel.get("el_deg", 0.0))
            el_i = int(el)  # 1-degree unit (truncate), signed
            el_txt = "0°" if el_i == 0 else f"{el_i:+d}°"
            return f"{top}\n{rb_txt}/{el_txt}"
        return self._format_los_short(rel)

    def _format_los_label_for_custom_link(self, a: str, b: str, cur_states: Dict[str, Dict], src_aid: Optional[str] = None) -> str:
        src = str(src_aid or "").strip()
        # For custom LOS, respect creator-side perspective.
        # - src in BA: mixed-pair labels use BA side only
        # - src in RA: show RA side only when src aircraft is part of the pair
        if {a, b} == {"#1", "#2"}:
            rel_21 = self._compute_relative_geometry(cur_states["#2"], cur_states["#1"])
            return self._format_los_short(rel_21)
        ba, ra = self._ba_ra_sets_for_current_mode()
        if ((a in ba and b in ra) or (a in ra and b in ba)):
            own_id: Optional[str] = None
            if src in ba:
                own_id = a if a in ba else b
            elif src in ra:
                if src in (a, b):
                    own_id = src
            if own_id is not None:
                tgt_id = b if own_id == a else a
                rel = self._compute_relative_geometry(cur_states[own_id], cur_states[tgt_id])
                aa_txt = self._aa_label_from_target_tail(cur_states[own_id], cur_states[tgt_id])
                top = f"{aa_txt}/{float(rel.get('rng_nm', 0.0)):.1f}nm"
                rb_txt = self._signed_deg_label_1deg(float(rel.get("rb_deg", 0.0)), use_lr=True, width=3)
                el = float(rel.get("el_deg", 0.0))
                el_i = int(el)
                el_txt = "0°" if el_i == 0 else f"{el_i:+d}°"
                return f"{top}\n{rb_txt}/{el_txt}"
        return self._format_los_label_for_pair(a, b, cur_states)

    def _build_los_overlay_text(self, a: str, b: str, cur_states: Dict[str, Dict]) -> str:
        return self._format_los_label_for_pair(a, b, cur_states)

    def _label_anchor_from_arrow(self, aid: str, cur_states: Dict[str, Dict]) -> np.ndarray:
        st = cur_states[aid]
        pos = np.array([float(st["x_ft"]), float(st["y_ft"]), float(st["z_ft"])], dtype=float)
        hdg_deg = float(st["hdg_deg"])
        hlen = self._arrow_len_for_aircraft(aid, step_idx=self.current_step, step_mode=True)
        hdg_rad = math.radians(hdg_deg)
        fwd = np.array([math.sin(hdg_rad), math.cos(hdg_rad), 0.0], dtype=float)
        perp = np.array([math.sin(hdg_rad - math.pi / 2.0), math.cos(hdg_rad - math.pi / 2.0), 0.0], dtype=float)
        shaft_start = pos + fwd * ARROW_BASE_GAP_FT
        shaft_tip = shaft_start + fwd * max(hlen - ARROW_BASE_GAP_FT, ARROW_MIN_SHAFT_LEN_FT)
        anchor = shaft_tip + perp * 250.0
        anchor[2] = pos[2]
        return anchor

    def update_ata_labels(self, cur_states: Optional[Dict[str, Dict]] = None, step_mode: Optional[bool] = None, verbose: bool = False):
        self._update_view_mode_from_camera()
        if not hasattr(self, "ata_labels"):
            return
        if (not hasattr(self, "view")) or (self.view is None) or (not hasattr(self.view, "_project_point")):
            for lbl in getattr(self, "ata_labels", {}).values():
                lbl.hide()
            if hasattr(self, "custom_los_drag_line"):
                self.custom_los_drag_line.setVisible(False)
            for it in getattr(self, "custom_los_line_items", []):
                it.setVisible(False)
            for lbl in getattr(self, "custom_los_link_labels", []):
                lbl.hide()
            self._hide_all_step_number_labels()
            return
        if cur_states is None:
            if not self.state_history:
                if hasattr(self, "custom_los_drag_line"):
                    self.custom_los_drag_line.setVisible(False)
                for it in getattr(self, "custom_los_line_items", []):
                    it.setVisible(False)
                for lbl in getattr(self, "custom_los_link_labels", []):
                    lbl.hide()
                self._hide_all_step_number_labels()
                return
            cur_states = self.state_history[self.current_step]
        if step_mode is None:
            step_mode = self.view_mode.currentText() == "Step View"

        playback_running = bool(getattr(self, "playback_running", False))
        playback_mode = playback_running or bool(getattr(self, "playback_active", False))
        los_toggle_on = bool(self.chk_show_los.isChecked())
        # Built-in LOS lines are shown in Step View only.
        # Overview View displays only user-created custom LOS links.
        show_los = los_toggle_on and bool(step_mode)
        if bool(step_mode) and bool(getattr(self, "hide_los_in_step_view", False)):
            show_los = False
        active_pairs = set(self._active_los_pairs())
        forced_dir_by_pairkey: Dict[Tuple[str, str], Tuple[str, str]] = {}
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if bool(step_mode) and (mk in {"1vs1", "2vs1", "2vs2"}):
            # Force-on fixed LOS set in Step View for 1vs1/2vs1/2vs2.
            show_los = True
            active_pairs = set()
            hidden = self.default_step_los_hidden.get((mk, int(self.current_step)), set())
            for src, dst in self._forced_step_default_pairs_by_mode(mk):
                if (src, dst) in hidden:
                    continue
                if (src not in cur_states) or (dst not in cur_states):
                    continue
                pk = (src, dst) if (src, dst) in self.los_items else ((dst, src) if (dst, src) in self.los_items else None)
                if pk is None:
                    continue
                active_pairs.add(pk)
                forced_dir_by_pairkey[pk] = (src, dst)
        stack_by_anchor = {aid: 0 for aid in AIRCRAFT_IDS}
        occupied_rects: List[Tuple[int, int, int, int]] = []

        for pair in self.los_pairs:
            try:
                a, b = pair
                line_item = self.los_items[pair]
                label = self.ata_labels[pair]

                if (not show_los) or (pair not in active_pairs):
                    line_item.setVisible(False)
                    label.hide()
                    continue

                pa = cur_states[a]
                pb = cur_states[b]
                style_dyn = self._los_style_for_pair(a, b)
                src_dir = None
                dst_dir = None
                if pair in forced_dir_by_pairkey:
                    src_dir, dst_dir = forced_dir_by_pairkey[pair]
                    csrc = self._aircraft_color(src_dir)
                    style_dyn = {"color": (csrc[0], csrc[1], csrc[2], 0.35), "text_color": self._hex_from_rgb01((csrc[0], csrc[1], csrc[2]))}
                pts = np.array(
                    [
                        [pa["x_ft"], pa["y_ft"], pa["z_ft"]],
                        [pb["x_ft"], pb["y_ft"], pb["z_ft"]],
                    ],
                    dtype=float,
                )
                line_item.setData(pos=pts, color=style_dyn["color"], width=1.0, antialias=True, mode="lines")
                line_item.setVisible(True)
                label.setStyleSheet(
                    "QLabel {"
                    " font-size: 10pt;"
                    f" color: {style_dyn['text_color']};"
                    " background-color: rgba(255, 255, 255, 0);"
                    " border: none;"
                    " padding: 0px;"
                    "}"
                )

                if src_dir is not None and dst_dir is not None:
                    anchor_aid = src_dir
                    anchor_world = self._label_anchor_from_arrow(anchor_aid, cur_states)
                elif pair == ("#1", "#2"):
                    pa = cur_states["#1"]
                    pb = cur_states["#2"]
                    if str(getattr(self, "current_mode_key", "")).strip() == "2vs2":
                        anchor_aid = "#2"
                        anchor_world = self._label_anchor_from_arrow("#2", cur_states)
                    else:
                        anchor_world = np.array(
                            [
                                0.5 * (float(pa["x_ft"]) + float(pb["x_ft"])),
                                0.5 * (float(pa["y_ft"]) + float(pb["y_ft"])),
                                0.5 * (float(pa["z_ft"]) + float(pb["z_ft"])),
                            ],
                            dtype=float,
                        )
                        anchor_aid = None
                else:
                    # For all other pairs, place label near ownship(a) arrow.
                    anchor_aid = a
                    anchor_world = self._label_anchor_from_arrow(anchor_aid, cur_states)
                sp = self.view._project_point(anchor_world)

                rel = self._compute_relative_geometry(cur_states[a], cur_states[b])
                if src_dir is not None and dst_dir is not None:
                    label.setText(self._format_los_label_for_custom_link(src_dir, dst_dir, cur_states, src_aid=src_dir))
                else:
                    label.setText(self._format_los_label_for_pair(a, b, cur_states))
                label.adjustSize()
                lw = int(label.width())
                lh = int(label.height())
                vw = int(self.view.width())
                vh = int(self.view.height())

                if sp is None:
                    label.hide()
                    if verbose:
                        print(f"[ATA-LBL] pair={a}->{b} anchor={anchor_world.tolist()} proj=None visible=False")
                    continue

                if anchor_aid is None:
                    idx = 0
                else:
                    idx = stack_by_anchor.get(anchor_aid, 0)
                    stack_by_anchor[anchor_aid] = idx + 1
                x, y = self._place_overlay_label_xy(
                    sp=sp,
                    lw=lw,
                    lh=lh,
                    vw=vw,
                    vh=vh,
                    occupied_rects=occupied_rects,
                    base_x=6,
                    base_y=6 + idx * 16,
                )
                label.move(x, y)
                occupied_rects.append((x, y, lw, lh))
                label.show()
                if verbose:
                    print(f"[ATA-LBL] pair={a}->{b} anchor={anchor_world.tolist()} proj=({int(sp[0])},{int(sp[1])}) visible=True")
            except Exception:
                if pair in self.ata_labels:
                    self.ata_labels[pair].hide()

        # Custom LOS links:
        # - Step-origin LOS: visible in Step View, uses current completed step during playback.
        # - Overview-origin LOS: hidden before its step, then stays visible after that step.
        show_custom_los = los_toggle_on
        self._ensure_custom_los_render_capacity()
        active_ids = set(self._active_aircraft_ids())
        for i, link in enumerate(self.custom_los_links):
            line_item = self.custom_los_line_items[i]
            lbl = self.custom_los_link_labels[i]
            if not show_custom_los:
                line_item.setVisible(False)
                lbl.hide()
                continue
            link_origin = str(link.get("origin", "overview"))
            if bool(step_mode):
                if link_origin != "step":
                    line_item.setVisible(False)
                    lbl.hide()
                    continue
            else:
                if link_origin != "overview":
                    line_item.setVisible(False)
                    lbl.hide()
                    continue
            try:
                a = str(link.get("a"))
                b = str(link.get("b"))
                link_step_i = int(link.get("step", -1))
            except Exception:
                line_item.setVisible(False)
                lbl.hide()
                continue
            # Step View: use current completed step in realtime.
            # (During interpolation, current_step is floor(playback_step_float),
            # so LOS stays on last completed step until next step completes.)
            # Overview View:
            # - Stopped: keep original link step behavior.
            # - Playing: hide until link step, then keep visible afterwards.
            if bool(step_mode):
                step_i = int(max(0, min(int(self.current_step), len(self.state_history) - 1)))
            else:
                if playback_running or bool(getattr(self, "playback_active", False)):
                    cur_play_step = int(max(0, min(int(self.current_step), len(self.state_history) - 1)))
                    if cur_play_step < int(link_step_i):
                        line_item.setVisible(False)
                        lbl.hide()
                        continue
                    step_i = cur_play_step
                else:
                    step_i = int(link_step_i)
            valid = (a in active_ids) and (b in active_ids) and (0 <= step_i < len(self.state_history))
            if not valid:
                line_item.setVisible(False)
                lbl.hide()
                continue
            sa = self.state_history[step_i][a]
            sb = self.state_history[step_i][b]
            pa = self._los_anchor_world(a, step_i, bool(step_mode))
            pb = self._los_anchor_world(b, step_i, bool(step_mode))
            if pa is None:
                pa = np.array([float(sa["x_ft"]), float(sa["y_ft"]), float(sa["z_ft"])], dtype=float)
            if pb is None:
                pb = np.array([float(sb["x_ft"]), float(sb["y_ft"]), float(sb["z_ft"])], dtype=float)
            pts = np.array(
                [
                    [float(pa[0]), float(pa[1]), float(pa[2])],
                    [float(pb[0]), float(pb[1]), float(pb[2])],
                ],
                dtype=float,
            )
            style_default = self.los_styles.get((a, b), self.los_styles.get((b, a), {"color": (0.0, 0.0, 0.0, 0.35), "text_color": "#111111"}))
            style_color = link.get("color", style_default["color"])
            if isinstance(style_color, list):
                style_color = tuple(style_color)
            if (not isinstance(style_color, tuple)) or (len(style_color) != 4):
                style_color = style_default["color"]
            style_text = str(link.get("text_color", style_default["text_color"]))
            line_item.setData(pos=pts, color=style_color, width=1.0, antialias=True, mode="lines")
            line_item.setVisible(True)
            rel = self._compute_relative_geometry(sa, sb)
            lbl.setText(self._format_los_label_for_custom_link(a, b, self.state_history[step_i], src_aid=str(link.get("src_aid", ""))))
            lbl.setStyleSheet(
                "QLabel {"
                " font-size: 10pt;"
                f" color: {style_text};"
                " background-color: rgba(255, 255, 255, 0);"
                " border: none;"
                " padding: 0px;"
                "}"
            )
            lbl.adjustSize()
            anchor_world = np.array(
                [
                    0.5 * (float(pa[0]) + float(pb[0])),
                    0.5 * (float(pa[1]) + float(pb[1])),
                    0.5 * (float(pa[2]) + float(pb[2])),
                ],
                dtype=float,
            )
            sp = self.view._project_point(anchor_world)
            if sp is None:
                lbl.hide()
                continue
            lw = int(lbl.width())
            lh = int(lbl.height())
            vw = int(self.view.width())
            vh = int(self.view.height())
            x, y = self._place_overlay_label_xy(
                sp=sp,
                lw=lw,
                lh=lh,
                vw=vw,
                vh=vh,
                occupied_rects=occupied_rects,
                base_x=6,
                base_y=6,
            )
            lbl.move(x, y)
            occupied_rects.append((x, y, lw, lh))
            lbl.show()
        for j in range(len(self.custom_los_links), len(self.custom_los_line_items)):
            self.custom_los_line_items[j].setVisible(False)
            self.custom_los_link_labels[j].hide()
        if self.custom_link_drag_src is None:
            self.custom_los_drag_line.setVisible(False)
        self.update_step_number_labels(step_mode=step_mode)

    def _build_or_update_ground_plane(self):
        if self._has_dca_mission_area():
            extent = max(1000.0, float(self.grid_extent_ft))
        else:
            extent = max(float(self.grid_extent_ft), float(GROUND_MIN_EXTENT_FT))
        if extent <= 0.0:
            return
        for it in self.ground_plane_items:
            self.view.removeItem(it)
        self.ground_plane_items = []
        verts = np.array(
            [
                [-extent, -extent, -5.0],
                [extent, -extent, -5.0],
                [extent, extent, -5.0],
                [-extent, extent, -5.0],
            ],
            dtype=float,
        )
        faces_up = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        faces_down = np.array([[2, 1, 0], [3, 2, 0]], dtype=np.int32)
        face_colors = np.array(
            [
                [210.0 / 255.0, 245.0 / 255.0, 210.0 / 255.0, 0.30],
                [210.0 / 255.0, 245.0 / 255.0, 210.0 / 255.0, 0.30],
            ],
            dtype=float,
        )
        item_up = gl.GLMeshItem(
            vertexes=verts,
            faces=faces_up,
            faceColors=face_colors,
            smooth=False,
            drawEdges=False,
            shader="balloon",
            drawFaces=True,
        )
        item_down = gl.GLMeshItem(
            vertexes=verts,
            faces=faces_down,
            faceColors=face_colors,
            smooth=False,
            drawEdges=False,
            shader="balloon",
            drawFaces=True,
        )
        item_up.setGLOptions("translucent")
        item_down.setGLOptions("translucent")
        self.view.addItem(item_up)
        self.view.addItem(item_down)
        self.ground_plane_items = [item_up, item_down]

    def _initial_states(self) -> Dict[str, Dict]:
        st = {}
        ac1 = self.controls["#1"]
        r1_ft = float(ac1.range_nm.value()) * NM_TO_FT
        b1 = math.radians(float(ac1.bearing_deg.value()))
        st["#1"] = {
            "x_ft": r1_ft * math.sin(b1),
            "y_ft": r1_ft * math.cos(b1),
            "z_ft": float(ac1.alt_ft.value()),
            "hdg_deg": self._wrap_hdg(float(ac1.hdg_deg.value())),
            "cas_kt": float(ac1.cas_kt.value()),
            "tas_kt": self._tas_from_cas(float(ac1.cas_kt.value()), float(ac1.alt_ft.value())),
            "ps_fps": np.nan,
            "g_cmd": np.nan,
            "g_cmd_effective": np.nan,
            "g_used": np.nan,
            "pitch_deg": 0.0,
            "bank_cmd_user": np.nan,
            "bank_used": np.nan,
            "power": "",
            "turn": "S",
            "clamped": False,
            "feasible": True,
            "cas_before": np.nan,
            "dV_ktsps": np.nan,
            "cas_after": np.nan,
            "tan_bank": np.nan,
            "bank_deg": np.nan,
            "radius_nm": np.nan,
            "radius_ft": np.nan,
            "g_max": np.nan,
            "turn_cmd_user": "S",
            "turn_effective": "S",
            "ps_primary": np.nan,
            "ps_fallback_1g_straight": np.nan,
            "ps_final": np.nan,
            "clamp_note": "",
            "turn_note": "",
        }

        for aid in AIRCRAFT_IDS[1:]:
            ac = self.controls[aid]
            r_ft = float(ac.range_nm.value()) * NM_TO_FT
            mk = str(getattr(self, "current_mode_key", "")).strip()
            if aid == "#4":
                ref = st["#3"]
                rel_b = float(ac.bearing_deg.value())
                world_b = self._wrap_hdg(float(ref["hdg_deg"]) + rel_b)
                b = math.radians(world_b)
                x = float(ref["x_ft"]) + r_ft * math.sin(b)
                y = float(ref["y_ft"]) + r_ft * math.cos(b)
            elif aid == "#6" and mk in {"4vs2", "4vs4"}:
                ref = st["#5"]
                rel_b = float(ac.bearing_deg.value())
                world_b = self._wrap_hdg(float(ref["hdg_deg"]) + rel_b)
                b = math.radians(world_b)
                x = float(ref["x_ft"]) + r_ft * math.sin(b)
                y = float(ref["y_ft"]) + r_ft * math.cos(b)
            elif aid == "#7" and mk in {"4vs2", "4vs4"}:
                ref = st["#5"]
                rel_b = float(ac.bearing_deg.value())
                world_b = self._wrap_hdg(float(ref["hdg_deg"]) + rel_b)
                b = math.radians(world_b)
                x = float(ref["x_ft"]) + r_ft * math.sin(b)
                y = float(ref["y_ft"]) + r_ft * math.cos(b)
            elif aid == "#8" and mk in {"4vs2", "4vs4"}:
                ref = st["#7"]
                rel_b = float(ac.bearing_deg.value())
                world_b = self._wrap_hdg(float(ref["hdg_deg"]) + rel_b)
                b = math.radians(world_b)
                x = float(ref["x_ft"]) + r_ft * math.sin(b)
                y = float(ref["y_ft"]) + r_ft * math.cos(b)
            else:
                b = math.radians(float(ac.bearing_deg.value()))
                x = r_ft * math.sin(b)
                y = r_ft * math.cos(b)
            alt = float(ac.alt_ft.value())
            cas = float(ac.cas_kt.value())
            st[aid] = {
                "x_ft": x,
                "y_ft": y,
                "z_ft": alt,
                "hdg_deg": self._wrap_hdg(float(ac.hdg_deg.value())),
                "cas_kt": cas,
                "tas_kt": self._tas_from_cas(cas, alt),
                "ps_fps": np.nan,
                "g_cmd": np.nan,
                "g_cmd_effective": np.nan,
                "g_used": np.nan,
                "pitch_deg": 0.0,
                "bank_cmd_user": np.nan,
                "bank_used": np.nan,
                "power": "",
                "turn": "S",
                "clamped": False,
                "feasible": True,
                "cas_before": np.nan,
                "dV_ktsps": np.nan,
                "cas_after": np.nan,
                "tan_bank": np.nan,
                "bank_deg": np.nan,
                "radius_nm": np.nan,
                "radius_ft": np.nan,
                "g_max": np.nan,
                "turn_cmd_user": "S",
                "turn_effective": "S",
                "ps_primary": np.nan,
                "ps_fallback_1g_straight": np.nan,
                "ps_final": np.nan,
                "clamp_note": "",
                "turn_note": "",
            }
        return st

    def _find_ps_with_clamp(self, power: str, cas_kt: float, alt_ft: float, g_cmd: float):
        g_used, ps, clamped, _reason, _attempts = find_max_feasible_g(self.db, power, cas_kt, alt_ft, g_cmd, 0.0, "CW")
        if g_used is None:
            return np.nan, 1.0, True, False
        return ps, g_used, clamped, True

    def _find_g_max(self, power: str, cas_kt: float, alt_ft: float, g_cap: float = 9.0):
        g_used, _ps, _clamped, _reason, _attempts = find_max_feasible_g(self.db, power, cas_kt, alt_ft, g_cap, 0.0, "CW")
        if g_used is not None:
            return float(g_used)
        return np.nan

    def _compute_step0_locked_ps(self, aid: str) -> float:
        if not self.state_history:
            return 0.0
        base = self.state_history[0][aid]
        cmd = self.controls[aid].read_command()
        power = cmd["power"]
        turn = cmd["turn"]
        g_cmd = float(cmd["g_cmd"])
        cas = float(base["cas_kt"])
        alt = float(base["z_ft"])
        if turn == "S":
            ps = self.db.lookup_ps(power, cas, 1.0, alt)
        else:
            g_used, ps_found, _clamped, _reason, _attempts = find_max_feasible_g(self.db, power, cas, alt, g_cmd, 0.0, turn)
            if g_used is not None:
                ps = ps_found
            else:
                ps = self.db.lookup_ps(power, cas, 1.0, alt)
        if np.isnan(ps):
            return 0.0
        return float(ps)

    def _simulate_one(self, aid: str, s: Dict, cmd: Dict, dt: float, step_idx: int) -> Dict:
        speed_lock_on = self._effective_hold_for_step(step_idx, aid)
        cas = float(s["cas_kt"])
        hold_source_step = self._effective_hold_source_step(step_idx, aid)
        if speed_lock_on and hold_source_step is not None:
            cas = float(self.lock_speed_value_by_step.get(hold_source_step, {}).get(aid, cas))
        alt = float(s["z_ft"])
        hdg = float(s["hdg_deg"])
        x = float(s["x_ft"])
        y = float(s["y_ft"])
        dt_use = max(float(dt), 1e-6)

        power = cmd["power"]
        turn_cmd_user = cmd["turn"]
        turn_effective = turn_cmd_user
        g_cmd_user = float(cmd["g_cmd"])
        if bool(cmd.get("g_use_max", False)):
            gmax_now = self._find_g_max(power, cas, alt, g_cap=9.0)
            if not np.isnan(gmax_now):
                g_cmd_user = quantize_g_01(gmax_now, min_g=1.0, max_g=9.0)
        level_hold = bool(cmd.get("level_hold", False))
        pitch_hold = bool(cmd.get("pitch_hold", False))
        g_cmd_q = quantize_g_01(g_cmd_user, min_g=1.0, max_g=9.0)
        g_cmd_effective = 1.0 if turn_cmd_user == "S" else g_cmd_q
        pitch_prev = float(s.get("pitch_deg", 0.0))
        pitch_cmd_user = float(cmd.get("pitch_deg", pitch_prev))
        pull_mode = str(cmd.get("pull_mode", "NONE")).upper()
        if pull_mode not in {"UP", "DOWN", "NONE"}:
            pull_mode = "NONE"
        bank_cmd_user = quantize_bank_deg(float(cmd.get("bank_deg", 0.0)), min_bank=0.0, max_bank=180.0)
        pitch_rad = math.radians(pitch_prev)

        g_max = np.nan
        ps_primary = np.nan
        ps_fallback_1g = np.nan
        clamp_note = ""
        turn_note = ""
        speed_domain_error = not self.db.cas_in_supported_range(power, cas)
        g_scan_first12 = [float(v) for _, v in zip(range(12), g_candidates_01(g_cmd_q, 1.0))]
        g_scan_first8 = g_scan_first12[:8]
        clamp_event_logged = False
        if speed_lock_on:
            if hold_source_step is not None:
                ps_final = float(self.lock_ps_value_by_step.get(hold_source_step, {}).get(aid, 0.0))
            else:
                ps_final = 0.0
            if turn_cmd_user == "S":
                g_used = 1.0
            else:
                g_used = quantize_g_01(g_cmd_q, min_g=1.0, max_g=9.0)
            clamped = g_used < (g_cmd_user - 1e-9)
            feasible = True
        else:
            g_max_used, _gmax_ps, _gmax_clamped, _gmax_reason, _gmax_attempts = find_max_feasible_g(
                self.db, power, cas, alt, 9.0, pitch_prev, turn_cmd_user
            )
            g_max = np.nan if g_max_used is None else float(g_max_used)
            ps_primary = self.db.lookup_ps(power, cas, g_cmd_q, alt)
            if turn_cmd_user == "S":
                g_used = 1.0
                ps_final = self.db.lookup_ps(power, cas, 1.0, alt)
                clamped = g_used < (g_cmd_user - 1e-9)
                feasible = not np.isnan(ps_final)
                if clamped:
                    clamp_note = f"G limited: {g_cmd_user:.1f} -> {g_used:.1f}"
            else:
                g_found, ps_found, clamped, reason, clamp_attempts = find_max_feasible_g(
                    self.db, power, cas, alt, g_cmd_q, pitch_prev, turn_cmd_user
                )
                if g_found is not None:
                    g_used = float(g_found)
                    ps_final = float(ps_found)
                    feasible = True
                    if clamped:
                        print(f"[G-CLAMP] step={self.current_step} {aid} user={g_cmd_user:.1f} used={g_used:.1f} (step=0.1)")
                        clamp_note = reason
                        print("Clamp candidates (first 8): " + " ".join(f"{v:.1f}" for v in g_scan_first8))
                        for at in clamp_attempts[:5]:
                            print(
                                "g_try={:.1f} -> g_left={:.1f} g_right={:.1f} ps10_left={:.3f} ps10_right={:.3f} ps20_left={:.3f} ps20_right={:.3f} -> ps={}".format(
                                    float(at.get("g_try", np.nan)),
                                    float(at.get("g_left_10", np.nan)),
                                    float(at.get("g_right_10", np.nan)),
                                    float(at.get("ps_left_10", np.nan)),
                                    float(at.get("ps_right_10", np.nan)),
                                    float(at.get("ps_left_20", np.nan)),
                                    float(at.get("ps_right_20", np.nan)),
                                    "nan" if np.isnan(float(at.get("ps_final", np.nan))) else f"{float(at.get('ps_final', np.nan)):.3f}",
                                )
                            )
                        clamp_event_logged = True
                else:
                    print("Clamp candidates (first 8): " + " ".join(f"{v:.1f}" for v in g_scan_first8))
                    for at in clamp_attempts[:5]:
                        print(
                            "g_try={:.1f} -> g_left={:.1f} g_right={:.1f} ps10_left={:.3f} ps10_right={:.3f} ps20_left={:.3f} ps20_right={:.3f} -> ps={}".format(
                                float(at.get("g_try", np.nan)),
                                float(at.get("g_left_10", np.nan)),
                                float(at.get("g_right_10", np.nan)),
                                float(at.get("ps_left_10", np.nan)),
                                float(at.get("ps_right_10", np.nan)),
                                float(at.get("ps_left_20", np.nan)),
                                float(at.get("ps_right_20", np.nan)),
                                "nan" if np.isnan(float(at.get("ps_final", np.nan))) else f"{float(at.get('ps_final', np.nan)):.3f}",
                            )
                        )
                    clamp_event_logged = True
                    turn_effective = "S"
                    g_used = 1.0
                    ps_fallback_1g = self.db.lookup_ps(power, cas, 1.0, alt)
                    if not np.isnan(ps_fallback_1g):
                        ps_final = ps_fallback_1g
                        feasible = True
                        clamped = True
                        clamp_note = "No feasible turn G at this CAS/ALT/POWER"
                        turn_note = "TURN FORCED TO S (TURN INFEASIBLE)"
                    else:
                        ps_final = np.nan
                        feasible = False
                        speed_domain_error = True
                        clamped = True
                        clamp_note = "No feasible turn G at this CAS/ALT/POWER"
                        turn_note = "TURN FORCED TO S (TURN INFEASIBLE)"
        if clamped and (not clamp_event_logged):
            print("Clamp candidates (first 8): " + " ".join(f"{v:.1f}" for v in g_scan_first8))

        g_cmd_effective = 1.0 if turn_effective == "S" else g_cmd_user
        tas_kt = self._tas_from_cas(cas, alt)
        tas_ftps = tas_kt * KT_TO_FTPS
        pitch_used = pitch_prev
        pitch_clamped = False

        if not feasible:
            bank_safe = quantize_bank_deg(float(s.get("bank_deg", bank_cmd_user)), min_bank=0.0, max_bank=180.0)
            if (str(turn_effective).upper() == "S") or (str(turn_cmd_user).upper() == "S"):
                bank_safe = 0.0
            bank_rad_safe = math.radians(bank_safe)
            tan_bank_safe = math.tan(bank_rad_safe) if abs(abs(bank_safe) - 90.0) > 1e-9 else math.copysign(1e6, bank_safe if bank_safe != 0.0 else 1.0)
            return {
                **s,
                "tas_kt": tas_kt,
                "ps_fps": np.nan,
                "g_cmd": g_cmd_user,
                "g_cmd_effective": g_cmd_effective,
                "g_used": 1.0 if np.isnan(g_used) else g_used,
                "pitch_deg": pitch_used,
                "pitch_cmd_user": pitch_cmd_user,
                "pitch_used": pitch_used,
                "pitch_clamped": pitch_clamped,
                "pull_mode": pull_mode,
                "level_hold": level_hold,
                "bank_cmd_user": bank_cmd_user,
                "bank_used": bank_safe,
                "power": power,
                "turn": "S",
                "clamped": clamped,
                "feasible": False,
                "speed_domain_error": speed_domain_error,
                "mach_break": False,
                "cas_before": cas,
                "dV_ktsps": np.nan,
                "cas_after": cas,
                "vxy_ftps": 0.0,
                "turn_rate_degps": 0.0,
                "x_before": x,
                "y_before": y,
                "x_after": x,
                "y_after": y,
                "tan_bank": float(tan_bank_safe),
                "bank_deg": float(bank_safe),
                "radius_nm": np.nan,
                "radius_ft": np.nan,
                "g_max": g_max,
                "turn_cmd_user": turn_cmd_user,
                "turn_effective": "S",
                "ps_primary": ps_primary,
                "ps_fallback_1g_straight": ps_fallback_1g,
                "ps_final": np.nan,
                "clamp_note": clamp_note,
                "turn_note": turn_note,
            }
        n_load = max(1.0, float(g_used))
        if level_hold:
            pull_mode = "NONE"
        radius_nm = np.inf
        radius_ft = np.inf
        turn_rate_base = 0.0
        level_t_to_zero = self._level_time_to_zero(pitch_prev) if level_hold else np.nan
        level_n_vertical_target = self._level_n_vertical_target(pitch_prev, tas_ftps, level_t_to_zero) if level_hold else np.nan

        if level_hold and turn_effective == "S":
            prev_g = float(s.get("g_used", 1.0))
            bank_prev = quantize_bank_deg(float(s.get("bank_deg", bank_cmd_user)), min_bank=0.0, max_bank=180.0)
            g_target_cmd = float(np.clip(g_cmd_q, 1.0, 9.0))
            if abs(pitch_prev) <= 0.5:
                g_target = 1.0
                bank_target = 0.0
            else:
                # Straight recovery uses G only (wing-level), bank remains zero.
                g_target = float(np.clip(level_n_vertical_target, 1.0, 9.0))
                if g_target < g_target_cmd:
                    g_target = g_target_cmd
                bank_target = 0.0
            g_ps_cap = self._find_g_max(power, cas, alt, g_cap=9.0)
            if not np.isnan(g_ps_cap):
                g_target = min(g_target, float(g_ps_cap))
            g_used = quantize_g_01(g_target, min_g=1.0, max_g=9.0)
            bank_used = quantize_bank_deg(bank_target, min_bank=0.0, max_bank=180.0)
            g_cmd_effective = g_used
            n_load = max(1.0, float(g_used))

        if turn_effective == "S":
            # Straight command always means wing-level; no bank turn component.
            bank_used = 0.0
            tan_bank = 0.0
            n_horizontal = 0.0
        elif level_hold:
            # Allow temporary G assist during level recovery in turns; cap by PS-feasible G.
            g_turn_target = float(np.clip(max(abs(level_n_vertical_target), float(g_used)), 1.0, 9.0))
            if abs(pitch_prev) <= 0.5:
                g_turn_target = float(np.clip(g_cmd_q, 1.0, 9.0))
            g_ps_cap = self._find_g_max(power, cas, alt, g_cap=9.0)
            if not np.isnan(g_ps_cap):
                g_turn_target = min(g_turn_target, float(g_ps_cap))
            g_used = quantize_g_01(g_turn_target, min_g=1.0, max_g=9.0)
            g_cmd_effective = g_used
            n_load = max(1.0, min(9.0, float(g_used)))
            bank_prev = quantize_bank_deg(float(s.get("bank_deg", bank_cmd_user)), min_bank=0.0, max_bank=180.0)
            bank_rec = self._compute_bank_for_vertical_target(n_load, level_n_vertical_target, max_over_bank=135.0)
            bank_lvl = self._compute_level_bank_from_g(n_load)
            if abs(pitch_prev) <= 5.0:
                w = float(np.clip((5.0 - abs(pitch_prev)) / 5.0, 0.0, 1.0))
                bank_target = quantize_bank_deg(((1.0 - w) * bank_rec) + (w * bank_lvl), min_bank=0.0, max_bank=180.0)
            else:
                bank_target = bank_rec
            if pitch_prev < -0.5:
                bank_target = min(bank_target, bank_lvl)
            bank_used = quantize_bank_deg(bank_target, min_bank=0.0, max_bank=180.0)
            bank_rad = math.radians(bank_used)
            sin_bank = math.sin(bank_rad)
            cos_bank = math.cos(bank_rad)
            tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
            n_horizontal = n_load * sin_bank
        elif pitch_hold:
            # Keep commanded pitch and solve bank from G to satisfy that flight-path angle.
            bank_used = self._bank_from_g_pitch(n_load, pitch_cmd_user)
            bank_rad = math.radians(bank_used)
            sin_bank = math.sin(bank_rad)
            cos_bank = math.cos(bank_rad)
            tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
            n_horizontal = n_load * sin_bank
        elif bank_cmd_user > 1e-9:
            # User-specified bank has priority when turn direction is commanded.
            bank_used = bank_cmd_user
            bank_rad = math.radians(bank_used)
            sin_bank = math.sin(bank_rad)
            cos_bank = math.cos(bank_rad)
            tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
            n_horizontal = n_load * sin_bank
        elif abs(pitch_used) <= 1e-9:
            # Fallback: if user did not set bank, infer bank from G in level turn.
            cos_gamma = math.cos(pitch_rad)
            cos_bank = float(np.clip(cos_gamma / max(n_load, 1e-6), -1.0, 1.0))
            sin_bank = math.sqrt(max(1.0 - (cos_bank * cos_bank), 0.0))
            tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
            bank_used = math.degrees(math.atan2(sin_bank, max(cos_bank, 1e-9)))
            n_horizontal = n_load * sin_bank
        else:
            # Non-level fallback keeps explicit bank command.
            bank_used = bank_cmd_user
            bank_rad = math.radians(bank_used)
            sin_bank = math.sin(bank_rad)
            cos_bank = math.cos(bank_rad)
            tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
            n_horizontal = n_load * sin_bank

        if pitch_hold and turn_effective != "S":
            pitch_rate_radps = 0.0
            pitch_next = float(pitch_cmd_user)
        elif pull_mode == "UP":
            n_pull = max(1.0, float(g_cmd_q))
            n_vertical = float(n_pull) * math.cos(math.radians(float(bank_used)))
            pitch_rate_radps = (G0 * (n_vertical - math.cos(math.radians(pitch_prev)))) / max(tas_ftps, 1e-6)
            pitch_next = float(pitch_prev + math.degrees(pitch_rate_radps) * dt_use)
        elif pull_mode == "DOWN":
            n_pull = 0.5
            n_vertical = float(n_pull) * math.cos(math.radians(float(bank_used)))
            pitch_rate_radps = (G0 * (n_vertical - math.cos(math.radians(pitch_prev)))) / max(tas_ftps, 1e-6)
            pitch_next = float(pitch_prev + math.degrees(pitch_rate_radps) * dt_use)
        else:
            # No pull checkbox: if turn/bank implies non-level vertical component, pitch evolves automatically.
            if turn_effective != "S":
                n_vertical = float(n_load) * math.cos(math.radians(float(bank_used)))
                pitch_rate_radps = (G0 * (n_vertical - math.cos(math.radians(pitch_prev)))) / max(tas_ftps, 1e-6)
                pitch_next = float(pitch_prev + math.degrees(pitch_rate_radps) * dt_use)
            else:
                if level_hold:
                    n_vertical = float(n_load) * math.cos(math.radians(float(bank_used)))
                    pitch_rate_radps = (G0 * (n_vertical - math.cos(math.radians(pitch_prev)))) / max(tas_ftps, 1e-6)
                    pitch_next = float(pitch_prev + math.degrees(pitch_rate_radps) * dt_use)
                else:
                    pitch_rate_radps = 0.0
                    pitch_next = float(pitch_prev)
        if level_hold and np.isfinite(level_t_to_zero):
            # Enforce monotonic pitch convergence to satisfy |pitch|/5s target when feasible.
            pitch_target_next = float(pitch_prev + ((-float(pitch_prev) / max(float(level_t_to_zero), 1e-6)) * dt_use))
            if (pitch_prev > 0.0 and pitch_target_next < 0.0) or (pitch_prev < 0.0 and pitch_target_next > 0.0):
                pitch_target_next = 0.0
            if abs(pitch_target_next) < abs(pitch_next):
                pitch_next = pitch_target_next
        if level_hold:
            crossed_zero = ((pitch_prev > 0.0 and pitch_next < 0.0) or (pitch_prev < 0.0 and pitch_next > 0.0))
            if crossed_zero:
                pitch_next = 0.0
                if turn_effective != "S":
                    bank_used = self._compute_level_bank_from_g(n_load)
                    bank_rad = math.radians(bank_used)
                    sin_bank = math.sin(bank_rad)
                    cos_bank = math.cos(bank_rad)
                    tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
                    n_horizontal = n_load * sin_bank
            elif (turn_effective != "S") and (abs(pitch_next) <= 0.5):
                bank_used = self._compute_level_bank_from_g(n_load)
                bank_rad = math.radians(bank_used)
                sin_bank = math.sin(bank_rad)
                cos_bank = math.cos(bank_rad)
                tan_bank = sin_bank / max(abs(cos_bank), 1e-6)
                n_horizontal = n_load * sin_bank
        pitch_used = pitch_next
        pitch_clamped = False
        pitch_rad = math.radians(pitch_used)
        roc_ftps = tas_ftps * math.sin(pitch_rad)
        # Keep horizontal speed magnitude positive; heading flip logic handles loop direction changes.
        vxy = tas_ftps * abs(math.cos(pitch_rad))

        if n_horizontal > 1e-6 and abs(vxy) > 1e-6:
            radius_ft = (vxy * vxy) / (G0 * n_horizontal)
            radius_nm = radius_ft / NM_TO_FT
            turn_rate_radps = (G0 * n_horizontal) / max(abs(vxy), 1e-6)
            turn_rate_base = math.degrees(turn_rate_radps)
        elif turn_effective == "S":
            pass
        else:
            radius_nm = np.inf
            radius_ft = np.inf
            turn_rate_base = 0.0

        if turn_effective == "CW":
            turn_rate_degps = turn_rate_base
        elif turn_effective == "CCW":
            turn_rate_degps = -turn_rate_base
        else:
            turn_rate_degps = 0.0

        # Mirror heading when crossing 90/270deg pitch boundaries (cos sign change).
        cos_prev = math.cos(math.radians(float(pitch_prev)))
        cos_now = math.cos(math.radians(float(pitch_used)))
        sign_prev = 1 if cos_prev >= 0.0 else -1
        sign_now = 1 if cos_now >= 0.0 else -1
        if sign_prev != sign_now:
            hdg = self._wrap_hdg_excel(hdg + 180.0)

        if turn_effective == "CW":
            hdg = self._wrap_hdg_excel(hdg + turn_rate_degps * dt_use)
        elif turn_effective == "CCW":
            hdg = self._wrap_hdg_excel(hdg + turn_rate_degps * dt_use)

        v = tas_ftps
        dV_ftps2 = (ps_final - roc_ftps) * G0 / max(v, 1e-6)
        dV_ktsps = dV_ftps2 / KT_TO_FTPS
        hdg_rad = math.radians(hdg)
        x_new = x + vxy * math.sin(hdg_rad) * dt_use
        y_new = y + vxy * math.cos(hdg_rad) * dt_use
        z_new = alt + roc_ftps * dt_use

        # Excel flow:
        # next ROC/alt uses current TAS, then next CAS is derived from next TAS and next alt.
        if speed_lock_on:
            if hold_source_step is not None:
                cas_new = float(self.lock_speed_value_by_step.get(hold_source_step, {}).get(aid, cas))
            else:
                cas_new = cas
            dV_ktsps = 0.0
            tas_new = self._tas_from_cas(float(cas_new), float(z_new))
        else:
            tas_new_raw = max(0.0, tas_kt + dV_ktsps * dt_use)
            cas_new_raw = tas_new_raw / max(1.0 + 0.0142 * (float(z_new) / 1000.0), 1e-6)
            cas_new = float(np.clip(cas_new_raw, 50.0, 700.0))
            tas_new = self._tas_from_cas(float(cas_new), float(z_new))

        mach_new = self._mach_from_tas_alt(float(tas_new), float(z_new))
        mach_break = mach_new >= 1.0

        return {
            "x_ft": x_new,
            "y_ft": y_new,
            "z_ft": z_new,
            "hdg_deg": hdg,
            "cas_kt": float(cas_new),
            "tas_kt": tas_new,
            "ps_fps": float(ps_final),
            "g_cmd": g_cmd_user,
            "g_cmd_effective": g_cmd_effective,
            "g_used": float(g_used),
            "pitch_deg": pitch_used,
            "pitch_cmd_user": pitch_cmd_user,
            "pitch_used": pitch_used,
            "pitch_clamped": pitch_clamped,
            "pull_mode": pull_mode,
            "level_hold": level_hold,
            "bank_cmd_user": bank_cmd_user,
            "bank_used": float(bank_used),
            "power": power,
            "turn": turn_effective,
            "clamped": clamped,
            "feasible": True,
            "speed_domain_error": speed_domain_error,
            "mach_break": mach_break,
            "cas_before": cas,
            "dV_ktsps": float(dV_ktsps),
            "cas_after": float(cas_new),
            "vxy_ftps": float(vxy),
            "turn_rate_degps": float(turn_rate_degps),
            "x_before": x,
            "y_before": y,
            "x_after": x_new,
            "y_after": y_new,
            "tan_bank": float(tan_bank),
            "bank_deg": float(bank_used),
            "radius_nm": float(radius_nm),
            "radius_ft": float(radius_ft),
            "g_max": g_max,
            "turn_cmd_user": turn_cmd_user,
            "turn_effective": turn_effective,
            "ps_primary": ps_primary,
            "ps_fallback_1g_straight": ps_fallback_1g,
            "ps_final": float(ps_final),
            "clamp_note": clamp_note,
            "turn_note": turn_note,
        }

    def _simulate_step(self, prev_states: Dict[str, Dict], cmds: Dict, dt: float, step_idx: int):
        next_states = {}
        recs = {}
        for aid in AIRCRAFT_IDS:
            nst = self._simulate_one(aid, prev_states[aid], cmds[aid], dt, step_idx)
            next_states[aid] = nst
            recs[aid] = {
                "power": nst["power"],
                "turn": nst["turn"],
                "turn_cmd_user": nst.get("turn_cmd_user", nst["turn"]),
                "turn_effective": nst.get("turn_effective", nst["turn"]),
                "g_cmd": nst["g_cmd"],
                "g_cmd_effective": nst.get("g_cmd_effective", nst["g_cmd"]),
                "g_used": nst["g_used"],
                "g_max": nst.get("g_max", np.nan),
                "pitch_deg": nst["pitch_deg"],
                "pitch_cmd_user": nst.get("pitch_cmd_user", nst["pitch_deg"]),
                "pitch_used": nst.get("pitch_used", nst["pitch_deg"]),
                "pitch_clamped": nst.get("pitch_clamped", False),
                "pull_mode": nst.get("pull_mode", "NONE"),
                "level_hold": nst.get("level_hold", False),
                "bank_cmd_user": nst.get("bank_cmd_user", np.nan),
                "bank_used": nst.get("bank_used", nst.get("bank_deg", np.nan)),
                "ps_fps": nst["ps_fps"],
                "ps_primary": nst.get("ps_primary", np.nan),
                "ps_fallback_1g_straight": nst.get("ps_fallback_1g_straight", np.nan),
                "ps_final": nst.get("ps_final", nst["ps_fps"]),
                "clamped": nst["clamped"],
                "feasible": nst["feasible"],
                "cas_before": nst["cas_before"],
                "dV_ktsps": nst["dV_ktsps"],
                "cas_after": nst["cas_after"],
                "tas_kt": nst["tas_kt"],
                "vxy_ftps": nst["vxy_ftps"],
                "hdg_deg": nst["hdg_deg"],
                "turn_rate_degps": nst["turn_rate_degps"],
                "x_before": nst["x_before"],
                "y_before": nst["y_before"],
                "x_after": nst["x_after"],
                "y_after": nst["y_after"],
                "tan_bank": nst["tan_bank"],
                "bank_deg": nst["bank_deg"],
                "radius_nm": nst["radius_nm"],
                "radius_ft": nst["radius_ft"],
                "clamp_note": nst.get("clamp_note", ""),
                "turn_note": nst.get("turn_note", ""),
                "speed_domain_error": nst.get("speed_domain_error", False),
                "mach_break": nst.get("mach_break", False),
            }
        return next_states, recs

    def _read_current_cmds(self) -> Dict[str, Dict]:
        return {aid: self.controls[aid].read_command() for aid in AIRCRAFT_IDS}

    def _cmd_values_equal(self, a: Dict, b: Dict) -> bool:
        if str(a.get("turn", "S")) != str(b.get("turn", "S")):
            return False
        if str(a.get("power", "M")) != str(b.get("power", "M")):
            return False
        a_gmax = bool(a.get("g_use_max", False))
        b_gmax = bool(b.get("g_use_max", False))
        if a_gmax != b_gmax:
            return False
        # If G MAX is enabled, g_cmd is auto-derived by current state and should not trigger "changed" prompt.
        if (not a_gmax) and (abs(float(a.get("g_cmd", 1.0)) - float(b.get("g_cmd", 1.0))) > 1e-9):
            return False
        a_ph = bool(a.get("pitch_hold", False))
        b_ph = bool(b.get("pitch_hold", False))
        if a_ph != b_ph:
            return False
        a_pm = str(a.get("pull_mode", "NONE")).upper()
        b_pm = str(b.get("pull_mode", "NONE")).upper()
        a_pus = bool(a.get("pitch_user_set", False))
        b_pus = bool(b.get("pitch_user_set", False))
        pull_pitch_mode = ((a_pm in {"UP", "DOWN"}) or (b_pm in {"UP", "DOWN"})) and (a_pus or b_pus)
        pitch_cmd_mode = a_ph or b_ph or pull_pitch_mode
        if pitch_cmd_mode and (abs(float(a.get("pitch_deg", 0.0)) - float(b.get("pitch_deg", 0.0))) > 1e-9):
            return False
        # In pitch-hold, bank is derived from G/pitch and should not count as user command delta.
        # Also compare bank with current UI resolution (1 deg). Older scenario CSV may contain
        # fractional bank values (e.g. 33.6) that are rounded by today's integer bank spinner.
        if not (a_ph or b_ph):
            a_bank_ui = float(math.floor(float(a.get("bank_deg", 0.0)) + 0.5))
            b_bank_ui = float(math.floor(float(b.get("bank_deg", 0.0)) + 0.5))
            if abs(a_bank_ui - b_bank_ui) > 1e-9:
                return False
        if a_pm != b_pm:
            return False
        if bool(a.get("level_hold", False)) != bool(b.get("level_hold", False)):
            return False
        return True

    def _step_cmds_changed_vs_saved(self, step: int, cur_cmds: Dict[str, Dict], cur_hold: Dict[str, bool]) -> bool:
        return len(self._changed_aids_vs_saved(step, cur_cmds, cur_hold)) > 0

    def _changed_aids_vs_saved(self, step: int, cur_cmds: Dict[str, Dict], cur_hold: Dict[str, bool]) -> List[str]:
        saved_pkg = self.step_cmds.get(step)
        saved_cmds = saved_pkg.get("cmds", self._default_step_cmds()) if isinstance(saved_pkg, dict) else self._default_step_cmds()
        changed: List[str] = []
        saved_hold = {aid: self._effective_hold_for_step(step, aid) for aid in AIRCRAFT_IDS}
        for aid in AIRCRAFT_IDS:
            cmd_changed = not self._cmd_values_equal(cur_cmds.get(aid, {}), saved_cmds.get(aid, {}))
            hold_changed = bool(cur_hold.get(aid, False)) != bool(saved_hold.get(aid, False))
            if cmd_changed or hold_changed:
                changed.append(aid)
        return changed

    def _maybe_prompt_future_step_policy(self, step: int, cur_cmds: Dict[str, Dict], cur_hold: Dict[str, bool]) -> bool:
        max_saved = max([int(k) for k in self.step_cmds.keys()], default=int(step))
        max_hist = max(0, int(len(self.state_history) - 1))
        last_future = max(max_saved, max_hist)
        future_steps = list(range(int(step) + 1, int(last_future) + 1))
        if not future_steps:
            return True
        changed_aids = self._changed_aids_vs_saved(step, cur_cmds, cur_hold)
        if not changed_aids:
            return True

        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Question)
        mbox.setWindowTitle("Update next steps?")
        if len(changed_aids) == 1:
            mbox.setText(
                f"You changed {changed_aids[0]} at this step.\n"
                f"Apply {changed_aids[0]}'s updated values to next steps too?"
            )
        else:
            aids_txt = ", ".join(changed_aids)
            mbox.setText(
                "You changed aircraft at this step.\n"
                f"Apply only these aircraft to next steps too?\n{aids_txt}"
            )
        btn_apply = mbox.addButton("Apply changed aircraft", QMessageBox.ButtonRole.AcceptRole)
        btn_keep = mbox.addButton("Keep old next steps", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = mbox.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        mbox.exec()

        clicked = mbox.clickedButton()
        if clicked is btn_cancel:
            return False
        if clicked is btn_apply:
            # Lock in current-step edits first.
            cur_pkg = self.step_cmds.setdefault(
                int(step),
                {"_dt": float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value()), "cmds": self._default_step_cmds()},
            )
            if "cmds" not in cur_pkg or (not isinstance(cur_pkg.get("cmds"), dict)):
                cur_pkg["cmds"] = self._default_step_cmds()
            for aid in AIRCRAFT_IDS:
                if aid not in cur_pkg["cmds"]:
                    cur_pkg["cmds"][aid] = dict(self._default_cmd_for_aircraft())
            for aid in changed_aids:
                cur_pkg["cmds"][aid] = dict(cur_cmds[aid])
            self.hold_state_by_step[int(step)] = {aid: bool(cur_hold.get(aid, False)) for aid in AIRCRAFT_IDS}

            # Propagate only changed aircraft through all future steps.
            for s in future_steps:
                prev_pkg = self.step_cmds.get(int(s) - 1, {})
                prev_cmds = prev_pkg.get("cmds", self._default_step_cmds()) if isinstance(prev_pkg, dict) else self._default_step_cmds()
                pkg = self.step_cmds.setdefault(
                    int(s),
                    {
                        "_dt": float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value()),
                        "cmds": {aid: dict(prev_cmds.get(aid, self._default_cmd_for_aircraft())) for aid in AIRCRAFT_IDS},
                    },
                )
                if "cmds" not in pkg or (not isinstance(pkg.get("cmds"), dict)):
                    pkg["cmds"] = {aid: dict(prev_cmds.get(aid, self._default_cmd_for_aircraft())) for aid in AIRCRAFT_IDS}
                for aid in AIRCRAFT_IDS:
                    if aid not in pkg["cmds"]:
                        pkg["cmds"][aid] = dict(prev_cmds.get(aid, self._default_cmd_for_aircraft()))
                for aid in changed_aids:
                    pkg["cmds"][aid] = dict(cur_cmds[aid])
                hold_map = {aid: self._effective_hold_for_step(int(s), aid) for aid in AIRCRAFT_IDS}
                for aid in changed_aids:
                    hold_map[aid] = bool(cur_hold.get(aid, False))
                self.hold_state_by_step[int(s)] = hold_map
        elif clicked is btn_keep:
            pass
        return True

    @staticmethod
    def _default_cmd_for_aircraft() -> Dict[str, float]:
        return {
            "turn": "S",
            "power": "M",
            "g_cmd": 1.0,
            "g_use_max": False,
            "pitch_deg": 0.0,
            "pitch_hold": False,
            "pitch_user_set": False,
            "bank_deg": 0.0,
            "bank_user_set": False,
            "pull_mode": "NONE",
            "level_hold": True,
        }

    def _default_step_cmds(self) -> Dict[str, Dict]:
        return {aid: dict(self._default_cmd_for_aircraft()) for aid in AIRCRAFT_IDS}

    def _current_hold_map_from_ui(self) -> Dict[str, bool]:
        return {aid: bool(self.controls[aid].read_hold_speed()) for aid in AIRCRAFT_IDS}

    def _effective_hold_for_step(self, step: int, aid: str) -> bool:
        keys = [k for k in self.hold_state_by_step.keys() if k <= step]
        if not keys:
            return False
        v = self.hold_state_by_step[max(keys)]
        if isinstance(v, dict):
            return bool(v.get(aid, False))
        return bool(v)

    def _effective_hold_source_step(self, step: int, aid: str) -> Optional[int]:
        keys = [k for k in self.hold_state_by_step.keys() if k <= step]
        if not keys:
            return None
        for k in sorted(keys, reverse=True):
            if self._effective_hold_for_step(k, aid):
                return k
        return None

    @staticmethod
    def _mach_from_tas_alt(tas_kt: float, alt_ft: float) -> float:
        tas_mps = float(tas_kt) * 0.514444
        h = max(0.0, float(alt_ft) * 0.3048)
        if h < 11000.0:
            t_k = 288.15 - 0.0065 * h
        else:
            t_k = 216.65
        a = math.sqrt(1.4 * 287.05 * max(t_k, 1.0))
        return tas_mps / max(a, 1e-6)

    def _show_rate_limited_warning(self, key: str, msg: str):
        if self.warning_shown.get(key, False):
            return
        self.warning_shown[key] = True
        QMessageBox.warning(self, "Warning", msg)

    def _show_step_event_warning(self, step_no: int, events: List[str]):
        if not events:
            return
        body = "\n".join(f"- {e}" for e in events)
        QMessageBox.warning(self, "Step Warning", f"Step {int(step_no)} events:\n{body}")

    def _ba_min_distance_ft(self, states: Dict[str, Dict]) -> Optional[float]:
        if not isinstance(states, dict):
            return None
        active_ids = set(self._active_aircraft_ids())
        ba_ids = [aid for aid in AIRCRAFT_IDS if (aid in active_ids) and (aid in self._ba_ids_for_mode()) and (aid in states)]
        if len(ba_ids) < 2:
            return None
        min_dist = float("inf")
        for i in range(len(ba_ids)):
            ai = ba_ids[i]
            si = states.get(ai, {})
            pi = np.array([float(si.get("x_ft", 0.0)), float(si.get("y_ft", 0.0)), float(si.get("z_ft", 0.0))], dtype=float)
            for j in range(i + 1, len(ba_ids)):
                aj = ba_ids[j]
                sj = states.get(aj, {})
                pj = np.array([float(sj.get("x_ft", 0.0)), float(sj.get("y_ft", 0.0)), float(sj.get("z_ft", 0.0))], dtype=float)
                d = float(np.linalg.norm(pi - pj))
                if d < min_dist:
                    min_dist = d
        if not np.isfinite(min_dist):
            return None
        return float(min_dist)

    def _ba_min_distance_during_step_ft(
        self, prev_states: Dict[str, Dict], next_states: Dict[str, Dict]
    ) -> Optional[Tuple[float, float, Tuple[str, str]]]:
        if (not isinstance(prev_states, dict)) or (not isinstance(next_states, dict)):
            return None
        active_ids = set(self._active_aircraft_ids())
        ba_ids = [
            aid
            for aid in AIRCRAFT_IDS
            if (aid in active_ids) and (aid in self._ba_ids_for_mode()) and (aid in prev_states) and (aid in next_states)
        ]
        if len(ba_ids) < 2:
            return None
        best_d = float("inf")
        best_t = 0.0
        best_pair = ("", "")
        for i in range(len(ba_ids)):
            ai = ba_ids[i]
            p0i = np.array(
                [
                    float(prev_states[ai].get("x_ft", 0.0)),
                    float(prev_states[ai].get("y_ft", 0.0)),
                    float(prev_states[ai].get("z_ft", 0.0)),
                ],
                dtype=float,
            )
            p1i = np.array(
                [
                    float(next_states[ai].get("x_ft", 0.0)),
                    float(next_states[ai].get("y_ft", 0.0)),
                    float(next_states[ai].get("z_ft", 0.0)),
                ],
                dtype=float,
            )
            vi = p1i - p0i
            for j in range(i + 1, len(ba_ids)):
                aj = ba_ids[j]
                p0j = np.array(
                    [
                        float(prev_states[aj].get("x_ft", 0.0)),
                        float(prev_states[aj].get("y_ft", 0.0)),
                        float(prev_states[aj].get("z_ft", 0.0)),
                    ],
                    dtype=float,
                )
                p1j = np.array(
                    [
                        float(next_states[aj].get("x_ft", 0.0)),
                        float(next_states[aj].get("y_ft", 0.0)),
                        float(next_states[aj].get("z_ft", 0.0)),
                    ],
                    dtype=float,
                )
                vj = p1j - p0j
                r0 = p0i - p0j
                rv = vi - vj
                den = float(np.dot(rv, rv))
                if den <= 1e-12:
                    t = 0.0
                else:
                    t = float(-np.dot(r0, rv) / den)
                    t = max(0.0, min(1.0, t))
                d = float(np.linalg.norm(r0 + (rv * t)))
                if d < best_d:
                    best_d = d
                    best_t = t
                    best_pair = (ai, aj)
        if not np.isfinite(best_d):
            return None
        return float(best_d), float(best_t), best_pair

    def _restore_hold_ui_for_step(self, step: int):
        hold_map = {aid: self._effective_hold_for_step(step, aid) for aid in AIRCRAFT_IDS}
        for aid in AIRCRAFT_IDS:
            self.controls[aid].set_hold_speed(hold_map[aid])
        hold = all(hold_map.values())
        self.chk_speed_lock.blockSignals(True)
        self.chk_speed_lock.setChecked(hold)
        self.chk_speed_lock.blockSignals(False)
        for aid in AIRCRAFT_IDS:
            self.controls[aid].hold_speed_chk.setEnabled(self.chk_speed_lock.isEnabled())

    def _update_dt_lock_ui(self):
        editable = (int(self.current_step) == 0)
        self.dt_sec.setEnabled(editable)
        self.dt_sec.setToolTip("dt는 Step 0에서만 변경할 수 있습니다.")
        if editable:
            self.dt_sec.setStyleSheet("")
        else:
            self.dt_sec.setStyleSheet("color: #888; background: #f0f0f0;")

    def _restore_cmd_ui_for_step(self, step: int):
        self.sync_ui_from_step(step)

    def _debug_cmd_g_binding_once(self):
        if self._g_binding_logged:
            return
        self._g_binding_logged = True
        for aid in AIRCRAFT_IDS:
            w = self.cmd_g_spin.get(aid)
            if w is None:
                print(f"[UI-G-BIND] aid={aid} spin=None")
                continue
            print(
                f"[UI-G-BIND] aid={aid} objectName={w.objectName()} "
                f"visible={w.isVisible()} enabled={w.isEnabled()}"
            )

    def sync_ui_from_step(self, step: int):
        pkg = self.step_cmds.get(step)
        cmds = pkg["cmds"] if (pkg is not None and "cmds" in pkg) else self._default_step_cmds()
        for aid in AIRCRAFT_IDS:
            self.controls[aid].set_command(cmds.get(aid, {}))
            st = self.state_history[step][aid] if (0 <= step < len(self.state_history)) else {}
            cmd_pitch_hold = bool(cmds.get(aid, {}).get("pitch_hold", False))
            if cmd_pitch_hold:
                # Pitch Hold semantics: keep user-commanded pitch setpoint visible/editable.
                self.controls[aid].set_pitch_from_auto(float(cmds.get(aid, {}).get("pitch_deg", 0.0)))
            else:
                self.controls[aid].set_pitch_display(float(st.get("pitch_deg", cmds.get(aid, {}).get("pitch_deg", 0.0))))
            self._update_cmd_g_dynamic_cap(aid, apply_cap_to_value=True)
            g_user = float(st.get("g_cmd", np.nan))
            g_used = float(st.get("g_used", np.nan))
            self.controls[aid].set_applied_g(g_used)
            clamped = bool(st.get("clamped", False))
            if clamped and (not np.isnan(g_user)) and (not np.isnan(g_used)) and (g_used < (g_user - 1e-9)):
                self.controls[aid].set_g_limit_indicator(g_user, g_used)
            else:
                self.controls[aid].clear_g_limit_indicator()

    def _commit_g_clamp_ui_and_step(self, step: int, aid: str, g_user: float, g_used: float):
        g_used_1 = quantize_g_01(float(g_used), min_g=1.0, max_g=9.0)
        pkg = self.step_cmds.setdefault(step, {"_dt": float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value()), "cmds": self._default_step_cmds()})
        if "cmds" not in pkg:
            pkg["cmds"] = self._default_step_cmds()
        if aid not in pkg["cmds"]:
            pkg["cmds"][aid] = self._default_cmd_for_aircraft()
        pkg["cmds"][aid]["g_cmd"] = g_used_1
        gw = self.cmd_g_spin[aid]
        gw_ctrl = self.controls[aid].g_cmd
        before = float(gw.value())
        gw.blockSignals(True)
        gw.setValue(g_used_1)
        gw.blockSignals(False)
        if gw is not gw_ctrl:
            gw_ctrl.blockSignals(True)
            gw_ctrl.setValue(g_used_1)
            gw_ctrl.blockSignals(False)
        after = float(gw.value())
        after_ctrl = float(gw_ctrl.value())
        self.controls[aid].set_applied_g(g_used_1)
        self.controls[aid].set_g_limit_indicator(g_user, g_used_1)
        print(
            f"[G-CLAMP-UI] step={step} {aid} user={g_user:.1f} used={g_used_1:.1f} committed_to_step_cmds=YES ui_set=YES"
        )
        print(
            f"[UI-G] aid={aid} spin_visible={gw.isVisible()} before={before:.1f} after={after:.1f} "
            f"after_ctrl={after_ctrl:.1f} applied_lbl={self.applied_g_label[aid].text()}"
        )

    def _set_inputs_enabled(self, enabled: bool):
        for ac in self.controls.values():
            ac.cmd_group.setEnabled(enabled)
            ac.hold_speed_chk.setEnabled(enabled)
            if self.current_step == 0:
                ac.init_state_group.setEnabled(enabled)
                if ac.offset_group is not None:
                    ac.offset_group.setEnabled(enabled)
        self.chk_speed_lock.setEnabled(enabled)
        self.btn_adv1.setEnabled(enabled)
        self.btn_adv5.setEnabled(enabled)
        self.btn_adv10.setEnabled(enabled)
        self.btn_back1.setEnabled(enabled)
        self.btn_back5.setEnabled(enabled)
        self.btn_back10.setEnabled(enabled)
        self.btn_reset_step.setEnabled(enabled)
        self.btn_reset.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_import_scn.setEnabled(enabled)
        self.btn_clear_los.setEnabled(enabled)
        self.dt_sec.setEnabled(enabled and (int(self.current_step) == 0))
        for cb in self.aircraft_enable_checks.values():
            cb.setEnabled(enabled)
        self._apply_dca_ra_ui_lock()

    def _tinted_standard_icon(self, sp: QStyle.StandardPixmap, color: QColor, size: int = 18) -> QIcon:
        base = self.style().standardIcon(sp)
        pm = base.pixmap(size, size)
        tinted = QPixmap(pm.size())
        tinted.fill(Qt.GlobalColor.transparent)
        p = QPainter(tinted)
        p.drawPixmap(0, 0, pm)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.fillRect(tinted.rect(), color)
        p.end()
        return QIcon(tinted)

    def _sync_play_button_icon(self):
        running = bool(self.playback_running)
        backward = bool(getattr(self, "playback_direction", 1) < 0)
        if hasattr(self, "btn_view_back") and self.btn_view_back is not None:
            self.btn_view_back.setToolTip("이전 step")
        if hasattr(self, "btn_view_fwd") and self.btn_view_fwd is not None:
            self.btn_view_fwd.setToolTip("다음 step")
        if hasattr(self, "btn_view_zoom_in") and self.btn_view_zoom_in is not None:
            self.btn_view_zoom_in.setToolTip("확대 (+ / PgUp)")
        if hasattr(self, "btn_view_zoom_out") and self.btn_view_zoom_out is not None:
            self.btn_view_zoom_out.setToolTip("축소 (- / PgDown)")
        if hasattr(self, "btn_view_stop") and self.btn_view_stop is not None:
            self.btn_view_stop.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaStop, QColor("#cf2f2f")))
            self.btn_view_stop.setToolTip("정지")
        if hasattr(self, "btn_view_play_pause") and self.btn_view_play_pause is not None:
            self.btn_view_play_pause.setText("")
            self.btn_view_play_pause.setToolTip("정방향 재생/일시정지")
        if hasattr(self, "btn_view_play_back") and self.btn_view_play_back is not None:
            self.btn_view_play_back.setText("")
        if running and (not backward):
            self.btn_play.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPause, QColor("#1e9e3e")))
            self.btn_play.setToolTip("일시정지")
            self.btn_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaSeekBackward, QColor("#1e9e3e")))
            self.btn_play_back.setToolTip("역방향 재생")
            if hasattr(self, "btn_view_play_pause") and self.btn_view_play_pause is not None:
                self.btn_view_play_pause.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPause, QColor("#1e9e3e")))
            if hasattr(self, "btn_view_play_back") and self.btn_view_play_back is not None:
                self.btn_view_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaSeekBackward, QColor("#1e9e3e")))
            return
        if running and backward:
            self.btn_play.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPlay, QColor("#1e9e3e")))
            self.btn_play.setToolTip("재생")
            self.btn_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPause, QColor("#1e9e3e")))
            self.btn_play_back.setToolTip("역방향 일시정지")
            if hasattr(self, "btn_view_play_pause") and self.btn_view_play_pause is not None:
                self.btn_view_play_pause.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPlay, QColor("#1e9e3e")))
            if hasattr(self, "btn_view_play_back") and self.btn_view_play_back is not None:
                self.btn_view_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPause, QColor("#1e9e3e")))
            return
        self.btn_play.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPlay, QColor("#1e9e3e")))
        self.btn_play.setToolTip("재생")
        self.btn_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaSeekBackward, QColor("#1e9e3e")))
        self.btn_play_back.setToolTip("역방향 재생")
        if hasattr(self, "btn_view_play_pause") and self.btn_view_play_pause is not None:
            self.btn_view_play_pause.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaPlay, QColor("#1e9e3e")))
        if hasattr(self, "btn_view_play_back") and self.btn_view_play_back is not None:
            self.btn_view_play_back.setIcon(self._tinted_standard_icon(QStyle.StandardPixmap.SP_MediaSeekBackward, QColor("#1e9e3e")))

    def _set_play_speed_preset(self, speed_text: str):
        txt = str(speed_text).strip()
        if txt not in {"x1", "x2", "x4"}:
            return
        self.play_speed.setCurrentText(txt)
        self._sync_view_speed_buttons()

    def _on_view_overlay_step_clicked(self):
        self.view_mode.setCurrentText("Step View")
        self._sync_view_mode_overlay_buttons()

    def _on_view_overlay_overview_clicked(self):
        self.view_mode.setCurrentText("Overview View")
        self._sync_view_mode_overlay_buttons()

    def _on_view_overlay_show_steps_clicked(self):
        if not hasattr(self, "chk_show_steps") or self.chk_show_steps is None:
            return
        self.chk_show_steps.setChecked(not self.chk_show_steps.isChecked())
        self._sync_view_mode_overlay_buttons()

    def _sync_view_mode_overlay_buttons(self):
        step_selected = str(self.view_mode.currentText()).strip() == "Step View"
        show_steps_on = bool(self.chk_show_steps.isChecked()) if hasattr(self, "chk_show_steps") else False
        btns = [
            (getattr(self, "btn_view_mode_step", None), step_selected),
            (getattr(self, "btn_view_mode_overview", None), (not step_selected)),
            (getattr(self, "btn_view_show_steps", None), show_steps_on),
        ]
        for btn, selected in btns:
            if btn is None:
                continue
            btn.blockSignals(True)
            btn.setChecked(bool(selected))
            btn.blockSignals(False)
            btn.setStyleSheet(
                "QPushButton {"
                " font-size: 8pt;"
                " font-weight: 700;"
                f" color: {'#ffffff' if selected else '#111111'};"
                f" background: {'rgba(20, 90, 200, 230)' if selected else 'rgba(255, 255, 255, 220)'};"
                f" border: 1px solid {'rgba(10, 45, 120, 220)' if selected else 'rgba(30, 30, 30, 130)'};"
                " border-radius: 4px;"
                " padding: 1px 6px;"
                "}"
            )
        self._sync_tail_overlay_buttons()

    def _sync_view_speed_buttons(self):
        cur = str(self.play_speed.currentText()).strip()
        if cur not in {"x1", "x2", "x4"}:
            cur = "x1"
        btns = [
            ("x1", getattr(self, "btn_view_speed_x1", None)),
            ("x2", getattr(self, "btn_view_speed_x2", None)),
            ("x4", getattr(self, "btn_view_speed_x4", None)),
        ]
        for key, btn in btns:
            if btn is None:
                continue
            selected = key == cur
            btn.setStyleSheet(
                "QPushButton {"
                " font-size: 9pt;"
                " font-weight: 700;"
                f" color: {'#ffffff' if selected else '#111111'};"
                f" background: {'rgba(20, 90, 200, 230)' if selected else 'rgba(255, 255, 255, 220)'};"
                f" border: 1px solid {'rgba(10, 45, 120, 220)' if selected else 'rgba(30, 30, 30, 130)'};"
                " border-radius: 4px;"
                " padding: 1px 6px;"
                "}"
            )

    def _set_step_tail_limit(self, limit: int):
        val = int(limit)
        if val not in {3, 10, -1}:
            return
        self.step_tail_limit = val
        self._sync_tail_overlay_buttons()
        self.refresh_ui()

    def _sync_tail_overlay_buttons(self):
        step_selected = str(self.view_mode.currentText()).strip() == "Step View"
        selected_key = "inf" if int(self.step_tail_limit) < 0 else str(int(self.step_tail_limit))
        btns = [
            ("3", getattr(self, "btn_view_tail_3", None)),
            ("10", getattr(self, "btn_view_tail_10", None)),
            ("inf", getattr(self, "btn_view_tail_inf", None)),
        ]
        if hasattr(self, "lbl_view_tail") and self.lbl_view_tail is not None:
            self.lbl_view_tail.setVisible(bool(step_selected))
        for key, btn in btns:
            if btn is None:
                continue
            btn.setVisible(bool(step_selected))
            selected = bool(step_selected) and (key == selected_key)
            btn.blockSignals(True)
            btn.setChecked(selected)
            btn.blockSignals(False)
            btn.setStyleSheet(
                "QPushButton {"
                " font-size: 9pt;"
                " font-weight: 700;"
                f" color: {'#ffffff' if selected else '#111111'};"
                f" background: {'rgba(20, 90, 200, 230)' if selected else 'rgba(255, 255, 255, 220)'};"
                f" border: 1px solid {'rgba(10, 45, 120, 220)' if selected else 'rgba(30, 30, 30, 130)'};"
                " border-radius: 4px;"
                " padding: 1px 6px;"
                "}"
            )

    def _tail_start_step(self) -> int:
        if int(self.step_tail_limit) < 0:
            return 0
        return max(0, int(self.current_step) - int(self.step_tail_limit))

    def _current_screen_up_bearing_deg(self) -> float:
        try:
            if hasattr(self.view, "_camera_basis"):
                _cam, _fwd, _right, up = self.view._camera_basis()
                ux = float(up[0])
                uy = float(up[1])
                n = math.hypot(ux, uy)
                if n > 1e-9:
                    return self._wrap_hdg(math.degrees(math.atan2(ux, uy)))
        except Exception:
            pass
        return self._wrap_hdg(float(self.view.opts.get("azimuth", 0.0)))

    def _sync_compass_overlay(self):
        up_brg = self._current_screen_up_bearing_deg()
        if hasattr(self, "compass_rose") and self.compass_rose is not None:
            self.compass_rose.set_up_azimuth(float(up_brg))

    def _set_top_view_cardinal(self, cardinal: str):
        key = str(cardinal).strip().upper()
        az_by_card = {"N": 0.0, "E": 90.0, "S": 180.0, "W": 270.0}
        if key not in az_by_card:
            return
        desired_up = float(az_by_card[key])
        self.camera_mode = "top"
        self._sync_view_mode_controls()
        base_az = float(self.view.opts.get("azimuth", 0.0))
        self.view.setCameraPosition(elevation=89.5, azimuth=base_az)
        cur_up = self._current_screen_up_bearing_deg()
        az_corr = self._wrap_to_pm180(desired_up - cur_up)

        # Try both correction signs and choose the one that best puts the selected
        # cardinal at screen 12 o'clock.
        az_plus = base_az + az_corr
        self.view.setCameraPosition(elevation=89.5, azimuth=az_plus)
        err_plus = abs(self._wrap_to_pm180(desired_up - self._current_screen_up_bearing_deg()))

        az_minus = base_az - az_corr
        self.view.setCameraPosition(elevation=89.5, azimuth=az_minus)
        err_minus = abs(self._wrap_to_pm180(desired_up - self._current_screen_up_bearing_deg()))

        best_az = az_plus if err_plus <= err_minus else az_minus
        self.view.setCameraPosition(elevation=89.5, azimuth=best_az)
        # Final micro-correction.
        cur_up2 = self._current_screen_up_bearing_deg()
        self.view.setCameraPosition(
            elevation=89.5,
            azimuth=(float(self.view.opts.get("azimuth", 0.0)) + self._wrap_to_pm180(desired_up - cur_up2)),
        )
        self._apply_grid_visibility_for_view("top")
        self._sync_compass_overlay()
        self.refresh_ui()

    @staticmethod
    def _interp_hdg_deg(h0: float, h1: float, t: float) -> float:
        d = (h1 - h0 + 540.0) % 360.0 - 180.0
        return (h0 + d * t) % 360.0

    def _get_display_states(self, base_states: Dict[str, Dict]) -> Dict[str, Dict]:
        if not (self.playback_running or self.playback_active):
            return base_states
        i = self.current_step
        if i + 1 >= len(self.state_history):
            return base_states
        a = float(self.playback_step_float - i)
        if a <= 1e-6:
            return base_states
        nst = self.state_history[i + 1]
        out = {}
        for aid in AIRCRAFT_IDS:
            s0 = base_states[aid]
            s1 = nst[aid]
            d = dict(s0)
            d["x_ft"] = float(s0["x_ft"]) + (float(s1["x_ft"]) - float(s0["x_ft"])) * a
            d["y_ft"] = float(s0["y_ft"]) + (float(s1["y_ft"]) - float(s0["y_ft"])) * a
            d["z_ft"] = float(s0["z_ft"]) + (float(s1["z_ft"]) - float(s0["z_ft"])) * a
            d["cas_kt"] = float(s0["cas_kt"]) + (float(s1["cas_kt"]) - float(s0["cas_kt"])) * a
            d["tas_kt"] = float(s0["tas_kt"]) + (float(s1["tas_kt"]) - float(s0["tas_kt"])) * a
            d["hdg_deg"] = self._interp_hdg_deg(float(s0["hdg_deg"]), float(s1["hdg_deg"]), a)
            out[aid] = d
        return out

    def toggle_playback(self):
        self._start_playback(1)

    def toggle_playback_backward(self):
        self._start_playback(-1)

    def _on_ata_label_timer_tick(self):
        # Playback loop already triggers redraw; avoid double updates that cause flicker.
        if bool(getattr(self, "playback_running", False)):
            return
        self.update_ata_labels()

    def _pause_playback(self):
        self.playback_running = False
        self.playback_timer.stop()
        self.playback_active = True
        max_step = max(0, len(self.state_history) - 1)
        self.playback_step_float = float(max(0.0, min(float(self.playback_step_float), float(max_step))))
        self.current_step = int(math.floor(self.playback_step_float))
        self._sync_play_button_icon()
        self._set_inputs_enabled(True)
        if self.current_step == 0:
            self._restore_step0_initial_widgets_from_history()
        self._restore_cmd_ui_for_step(self.current_step)
        self._restore_hold_ui_for_step(self.current_step)
        self.refresh_ui()

    def _start_playback(self, direction: int):
        if len(self.state_history) <= 1:
            return
        direction = 1 if int(direction) >= 0 else -1
        if self.playback_running and int(getattr(self, "playback_direction", 1)) == direction:
            self._pause_playback()
            return

        max_step = len(self.state_history) - 1
        if not self.playback_running:
            if bool(getattr(self, "playback_active", False)):
                # Resume from paused interpolated location.
                self.playback_step_float = float(max(0.0, min(float(self.playback_step_float), float(max_step))))
                self.current_step = int(math.floor(self.playback_step_float))
            else:
                # Fresh playback run: remember origin for Stop.
                self.playback_origin_step = int(max(0, min(int(self.current_step), max_step)))
                if direction > 0:
                    if self.current_step >= max_step:
                        self.current_step = 0
                        self.playback_step_float = 0.0
                    else:
                        self.playback_step_float = float(self.current_step)
                else:
                    if self.current_step <= 0:
                        self.current_step = max_step
                        self.playback_step_float = float(max_step)
                    else:
                        self.playback_step_float = float(self.current_step)

        self.playback_direction = direction
        self.playback_running = True
        self.playback_active = True
        self._last_playback_wall = time.perf_counter()
        self.playback_timer.start()
        self._sync_play_button_icon()
        self._set_inputs_enabled(False)
        self.refresh_ui()

    def stop_playback(self):
        self.playback_running = False
        self.playback_active = False
        self.playback_direction = 1
        self.playback_timer.stop()
        max_step = max(0, len(self.state_history) - 1)
        self.current_step = int(max(0, min(int(getattr(self, "playback_origin_step", self.current_step)), max_step)))
        self.playback_step_float = float(self.current_step)
        self._sync_play_button_icon()
        self._set_inputs_enabled(True)
        if self.current_step == 0:
            self._restore_step0_initial_widgets_from_history()
        self._restore_cmd_ui_for_step(self.current_step)
        self._restore_hold_ui_for_step(self.current_step)
        self.refresh_ui()

    def _on_playback_tick(self):
        if not self.playback_running or len(self.state_history) <= 1:
            return
        prev_step = int(self.current_step)
        now = time.perf_counter()
        prev = self._last_playback_wall if self._last_playback_wall is not None else now
        self._last_playback_wall = now
        dt_real = max(0.0, now - prev)
        speed_mul = float(self.play_speed.currentText().replace("x", ""))
        step_dt = float(self.fixed_dt if self.fixed_dt is not None else max(1.0, self.dt_sec.value()))
        delta = (dt_real * speed_mul) / max(step_dt, 1e-6)
        self.playback_step_float += delta * float(getattr(self, "playback_direction", 1))
        max_step = len(self.state_history) - 1
        if self.playback_step_float >= max_step:
            self.playback_step_float = float(max_step)
            self.current_step = max_step
            self.playback_running = False
            self.playback_timer.stop()
            self.playback_active = True
            self._sync_play_button_icon()
            self._set_inputs_enabled(True)
            self._restore_cmd_ui_for_step(self.current_step)
            self._restore_hold_ui_for_step(self.current_step)
            self.refresh_ui()
            return
        if self.playback_step_float <= 0.0:
            self.playback_step_float = 0.0
            self.current_step = 0
            self.playback_running = False
            self.playback_timer.stop()
            self.playback_active = True
            self._sync_play_button_icon()
            self._set_inputs_enabled(True)
            self._restore_step0_initial_widgets_from_history()
            self._restore_cmd_ui_for_step(self.current_step)
            self._restore_hold_ui_for_step(self.current_step)
            self.refresh_ui()
            return
        self.current_step = int(math.floor(self.playback_step_float))
        if int(self.current_step) != prev_step:
            # Keep command/hold panels in sync with playback step changes.
            self._restore_cmd_ui_for_step(self.current_step)
            self._restore_hold_ui_for_step(self.current_step)
        self.refresh_ui()

    def _apply_step0_inputs_to_state(self):
        if self.current_step != 0:
            return
        self.state_history = [self._initial_states()]
        self.transition_history = []
        self._refresh_speed_lock_baseline()

    def _restore_step0_initial_widgets_from_history(self):
        if not self.state_history:
            return
        st0 = self.state_history[0]
        if not isinstance(st0, dict):
            return
        for aid in AIRCRAFT_IDS:
            ac = self.controls[aid]
            st = st0.get(aid, {})
            if not isinstance(st, dict):
                continue
            alt = float(st.get("z_ft", ac.alt_ft.value()))
            hdg = float(st.get("hdg_deg", ac.hdg_deg.value()))
            cas = float(st.get("cas_kt", ac.cas_kt.value()))
            hdg_v = float(int(round(hdg)) % 360)
            ac.alt_ft.blockSignals(True)
            ac.hdg_deg.blockSignals(True)
            ac.cas_kt.blockSignals(True)
            ac.mach.blockSignals(True)
            try:
                ac.alt_ft.setValue(alt)
                ac.hdg_deg.setValue(hdg_v)
                ac.cas_kt.setValue(cas)
                ac._sync_mach_from_cas()
            finally:
                ac.alt_ft.blockSignals(False)
                ac.hdg_deg.blockSignals(False)
                ac.cas_kt.blockSignals(False)
                ac.mach.blockSignals(False)

    def _refresh_speed_lock_baseline(self):
        if not self.state_history:
            return
        base = self.state_history[0]
        for aid in AIRCRAFT_IDS:
            self.speed_lock_initial_cas[aid] = float(base[aid]["cas_kt"])
            self.speed_lock_initial_ps[aid] = self._compute_step0_locked_ps(aid)

    def _on_step0_initial_state_changed(self, *_args):
        if bool(getattr(self, "_bulk_initial_update", False)):
            return
        if self.current_step != 0:
            return
        if bool(getattr(self, "playback_running", False)):
            return
        self._apply_step0_inputs_to_state()
        self._auto_apply_cmd_limits_all()
        self.refresh_ui()

    def _on_dt_sec_changed(self, _v: float):
        if bool(self.dt_sec.signalsBlocked()):
            return
        if int(self.current_step) != 0:
            return
        if bool(getattr(self, "playback_running", False)):
            return
        if not bool(self.dt_sec.hasFocus()):
            return
        # At step 0, allow re-assigning fixed dt so newly advanced steps use the updated value.
        self.fixed_dt = float(self.dt_sec.value())
        if 1 in self.step_cmds or len(self.state_history) > 1:
            self._show_rate_limited_warning(
                "dt_step0_edit",
                "Step 0에서 Step(sec)을 변경했습니다.\n이미 만들어진 step 결과가 어긋나거나 망가질 수 있습니다.",
            )

    def _set_initial_for_aircraft(
        self,
        aid: str,
        *,
        alt_ft: Optional[float] = None,
        hdg_deg: Optional[float] = None,
        cas_kt: Optional[float] = None,
        range_nm: Optional[float] = None,
        bearing_deg: Optional[float] = None,
    ):
        ac = self.controls[aid]
        if alt_ft is not None:
            ac.alt_ft.setValue(float(alt_ft))
        if hdg_deg is not None:
            ac.hdg_deg.setValue(float(hdg_deg))
        if cas_kt is not None:
            ac.cas_kt.setValue(float(cas_kt))
        if range_nm is not None:
            ac.range_nm.setValue(float(range_nm))
        if bearing_deg is not None:
            ac.bearing_deg.setValue(float(bearing_deg))
        ac._sync_mach_from_cas()

    def _set_target_from_anchor_relative(self, anchor_aid: str, target_aid: str, rel_range_nm: float, rel_bearing_deg: float):
        # rel_bearing_deg is relative to anchor heading (0=fwd, 90=right, 180=aft, 270=left).
        a = self.controls[anchor_aid]
        t = self.controls[target_aid]
        if target_aid == "#4" and anchor_aid == "#3":
            # #4 input semantics are relative to #3 by definition.
            t.range_nm.setValue(float(rel_range_nm))
            t.bearing_deg.setValue(self._wrap_hdg(float(rel_bearing_deg)))
            return
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if target_aid == "#6" and anchor_aid == "#5" and mk in {"4vs2", "4vs4"}:
            # In 4vs2/4vs4, #6 input semantics are relative to #5 by definition.
            t.range_nm.setValue(float(rel_range_nm))
            t.bearing_deg.setValue(self._wrap_hdg(float(rel_bearing_deg)))
            return
        if target_aid == "#7" and anchor_aid == "#5" and mk in {"4vs2", "4vs4"}:
            # In 4vs2/4vs4, #7 input semantics are relative to #5 by definition.
            t.range_nm.setValue(float(rel_range_nm))
            t.bearing_deg.setValue(self._wrap_hdg(float(rel_bearing_deg)))
            return
        if target_aid == "#8" and anchor_aid == "#7" and mk in {"4vs2", "4vs4"}:
            # In 4vs2/4vs4, #8 input semantics are relative to #7 by definition.
            t.range_nm.setValue(float(rel_range_nm))
            t.bearing_deg.setValue(self._wrap_hdg(float(rel_bearing_deg)))
            return
        ar = float(a.range_nm.value()) * NM_TO_FT
        ab = math.radians(float(a.bearing_deg.value()))
        ax = ar * math.sin(ab)
        ay = ar * math.cos(ab)
        ah = float(a.hdg_deg.value())
        world_b = self._wrap_hdg(ah + float(rel_bearing_deg))
        wb = math.radians(world_b)
        rr_ft = float(rel_range_nm) * NM_TO_FT
        tx = ax + rr_ft * math.sin(wb)
        ty = ay + rr_ft * math.cos(wb)
        tr_nm = math.hypot(tx, ty) / NM_TO_FT
        tb_deg = self._wrap_hdg(math.degrees(math.atan2(tx, ty)))
        t.range_nm.setValue(float(tr_nm))
        t.bearing_deg.setValue(float(tb_deg))

    def _world_point_from_anchor_relative(self, anchor_aid: str, rel_range_nm: float, rel_bearing_deg: float, z_ft: Optional[float] = None) -> np.ndarray:
        a = self.controls[anchor_aid]
        ar = float(a.range_nm.value()) * NM_TO_FT
        ab = math.radians(float(a.bearing_deg.value()))
        ax = ar * math.sin(ab)
        ay = ar * math.cos(ab)
        ah = float(a.hdg_deg.value())
        world_b = self._wrap_hdg(ah + float(rel_bearing_deg))
        wb = math.radians(world_b)
        rr_ft = float(rel_range_nm) * NM_TO_FT
        x = ax + rr_ft * math.sin(wb)
        y = ay + rr_ft * math.cos(wb)
        z = float(a.alt_ft.value()) if z_ft is None else float(z_ft)
        return np.array([x, y, z], dtype=float)

    @staticmethod
    def _world_point_from_point_relative(origin_ft: np.ndarray, rel_range_nm: float, rel_bearing_deg: float) -> np.ndarray:
        o = np.array(origin_ft, dtype=float)
        rr_ft = float(rel_range_nm) * NM_TO_FT
        wb = math.radians(float(rel_bearing_deg))
        x = float(o[0]) + rr_ft * math.sin(wb)
        y = float(o[1]) + rr_ft * math.cos(wb)
        z = float(o[2])
        return np.array([x, y, z], dtype=float)

    def _clear_dca_be(self):
        self.dca_be_center_ft = None
        self.dca_asset_center_ft = None
        self.dca_ra_zone_center_ft = None
        self.dca_ra_line_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_rect_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_diag1_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_mission_diag2_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_front_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_rear_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_front_center_ft = None
        self.dca_cap_rear_center_ft = None
        self.dca_cap_front_split_centers_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_rear_split_centers_ft = np.zeros((0, 3), dtype=float)
        self.dca_hmrl_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_ldez_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_hdez_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_commit_pts_ft = np.zeros((0, 3), dtype=float)
        self.dca_ra_ui_locked = False
        self._apply_dca_ra_ui_lock()

    def _current_ra_shape_from_setup(self) -> str:
        mk = str(getattr(self, "current_mode_key", "")).strip().lower()
        sk = str(getattr(self, "current_setup_key", "")).upper()
        if mk == "2vs2":
            if "ECHELON" in sk:
                return "ECHELON"
            if "LAB" in sk:
                return "LAB"
            return "RANGE"
        if mk == "4vs2":
            # Prefer broad token check first to avoid exact-string mismatch issues.
            if "ECHELON" in sk:
                return "ECHELON"
            if "LAB" in sk:
                return "LAB"
            if "+ RA " in sk:
                rhs = sk.split("+ RA ", 1)[1].strip()
                if rhs in {"RANGE", "LAB", "ECHELON"}:
                    return rhs
            if "RA ECHELON" in sk:
                return "ECHELON"
            if "RA LAB" in sk:
                return "LAB"
            return "RANGE"
        return "RANGE"

    def _infer_two_ship_ra_shape_from_controls(self, mode_key: str, ra_ids: List[str]) -> str:
        mk = str(mode_key).strip().lower()
        if mk not in {"2vs2", "4vs2"}:
            return ""
        if len(ra_ids) < 2:
            return ""
        wing = str(ra_ids[1])
        if wing not in self.controls:
            return ""
        try:
            rel_b = self._wrap_hdg(float(self.controls[wing].bearing_deg.value()))
        except Exception:
            return ""
        # Two-ship geometry can appear mirrored; accept both-side bearings.
        def _near(targets: List[float]) -> float:
            return min(abs(self._wrap_to_pm180(float(rel_b) - float(t))) for t in targets)

        err_lab = _near([90.0, 270.0])
        err_ech = _near([135.0, 225.0])
        err_rng = _near([180.0, 0.0])
        best_name = "RANGE"
        best_err = err_rng
        if err_lab < best_err:
            best_name = "LAB"
            best_err = err_lab
        if err_ech < best_err:
            best_name = "ECHELON"
            best_err = err_ech
        return best_name

    def _apply_dca_ra_ui_lock(self):
        lock = bool(self.dca_ra_ui_locked) and bool(self._is_dca_active())
        _ba_ids, ra_ids = self._active_ba_ra_ids_for_mode(str(getattr(self, "current_mode_key", "2vs1")))
        for aid in ra_ids:
            if aid not in self.controls:
                continue
            ac = self.controls[aid]
            allow_edit = (not lock) and (int(self.current_step) == 0)
            ac.range_nm.setEnabled(bool(allow_edit))
            ac.bearing_deg.setEnabled(bool(allow_edit))
            if lock:
                ac.range_nm.setToolTip("DCA setup 적용 상태에서는 RA 위치 수동 입력이 비활성화됩니다.")
                ac.bearing_deg.setToolTip("DCA setup 적용 상태에서는 RA 위치 수동 입력이 비활성화됩니다.")

    def _is_dca_active(self) -> bool:
        if self.dca_be_center_ft is not None:
            return True
        if self.dca_asset_center_ft is not None:
            return True
        for pts in (
            self.dca_ra_line_pts_ft,
            self.dca_mission_rect_pts_ft,
            self.dca_mission_diag1_pts_ft,
            self.dca_mission_diag2_pts_ft,
            self.dca_cap_front_pts_ft,
            self.dca_cap_rear_pts_ft,
            self.dca_hmrl_pts_ft,
            self.dca_ldez_pts_ft,
            self.dca_hdez_pts_ft,
            self.dca_commit_pts_ft,
        ):
            if isinstance(pts, np.ndarray) and (pts.size > 0):
                return True
        return False

    def _apply_dca_from_saved_meta(self, dca_meta: Dict[str, str]):
        def _mf(key: str, default: float) -> float:
            try:
                v = dca_meta.get(key, "")
                if v is None or str(v).strip() == "":
                    return float(default)
                return float(v)
            except Exception:
                return float(default)

        def _mb(key: str, default: bool) -> bool:
            v = str(dca_meta.get(key, "")).strip().lower()
            if v == "":
                return bool(default)
            return v in {"1", "true", "yes", "y", "on"}

        mode_key_now = str(getattr(self, "current_mode_key", "2vs1"))
        be_bearing = _mf("dca_be_bearing_deg", float(self.dca_be_default_bearing_deg))
        be_range = _mf("dca_be_range_nm", float(self.dca_be_default_range_nm))
        asset_bearing = _mf("dca_asset_bearing_from_be_deg", float(self.dca_asset_default_bearing_from_be_deg))
        asset_range = _mf("dca_asset_range_from_be_nm", float(self.dca_asset_default_range_from_be_nm))
        asset_same_as_be = _mb("dca_asset_same_as_be", bool(self.dca_asset_same_as_be_default))
        ba_from_asset = _mf("dca_ba_from_asset_nm", float(self.dca_ba_from_asset_nm_default))
        ra_from_asset = _mf("dca_ra_from_asset_nm", float(self.dca_ra_from_asset_nm_default))
        ba_heading = _mf("dca_ba_heading_deg", float(self.dca_ba_heading_deg_default))
        ra_heading = _mf("dca_ra_heading_deg", float(self.dca_ra_heading_deg_default))
        ra_zone_radius = _mf("dca_ra_zone_radius_nm", float(self.dca_ra_zone_radius_nm_default))
        ra_line_forward = _mf("dca_ra_line_forward_nm", float(self.dca_ra_line_forward_nm_default))
        ra_zone_mode = str(dca_meta.get("dca_ra_zone_mode", self.dca_ra_zone_mode_default)).strip().lower()
        if ra_zone_mode not in {"radius", "line"}:
            ra_zone_mode = str(self.dca_ra_zone_mode_default)
        mission_width = _mf("dca_mission_width_nm", float(self.dca_mission_width_nm_default))
        mission_height = _mf("dca_mission_height_nm", float(self.dca_mission_height_nm_default))
        cap_front = _mf("dca_cap_front_nm", float(self.dca_cap_front_nm_default))
        cap_rear = _mf("dca_cap_rear_nm", float(self.dca_cap_rear_nm_default))
        cap_pair_enabled = _mb("dca_cap_pair_enabled", bool(self.dca_cap_pair_enabled_default))
        cap_pair_half_sep = _mf("dca_cap_pair_half_sep_nm", float(self.dca_cap_pair_half_sep_nm_default))
        hmrl = _mf("dca_hmrl_nm", float(self.dca_hmrl_nm_default))
        ldez = _mf("dca_ldez_nm", float(self.dca_ldez_nm_default))
        hdez = _mf("dca_hdez_nm", float(self.dca_hdez_nm_default))
        commit = _mf("dca_commit_nm", float(self.dca_commit_nm_default))

        self.dca_be_default_bearing_deg = float(be_bearing)
        self.dca_be_default_range_nm = float(be_range)
        self.dca_asset_default_bearing_from_be_deg = float(asset_bearing)
        self.dca_asset_default_range_from_be_nm = float(asset_range)
        self.dca_asset_same_as_be_default = bool(asset_same_as_be)
        self.dca_ba_from_asset_nm_default = float(ba_from_asset)
        self.dca_ra_from_asset_nm_default = float(ra_from_asset)
        self.dca_ba_heading_deg_default = float(ba_heading)
        self.dca_ra_heading_deg_default = float(ra_heading)
        self.dca_ra_zone_radius_nm_default = float(ra_zone_radius)
        self.dca_ra_line_forward_nm_default = float(ra_line_forward)
        self.dca_ra_zone_mode_default = str(ra_zone_mode)
        self.dca_mission_width_nm_default = float(mission_width)
        self.dca_mission_height_nm_default = float(mission_height)
        self.dca_cap_front_nm_default = float(cap_front)
        self.dca_cap_rear_nm_default = float(cap_rear)
        self.dca_cap_pair_enabled_default = bool(cap_pair_enabled)
        self.dca_cap_pair_half_sep_nm_default = float(cap_pair_half_sep)
        self.dca_hmrl_nm_default = float(hmrl)
        self.dca_ldez_nm_default = float(ldez)
        self.dca_hdez_nm_default = float(hdez)
        self.dca_commit_nm_default = float(commit)

        self._set_dca_be_absolute(range_nm=float(be_range), bearing_deg=float(be_bearing))
        if bool(asset_same_as_be):
            self.dca_asset_center_ft = np.array(self.dca_be_center_ft, dtype=float) if self.dca_be_center_ft is not None else None
        else:
            self._set_dca_asset_from_be(rel_range_nm=float(asset_range), rel_bearing_deg=float(asset_bearing))
        self._apply_dca_ba_ra_layout_via_be(
            mode_key=str(mode_key_now),
            asset_bearing_from_be_deg=float(asset_bearing),
            asset_range_from_be_nm=float(asset_range),
            ba_from_asset_nm=float(ba_from_asset),
            ra_from_asset_nm=float(ra_from_asset),
            ba_heading_deg=float(ba_heading),
            ra_heading_deg=float(ra_heading),
        )
        self._set_dca_ra_touchdown_zone(
            asset_forward_bearing_deg=float(asset_bearing),
            zone_radius_nm=float(ra_zone_radius),
            line_forward_nm=float(ra_line_forward),
            mode=str(ra_zone_mode),
        )
        self._set_dca_mission_area(
            width_nm=float(mission_width),
            height_nm=float(mission_height),
            asset_forward_bearing_deg=float(asset_bearing),
        )
        self._set_dca_operational_lines(
            asset_forward_bearing_deg=float(asset_bearing),
            width_nm=float(mission_width),
            cap_front_nm=float(cap_front),
            cap_rear_nm=float(cap_rear),
            cap_pair_enabled=bool(cap_pair_enabled),
            cap_pair_half_sep_nm=float(cap_pair_half_sep),
            hmrl_nm=float(hmrl),
            ldez_nm=float(ldez),
            hdez_nm=float(hdez),
            commit_nm=float(commit),
        )
        self.dca_ra_ui_locked = True
        self._apply_dca_ra_ui_lock()

    def _set_dca_be_absolute(self, range_nm: float, bearing_deg: float, z_ft: Optional[float] = None):
        rr_ft = float(range_nm) * NM_TO_FT
        wb = math.radians(float(bearing_deg))
        x = rr_ft * math.sin(wb)
        y = rr_ft * math.cos(wb)
        if z_ft is None:
            z = float(self.controls["#1"].alt_ft.value()) if "#1" in self.controls else 20000.0
        else:
            z = float(z_ft)
        self.dca_be_center_ft = np.array([x, y, z], dtype=float)

    def _set_dca_asset_from_be(self, rel_range_nm: float, rel_bearing_deg: float):
        if self.dca_be_center_ft is None:
            self.dca_asset_center_ft = None
            return
        self.dca_asset_center_ft = self._world_point_from_point_relative(
            origin_ft=self.dca_be_center_ft,
            rel_range_nm=float(rel_range_nm),
            rel_bearing_deg=float(rel_bearing_deg),
        )

    def _world_point_from_control(self, aid: str) -> np.ndarray:
        st0 = self._initial_states()
        if aid in st0:
            return np.array([float(st0[aid]["x_ft"]), float(st0[aid]["y_ft"]), float(st0[aid]["z_ft"])], dtype=float)
        ac = self.controls[aid]
        r_ft = float(ac.range_nm.value()) * NM_TO_FT
        b = math.radians(float(ac.bearing_deg.value()))
        return np.array([r_ft * math.sin(b), r_ft * math.cos(b), float(ac.alt_ft.value())], dtype=float)

    def _set_control_from_world_point(self, aid: str, p: np.ndarray):
        ac = self.controls[aid]
        x = float(p[0])
        y = float(p[1])
        z = float(p[2])
        r_nm = math.hypot(x, y) / NM_TO_FT
        b_deg = self._wrap_hdg(math.degrees(math.atan2(x, y)))
        ac.range_nm.setValue(float(r_nm))
        ac.bearing_deg.setValue(float(b_deg))
        ac.alt_ft.setValue(float(z))

    def _set_control_from_world_point_mode(self, aid: str, p: np.ndarray, mode_key: str, world_targets: Dict[str, np.ndarray], heading_targets: Dict[str, float]):
        mk = str(mode_key).strip()
        if aid == "#4":
            ref_id = "#3"
        elif mk in {"4vs2", "4vs4"} and aid in {"#6", "#7"}:
            ref_id = "#5"
        elif mk in {"4vs2", "4vs4"} and aid == "#8":
            ref_id = "#7"
        else:
            ref_id = ""
        if not ref_id or (ref_id not in world_targets):
            self._set_control_from_world_point(aid, p)
            return
        ref_p = np.array(world_targets[ref_id], dtype=float)
        ref_h = float(heading_targets.get(ref_id, self.controls[ref_id].hdg_deg.value()))
        v = np.array(p, dtype=float) - ref_p
        r_nm = math.hypot(float(v[0]), float(v[1])) / NM_TO_FT
        world_b = self._wrap_hdg(math.degrees(math.atan2(float(v[0]), float(v[1]))))
        rel_b = self._wrap_hdg(world_b - ref_h)
        ac = self.controls[aid]
        ac.range_nm.setValue(float(r_nm))
        ac.bearing_deg.setValue(float(rel_b))
        ac.alt_ft.setValue(float(p[2]))

    def _active_ba_ra_ids_for_mode(self, mode_key: str) -> Tuple[List[str], List[str]]:
        mk = str(mode_key).strip()
        active = [aid for aid in MODE_ACTIVE_IDS.get(mk, MODE_ACTIVE_IDS["2vs1"]) if aid in AIRCRAFT_IDS]
        ba = [aid for aid in DCA_BA_IDS_BY_MODE.get(mk, ["#1", "#2"]) if aid in active]
        ra = [aid for aid in active if aid not in ba]
        return ba, ra

    def _collect_group_offsets_nm(self, ids: List[str]) -> Dict[str, Tuple[float, float]]:
        if not ids:
            return {}
        lead = str(ids[0])
        world_now = {aid: self._world_point_from_control(str(aid)) for aid in ids}
        lead_p = np.array(world_now[lead], dtype=float)
        out: Dict[str, Tuple[float, float]] = {lead: (0.0, 0.0)}
        for aid in ids[1:]:
            p = np.array(world_now[str(aid)], dtype=float)
            d = p - lead_p
            out[str(aid)] = (float(d[0]) / NM_TO_FT, float(d[1]) / NM_TO_FT)
        return out

    def _apply_dca_ba_ra_layout_via_be(
        self,
        *,
        mode_key: str,
        asset_bearing_from_be_deg: float,
        asset_range_from_be_nm: float,
        ba_from_asset_nm: float,
        ra_from_asset_nm: float,
        ba_heading_deg: float,
        ra_heading_deg: float,
        ba_member_offsets_nm: Optional[Dict[str, Tuple[float, float]]] = None,
        ra_member_offsets_nm: Optional[Dict[str, Tuple[float, float]]] = None,
        respect_member_offsets: bool = False,
        ba_heading_overrides: Optional[Dict[str, float]] = None,
    ):
        if self.dca_be_center_ft is None:
            return
        ba_ids, ra_ids = self._active_ba_ra_ids_for_mode(mode_key)
        if not ba_ids:
            return
        # Internal anchor uses absolute B.E reference.
        asset_vec = np.array(
            [
                float(asset_range_from_be_nm) * NM_TO_FT * math.sin(math.radians(float(asset_bearing_from_be_deg))),
                float(asset_range_from_be_nm) * NM_TO_FT * math.cos(math.radians(float(asset_bearing_from_be_deg))),
                0.0,
            ],
            dtype=float,
        )
        be = np.array(self.dca_be_center_ft, dtype=float)
        asset_world = be + asset_vec
        world_now = {aid: self._world_point_from_control(aid) for aid in (ba_ids + ra_ids)}
        ba_offsets = dict(ba_member_offsets_nm or {})
        ra_offsets = dict(ra_member_offsets_nm or {})
        ba_heading_overrides = dict(ba_heading_overrides or {})
        ba_target = np.array(self._world_point_from_point_relative(asset_world, float(ba_from_asset_nm), float(ba_heading_deg)), dtype=float)

        targets: Dict[str, np.ndarray] = {}
        headings: Dict[str, float] = {}
        ba_lead = str(ba_ids[0])
        ba_lead_off = np.array(ba_offsets.get(ba_lead, (0.0, 0.0)), dtype=float)
        ba_lead_pos = np.array(ba_target, dtype=float) + np.array([float(ba_lead_off[0]) * NM_TO_FT, float(ba_lead_off[1]) * NM_TO_FT, 0.0], dtype=float)
        for aid in ba_ids:
            p = np.array(ba_lead_pos, dtype=float)
            if str(aid) != ba_lead:
                off = np.array(ba_offsets.get(str(aid), (0.0, 0.0)), dtype=float)
                p = p + np.array([float(off[0]) * NM_TO_FT, float(off[1]) * NM_TO_FT, 0.0], dtype=float)
            p[2] = float(world_now[aid][2])
            targets[aid] = p
            headings[aid] = float(ba_heading_overrides.get(str(aid), float(ba_heading_deg)))

        if ra_ids:
            # RA center is always placed on ASSET forward-axis.
            ra_target = np.array(
                self._world_point_from_point_relative(asset_world, float(ra_from_asset_nm), float(asset_bearing_from_be_deg)),
                dtype=float,
            )
            ra_shape = str(self._current_ra_shape_from_setup()).upper()
            # Fallback to control-state inference if setup-key parsing was stale or ambiguous.
            inferred_shape = str(self._infer_two_ship_ra_shape_from_controls(mode_key, ra_ids)).upper()
            if (ra_shape not in {"LAB", "ECHELON"}) and (inferred_shape in {"LAB", "ECHELON", "RANGE"}):
                ra_shape = inferred_shape
            if (len(ra_ids) >= 2) and (ra_shape in {"LAB", "ECHELON"}) and (not bool(respect_member_offsets)):
                lead = str(ra_ids[0])
                wing = str(ra_ids[1])
                pair_dist_nm = float(self.controls[wing].range_nm.value()) if wing in self.controls else 2.0
                if (not np.isfinite(pair_dist_nm)) or (pair_dist_nm <= 0.0):
                    pair_dist_nm = 2.0
                half_ft = 0.5 * float(pair_dist_nm) * NM_TO_FT
                fw_rad = math.radians(float(asset_bearing_from_be_deg))
                fwd = np.array([math.sin(fw_rad), math.cos(fw_rad), 0.0], dtype=float)
                right = np.array([math.cos(fw_rad), -math.sin(fw_rad), 0.0], dtype=float)
                left = -right
                if ra_shape == "LAB":
                    d_lead = left
                    d_wing = right
                else:
                    # ECHELON: lead = left-forward, wing = right-aft
                    d_lead = left + fwd
                    d_wing = right - fwd
                    n1 = max(float(np.linalg.norm(d_lead)), 1e-9)
                    n2 = max(float(np.linalg.norm(d_wing)), 1e-9)
                    d_lead = d_lead / n1
                    d_wing = d_wing / n2
                p_lead = np.array(ra_target, dtype=float) + (d_lead * half_ft)
                p_wing = np.array(ra_target, dtype=float) + (d_wing * half_ft)
                p_lead[2] = float(world_now[lead][2])
                p_wing[2] = float(world_now[wing][2])
                targets[lead] = p_lead
                targets[wing] = p_wing
                headings[lead] = float(ra_heading_deg)
                headings[wing] = float(ra_heading_deg)
                for aid in ra_ids[2:]:
                    p = np.array(ra_target, dtype=float)
                    off = np.array(ra_offsets.get(str(aid), (0.0, 0.0)), dtype=float)
                    p = p + np.array([float(off[0]) * NM_TO_FT, float(off[1]) * NM_TO_FT, 0.0], dtype=float)
                    p[2] = float(world_now[aid][2])
                    targets[aid] = p
                    headings[aid] = float(ra_heading_deg)
            else:
                ra_lead = str(ra_ids[0])
                ra_lead_off = np.array(ra_offsets.get(ra_lead, (0.0, 0.0)), dtype=float)
                ra_lead_pos = np.array(ra_target, dtype=float) + np.array([float(ra_lead_off[0]) * NM_TO_FT, float(ra_lead_off[1]) * NM_TO_FT, 0.0], dtype=float)
                for aid in ra_ids:
                    p = np.array(ra_lead_pos, dtype=float)
                    if str(aid) != ra_lead:
                        off = np.array(ra_offsets.get(str(aid), (0.0, 0.0)), dtype=float)
                        p = p + np.array([float(off[0]) * NM_TO_FT, float(off[1]) * NM_TO_FT, 0.0], dtype=float)
                    p[2] = float(world_now[aid][2])
                    targets[aid] = p
                    headings[aid] = float(ra_heading_deg)

        for aid in ba_ids:
            self.controls[aid].hdg_deg.setValue(float(headings.get(aid, float(ba_heading_deg))))
        for aid in ra_ids:
            self.controls[aid].hdg_deg.setValue(float(ra_heading_deg))
        for aid in (ba_ids + ra_ids):
            self._set_control_from_world_point_mode(aid, targets[aid], mode_key, targets, headings)

    def _set_dca_ra_touchdown_zone(self, asset_forward_bearing_deg: float, zone_radius_nm: float, line_forward_nm: float, mode: str = "radius"):
        mode_key = str(mode).strip().lower()
        if mode_key not in {"radius", "line"}:
            mode_key = "radius"
        self.dca_ra_zone_mode = mode_key
        self.dca_ra_zone_radius_nm = float(zone_radius_nm)
        self.dca_ra_line_forward_nm = float(line_forward_nm)
        if self.dca_asset_center_ft is None:
            self.dca_ra_zone_center_ft = None
            self.dca_ra_line_pts_ft = np.zeros((0, 3), dtype=float)
            return
        if mode_key == "radius":
            self.dca_ra_zone_center_ft = np.array(self.dca_asset_center_ft, dtype=float)
            self.dca_ra_line_pts_ft = np.zeros((0, 3), dtype=float)
            return
        self.dca_ra_zone_center_ft = None
        line_anchor = self._world_point_from_point_relative(
            origin_ft=self.dca_asset_center_ft,
            rel_range_nm=float(line_forward_nm),
            rel_bearing_deg=float(asset_forward_bearing_deg),
        )
        half_len_ft = max(100.0, float(zone_radius_nm) * NM_TO_FT)
        dir_270 = np.array([math.sin(math.radians(270.0)), math.cos(math.radians(270.0)), 0.0], dtype=float)
        p1 = line_anchor - (dir_270 * half_len_ft)
        p2 = line_anchor + (dir_270 * half_len_ft)
        self.dca_ra_line_pts_ft = np.vstack([p1, p2]).astype(float)

    def _set_dca_mission_area(self, width_nm: float, height_nm: float, asset_forward_bearing_deg: float):
        self.dca_mission_width_nm = float(width_nm)
        self.dca_mission_height_nm = float(height_nm)
        if self.dca_asset_center_ft is None:
            self.dca_mission_rect_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_mission_diag1_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_mission_diag2_pts_ft = np.zeros((0, 3), dtype=float)
            return
        c = np.array(self.dca_asset_center_ft, dtype=float)
        fw = math.radians(float(asset_forward_bearing_deg))
        fwd = np.array([math.sin(fw), math.cos(fw), 0.0], dtype=float)
        right = np.array([math.sin(math.radians(float(asset_forward_bearing_deg) + 90.0)), math.cos(math.radians(float(asset_forward_bearing_deg) + 90.0)), 0.0], dtype=float)
        hw = 0.5 * float(width_nm) * NM_TO_FT
        h = float(height_nm) * NM_TO_FT
        rear_left = c - (right * hw)
        rear_right = c + (right * hw)
        front_left = rear_left + (fwd * h)
        front_right = rear_right + (fwd * h)
        # Rear edge crosses ASSET; height extends only forward.
        self.dca_mission_rect_pts_ft = np.vstack([rear_left, rear_right, front_right, front_left, rear_left]).astype(float)
        # Side connections: near-left <-> far-left, near-right <-> far-right.
        self.dca_mission_diag1_pts_ft = np.vstack([rear_left, front_left]).astype(float)
        self.dca_mission_diag2_pts_ft = np.vstack([rear_right, front_right]).astype(float)

    def _build_width_line_at_distance(self, asset_forward_bearing_deg: float, dist_nm: float, width_nm: float) -> np.ndarray:
        if self.dca_asset_center_ft is None:
            return np.zeros((0, 3), dtype=float)
        c = np.array(self.dca_asset_center_ft, dtype=float)
        fw = math.radians(float(asset_forward_bearing_deg))
        fwd = np.array([math.sin(fw), math.cos(fw), 0.0], dtype=float)
        r = math.radians(float(asset_forward_bearing_deg) + 90.0)
        right = np.array([math.sin(r), math.cos(r), 0.0], dtype=float)
        center = c + (fwd * (float(dist_nm) * NM_TO_FT))
        hw = 0.5 * float(width_nm) * NM_TO_FT
        p1 = center - (right * hw)
        p2 = center + (right * hw)
        return np.vstack([p1, p2]).astype(float)

    def _build_point_at_distance(self, asset_forward_bearing_deg: float, dist_nm: float) -> Optional[np.ndarray]:
        if self.dca_asset_center_ft is None:
            return None
        c = np.array(self.dca_asset_center_ft, dtype=float)
        fw = math.radians(float(asset_forward_bearing_deg))
        fwd = np.array([math.sin(fw), math.cos(fw), 0.0], dtype=float)
        p = c + (fwd * (float(dist_nm) * NM_TO_FT))
        return np.array(p, dtype=float)

    def _set_dca_operational_lines(
        self,
        *,
        asset_forward_bearing_deg: float,
        width_nm: float,
        cap_front_nm: float,
        cap_rear_nm: float,
        cap_pair_enabled: bool = False,
        cap_pair_half_sep_nm: float = 0.0,
        hmrl_nm: float,
        ldez_nm: float,
        hdez_nm: float,
        commit_nm: float,
    ):
        self.dca_cap_front_nm_default = float(cap_front_nm)
        self.dca_cap_rear_nm_default = float(cap_rear_nm)
        self.dca_cap_pair_enabled_default = bool(cap_pair_enabled)
        self.dca_cap_pair_half_sep_nm_default = float(cap_pair_half_sep_nm)
        self.dca_hmrl_nm_default = float(hmrl_nm)
        self.dca_ldez_nm_default = float(ldez_nm)
        self.dca_hdez_nm_default = float(hdez_nm)
        self.dca_commit_nm_default = float(commit_nm)
        if self.dca_asset_center_ft is None:
            self.dca_cap_front_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_cap_rear_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_cap_front_center_ft = None
            self.dca_cap_rear_center_ft = None
            self.dca_cap_front_split_centers_ft = np.zeros((0, 3), dtype=float)
            self.dca_cap_rear_split_centers_ft = np.zeros((0, 3), dtype=float)
            self.dca_hmrl_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_ldez_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_hdez_pts_ft = np.zeros((0, 3), dtype=float)
            self.dca_commit_pts_ft = np.zeros((0, 3), dtype=float)
            return
        self.dca_cap_front_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(cap_front_nm), float(width_nm))
        self.dca_cap_rear_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(cap_rear_nm), float(width_nm))
        self.dca_cap_front_center_ft = self._build_point_at_distance(asset_forward_bearing_deg, float(cap_front_nm))
        self.dca_cap_rear_center_ft = self._build_point_at_distance(asset_forward_bearing_deg, float(cap_rear_nm))
        self.dca_cap_front_split_centers_ft = np.zeros((0, 3), dtype=float)
        self.dca_cap_rear_split_centers_ft = np.zeros((0, 3), dtype=float)
        if bool(cap_pair_enabled) and (self.dca_cap_front_center_ft is not None) and (self.dca_cap_rear_center_ft is not None):
            fw = math.radians(float(asset_forward_bearing_deg))
            right = np.array([math.cos(fw), -math.sin(fw), 0.0], dtype=float)
            half_w_nm = 0.5 * float(width_nm)
            sep_nm = float(min(max(0.0, float(cap_pair_half_sep_nm)), half_w_nm))
            sep_ft = sep_nm * NM_TO_FT
            cf = np.array(self.dca_cap_front_center_ft, dtype=float)
            cr = np.array(self.dca_cap_rear_center_ft, dtype=float)
            self.dca_cap_front_split_centers_ft = np.array([cf - (right * sep_ft), cf + (right * sep_ft)], dtype=float)
            self.dca_cap_rear_split_centers_ft = np.array([cr - (right * sep_ft), cr + (right * sep_ft)], dtype=float)
        self.dca_hmrl_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(hmrl_nm), float(width_nm))
        self.dca_ldez_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(ldez_nm), float(width_nm))
        self.dca_hdez_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(hdez_nm), float(width_nm))
        self.dca_commit_pts_ft = self._build_width_line_at_distance(asset_forward_bearing_deg, float(commit_nm), float(width_nm))

    def _update_dca_point_labels(self):
        # DCA output view: hide BE/ASSET text labels by request.
        self.dca_be_label.hide()
        self.dca_asset_label.hide()
        return

        def _place(lbl: QLabel, p: Optional[np.ndarray]):
            if p is None:
                lbl.hide()
                return
            sp = self.view._project_point(np.array(p, dtype=float)) if hasattr(self.view, "_project_point") else None
            if sp is None:
                lbl.hide()
                return
            lbl.adjustSize()
            x = int(round(float(sp[0]) + 4.0))
            y = int(round(float(sp[1]) - (0.5 * float(lbl.height()))))
            vw = int(max(1, self.view.width()))
            vh = int(max(1, self.view.height()))
            if (x < 0) or (y < 0) or (x > (vw - lbl.width())) or (y > (vh - lbl.height())):
                lbl.hide()
                return
            lbl.move(x, y)
            lbl.show()
            lbl.raise_()

        _place(self.dca_be_label, self.dca_be_center_ft)
        _place(self.dca_asset_label, self.dca_asset_center_ft)

    def _should_prompt_dca_setup(self, mode_key: str, setup_key: str) -> bool:
        mk = str(mode_key).strip().upper()
        sk = str(setup_key).strip().upper()
        if mk in {"2VS2", "4VS2", "4VS4"}:
            return True
        if mk == "2VS1" and sk == "TI SETUP":
            return True
        return False

    def _prompt_dca_be_setup(self):
        ask = QMessageBox.question(
            self,
            "DCA Setup",
            "DCA setup을 실시할까요?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if ask != QMessageBox.StandardButton.Yes:
            self._clear_dca_be()
            return
        # Default B.E: absolute world bearing/range.
        self._set_dca_be_absolute(
            range_nm=float(self.dca_be_default_range_nm),
            bearing_deg=float(self.dca_be_default_bearing_deg),
        )
        self.dca_asset_center_ft = np.array(self.dca_be_center_ft, dtype=float) if self.dca_be_center_ft is not None else None
        suggested_ba_from_asset_nm = float(self.dca_cap_front_nm_default)
        suggested_ra_from_asset_nm = float(self.dca_commit_nm_default) + (
            0.5 * (float(self.dca_mission_height_nm_default) - float(self.dca_commit_nm_default))
        )
        ba_from_asset_for_dialog = (
            float(self.dca_ba_from_asset_nm_default)
            if bool(self.dca_ba_from_asset_user_set)
            else float(suggested_ba_from_asset_nm)
        )
        ra_from_asset_for_dialog = (
            float(self.dca_ra_from_asset_nm_default)
            if bool(self.dca_ra_from_asset_user_set)
            else float(suggested_ra_from_asset_nm)
        )
        mode_key_now = str(getattr(self, "current_mode_key", "2vs1"))
        ba_ids, ra_ids = self._active_ba_ra_ids_for_mode(mode_key_now)
        ba_offsets_nm = self._collect_group_offsets_nm(ba_ids)
        ra_offsets_nm = self._collect_group_offsets_nm(ra_ids)
        dlg = DcaSetupDialog(
            self,
            be_bearing_deg=float(self.dca_be_default_bearing_deg),
            be_range_nm=float(self.dca_be_default_range_nm),
            asset_bearing_from_be_deg=float(self.dca_asset_default_bearing_from_be_deg),
            asset_range_from_be_nm=float(self.dca_asset_default_range_from_be_nm),
            asset_same_as_be=bool(self.dca_asset_same_as_be_default),
            ba_from_asset_nm=float(ba_from_asset_for_dialog),
            ra_from_asset_nm=float(ra_from_asset_for_dialog),
            ba_heading_deg=float(self.dca_ba_heading_deg_default),
            ra_heading_deg=float(self.dca_ra_heading_deg_default),
            mode_key=str(getattr(self, "current_mode_key", "2vs1")),
            ra_zone_radius_nm=float(self.dca_ra_zone_radius_nm_default),
            ra_line_forward_nm=float(self.dca_ra_line_forward_nm_default),
            ra_zone_mode=str(self.dca_ra_zone_mode_default),
            mission_width_nm=float(self.dca_mission_width_nm_default),
            mission_height_nm=float(self.dca_mission_height_nm_default),
            cap_front_nm=float(self.dca_cap_front_nm_default),
            cap_rear_nm=float(self.dca_cap_rear_nm_default),
            cap_pair_enabled=bool(self.dca_cap_pair_enabled_default),
            cap_pair_half_sep_nm=float(self.dca_cap_pair_half_sep_nm_default),
            hmrl_nm=float(self.dca_hmrl_nm_default),
            ldez_nm=float(self.dca_ldez_nm_default),
            hdez_nm=float(self.dca_hdez_nm_default),
            commit_nm=float(self.dca_commit_nm_default),
            ba_ids_preview=ba_ids,
            ra_ids_preview=ra_ids,
            ba_member_offsets_nm=ba_offsets_nm,
            ra_member_offsets_nm=ra_offsets_nm,
            ra_shape_preview=str(self._current_ra_shape_from_setup()),
        )
        # Open DCA setup dialog in full-window mode (maximized).
        try:
            scr = self.screen() or QApplication.primaryScreen()
            if scr is not None:
                dlg.setGeometry(scr.availableGeometry())
        except Exception:
            pass
        dlg.setWindowState((dlg.windowState() & ~Qt.WindowState.WindowFullScreen) | Qt.WindowState.WindowMaximized)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        (
            be_bearing_deg,
            be_range_nm,
            asset_bearing_deg,
            asset_range_nm,
            asset_same_as_be,
            ba_from_asset_nm,
            ra_from_asset_nm,
            ba_heading_deg,
            ra_heading_deg,
            ra_zone_radius_nm,
            ra_line_forward_nm,
            ra_zone_mode,
            mission_width_nm,
            mission_height_nm,
            cap_front_nm,
            cap_rear_nm,
            hmrl_nm,
            ldez_nm,
            hdez_nm,
            commit_nm,
            cap_pair_enabled,
            cap_pair_half_sep_nm,
            ba_member_offsets_nm_new,
            ra_member_offsets_nm_new,
            _drag_changed,
            ba_heading_overrides_new,
        ) = dlg.selection()
        self.dca_be_default_bearing_deg = float(be_bearing_deg)
        self.dca_be_default_range_nm = float(be_range_nm)
        self.dca_asset_default_bearing_from_be_deg = float(asset_bearing_deg)
        self.dca_asset_default_range_from_be_nm = float(asset_range_nm)
        self.dca_asset_same_as_be_default = bool(asset_same_as_be)
        suggested_ba_from_asset_nm_after = float(cap_front_nm)
        suggested_ra_from_asset_nm_after = float(commit_nm) + (0.5 * (float(mission_height_nm) - float(commit_nm)))
        self.dca_ba_from_asset_user_set = abs(float(ba_from_asset_nm) - suggested_ba_from_asset_nm_after) > 1e-9
        self.dca_ra_from_asset_user_set = abs(float(ra_from_asset_nm) - suggested_ra_from_asset_nm_after) > 1e-9
        self.dca_ba_from_asset_nm_default = float(ba_from_asset_nm)
        self.dca_ra_from_asset_nm_default = float(ra_from_asset_nm)
        self.dca_ba_heading_deg_default = float(ba_heading_deg)
        self.dca_ra_heading_deg_default = float(ra_heading_deg)
        self.dca_ra_zone_radius_nm_default = float(ra_zone_radius_nm)
        self.dca_ra_line_forward_nm_default = float(ra_line_forward_nm)
        self.dca_ra_zone_mode_default = str(ra_zone_mode)
        self.dca_mission_width_nm_default = float(mission_width_nm)
        self.dca_mission_height_nm_default = float(mission_height_nm)
        self.dca_cap_front_nm_default = float(cap_front_nm)
        self.dca_cap_rear_nm_default = float(cap_rear_nm)
        self.dca_cap_pair_enabled_default = bool(cap_pair_enabled)
        self.dca_cap_pair_half_sep_nm_default = float(cap_pair_half_sep_nm)
        self.dca_hmrl_nm_default = float(hmrl_nm)
        self.dca_ldez_nm_default = float(ldez_nm)
        self.dca_hdez_nm_default = float(hdez_nm)
        self.dca_commit_nm_default = float(commit_nm)
        self._set_dca_be_absolute(range_nm=float(be_range_nm), bearing_deg=float(be_bearing_deg))
        if bool(asset_same_as_be):
            self.dca_asset_center_ft = np.array(self.dca_be_center_ft, dtype=float) if self.dca_be_center_ft is not None else None
        else:
            self._set_dca_asset_from_be(rel_range_nm=float(asset_range_nm), rel_bearing_deg=float(asset_bearing_deg))
        self._apply_dca_ba_ra_layout_via_be(
            mode_key=str(getattr(self, "current_mode_key", "2vs1")),
            asset_bearing_from_be_deg=float(asset_bearing_deg),
            asset_range_from_be_nm=float(asset_range_nm),
            ba_from_asset_nm=float(ba_from_asset_nm),
            ra_from_asset_nm=float(ra_from_asset_nm),
            ba_heading_deg=float(ba_heading_deg),
            ra_heading_deg=float(ra_heading_deg),
            ba_member_offsets_nm=dict(ba_member_offsets_nm_new or {}),
            ra_member_offsets_nm=dict(ra_member_offsets_nm_new or {}),
            respect_member_offsets=bool(_drag_changed),
            ba_heading_overrides=dict(ba_heading_overrides_new or {}),
        )
        self._set_dca_ra_touchdown_zone(
            asset_forward_bearing_deg=float(asset_bearing_deg),
            zone_radius_nm=float(ra_zone_radius_nm),
            line_forward_nm=float(ra_line_forward_nm),
            mode=str(ra_zone_mode),
        )
        self._set_dca_mission_area(
            width_nm=float(mission_width_nm),
            height_nm=float(mission_height_nm),
            asset_forward_bearing_deg=float(asset_bearing_deg),
        )
        self._set_dca_operational_lines(
            asset_forward_bearing_deg=float(asset_bearing_deg),
            width_nm=float(mission_width_nm),
            cap_front_nm=float(cap_front_nm),
            cap_rear_nm=float(cap_rear_nm),
            cap_pair_enabled=bool(cap_pair_enabled),
            cap_pair_half_sep_nm=float(cap_pair_half_sep_nm),
            hmrl_nm=float(hmrl_nm),
            ldez_nm=float(ldez_nm),
            hdez_nm=float(hdez_nm),
            commit_nm=float(commit_nm),
        )
        self.dca_ra_ui_locked = True
        self._apply_dca_ra_ui_lock()

    def _arrange_aircraft_panels_for_mode(self, mode_key: str):
        if not hasattr(self, "aircraft_row_layout") or self.aircraft_row_layout is None:
            return
        if not hasattr(self, "controls") or not self.controls:
            return
        mk = str(mode_key).strip()
        layout = self.aircraft_row_layout
        for aid in AIRCRAFT_IDS:
            try:
                layout.removeWidget(self.controls[aid].group)
            except Exception:
                pass
        if mk in {"4vs2", "4vs4"}:
            # Top row: #1~#4, Bottom row: #5~#8
            for idx, aid in enumerate(AIRCRAFT_IDS):
                r = 0 if idx < 4 else 1
                c = idx if idx < 4 else (idx - 4)
                layout.addWidget(self.controls[aid].group, r, c)
            for c in range(8):
                layout.setColumnStretch(c, 1 if c < 4 else 0)
        else:
            # Default layout: 2 columns
            for i, aid in enumerate(AIRCRAFT_IDS):
                layout.addWidget(self.controls[aid].group, i // 2, i % 2)
            for c in range(8):
                layout.setColumnStretch(c, 1 if c < 2 else 0)

    def _refresh_offset_anchor_labels_for_mode(self, mode_key: str):
        mk = str(mode_key).strip()
        anchors: Dict[str, str] = {aid: "#1" for aid in AIRCRAFT_IDS if aid != "#1"}
        anchors["#4"] = "#3"
        if mk in {"4vs2", "4vs4"}:
            anchors["#6"] = "#5"
            anchors["#7"] = "#5"
            anchors["#8"] = "#7"
        for aid, anc in anchors.items():
            if aid in self.controls:
                self.controls[aid].set_offset_anchor_label(anc)

    def _current_state_for_aid(self, aid: str) -> Dict:
        if (0 <= int(self.current_step) < len(self.state_history)):
            st = self.state_history[self.current_step].get(aid, {})
            if isinstance(st, dict):
                return st
        return {}

    def _compute_cmd_g_ps_max(self, aid: str) -> float:
        st = self._current_state_for_aid(aid)
        cmd = self.controls[aid].read_command()
        power = str(cmd.get("power", "M"))
        cas_now = float(st.get("cas_kt", self.controls[aid].cas_kt.value() if aid in self.controls else 350.0))
        alt_now = float(st.get("z_ft", self.controls[aid].alt_ft.value() if aid in self.controls else 15000.0))
        g_ps_cap = self._find_g_max(power, cas_now, alt_now, g_cap=9.0)
        if np.isnan(g_ps_cap):
            return 9.0
        return float(np.clip(g_ps_cap, 1.0, 9.0))

    def _update_cmd_g_dynamic_cap(self, aid: str, apply_cap_to_value: bool = True):
        if aid not in self.controls:
            return
        ac = self.controls[aid]
        gmax = quantize_g_01(self._compute_cmd_g_ps_max(aid), min_g=1.0, max_g=9.0)
        cur_min = max(0.5, float(ac.g_cmd.minimum()))
        use_max = bool(ac.g_max_chk.isChecked())
        # Important: if MAX is not checked, keep full command range and never auto-clip g_cmd.
        ac.g_cmd.setRange(cur_min, float(gmax if use_max else 9.0))
        if use_max:
            ac.g_cmd.setToolTip(f"현재 조건 기준 Max G: {gmax:.1f} (PS 기반, MAX 적용)")
        else:
            ac.g_cmd.setToolTip(f"현재 조건 기준 Max G: {gmax:.1f} (PS 기반, 참고값)")
        if apply_cap_to_value and use_max:
            gv = float(ac.g_cmd.value())
            if gv > gmax + 1e-9:
                ac.g_cmd.setValue(float(gmax))

    @staticmethod
    def _bank_from_g_pitch(g_cmd: float, pitch_deg: float) -> float:
        n = max(1.0, float(g_cmd))
        cos_gamma = math.cos(math.radians(float(pitch_deg)))
        cos_bank = float(np.clip(cos_gamma / max(n, 1e-6), -1.0, 1.0))
        return quantize_bank_deg(math.degrees(math.acos(cos_bank)), min_bank=0.0, max_bank=180.0)

    @staticmethod
    def _pitch_from_g_bank(g_cmd: float, bank_deg: float, pull_mode: str) -> float:
        n = max(1.0, float(g_cmd))
        n_vertical = n * math.cos(math.radians(float(bank_deg)))
        if n_vertical >= 1.0:
            p = 0.0
        else:
            p = math.degrees(math.acos(float(np.clip(n_vertical, -1.0, 1.0))))
        if str(pull_mode).upper() == "DOWN":
            p = -abs(p)
        elif str(pull_mode).upper() == "UP":
            p = abs(p)
        return float(p)

    def _on_cmd_input_changed(self, aid: str):
        if bool(getattr(self, "_bulk_initial_update", False)):
            return
        if bool(getattr(self, "_auto_cmd_limit_guard", False)):
            return
        if bool(getattr(self, "_auto_mode_guard", False)):
            return
        if bool(getattr(self, "playback_running", False)) or bool(getattr(self, "playback_active", False)):
            return
        self._update_cmd_g_dynamic_cap(str(aid), apply_cap_to_value=True)
        if aid in self.controls and bool(self.controls[aid].g_max_chk.isChecked()):
            gmax = quantize_g_01(self._compute_cmd_g_ps_max(str(aid)), min_g=1.0, max_g=9.0)
            if abs(float(self.controls[aid].g_cmd.value()) - gmax) > 1e-9:
                self.controls[aid].g_cmd.setValue(gmax)
        self._enforce_level_and_pull_logic(str(aid))
        self._apply_level_g_to_bank_autofill(str(aid))
        self._auto_apply_cmd_limits_for_aid(str(aid))
        self._update_bank_input_prompt(str(aid), show_popup=False)

    def _on_cmd_input_finalize(self, aid: str):
        if bool(getattr(self, "_bulk_initial_update", False)):
            return
        if bool(getattr(self, "_auto_cmd_limit_guard", False)):
            return
        if bool(getattr(self, "playback_running", False)) or bool(getattr(self, "playback_active", False)):
            return
        self._update_bank_input_prompt(str(aid), show_popup=True)

    def _on_pull_mode_toggled(self, aid: str):
        self._on_cmd_input_changed(str(aid))
        self._on_cmd_input_finalize(str(aid))

    def _set_pull_mode_for_aid(self, aid: str, mode: str):
        if aid not in self.controls:
            return
        m = str(mode).upper()
        ac = self.controls[aid]
        ac.pull_up_chk.blockSignals(True)
        ac.pull_down_chk.blockSignals(True)
        try:
            ac.pull_up_chk.setChecked(m == "UP")
            ac.pull_down_chk.setChecked(m == "DOWN")
        finally:
            ac.pull_up_chk.blockSignals(False)
            ac.pull_down_chk.blockSignals(False)

    def _enforce_level_and_pull_logic(self, aid: str):
        if aid not in self.controls:
            return
        ac = self.controls[aid]
        cmd = ac.read_command()
        turn = str(cmd.get("turn", "S")).upper()
        g_cmd = float(cmd.get("g_cmd", 1.0))
        pitch_cmd = float(cmd.get("pitch_deg", 0.0))
        pitch_hold = bool(cmd.get("pitch_hold", False))
        bank_cmd = quantize_bank_deg(float(cmd.get("bank_deg", 0.0)), min_bank=0.0, max_bank=180.0)
        pull_mode = str(cmd.get("pull_mode", "NONE")).upper()
        level_on = bool(cmd.get("level_hold", False))
        level_bank = self._compute_level_bank_from_g(g_cmd)
        cur_st = None
        if (0 <= int(self.current_step) < len(self.state_history)):
            st = self.state_history[self.current_step].get(aid, {})
            if isinstance(st, dict):
                cur_st = st

        self._auto_mode_guard = True
        try:
            if turn == "S":
                if abs(bank_cmd) > 1e-9:
                    ac.set_bank_from_auto(0.0)
                # Straight flight must remain wing-level (bank=0), but pull modes are valid:
                # user can command Pull Up / Pull Down with G to change pitch without turning.
                # Only LEVEL or Pitch Hold should suppress pull mode.
                if level_on or pitch_hold:
                    self._set_pull_mode_for_aid(aid, "NONE")
                return
            if pitch_hold:
                if level_on:
                    ac.level_chk.blockSignals(True)
                    try:
                        ac.level_chk.setChecked(False)
                    finally:
                        ac.level_chk.blockSignals(False)
                self._set_pull_mode_for_aid(aid, "NONE")
                bank_auto = self._bank_from_g_pitch(g_cmd, pitch_cmd)
                ac.set_bank_from_auto(bank_auto)
                return
            # User intent rule:
            # When turn + G are commanded and user explicitly edits bank,
            # treat it as climb/descent turn intent: keep user bank and auto-enable Pull Up.
            user_bank_turn_intent = (
                (turn != "S")
                and bool(ac.has_user_bank_input())
                and (g_cmd > 1.0 + 1e-9)
                and (abs(bank_cmd) > 1e-9)
            )
            user_pitch_turn_intent = (
                (turn != "S")
                and bool(ac.has_user_pitch_input())
                and (g_cmd > 1.0 + 1e-9)
            )
            if (level_on and (user_bank_turn_intent or user_pitch_turn_intent)) or (pull_mode == "UP"):
                if level_on:
                    ac.level_chk.blockSignals(True)
                    try:
                        ac.level_chk.setChecked(False)
                    finally:
                        ac.level_chk.blockSignals(False)
                self._set_pull_mode_for_aid(aid, "UP")

                # Pull-Up intent with one-side user input:
                # - user pitch -> auto bank
                # - user bank  -> auto pitch
                if bool(ac.has_user_pitch_input()) and (not bool(ac.has_user_bank_input())):
                    bank_auto = self._bank_from_g_pitch(g_cmd, pitch_cmd)
                    ac.set_bank_from_auto(bank_auto)
                elif bool(ac.has_user_bank_input()):
                    pitch_auto = self._pitch_from_g_bank(g_cmd, bank_cmd, "UP")
                    ac.set_pitch_from_auto(pitch_auto)
                return

            if user_bank_turn_intent:
                if level_on:
                    ac.level_chk.blockSignals(True)
                    try:
                        ac.level_chk.setChecked(False)
                    finally:
                        ac.level_chk.blockSignals(False)
                self._set_pull_mode_for_aid(aid, "UP")
                pitch_auto = self._pitch_from_g_bank(g_cmd, bank_cmd, "UP")
                ac.set_pitch_from_auto(pitch_auto)
                return
            if level_on:
                # LEVEL assist: straight flight -> adjust G, turning -> adjust bank.
                self._set_pull_mode_for_aid(aid, "NONE")
                g_limited = quantize_g_01(float(np.clip(g_cmd, 1.0, 9.0)), min_g=1.0, max_g=9.0)
                power_now = str(cmd.get("power", "M"))
                if abs(float(ac.g_cmd.value()) - g_limited) > 1e-9:
                    ac.g_cmd.setValue(g_limited)
                pitch_now = float(cur_st.get("pitch_deg", 0.0)) if isinstance(cur_st, dict) else 0.0
                cas_now = float(cur_st.get("cas_kt", 350.0)) if isinstance(cur_st, dict) else 350.0
                alt_now = float(cur_st.get("z_ft", 15000.0)) if isinstance(cur_st, dict) else 15000.0
                g_ps_cap = self._find_g_max(power_now, cas_now, alt_now, g_cap=9.0)
                if not np.isnan(g_ps_cap):
                    g_limited = quantize_g_01(min(float(g_limited), float(g_ps_cap)), min_g=1.0, max_g=9.0)
                    if abs(float(ac.g_cmd.value()) - g_limited) > 1e-9:
                        ac.g_cmd.setValue(g_limited)
                tas_ftps = max(1e-6, self._tas_from_cas(cas_now, alt_now) * KT_TO_FTPS)
                t_level = self._level_time_to_zero(pitch_now)
                n_vert_target = self._level_n_vertical_target(pitch_now, tas_ftps, t_level)
                bank_rec = self._compute_bank_for_vertical_target(g_limited, n_vert_target, max_over_bank=135.0)
                bank_lvl = self._compute_level_bank_from_g(g_limited)
                if abs(pitch_now) <= 5.0:
                    w = float(np.clip((5.0 - abs(pitch_now)) / 5.0, 0.0, 1.0))
                    bank_target = quantize_bank_deg(((1.0 - w) * bank_rec) + (w * bank_lvl), min_bank=0.0, max_bank=180.0)
                else:
                    bank_target = bank_rec
                # -pitch recovery in turning flight: relax bank toward level instead of adding overbank.
                if pitch_now < -0.5:
                    bank_target = min(bank_target, bank_lvl)
                if abs(bank_cmd - bank_target) > 1e-9:
                    ac.set_bank_from_auto(bank_target)
                self._set_pull_mode_for_aid(aid, "NONE")
                return
            # If user bank exceeds level-maintainable value, force pull-up assistance.
            if bank_cmd > (level_bank + 1e-9):
                self._set_pull_mode_for_aid(aid, "UP")
        finally:
            self._auto_mode_guard = False

    @staticmethod
    def _compute_level_bank_from_g(g_cmd: float) -> float:
        n = max(1.0, float(g_cmd))
        cos_bank = 1.0 / max(n, 1e-6)
        cos_bank = float(np.clip(cos_bank, -1.0, 1.0))
        return quantize_bank_deg(math.degrees(math.acos(cos_bank)), min_bank=0.0, max_bank=180.0)

    @staticmethod
    def _level_time_to_zero(pitch_deg: float) -> float:
        # User rule: recover level within |pitch|/5 seconds.
        return max(abs(float(pitch_deg)) / 5.0, 1.0)

    @staticmethod
    def _level_n_vertical_target(pitch_deg: float, tas_ftps: float, time_to_zero_sec: float) -> float:
        # Target pitch rate to reach 0 within requested time horizon.
        pitch_rad = math.radians(float(pitch_deg))
        pitch_rate_target = -pitch_rad / max(float(time_to_zero_sec), 1e-6)
        n_vert_target = math.cos(pitch_rad) + (pitch_rate_target * max(float(tas_ftps), 1e-6) / G0)
        # Keep full signed vertical-load demand so overbank (>90) can be used when needed.
        return float(np.clip(n_vert_target, -4.0, 4.0))

    @staticmethod
    def _compute_bank_for_vertical_target(g_cmd: float, n_vertical_target: float, max_over_bank: float = 135.0) -> float:
        n = max(1.0, min(4.0, float(g_cmd)))
        cos_bank = float(np.clip(float(n_vertical_target) / max(n, 1e-6), -1.0, 1.0))
        # Allow overbank for recovery, but cap to configured limit.
        bank = math.degrees(math.acos(cos_bank))
        return quantize_bank_deg(float(np.clip(bank, 0.0, float(max_over_bank))), min_bank=0.0, max_bank=180.0)

    @staticmethod
    def _move_toward(current: float, target: float, max_delta: float) -> float:
        c = float(current)
        t = float(target)
        md = max(0.0, float(max_delta))
        if t > c + md:
            return c + md
        if t < c - md:
            return c - md
        return t

    def _apply_level_g_to_bank_autofill(self, aid: str):
        if aid not in self.controls:
            return
        ac = self.controls[aid]
        cmd = ac.read_command()
        if bool(cmd.get("pitch_hold", False)):
            return
        turn = str(cmd.get("turn", "S")).upper()
        pull_mode = str(cmd.get("pull_mode", "NONE")).upper()
        level_on = bool(cmd.get("level_hold", False))
        pitch_deg = 0.0
        if (0 <= int(self.current_step) < len(self.state_history)) and isinstance(self.state_history[self.current_step].get(aid, {}), dict):
            pitch_deg = float(self.state_history[self.current_step][aid].get("pitch_deg", 0.0))
        if (turn == "S") or bool(level_on) or (abs(pitch_deg) > 1e-9) or (pull_mode in {"UP", "DOWN"}) or bool(ac.has_user_bank_input()):
            return
        g_cmd = float(cmd.get("g_cmd", 1.0))
        bank_from_g = self._compute_level_bank_from_g(g_cmd)
        cur_bank = quantize_bank_deg(float(cmd.get("bank_deg", 0.0)), min_bank=0.0, max_bank=180.0)
        if abs(cur_bank - bank_from_g) > 1e-9:
            ac.set_bank_from_auto(bank_from_g)

    def _update_bank_input_prompt(self, aid: str, show_popup: bool):
        if aid not in self.controls:
            return
        ac = self.controls[aid]
        cmd = ac.read_command()
        turn = str(cmd.get("turn", "S")).upper()
        pull_mode = str(cmd.get("pull_mode", "NONE")).upper()
        bank_missing = not bool(ac.has_user_bank_input())
        need_prompt = (turn != "S") and (pull_mode in {"UP", "DOWN"}) and bank_missing
        ac.set_bank_input_highlight(need_prompt)
        if not need_prompt:
            self._bank_prompt_shown[aid] = False
            return
        if (not bool(show_popup)) or bool(self._bank_prompt_shown.get(aid, False)):
            return
        QMessageBox.information(
            self,
            "Bank 입력",
            "bank량을 입력해주세요 (미입력시 G값은 Pull up G로만 사용)",
        )
        self._bank_prompt_shown[aid] = True

    def _auto_apply_cmd_limits_for_aid(self, aid: str):
        if bool(getattr(self, "_auto_cmd_limit_guard", False)):
            return
        if aid not in self.controls:
            return
        if (not self.state_history) or (self.current_step < 0) or (self.current_step >= len(self.state_history)):
            return
        cur_st = self.state_history[self.current_step].get(aid)
        if not isinstance(cur_st, dict):
            return
        dt = float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value())
        cmd = self.controls[aid].read_command()
        self._auto_cmd_limit_guard = True
        try:
            rec = self._simulate_one(aid, cur_st, dict(cmd), dt, self.current_step)
            pull_mode = str(cmd.get("pull_mode", "NONE")).upper()
            pitch_hold = bool(cmd.get("pitch_hold", False))
            # Keep manual/setpoint pitch editable in Pull-Up or Pitch-Hold intent; avoid preview overwrite.
            if not ((pull_mode == "UP" and bool(self.controls[aid].has_user_pitch_input())) or pitch_hold):
                self.controls[aid].set_pitch_display(float(rec.get("pitch_used", cmd.get("pitch_deg", 0.0))))
            g_user = float(cmd.get("g_cmd", 1.0))
            g_used = float(rec.get("g_used", np.nan))
            turn_cmd = str(cmd.get("turn", "S")).upper()
            g_new = quantize_g_01(g_used if (not np.isnan(g_used)) else g_user, min_g=1.0, max_g=9.0)
            if (turn_cmd != "S") and (not np.isnan(g_used)) and (g_used < (g_user - 1e-9)):
                self.controls[aid].g_cmd.setValue(g_new)
                self.controls[aid].set_applied_g(g_new)
                self.controls[aid].set_g_limit_indicator(g_user, g_new)
            else:
                self.controls[aid].clear_g_limit_indicator()
        finally:
            self._auto_cmd_limit_guard = False

    def _auto_apply_cmd_limits_all(self):
        for aid in AIRCRAFT_IDS:
            self._auto_apply_cmd_limits_for_aid(aid)

    def _maybe_prompt_panel_detach_recommendation(self, mode_key: str):
        mk = str(mode_key).strip()
        if mk not in {"4vs2", "4vs4"}:
            return
        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Information)
        mbox.setWindowTitle("Panel Detach Recommended")
        mbox.setText(f"{mk} 모드에서는 좌측 UI 패널 분리를 권장합니다.")
        btn_detach = mbox.addButton("지금 패널 분리", QMessageBox.ButtonRole.AcceptRole)
        mbox.addButton("나중에", QMessageBox.ButtonRole.RejectRole)
        mbox.exec()
        if (mbox.clickedButton() is btn_detach) and (not bool(getattr(self, "_left_ui_popped", False))):
            self._toggle_left_ui_popout()

    def _refresh_setup_combo_by_mode(self, mode: str):
        mk = str(mode).strip()
        if mk not in MODE_KEYS:
            mk = "2vs1"
        opts = MODE_SETUP_OPTIONS.get(mk, ["DEFAULT"])
        prev = str(self.setup_combo.currentText()).strip()
        self.setup_combo.blockSignals(True)
        self.setup_combo.clear()
        self.setup_combo.addItems(opts)
        if prev in opts:
            self.setup_combo.setCurrentText(prev)
        elif self.current_setup_key in opts:
            self.setup_combo.setCurrentText(self.current_setup_key)
        else:
            self.setup_combo.setCurrentIndex(0)
        self.setup_combo.blockSignals(False)

    def _on_apply_setup_clicked(self):
        mode = str(self.mode_combo.currentText()).strip()
        setup = str(self.setup_combo.currentText()).strip() or "DEFAULT"
        self.apply_startup_profile(mode, setup)

    def _on_setup_popup_clicked(self):
        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Question)
        mbox.setWindowTitle("Apply New Setup")
        mbox.setText("현재 상태를 저장한 뒤 새 Setup을 적용할까요?")
        btn_save = mbox.addButton("Save and Continue", QMessageBox.ButtonRole.AcceptRole)
        btn_skip = mbox.addButton("Continue without Save", QMessageBox.ButtonRole.DestructiveRole)
        btn_cancel = mbox.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        mbox.exec()
        clicked = mbox.clickedButton()
        if clicked is btn_cancel:
            return
        if clicked is btn_save:
            self.export_scenario_csv()
        self.prompt_startup_selection()

    def _toggle_left_ui_popout(self):
        if not self._left_ui_popped:
            # Always dock GLOBAL back into the left panel before detaching,
            # so the detached window contains GLOBAL + all UI sections together.
            if hasattr(self, "global_group") and self.global_group is not None:
                try:
                    self._set_global_overlay_mode(False)
                except Exception:
                    pass
                try:
                    if hasattr(self, "global_overlay_layout") and self.global_overlay_layout is not None:
                        self.global_overlay_layout.removeWidget(self.global_group)
                except Exception:
                    pass
                if self.global_group.parent() is not self.left_panel:
                    self.global_group.setParent(self.left_panel)
                    if hasattr(self, "left_layout") and self.left_layout is not None:
                        self.left_layout.insertWidget(0, self.global_group)
                        self.left_layout.update()
                # Keep GLOBAL fully opaque in detached panel mode.
                self.global_group.setGraphicsEffect(None)
                self.global_group.setStyleSheet("")
                self.global_group.show()
            # If the left panel was collapsed, clear 0-width constraints first;
            # otherwise detached dialog can appear empty.
            try:
                self._set_left_panel_collapsed_limits(False)
            except Exception:
                pass
            try:
                sizes = self.main_splitter.sizes() if hasattr(self, "main_splitter") else []
                left_w = int(sizes[0]) if sizes and len(sizes) > 0 else int(self.left_scroll.width())
                if left_w <= 1 and hasattr(self, "main_splitter"):
                    total = int(sum(sizes)) if sizes else int(self.main_splitter.width())
                    if total <= 0:
                        total = int(self.width())
                    min_left = int(max(getattr(self, "_left_min_width", 320), getattr(self, "_left_panel_last_width", 0)))
                    min_left = max(320, min_left)
                    self.main_splitter.setSizes([min_left, max(1, total - min_left)])
            except Exception:
                pass
            self.left_scroll.updateGeometry()
            if hasattr(self, "btn_left_panel_toggle") and self.btn_left_panel_toggle is not None:
                self.btn_left_panel_toggle.hide()
            placeholder = QWidget()
            placeholder.setMinimumWidth(0)
            placeholder.setMaximumWidth(0)
            placeholder.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self._left_panel_placeholder = placeholder
            self.main_splitter.insertWidget(0, placeholder)
            self.left_scroll.setParent(None)
            dlg = QDialog(self, Qt.WindowType.Window)
            dlg.setWindowTitle("UI 패널")
            lay = QVBoxLayout(dlg)
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(0)
            lay.addWidget(self.left_scroll)
            sizes = self.main_splitter.sizes() if hasattr(self, "main_splitter") else []
            total_w = int(sum(sizes)) if sizes else int(self.main_splitter.width() if hasattr(self, "main_splitter") else self.width())
            left_now = int(sizes[0]) if sizes and len(sizes) > 0 else int(self.left_scroll.width())
            left_last = int(getattr(self, "_left_panel_last_width", 0))
            min_left = int(getattr(self, "_left_min_width", 320))
            mk = str(getattr(self, "current_mode_key", "")).strip()
            if mk in {"4vs2", "4vs4"}:
                left_target = max(left_now, left_last, min_left, int(round(float(max(1, total_w)) * 0.70)))
            else:
                left_target = max(left_now, left_last, min_left)
            hint_w = int(self.left_scroll.sizeHint().width()) + 4
            split_h = int(self.main_splitter.height()) if hasattr(self, "main_splitter") else int(self.left_scroll.height())
            hint_h = int(self.left_scroll.sizeHint().height()) + 4
            pop_w = max(420, left_target + 4, hint_w)
            pop_h = max(520, split_h + 4, hint_h)
            dlg.resize(pop_w, pop_h)
            dlg.finished.connect(self._dock_left_ui_back)
            self._left_ui_pop_dialog = dlg
            self._left_ui_popped = True
            self.btn_global_popout.setText("패널 복귀")
            self.main_splitter.setSizes([0, max(1, self.main_splitter.width())])
            self._left_panel_hidden = False
            dlg.show()
            # User request: on panel detach click, apply compass W effect immediately.
            self._set_camera_mode("top")
            self._set_top_view_cardinal("W")
            for _ in range(13):
                self._adjust_view_zoom(1.0 / 0.85)
            # Force immediate layout stabilization so detached panel looks final
            # without requiring a first Fwd/Back action.
            self._stabilize_detached_panel_layout()
            QTimer.singleShot(0, self._stabilize_detached_panel_layout)
            QTimer.singleShot(60, self._stabilize_detached_panel_layout)
        else:
            self._dock_left_ui_back()

    def _stabilize_detached_panel_layout(self):
        if not bool(getattr(self, "_left_ui_popped", False)):
            return
        try:
            if hasattr(self, "global_group") and self.global_group is not None:
                if hasattr(self, "left_panel") and (self.global_group.parent() is not self.left_panel):
                    self.global_group.setParent(self.left_panel)
                    if hasattr(self, "left_layout") and self.left_layout is not None:
                        self.left_layout.insertWidget(0, self.global_group)
                self.global_group.setGraphicsEffect(None)
                self.global_group.setStyleSheet("")
                self.global_group.show()
            if hasattr(self, "left_layout") and self.left_layout is not None:
                self.left_layout.activate()
            if hasattr(self, "left_scroll") and self.left_scroll is not None:
                if self.left_scroll.widget() is not None:
                    self.left_scroll.widget().updateGeometry()
                self.left_scroll.updateGeometry()
            self._update_aircraft_group_widths()
            self._position_view_overlays()
            self.refresh_ui()
        except Exception:
            pass

    def _dock_left_ui_back(self, *_args):
        if not self._left_ui_popped:
            return
        dlg = self._left_ui_pop_dialog
        if dlg is not None:
            try:
                if self.left_scroll.parent() is dlg:
                    dlg.layout().removeWidget(self.left_scroll)
            except Exception:
                pass
        placeholder = self._left_panel_placeholder
        if placeholder is not None:
            idx = self.main_splitter.indexOf(placeholder)
            if idx < 0:
                idx = 0
            self.main_splitter.insertWidget(idx, self.left_scroll)
            placeholder.setParent(None)
            self._left_panel_placeholder = None
        else:
            self.main_splitter.insertWidget(0, self.left_scroll)
        if dlg is not None:
            try:
                dlg.finished.disconnect(self._dock_left_ui_back)
            except Exception:
                pass
            if dlg.isVisible():
                dlg.close()
        self._left_ui_pop_dialog = None
        self._left_ui_popped = False
        self.btn_global_popout.setText("패널 분리")
        self._set_left_panel_collapsed_limits(False)
        self._recompute_left_min_width()
        self._apply_main_minimum_size()
        self._apply_splitter_start_min_left()
        self._position_left_panel_toggle()
        if hasattr(self, "btn_left_panel_toggle") and self.btn_left_panel_toggle is not None:
            self.btn_left_panel_toggle.hide()

    def apply_startup_profile(self, mode: str, setup: str, formation_dist_nm: Optional[float] = None):
        prev_mode_key = str(getattr(self, "current_mode_key", "")).strip()
        mode_key = str(mode).strip()
        if mode_key not in MODE_KEYS:
            mode_key = "2vs1"
        setup_key = str(setup).strip() or "DEFAULT"
        self.current_mode_key = mode_key
        self.current_setup_key = setup_key
        self.hide_los_in_step_view = self.current_mode_key in {"4vs2", "4vs4"}
        self._refresh_offset_anchor_labels_for_mode(self.current_mode_key)
        self._arrange_aircraft_panels_for_mode(self.current_mode_key)
        if hasattr(self, "mode_combo"):
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentText(self.current_mode_key)
            self.mode_combo.blockSignals(False)
            self._refresh_setup_combo_by_mode(self.current_mode_key)
            self.setup_combo.setCurrentText(self.current_setup_key if self.current_setup_key in MODE_SETUP_OPTIONS.get(self.current_mode_key, []) else self.setup_combo.currentText())

        active = set(MODE_ACTIVE_IDS.get(mode_key, MODE_ACTIVE_IDS["2vs1"]))
        palette = MODE_COLOR_KEYS.get(mode_key, MODE_COLOR_KEYS["2vs1"])
        self._bulk_initial_update = True
        try:
            for i, aid in enumerate(AIRCRAFT_IDS):
                color_key = palette[min(i, len(palette) - 1)] if i < len(palette) else DEFAULT_COLOR_BY_AID.get(aid, "BLACK")
                self.controls[aid].set_color_key(color_key)
                cb = self.aircraft_enable_checks.get(aid)
                if cb is not None:
                    cb.setChecked(aid in active)
            self.aircraft_colors = {aid: tuple(self.controls[aid].current_color_rgba()) for aid in AIRCRAFT_IDS}

            if mode_key == "1vs1":
                sk = setup_key.upper()
                if sk == "TI SETUP":
                    # Reuse 2vs1 TI geometry with #1 and #3 only -> mapped to #1/#2.
                    self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=18000, hdg_deg=180, cas_kt=350, range_nm=25.0, bearing_deg=360.0)
                elif sk == "BFM 3K":
                    self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=250, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=22000, hdg_deg=360, cas_kt=250)
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=1.0, rel_bearing_deg=90.0)
                elif sk == "BFM 9K":
                    self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=22000, hdg_deg=360, cas_kt=400)
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=2.0, rel_bearing_deg=90.0)
            elif mode_key == "2vs1":
                sk = setup_key.upper()
                if sk == "TI SETUP":
                    self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=1.5, bearing_deg=145.0)
                    self._set_initial_for_aircraft("#3", alt_ft=18000, hdg_deg=180, cas_kt=350, range_nm=25.0, bearing_deg=360.0)
                elif sk == "OACM SETUP":
                    self._set_initial_for_aircraft("#1", alt_ft=18000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=17000, hdg_deg=360, cas_kt=400, range_nm=2.5, bearing_deg=150.0)
                    self._set_initial_for_aircraft("#3", alt_ft=19000, hdg_deg=360, cas_kt=400, range_nm=1.5, bearing_deg=330.0)
                elif sk == "DACM SETUP":
                    self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                    self._set_initial_for_aircraft("#2", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=2.0, bearing_deg=90.0)
                    # #3 at 1.5nm / 180deg from #2 -> converted to #1-referenced bearing/range.
                    self._set_initial_for_aircraft("#3", alt_ft=23000, hdg_deg=360, cas_kt=400, range_nm=2.5, bearing_deg=126.9)
            elif mode_key == "2vs2":
                sk = setup_key.upper()
                # In 2vs2, #3/#4 are one team with common heading 180.
                # Keep #1/#2 in the same initial formation used by 2vs1 TI setup.
                self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                self._set_initial_for_aircraft("#2", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=1.5, bearing_deg=145.0)
                # Fully reset #3/#4 baseline so switching from 4vs2/4vs4 never carries stale offsets.
                self._set_initial_for_aircraft("#3", alt_ft=18000, hdg_deg=180.0, cas_kt=350, range_nm=25.0, bearing_deg=360.0)
                self._set_initial_for_aircraft("#4", alt_ft=18000, hdg_deg=180.0, cas_kt=350, range_nm=2.0, bearing_deg=90.0)
                # Keep #1/#2 formation as-is; only shape #3/#4 pair.
                if sk in {
                    "2VS2 RANGE",
                    "2VS2 LAB",
                    "2VS2 ECHELON",
                    "2VS2 SGL GRP RANGE",
                    "2VS2 SGL GRP LAB",
                    "2VS2 SGL GRP ECHELON",
                    "2VS2 TWO GRP RANGE",
                    "2VS2 TWO GRP LAB",
                    "2VS2 TWO GRP ECHELON",
                }:
                    default_nm = 2.0
                    dist_nm = float(formation_dist_nm) if formation_dist_nm is not None else float(default_nm)
                    dist_nm = max(0.1, dist_nm)
                    if sk.endswith("RANGE"):
                        # RANGE = trail formation.
                        self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=dist_nm, rel_bearing_deg=180.0)
                    elif sk.endswith("LAB"):
                        # LAB = line-abreast formation.
                        self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=dist_nm, rel_bearing_deg=90.0)
                    elif sk.endswith("ECHELON"):
                        # ECHELON = #4 trails #3 by 45deg.
                        self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=dist_nm, rel_bearing_deg=135.0)
            elif mode_key == "4vs2":
                sk = setup_key.upper()
                # BA(#1~#4) baseline: common speed/heading with fixed altitude stack.
                self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                self._set_initial_for_aircraft("#2", alt_ft=21000, hdg_deg=360, cas_kt=400)
                self._set_initial_for_aircraft("#3", alt_ft=23000, hdg_deg=360, cas_kt=400)
                self._set_initial_for_aircraft("#4", alt_ft=24000, hdg_deg=360, cas_kt=400)
                # RA(#5~#6) baseline.
                self._set_initial_for_aircraft("#5", alt_ft=18000, hdg_deg=180, cas_kt=350, range_nm=25.0, bearing_deg=360.0)
                self._set_initial_for_aircraft("#6", alt_ft=17000, hdg_deg=180, cas_kt=350)

                ba_shape = "OFFSET BOX"
                ra_shape = "RANGE"
                if "+ RA " in sk:
                    left, right = sk.split("+ RA ", 1)
                    if "BA FLUID FOUR" in left:
                        ba_shape = "FLUID FOUR"
                    elif "BA OFFSET BOX" in left:
                        ba_shape = "OFFSET BOX"
                    rr = right.strip()
                    if rr in {"RANGE", "LAB", "ECHELON"}:
                        ra_shape = rr
                else:
                    if "BA FLUID FOUR" in sk:
                        ba_shape = "FLUID FOUR"
                    elif "BA OFFSET BOX" in sk or sk == "DEFAULT":
                        ba_shape = "OFFSET BOX"
                    if "RA LAB" in sk:
                        ra_shape = "LAB"
                    elif "RA ECHELON" in sk:
                        ra_shape = "ECHELON"
                    else:
                        ra_shape = "RANGE"

                if ba_shape == "OFFSET BOX":
                    # #1-#2: 2nm LAB / #1-#3: 3nm TRAIL / #3-#4: 2nm LAB
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#1", "#3", rel_range_nm=3.0, rel_bearing_deg=180.0)
                    self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=2.0, rel_bearing_deg=90.0)
                elif ba_shape == "FLUID FOUR":
                    # #2 from #1 (left trailing 45deg, 4500ft), #3 from #1 (right 2nm LAB),
                    # #4 from #3 (right trailing 45deg, 4500ft)
                    r_4500_nm = 4500.0 / NM_TO_FT
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=r_4500_nm, rel_bearing_deg=225.0)
                    self._set_target_from_anchor_relative("#1", "#3", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=r_4500_nm, rel_bearing_deg=135.0)

                ra_dist_nm = float(formation_dist_nm) if formation_dist_nm is not None else 2.0
                ra_dist_nm = max(0.1, ra_dist_nm)
                if ra_shape == "RANGE":
                    self._set_target_from_anchor_relative("#5", "#6", rel_range_nm=ra_dist_nm, rel_bearing_deg=180.0)
                elif ra_shape == "LAB":
                    # Keep RA pair symmetric about current RA width-center.
                    ra_center = self._world_point_from_control("#5")
                    half_span_nm = 0.5 * ra_dist_nm
                    p5 = self._world_point_from_point_relative(ra_center, rel_range_nm=half_span_nm, rel_bearing_deg=270.0)
                    self._set_control_from_world_point("#5", p5)
                    self._set_target_from_anchor_relative("#5", "#6", rel_range_nm=ra_dist_nm, rel_bearing_deg=90.0)
                elif ra_shape == "ECHELON":
                    # Place #5/#6 on a 45deg diagonal around the width-center:
                    # #5 upper-left (315deg), #6 lower-right (135deg) with equal half-span.
                    ra_center = self._world_point_from_control("#5")
                    half_span_nm = 0.5 * ra_dist_nm
                    p5 = self._world_point_from_point_relative(ra_center, rel_range_nm=half_span_nm, rel_bearing_deg=315.0)
                    self._set_control_from_world_point("#5", p5)
                    self._set_target_from_anchor_relative("#5", "#6", rel_range_nm=ra_dist_nm, rel_bearing_deg=135.0)
            elif mode_key == "4vs4":
                sk = setup_key.upper()
                # BA baseline.
                self._set_initial_for_aircraft("#1", alt_ft=22000, hdg_deg=360, cas_kt=400, range_nm=0.0, bearing_deg=0.0)
                self._set_initial_for_aircraft("#2", alt_ft=21000, hdg_deg=360, cas_kt=400)
                self._set_initial_for_aircraft("#3", alt_ft=23000, hdg_deg=360, cas_kt=400)
                self._set_initial_for_aircraft("#4", alt_ft=24000, hdg_deg=360, cas_kt=400)
                # RA baseline.
                self._set_initial_for_aircraft("#5", alt_ft=17000, hdg_deg=180, cas_kt=350, range_nm=25.0, bearing_deg=360.0)
                self._set_initial_for_aircraft("#6", alt_ft=16000, hdg_deg=180, cas_kt=350)
                self._set_initial_for_aircraft("#7", alt_ft=18000, hdg_deg=180, cas_kt=350)
                self._set_initial_for_aircraft("#8", alt_ft=19000, hdg_deg=180, cas_kt=350)

                ba_shape = "OFFSET BOX"
                ra_shape = "OFFSET BOX"
                if "+ RA " in sk:
                    left, right = sk.split("+ RA ", 1)
                    if "BA FLUID FOUR" in left:
                        ba_shape = "FLUID FOUR"
                    elif "BA OFFSET BOX" in left:
                        ba_shape = "OFFSET BOX"
                    rr = right.strip()
                    if rr in {"OFFSET BOX", "FLUID FOUR"}:
                        ra_shape = rr
                else:
                    if "BA FLUID FOUR" in sk:
                        ba_shape = "FLUID FOUR"
                    if "RA FLUID FOUR" in sk:
                        ra_shape = "FLUID FOUR"

                if ba_shape == "OFFSET BOX":
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#1", "#3", rel_range_nm=3.0, rel_bearing_deg=180.0)
                    self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=2.0, rel_bearing_deg=90.0)
                elif ba_shape == "FLUID FOUR":
                    r_4500_nm = 4500.0 / NM_TO_FT
                    self._set_target_from_anchor_relative("#1", "#2", rel_range_nm=r_4500_nm, rel_bearing_deg=225.0)
                    self._set_target_from_anchor_relative("#1", "#3", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#3", "#4", rel_range_nm=r_4500_nm, rel_bearing_deg=135.0)

                if ra_shape == "OFFSET BOX":
                    self._set_target_from_anchor_relative("#5", "#6", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#5", "#7", rel_range_nm=3.0, rel_bearing_deg=180.0)
                    self._set_target_from_anchor_relative("#7", "#8", rel_range_nm=2.0, rel_bearing_deg=90.0)
                elif ra_shape == "FLUID FOUR":
                    r_4500_nm = 4500.0 / NM_TO_FT
                    self._set_target_from_anchor_relative("#5", "#6", rel_range_nm=r_4500_nm, rel_bearing_deg=225.0)
                    self._set_target_from_anchor_relative("#5", "#7", rel_range_nm=2.0, rel_bearing_deg=90.0)
                    self._set_target_from_anchor_relative("#7", "#8", rel_range_nm=r_4500_nm, rel_bearing_deg=135.0)
        finally:
            self._bulk_initial_update = False

        self.current_step = 0
        self.playback_step_float = 0.0
        self._apply_step0_inputs_to_state()
        self._auto_apply_cmd_limits_all()
        self._restore_cmd_ui_for_step(0)

        enable_hold_default = (
            (mode_key in {"2vs2", "4vs2", "4vs4"})
            or ((mode_key in {"1vs1", "2vs1"}) and (str(setup_key).upper() == "TI SETUP"))
        )
        if enable_hold_default:
            hold_all = {aid: True for aid in AIRCRAFT_IDS}
            self.hold_state_by_step[0] = hold_all
            for aid in AIRCRAFT_IDS:
                self.controls[aid].set_hold_speed(True)
            self.chk_speed_lock.blockSignals(True)
            self.chk_speed_lock.setChecked(True)
            self.chk_speed_lock.blockSignals(False)

        self._restore_hold_ui_for_step(0)
        if not bool(getattr(self, "_suppress_dca_prompt", False)):
            if self._should_prompt_dca_setup(mode_key, setup_key):
                self._prompt_dca_be_setup()
            else:
                self._clear_dca_be()
        if enable_hold_default:
            QMessageBox.information(self, "Hold Speed", "hold speed가 활성화된 상태입니다.")
        self.refresh_ui()
        self._apply_top_north_startup_frame()
        mode_changed = (self.current_mode_key != prev_mode_key)
        if mode_changed and (not bool(getattr(self, "_left_ui_popped", False))):
            self._recompute_left_min_width()
            self._apply_main_minimum_size()
            self._apply_splitter_start_min_left()
        if self.current_mode_key in {"4vs2", "4vs4"} and mode_changed:
            self._maybe_prompt_panel_detach_recommendation(self.current_mode_key)

    def prompt_startup_selection(self):
        # Mandatory modal selection after main UI is shown.
        while True:
            dlg = StartupScenarioDialog(self, initial_mode=self.current_mode_key, initial_setup=self.current_setup_key)
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            res = dlg.exec()
            if res == QDialog.DialogCode.Accepted:
                if dlg.open_saved_requested():
                    if self.import_scenario_csv():
                        break
                    continue
                mode_sel, setup_sel, dist_nm = dlg.selection()
                self.apply_startup_profile(mode_sel, setup_sel, formation_dist_nm=dist_nm)
                break

    def _on_speed_lock_toggled(self, checked: bool):
        for aid in AIRCRAFT_IDS:
            self.controls[aid].set_hold_speed(bool(checked))
        self._on_aircraft_hold_toggled("ALL", bool(checked))

    def _on_aircraft_hold_toggled(self, _aid: str, _checked: bool):
        hold_map = self._current_hold_map_from_ui()
        self.hold_state_by_step[self.current_step] = hold_map
        if self.state_history:
            cur = self.state_history[self.current_step]
            self.lock_speed_value_by_step[self.current_step] = {}
            self.lock_ps_value_by_step[self.current_step] = {}
            for aid in AIRCRAFT_IDS:
                if not hold_map.get(aid, False):
                    continue
                st = cur[aid]
                if self.current_step == 0:
                    self.lock_speed_value_by_step[self.current_step][aid] = float(self.controls[aid].cas_kt.value())
                else:
                    self.lock_speed_value_by_step[self.current_step][aid] = float(st["cas_kt"])
                psv = float(st.get("ps_fps", 0.0))
                if np.isnan(psv):
                    psv = 0.0
                self.lock_ps_value_by_step[self.current_step][aid] = psv
        self.chk_speed_lock.blockSignals(True)
        self.chk_speed_lock.setChecked(all(hold_map.values()))
        self.chk_speed_lock.blockSignals(False)
        self.refresh_ui()

    def _replay_to_step(self, target_step: int):
        # Rebuild from the original Step-0 state snapshot, not from current UI fields.
        # UI fields are reused to display "current state" at Step>0, so reading them here
        # can corrupt replay/back-forward consistency.
        init_states = None
        if self.state_history and isinstance(self.state_history[0], dict):
            try:
                init_states = {aid: dict(self.state_history[0][aid]) for aid in AIRCRAFT_IDS}
            except Exception:
                init_states = None
        if init_states is None:
            init_states = self._initial_states()
        self.state_history = [init_states]
        self.transition_history = []
        for s in range(target_step):
            pkg = self.step_cmds.get(s)
            if pkg is None:
                break
            dt = float(self.fixed_dt if self.fixed_dt is not None else pkg["_dt"])
            cmds = pkg["cmds"]
            nxt, recs = self._simulate_step(self.state_history[-1], cmds, dt, s)
            self.state_history.append(nxt)
            self.transition_history.append(recs)
        self._refresh_speed_lock_baseline()

    def on_reset_scenario_clicked(self):
        mbox = QMessageBox(self)
        mbox.setIcon(QMessageBox.Icon.Warning)
        mbox.setWindowTitle("Reset Scenario")
        mbox.setText("This will clear all steps, commands, and history. Continue?")
        btn_continue = mbox.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
        mbox.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        mbox.exec()
        if mbox.clickedButton() is not btn_continue:
            return
        self.reset_sim()

    def reset_sim(self):
        self.playback_running = False
        self.playback_active = False
        self.playback_direction = 1
        self.playback_timer.stop()
        self.playback_origin_step = 0
        self.playback_step_float = 0.0
        self._sync_play_button_icon()
        self._set_inputs_enabled(True)
        self._restore_boot_init_values()
        self.step_cmds.clear()
        self.hold_state_by_step.clear()
        self.lock_speed_value_by_step.clear()
        self.lock_ps_value_by_step.clear()
        self.warning_shown = {"impl": False, "mach": False}
        self._clear_custom_los_links()
        self.step_bookmarks = {}
        self.bookmark_selected_step = None
        self.current_step = 0
        self.fixed_dt = None
        self.state_history = [self._initial_states()]
        self.transition_history = []
        self._restore_cmd_ui_for_step(0)
        self._restore_hold_ui_for_step(0)
        self._refresh_speed_lock_baseline()
        self._recompute_left_min_width()
        self._apply_main_minimum_size()
        if not bool(getattr(self, "_splitter_ratio_initialized", False)):
            self._apply_splitter_start_min_left()
        self._update_aircraft_group_widths()
        self.refresh_ui()
        self._apply_top_north_startup_frame()

    def _apply_top_north_startup_frame(self):
        pts: List[np.ndarray] = []
        try:
            sidx = int(max(0, min(int(self.current_step), len(self.state_history) - 1)))
            st = self.state_history[sidx] if self.state_history else {}
            for aid in self._active_aircraft_ids():
                v = st.get(aid) if isinstance(st, dict) else None
                if isinstance(v, dict):
                    pts.append(np.array([float(v["x_ft"]), float(v["y_ft"]), float(v["z_ft"])], dtype=float))
        except Exception:
            pass
        if self._has_dca_mission_area():
            try:
                for p in np.array(self.dca_mission_rect_pts_ft[:4], dtype=float):
                    pts.append(np.array([float(p[0]), float(p[1]), 0.0], dtype=float))
            except Exception:
                pass

        if pts:
            arr = np.vstack(pts)
            minv = np.min(arr, axis=0)
            maxv = np.max(arr, axis=0)
            cx = 0.5 * (float(minv[0]) + float(maxv[0]))
            cy = 0.5 * (float(minv[1]) + float(maxv[1]))
            cz = max(12000.0, 0.5 * (float(minv[2]) + float(maxv[2])))
            dx = float(maxv[0] - minv[0])
            dy = float(maxv[1] - minv[1])
            span = max(8.0 * NM_TO_FT, math.hypot(dx, dy))
            dist = float(np.clip(span * 1.60, 18000.0, 1800000.0))
        else:
            cx, cy, cz = 0.0, 0.0, 12000.0
            extent = float(max(1000.0, self._grid_extent_target()))
            dist = float(np.clip(extent * 1.60, 18000.0, 1800000.0))

        self.view.opts["center"] = QVector3D(float(cx), float(cy), float(cz))
        self.view.setCameraPosition(distance=float(dist), elevation=89.5, azimuth=0.0)
        self._set_camera_mode("top")
        self._set_top_view_cardinal("N")
        if not bool(getattr(self, "_left_ui_popped", False)):
            for _ in range(3):
                self._adjust_view_zoom(0.85)

    def back_steps(self, n: int):
        if self.playback_running:
            self._pause_playback()
        self.playback_active = False
        n = max(1, int(n))
        if self.current_step <= 0:
            return
        self.current_step = max(0, self.current_step - n)
        self.playback_step_float = float(self.current_step)
        self._replay_to_step(self.current_step)
        if self.current_step == 0:
            self._restore_step0_initial_widgets_from_history()
        self._restore_cmd_ui_for_step(self.current_step)
        self._restore_hold_ui_for_step(self.current_step)
        self.refresh_ui()

    def back_one(self):
        self.back_steps(1)

    def advance_steps(self, n: int):
        if self.playback_running:
            self._pause_playback()
        self.playback_active = False
        n = max(1, int(n))
        if n > 1:
            max_existing = int(self.current_step)
            if self.step_cmds:
                try:
                    max_existing = max(max_existing, max(int(k) for k in self.step_cmds.keys()))
                except Exception:
                    pass
            remain = max_existing - int(self.current_step)
            if remain <= 0:
                return
            n = min(n, remain)
        if self.current_step == 0 and self.fixed_dt is None:
            self.fixed_dt = float(self.dt_sec.value())
        dt = float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value())
        if self.current_step == 0:
            self._apply_step0_inputs_to_state()
        pre_cmds = self._read_current_cmds()
        pre_hold = self._current_hold_map_from_ui()
        if not self._maybe_prompt_future_step_policy(self.current_step, pre_cmds, pre_hold):
            return

        for i in range(n):
            if i > 0:
                self._restore_cmd_ui_for_step(self.current_step)
                self._restore_hold_ui_for_step(self.current_step)
            cmds = self._read_current_cmds()
            self.step_cmds[self.current_step] = {"_dt": dt, "cmds": cmds}
            hold_map = self._current_hold_map_from_ui()
            self.hold_state_by_step[self.current_step] = hold_map
            if any(hold_map.values()):
                cur_st = self.state_history[self.current_step]
                self.lock_speed_value_by_step[self.current_step] = {}
                self.lock_ps_value_by_step[self.current_step] = {}
                for aid in AIRCRAFT_IDS:
                    if not hold_map.get(aid, False):
                        continue
                    if self.current_step == 0:
                        self.lock_speed_value_by_step[self.current_step][aid] = float(self.controls[aid].cas_kt.value())
                    else:
                        self.lock_speed_value_by_step[self.current_step][aid] = float(cur_st[aid]["cas_kt"])
                    psv = float(cur_st[aid].get("ps_fps", 0.0))
                    if np.isnan(psv):
                        psv = 0.0
                    self.lock_ps_value_by_step[self.current_step][aid] = psv
            prev_step_states = self.state_history[-1]
            nxt, recs = self._simulate_step(prev_step_states, cmds, dt, self.current_step)
            self.state_history.append(nxt)
            self.transition_history.append(recs)
            near_miss_info = self._ba_min_distance_during_step_ft(prev_step_states, nxt)
            if near_miss_info is not None:
                near_miss_ft, near_t, near_pair = near_miss_info
                if near_miss_ft <= 990.0:
                    t_sec = float(near_t) * float(dt)
                    QMessageBox.warning(
                        self,
                        "Warning",
                        (
                            f"WARNING : NEAR MISS OCCURS! ({near_miss_ft:.1f} ft)\n"
                            f"PAIR: {near_pair[0]} - {near_pair[1]}, t={t_sec:.2f}s within step"
                        ),
                    )
            impl_warn = False
            mach_warn = False
            step_events: List[str] = []
            for aid in AIRCRAFT_IDS:
                r = recs[aid]
                g_user_cur = float(cmds[aid].get("g_cmd", 1.0))
                g_used_cur = float(r["g_used"]) if not np.isnan(r["g_used"]) else np.nan
                if (str(r.get("turn_cmd_user", "S")).upper() != "S") and (not np.isnan(g_used_cur)) and (g_used_cur < (g_user_cur - 1e-9)):
                    self._commit_g_clamp_ui_and_step(self.current_step, aid, g_user_cur, g_used_cur)
                    cmds[aid]["g_cmd"] = float(round(g_used_cur, 1))
                    clamp_text = str(r.get("clamp_note", "")).strip()
                    if clamp_text.startswith("G limited:") or clamp_text.startswith("No feasible turn G"):
                        self.controls[aid].status.setText(clamp_text)
                        self.controls[aid].status.setVisible(True)
                else:
                    self.controls[aid].clear_g_limit_indicator()
                if bool(r.get("pitch_clamped", False)):
                    pw = self.controls[aid].pitch_deg
                    pw.blockSignals(True)
                    pw.setValue(float(self.controls[aid]._display_pitch_deg(r.get("pitch_used", 0.0))))
                    pw.blockSignals(False)
                    step_events.append(
                        f"{aid}: pitch adjusted {float(r.get('pitch_cmd_user', 0.0)):.0f} -> {float(r.get('pitch_used', 0.0)):.0f} deg"
                    )
                if (
                    str(r.get("turn_cmd_user", "S")).upper() != "S"
                    and (not np.isnan(g_used_cur))
                    and (g_used_cur <= 1.0 + 1e-9)
                    and bool(r.get("clamped", False))
                ):
                    step_events.append(
                        f"{aid}: G released to 1.0 (cmd {g_user_cur:.1f}, turn {str(r.get('turn_cmd_user', 'S'))}->{str(r.get('turn_effective', 'S'))})"
                    )
                if bool(cmds[aid].get("level_hold", False)):
                    # Reflect level-assist bank scheduling immediately in UI and next-step command seed.
                    bank_auto = quantize_bank_deg(float(r.get("bank_used", cmds[aid].get("bank_deg", 0.0))), min_bank=0.0, max_bank=180.0)
                    if (abs(float(r.get("pitch_used", 0.0))) <= 0.5) and (str(r.get("turn_effective", "S")).upper() != "S"):
                        bank_auto = self._compute_level_bank_from_g(float(r.get("g_used", cmds[aid].get("g_cmd", 1.0))))
                    cmds[aid]["bank_deg"] = bank_auto
                    self.controls[aid].set_bank_from_auto(bank_auto)
                    g_auto = quantize_g_01(float(r.get("g_used", cmds[aid].get("g_cmd", 1.0))), min_g=1.0, max_g=9.0)
                    if (str(r.get("turn_effective", "S")).upper() == "S") and (abs(float(r.get("pitch_used", 0.0))) <= 0.5):
                        g_auto = 1.0
                    cmds[aid]["g_cmd"] = float(g_auto)
                    self.controls[aid].g_cmd.setValue(float(g_auto))
                if bool(r.get("speed_domain_error", False)) or (not bool(r.get("feasible", True))):
                    impl_warn = True
                if bool(r.get("mach_break", False)):
                    mach_warn = True
                print(
                    "[step {} {}] power={}, turn_cmd_user={}, turn_effective={}, g_cmd_user={:.2f}, g_used={:.2f}, g_max={}, clamped={}, ps_primary={}, ps_fallback_1g_straight={}, ps_final={}, feasible={}, cas_before={:.3f}, dV_ktsps={}, cas_after={:.3f}, tas_kt={:.3f}, vxy_ftps={:.3f}, hdg_deg={:.3f}, turn_rate_degps={:.6f}, x_before={:.3f}, y_before={:.3f}, x_after={:.3f}, y_after={:.3f}".format(
                        self.current_step + 1,
                        aid,
                        r["power"],
                        r["turn_cmd_user"],
                        r["turn_effective"],
                        float(r["g_cmd"]),
                        float(r["g_used"]) if not np.isnan(r["g_used"]) else np.nan,
                        "nan" if np.isnan(r["g_max"]) else f"{float(r['g_max']):.2f}",
                        bool(r["clamped"]),
                        "nan" if np.isnan(r["ps_primary"]) else f"{float(r['ps_primary']):.3f}",
                        "nan" if np.isnan(r["ps_fallback_1g_straight"]) else f"{float(r['ps_fallback_1g_straight']):.3f}",
                        "nan" if np.isnan(r["ps_final"]) else f"{float(r['ps_final']):.3f}",
                        bool(r["feasible"]),
                        float(r["cas_before"]),
                        "nan" if np.isnan(r["dV_ktsps"]) else f"{float(r['dV_ktsps']):.6f}",
                        float(r["cas_after"]),
                        float(r["tas_kt"]),
                        float(r["vxy_ftps"]),
                        float(r["hdg_deg"]),
                        float(r["turn_rate_degps"]),
                        float(r["x_before"]),
                        float(r["y_before"]),
                        float(r["x_after"]),
                        float(r["y_after"]),
                    )
                )
            if impl_warn:
                self._show_rate_limited_warning("impl", "Infeasible speed envelope")
            if mach_warn:
                self._show_rate_limited_warning("mach", "Supersonic (Mach >= 1.0)")
            self._show_step_event_warning(self.current_step + 1, step_events)
            next_step = self.current_step + 1
            # If G MAX is enabled, carry forward re-computed max-G for the newly reached state.
            for aid in AIRCRAFT_IDS:
                if bool(cmds.get(aid, {}).get("g_use_max", False)):
                    try:
                        power_n = str(cmds[aid].get("power", "M"))
                        st_n = nxt.get(aid, {})
                        cas_n = float(st_n.get("cas_kt", prev_step_states.get(aid, {}).get("cas_kt", self.controls[aid].cas_kt.value())))
                        alt_n = float(st_n.get("z_ft", prev_step_states.get(aid, {}).get("z_ft", self.controls[aid].alt_ft.value())))
                        gmax_n = self._find_g_max(power_n, cas_n, alt_n, g_cap=9.0)
                        if not np.isnan(gmax_n):
                            cmds[aid]["g_cmd"] = quantize_g_01(gmax_n, min_g=1.0, max_g=9.0)
                    except Exception:
                        pass
            if self.step_cmds.get(next_step) is None:
                copied_cmds = {aid: dict(cmds[aid]) for aid in AIRCRAFT_IDS}
                self.step_cmds[next_step] = {"_dt": dt, "cmds": copied_cmds}
            else:
                # Existing next step: keep user-authored fields, but refresh g_cmd where g_use_max is on.
                for aid in AIRCRAFT_IDS:
                    if bool(cmds.get(aid, {}).get("g_use_max", False)):
                        self.step_cmds[next_step]["cmds"].setdefault(aid, dict(self._default_cmd_for_aircraft()))
                        self.step_cmds[next_step]["cmds"][aid]["g_cmd"] = float(cmds[aid]["g_cmd"])
            self.current_step += 1
            self.playback_step_float = float(self.current_step)
        self._restore_cmd_ui_for_step(self.current_step)
        self._restore_hold_ui_for_step(self.current_step)
        self.refresh_ui()

    def reset_current_step_cmds(self):
        self.playback_active = False
        defaults = self._default_step_cmds()
        for aid in AIRCRAFT_IDS:
            self.controls[aid].set_command(defaults[aid])
            self.controls[aid].clear_g_limit_indicator()
        dt = float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value())
        self.step_cmds[self.current_step] = {"_dt": dt, "cmds": self._read_current_cmds()}
        self.refresh_ui()

    def _step_tail_points(self, aid: str):
        s0 = self._tail_start_step()
        pts = []
        for s in range(s0, self.current_step):
            st = self.state_history[s][aid]
            pts.append([st["x_ft"], st["y_ft"], st["z_ft"]])
        if not pts:
            return np.zeros((0, 3), dtype=float)
        return np.array(pts, dtype=float)

    def _step_tail_states(self, aid: str):
        s0 = self._tail_start_step()
        out = []
        for s in range(s0, self.current_step):
            out.append(self.state_history[s][aid])
        return out

    def _step0_virtual_prev_point(self, aid: str, cur_st: Dict) -> np.ndarray:
        dt = float(self.fixed_dt if self.fixed_dt is not None else max(1.0, float(self.dt_sec.value())))
        tas_kt = float(cur_st.get("tas_kt", np.nan))
        if np.isnan(tas_kt):
            tas_kt = self._tas_from_cas(float(cur_st.get("cas_kt", 0.0)), float(cur_st.get("z_ft", 0.0)))
        speed_ftps = float(max(0.0, tas_kt) * KT_TO_FTPS)
        pitch_deg = float(self.controls[aid].read_command().get("pitch_deg", cur_st.get("pitch_deg", 0.0)))
        u = self._safe_heading_pitch_velocity_unit(float(cur_st.get("hdg_deg", 0.0)), pitch_deg)
        cur_pt = np.array([float(cur_st["x_ft"]), float(cur_st["y_ft"]), float(cur_st["z_ft"])], dtype=float)
        return cur_pt - (u * speed_ftps * dt)

    def _full_points(self, aid: str):
        pts = []
        for s in range(0, self.current_step + 1):
            st = self.state_history[s][aid]
            pts.append([st["x_ft"], st["y_ft"], st["z_ft"]])
        if not pts:
            return np.zeros((0, 3), dtype=float)
        return np.array(pts, dtype=float)

    def _arrow_len_for_aircraft(self, aid: str, step_idx: Optional[int] = None, step_mode: bool = True) -> float:
        if not self.state_history:
            return 500.0
        if step_idx is None:
            step_idx = self.current_step
        step_idx = max(0, min(int(step_idx), len(self.state_history) - 1))
        if step_mode:
            s0 = max(0, step_idx - 10)
        else:
            s0 = 0
        pts = []
        for s in range(s0, step_idx + 1):
            st = self.state_history[s][aid]
            pts.append([st["x_ft"], st["y_ft"], st["z_ft"]])
        arr = np.array(pts, dtype=float) if pts else np.zeros((0, 3), dtype=float)
        if len(arr) < 2:
            return 500.0
        bb_min = np.min(arr, axis=0)
        bb_max = np.max(arr, axis=0)
        extent = float(np.linalg.norm(bb_max - bb_min))
        return max(500.0, 0.1 * extent)

    @staticmethod
    def _dynamic_arrow_gap_and_shaft(start: np.ndarray, hdg_deg: float, length_ft: float, next_pos: Optional[np.ndarray] = None):
        base_gap = ARROW_BASE_GAP_FT
        min_gap = ARROW_MIN_GAP_FT
        max_gap = ARROW_MAX_GAP_FT
        min_shaft = ARROW_MIN_SHAFT_LEN_FT
        safety = ARROW_DYNAMIC_SAFETY_FT
        gap = float(min(max(base_gap, min_gap), max_gap))
        shaft_default = max(float(length_ft) - gap, min_shaft)

        if next_pos is None:
            return gap, shaft_default

        delta = np.array(next_pos, dtype=float) - np.array(start, dtype=float)
        step_sep = float(np.linalg.norm(delta))
        if step_sep <= 1e-6:
            return min_gap, 0.0
        usable = max(step_sep - safety, 0.0)
        # For very short per-step moves, still constrain arrow into the step span.
        if usable <= 1e-6:
            usable = step_sep * 0.80

        gap = min(gap, usable * 0.35)
        gap = max(0.0, min(gap, max_gap))

        # Force clearance near the next step start so prior head/wings and next shaft never overlap.
        boundary_clear = max(350.0, base_gap * 0.90)
        shaft_max = min(usable - gap, step_sep - gap - boundary_clear)
        if shaft_max <= 0.0:
            gap = max(0.0, min(gap, usable))
            return gap, 0.0

        if shaft_max < min_shaft:
            return gap, max(0.0, shaft_max)
        return gap, min(shaft_default, shaft_max)

    @staticmethod
    def _arrow_geometry(start: np.ndarray, hdg_deg: float, length_ft: float, next_pos: Optional[np.ndarray] = None, pitch_deg: float = 0.0):
        hdg_rad = math.radians(hdg_deg)
        pitch_rad = math.radians(float(pitch_deg))
        fwd = np.array(
            [
                math.sin(hdg_rad) * math.cos(pitch_rad),
                math.cos(hdg_rad) * math.cos(pitch_rad),
                math.sin(pitch_rad),
            ],
            dtype=float,
        )
        fn = float(np.linalg.norm(fwd))
        if fn > 1e-9:
            fwd = fwd / fn
        # Keep wing axis as aircraft left-right in horizontal plane.
        wing_axis = np.array([math.sin(hdg_rad - math.pi / 2.0), math.cos(hdg_rad - math.pi / 2.0), 0.0], dtype=float)
        wn = float(np.linalg.norm(wing_axis))
        if wn > 1e-9:
            wing_axis = wing_axis / wn
        gap_ft, shaft_len = MainWindow._dynamic_arrow_gap_and_shaft(start, hdg_deg, length_ft, next_pos)
        shaft_start = start + fwd * gap_ft
        shaft_end = shaft_start + fwd * shaft_len
        head_basis = max(float(length_ft), float(shaft_len), ARROW_MIN_SHAFT_LEN_FT)
        head_back_len = head_basis * 0.35
        head_half_len = head_basis * (0.36 * 2.0)
        wing_back = fwd * head_back_len
        wing_side = wing_axis * head_half_len
        # No detached tip: head apex is the shaft end.
        # Left/right wings represent aircraft lateral axis.
        slash_scale = 2.0
        wing_r = shaft_end + (-wing_back - wing_side) * slash_scale
        wing_l = shaft_end + (-wing_back + wing_side) * slash_scale
        return shaft_start, shaft_end, wing_l, wing_r

    @staticmethod
    def _build_dashed_line_points(p0: np.ndarray, p1: np.ndarray, dash_len: float = 200.0, gap_len: float = 200.0):
        seg = p1 - p0
        dist = float(np.linalg.norm(seg))
        if dist < 1e-9:
            return np.zeros((0, 3), dtype=float)
        d = seg / dist
        dash_eff = min(float(dash_len), max(20.0, dist * 0.4))
        gap_eff = min(float(gap_len), max(20.0, dist * 0.4))
        step = max(1.0, dash_eff + gap_eff)
        pts = []
        t = 0.0
        while t < dist:
            t2 = min(t + dash_eff, dist)
            a = p0 + d * t
            b = p0 + d * t2
            pts.extend([a, b])
            t += step
        return np.array(pts, dtype=float) if pts else np.zeros((0, 3), dtype=float)

    def _build_dashed_arrow_points(self, start: np.ndarray, hdg_deg: float, length_ft: float, next_pos: Optional[np.ndarray] = None):
        shaft_start, shaft_end, wing_l, wing_r = self._arrow_geometry(start, hdg_deg, length_ft, next_pos)
        p1 = self._build_dashed_line_points(shaft_start, shaft_end, 200.0, 200.0)
        # Head is always solid for readability and to avoid detached-looking dashed chevrons.
        p2 = np.array([shaft_end, wing_l], dtype=float)
        p3 = np.array([shaft_end, wing_r], dtype=float)
        parts = [p for p in [p1, p2, p3] if len(p) > 0]
        return np.vstack(parts) if parts else np.zeros((0, 3), dtype=float)

    def _arrow_points_for_turn(self, start: np.ndarray, hdg_deg: float, length_ft: float, turn_dir: str, next_pos: Optional[np.ndarray] = None):
        shaft_start, shaft_end, wing_l, wing_r = self._arrow_geometry(start, hdg_deg, length_ft, next_pos)
        pts = [shaft_start, shaft_end]
        td = str(turn_dir or "S").upper()
        if td == "CW":
            pts.extend([shaft_end, wing_r])
        elif td == "CCW":
            pts.extend([shaft_end, wing_l])
        else:
            pts.extend([shaft_end, wing_l, shaft_end, wing_r])
        return np.array(pts, dtype=float)

    def _build_dashed_arrow_points_with_turn(self, start: np.ndarray, hdg_deg: float, length_ft: float, turn_dir: str, next_pos: Optional[np.ndarray] = None):
        shaft_start, shaft_end, wing_l, wing_r = self._arrow_geometry(start, hdg_deg, length_ft, next_pos)
        p1 = self._build_dashed_line_points(shaft_start, shaft_end, 200.0, 200.0)
        parts = [p1] if len(p1) > 0 else []
        td = str(turn_dir or "S").upper()
        if td == "CW":
            p = np.array([shaft_end, wing_r], dtype=float)
            if len(p) > 0:
                parts.append(p)
        elif td == "CCW":
            p = np.array([shaft_end, wing_l], dtype=float)
            if len(p) > 0:
                parts.append(p)
        else:
            p2 = np.array([shaft_end, wing_l], dtype=float)
            p3 = np.array([shaft_end, wing_r], dtype=float)
            if len(p2) > 0:
                parts.append(p2)
            if len(p3) > 0:
                parts.append(p3)
        return np.vstack(parts) if parts else np.zeros((0, 3), dtype=float)

    def _clear_step_arrow_items(self, aid: str):
        for it in self.step_arrow_items.get(aid, []):
            try:
                self.view.removeItem(it)
            except Exception:
                pass
        self.step_arrow_items[aid] = []

    def _add_step_arrow_segment(self, aid: str, p0: np.ndarray, p1: np.ndarray, color: Tuple[float, float, float, float], width: float):
        seg = np.array([p0, p1], dtype=float)
        item = gl.GLLinePlotItem(pos=seg, color=color, width=width, antialias=True, mode="lines")
        # Keep step arrows visually on top in overview/play to avoid depth-fight shaft dropout.
        item.setGLOptions("additive")
        item.setDepthValue(100.0)
        self.view.addItem(item)
        self.step_arrow_items[aid].append(item)

    def _add_step_arrow_poly(self, aid: str, pts: np.ndarray, color: Tuple[float, float, float, float], width: float):
        if pts is None or len(pts) < 2:
            return
        item = gl.GLLinePlotItem(pos=np.array(pts, dtype=float), color=color, width=width, antialias=True, mode="lines")
        item.setGLOptions("additive")
        item.setDepthValue(100.0)
        self.view.addItem(item)
        self.step_arrow_items[aid].append(item)

    @staticmethod
    def _attached_tip_geometry(
        start: np.ndarray,
        hdg_deg: float,
        pitch_deg: float,
        tip_len_ft: float,
        next_pos: Optional[np.ndarray] = None,
    ):
        hdg_rad = math.radians(float(hdg_deg))
        pitch_rad = math.radians(float(pitch_deg))
        fwd = np.array(
            [
                math.sin(hdg_rad) * math.cos(pitch_rad),
                math.cos(hdg_rad) * math.cos(pitch_rad),
                math.sin(pitch_rad),
            ],
            dtype=float,
        )
        fn = float(np.linalg.norm(fwd))
        if fn > 1e-9:
            fwd = fwd / fn
        wing_axis = np.array([math.sin(hdg_rad - math.pi / 2.0), math.cos(hdg_rad - math.pi / 2.0), 0.0], dtype=float)
        wn = float(np.linalg.norm(wing_axis))
        if wn > 1e-9:
            wing_axis = wing_axis / wn
        tip_len = max(1.0, float(tip_len_ft))
        # IMPORTANT:
        # Do not cap tip/shaft length by next-step spacing.
        # This avoids intermittent shaft collapse for some aircraft/steps in overview/play.
        tail = np.array(start, dtype=float)
        apex = tail + fwd * tip_len
        wing_half = wing_axis * (tip_len * (0.32 * 2.0))
        base_l = (tail + wing_half) - apex
        base_r = (tail - wing_half) - apex
        slash_scale = 2.0
        wing_l = apex + base_l * slash_scale
        wing_r = apex + base_r * slash_scale
        return tail, apex, wing_l, wing_r

    def _draw_arrow_dashed(self, aid: str, start: np.ndarray, hdg_deg: float, pitch_deg: float, length_ft: float, turn_dir: str, next_pos: Optional[np.ndarray], color: Tuple[float, float, float, float]):
        tail, apex, wing_l, wing_r = self._attached_tip_geometry(start, hdg_deg, pitch_deg, length_ft, next_pos=next_pos)
        td = str(turn_dir or "S").upper()
        # Draw shaft and wings as separate segments to avoid intermittent shaft drop
        # on some aircraft/steps in overview/play rendering paths.
        self._add_step_arrow_segment(aid, tail, apex, color, self._lw(3.36))
        if td in ("S", "CCW"):
            self._add_step_arrow_segment(aid, apex, wing_l, color, self._lw(3.36))
        if td in ("S", "CW"):
            self._add_step_arrow_segment(aid, apex, wing_r, color, self._lw(3.36))

    def _draw_arrow_solid(self, aid: str, start: np.ndarray, hdg_deg: float, pitch_deg: float, length_ft: float, turn_dir: str, next_pos: Optional[np.ndarray], color: Tuple[float, float, float, float]):
        tail, apex, wing_l, wing_r = self._attached_tip_geometry(start, hdg_deg, pitch_deg, length_ft, next_pos=next_pos)
        td = str(turn_dir or "S").upper()
        self._add_step_arrow_segment(aid, tail, apex, color, self._lw(5.04))
        if td in ("S", "CCW"):
            self._add_step_arrow_segment(aid, apex, wing_l, color, self._lw(5.04))
        if td in ("S", "CW"):
            self._add_step_arrow_segment(aid, apex, wing_r, color, self._lw(5.04))

    def _draw_last_head_only(self, aid: str, start: np.ndarray, hdg_deg: float, pitch_deg: float, length_ft: float, next_pos: Optional[np.ndarray], color: Tuple[float, float, float, float]):
        _shaft_start, shaft_end, wing_l, wing_r = self._arrow_geometry(start, hdg_deg, length_ft, next_pos, pitch_deg=pitch_deg)
        # Overview/playback rule: no shaft, last step head only (two wing lines).
        self._add_step_arrow_segment(aid, shaft_end, wing_l, color, self._lw(3.0))
        self._add_step_arrow_segment(aid, shaft_end, wing_r, color, self._lw(3.0))

    def _draw_overview_step_arrow_from_pair(
        self,
        aid: str,
        p0: np.ndarray,
        p1: np.ndarray,
        turn_dir: str,
        color: Tuple[float, float, float, float],
        width: float,
    ):
        # Use actual step segment (p0->p1) as shaft in overview/play so every step is represented.
        s = np.array(p0, dtype=float)
        e = np.array(p1, dtype=float)
        d = e - s
        dist = float(np.linalg.norm(d))
        if dist <= 1e-6:
            return
        self._add_step_arrow_segment(aid, s, e, color, width)
        fwd = d / dist
        hdg = self._wrap_hdg(math.degrees(math.atan2(float(fwd[0]), float(fwd[1]))))
        hxy = max(1e-9, float(math.hypot(float(fwd[0]), float(fwd[1]))))
        pitch = math.degrees(math.atan2(float(fwd[2]), hxy))
        head_len = max(55.0, min(220.0, 0.72 * dist))
        head_start = e - (fwd * head_len)
        _tail, apex, wing_l, wing_r = self._attached_tip_geometry(head_start, hdg, pitch, head_len, next_pos=None)
        td = str(turn_dir or "S").upper()
        if td in ("S", "CCW"):
            self._add_step_arrow_segment(aid, apex, wing_l, color, width)
        if td in ("S", "CW"):
            self._add_step_arrow_segment(aid, apex, wing_r, color, width)

    @staticmethod
    def _seven_seg_strokes(ch: str) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        # 7-segment in local box: x:[0,1], y:[0,2]
        seg = {
            "a": ((0.0, 2.0), (1.0, 2.0)),
            "b": ((1.0, 2.0), (1.0, 1.0)),
            "c": ((1.0, 1.0), (1.0, 0.0)),
            "d": ((0.0, 0.0), (1.0, 0.0)),
            "e": ((0.0, 1.0), (0.0, 0.0)),
            "f": ((0.0, 2.0), (0.0, 1.0)),
            "g": ((0.0, 1.0), (1.0, 1.0)),
        }
        mapping = {
            "0": "abcedf",
            "1": "bc",
            "2": "abged",
            "3": "abgcd",
            "4": "fgbc",
            "5": "afgcd",
            "6": "afgecd",
            "7": "abc",
            "8": "abcdefg",
            "9": "abfgcd",
        }
        use = mapping.get(str(ch), "")
        return [seg[k] for k in use if k in seg]

    def _draw_step_number_attached(
        self,
        aid: str,
        step_idx: int,
        apex: np.ndarray,
        hdg_deg: float,
        tip_len_ft: float,
        color: Tuple[float, float, float, float],
    ):
        if (not hasattr(self, "chk_show_steps")) or (not self.chk_show_steps.isChecked()):
            return
        text = str(int(step_idx))
        if not text:
            return
        if (not hasattr(self, "view")) or (self.view is None) or (not hasattr(self.view, "_camera_basis")):
            return
        cam, cam_fwd, cam_right, cam_up = self.view._camera_basis()
        rel = np.array(apex, dtype=float) - np.array(cam, dtype=float)
        zc = float(np.dot(rel, cam_fwd))
        if zc <= 1.0:
            return
        fov = float(self.view.opts.get("fov", 60.0))
        view_h = max(1.0, float(self.view.height()))
        world_per_px = (2.0 * zc * math.tan(math.radians(fov) * 0.5)) / view_h

        char_w = 1.0
        gap = 0.35
        text_w = max(1.0, (len(text) * char_w) + (max(0, len(text) - 1) * gap))
        target_digit_h_px = 16.0
        scale = float(np.clip(world_per_px * (0.5 * target_digit_h_px), 18.0, 420.0))
        origin = (
            np.array(apex, dtype=float)
            + cam_right * (world_per_px * 18.0)
            + cam_up * (world_per_px * 10.0)
        )
        if hasattr(self, "step_number_pick_cache") and isinstance(self.step_number_pick_cache, dict):
            self.step_number_pick_cache[(str(aid), int(step_idx))] = np.array(origin, dtype=float)
        x_cursor = -0.5 * text_w
        for ch in text:
            strokes = self._seven_seg_strokes(ch)
            for (x0, y0), (x1, y1) in strokes:
                p0 = origin + cam_right * ((x_cursor + x0) * scale) + cam_up * ((y0 - 1.0) * scale)
                p1 = origin + cam_right * ((x_cursor + x1) * scale) + cam_up * ((y1 - 1.0) * scale)
                self._add_step_arrow_segment(aid, p0, p1, (color[0], color[1], color[2], max(0.92, color[3])), self._lw(3.8))
            x_cursor += char_w + gap

    def _turn_dir_for_state(self, aid: str, step_idx: int) -> str:
        if not self.state_history:
            return "S"
        k = max(0, min(step_idx, len(self.state_history) - 1))
        st = self.state_history[k][aid]
        t = str(st.get("turn_effective", st.get("turn", "S"))).upper()
        if t in ("S", "CW", "CCW"):
            return t
        if k <= 0:
            return "S"
        prev_h = float(self.state_history[k - 1][aid]["hdg_deg"])
        cur_h = float(st["hdg_deg"])
        d = (cur_h - prev_h + 540.0) % 360.0 - 180.0
        if d > 1e-6:
            return "CW"
        if d < -1e-6:
            return "CCW"
        return "S"

    def _overview_arrow_hdg_deg(self, aid: str, step_idx: int, fallback_hdg: float) -> float:
        # In overview, prefer track-based heading so shaft/tip always align with the
        # rendered trajectory even if stored heading is stale or inconsistent.
        if (step_idx < 0) or (step_idx >= len(self.state_history)):
            return float(fallback_hdg)
        cur = self.state_history[step_idx][aid]
        if (step_idx + 1) < len(self.state_history):
            nxt = self.state_history[step_idx + 1][aid]
            dx = float(nxt["x_ft"]) - float(cur["x_ft"])
            dy = float(nxt["y_ft"]) - float(cur["y_ft"])
            if (abs(dx) + abs(dy)) > 1e-6:
                return self._wrap_hdg(math.degrees(math.atan2(dx, dy)))
        if step_idx > 0:
            prv = self.state_history[step_idx - 1][aid]
            dx = float(cur["x_ft"]) - float(prv["x_ft"])
            dy = float(cur["y_ft"]) - float(prv["y_ft"])
            if (abs(dx) + abs(dy)) > 1e-6:
                return self._wrap_hdg(math.degrees(math.atan2(dx, dy)))
        return float(fallback_hdg)

    @staticmethod
    def _marker_line_points_for_kind(
        pos: np.ndarray,
        hdg_deg: float,
        kind: str,
        arrow_len_ft: float,
        next_pos: Optional[np.ndarray] = None,
    ):
        hdg_rad = math.radians(hdg_deg)
        fwd = np.array([math.sin(hdg_rad), math.cos(hdg_rad), 0.0], dtype=float)
        perp = np.array([math.sin(hdg_rad - math.pi / 2.0), math.cos(hdg_rad - math.pi / 2.0), 0.0], dtype=float)
        base_long_len = 400.0
        len_scale = 9.0
        long_len = base_long_len * len_scale
        short_len = long_len * 0.20  # short segment is 20% of long segment.
        long_half = long_len * 0.5
        short_half = short_len * 0.5
        pos_np = np.array(pos, dtype=float)
        next_np = None if next_pos is None else np.array(next_pos, dtype=float)
        shaft_start, shaft_end, _wing_l, _wing_r = MainWindow._arrow_geometry(
            pos_np,
            float(hdg_deg),
            float(arrow_len_ft),
            next_np,
        )
        shaft_len = float(np.linalg.norm(shaft_end - shaft_start))
        # Marker pair spacing scales with shaft length for consistent look across arrow sizes.
        sep = max(20.0, float(shaft_len) * 2.00)
        # Keep marker anchor rule fixed to midpoint of step straight segment.
        if next_np is not None:
            marker_anchor = 0.5 * (pos_np + next_np)
        else:
            marker_anchor = 0.5 * (shaft_start + shaft_end)
        back_center = marker_anchor - fwd * (0.5 * sep)
        front_center = marker_anchor + fwd * (0.5 * sep)

        if kind == "up":
            # Climb: short then long along forward direction.
            back_half = short_half
            front_half = long_half
        elif kind == "down":
            # Descent: long then short along forward direction.
            back_half = long_half
            front_half = short_half
        else:
            # Level-off: long + long.
            back_half = long_half
            front_half = long_half

        front_a = front_center - perp * front_half
        front_b = front_center + perp * front_half
        back_a = back_center - perp * back_half
        back_b = back_center + perp * back_half
        # Keep markers on the same altitude plane as the arrow shaft to avoid "floating" artifacts.
        z_anchor = float(marker_anchor[2])
        front_a[2] = z_anchor
        front_b[2] = z_anchor
        back_a[2] = z_anchor
        back_b[2] = z_anchor
        return np.array([front_a, front_b, back_a, back_b], dtype=float)

    def _vertical_transition_markers(self, aid: str, step_mode: bool, arrow_len_ft: float):
        if self.current_step <= 0:
            return np.zeros((0, 3), dtype=float)
        dz_threshold = 1.0
        if step_mode:
            k0 = max(1, self.current_step - 10)
        else:
            k0 = 1
        k1 = self.current_step
        parts = []
        for k in range(k0, k1 + 1):
            prev_st = self.state_history[k - 1][aid]
            cur_st = self.state_history[k][aid]
            dz_now = float(cur_st["z_ft"] - prev_st["z_ft"])
            if k >= 2:
                prev2 = self.state_history[k - 2][aid]
                dz_prev = float(prev_st["z_ft"] - prev2["z_ft"])
            else:
                dz_prev = 0.0
            kind = None
            if dz_now >= dz_threshold and dz_prev <= dz_threshold:
                kind = "up"
            elif dz_now <= -dz_threshold and dz_prev >= -dz_threshold:
                kind = "down"
            elif dz_prev > dz_threshold and abs(dz_now) <= dz_threshold:
                kind = "level_up"
            elif dz_prev < -dz_threshold and abs(dz_now) <= dz_threshold:
                kind = "level_down"
            if kind is None:
                continue
            # Map marker to the same step arrow segment that is rendered in step mode.
            if k < (len(self.state_history) - 1):
                st0 = self.state_history[k][aid]
                st1 = self.state_history[k + 1][aid]
            else:
                st0 = self.state_history[k - 1][aid]
                st1 = self.state_history[k][aid]
            p0 = np.array([st0["x_ft"], st0["y_ft"], st0["z_ft"]], dtype=float)
            p1 = np.array([st1["x_ft"], st1["y_ft"], st1["z_ft"]], dtype=float)
            hdg0 = float(st0["hdg_deg"])
            parts.append(self._marker_line_points_for_kind(p0, hdg0, kind, arrow_len_ft, next_pos=p1))
        return np.vstack(parts) if parts else np.zeros((0, 3), dtype=float)

    def _set_mode_visibility(self, aid: str, step_mode: bool):
        p = self.plot_items[aid]
        p["trail_dashed"].setVisible(step_mode)
        p["trail_recent"].setVisible(step_mode)
        p["arrows_dashed"].setVisible(False)
        p["arrow_current"].setVisible(False)
        p["vertical_markers"].setVisible(True)
        for k in ["overview_line", "overview_scatter"]:
            p[k].setVisible(not step_mode)

    def _current_positions_for_pivot(self) -> Dict[str, np.ndarray]:
        if not self.state_history:
            return {}
        st = self.state_history[-1]
        out = {}
        for aid in self._active_aircraft_ids():
            out[aid] = np.array([st[aid]["x_ft"], st[aid]["y_ft"], st[aid]["z_ft"]], dtype=float)
        return out

    def _set_pivot_marker(self, p: np.ndarray):
        if not hasattr(self, "pivot_marker") or self.pivot_marker is None:
            return
        self.pivot_marker.setData(
            pos=np.array([[float(p[0]), float(p[1]), float(p[2])]], dtype=float),
            color=np.array([[0.20, 0.60, 0.20, 0.45]], dtype=float),
            size=12.0,
            pxMode=True,
        )
        self.update_ata_labels()

    def _position_view_overlays(self):
        if not hasattr(self, "grid_spacing_combo") or self.grid_spacing_combo is None:
            return
        m = 10
        popped_mode = bool(getattr(self, "_left_ui_popped", False))
        if popped_mode:
            if hasattr(self, "global_overlay") and self.global_overlay is not None and self.global_overlay.isVisible():
                self.global_overlay.hide()
            if hasattr(self, "global_group") and self.global_group is not None:
                if self.global_group.parent() is self.global_overlay:
                    self._set_global_overlay_mode(False)
                if hasattr(self, "left_panel") and (self.global_group.parent() is not self.left_panel):
                    self.global_group.setParent(self.left_panel)
                    if hasattr(self, "left_layout") and self.left_layout is not None:
                        self.left_layout.insertWidget(0, self.global_group)
                # Detached panel mode: keep GLOBAL opaque and visible.
                self.global_group.setGraphicsEffect(None)
                self.global_group.setStyleSheet("")
                if not self.global_group.isVisible():
                    self.global_group.show()
            self._position_left_panel_toggle()
        else:
            hidden_now = self._is_left_panel_effectively_hidden()
            self._left_panel_hidden = bool(hidden_now)
            if hidden_now:
                if self.global_group.parent() is not self.global_overlay:
                    self._set_global_overlay_mode(True)
                if not self.global_group.isVisible():
                    self.global_group.show()
                if not self.global_overlay.isVisible():
                    self.global_overlay.show()
                self._ensure_global_overlay_alive()
            else:
                if self.global_group.parent() is self.global_overlay:
                    self._set_global_overlay_mode(False)
        self._position_global_overlay()
        top_base = m
        y_cursor = top_base
        # Row 1: BACK/FWD and ZOOM text buttons (left-top)
        if hasattr(self, "btn_view_back") and hasattr(self, "btn_view_fwd") and hasattr(self, "btn_view_zoom_in") and hasattr(self, "btn_view_zoom_out"):
            gap = 6
            b1w = max(56, self.btn_view_fwd.sizeHint().width() + 4)
            b1h = max(26, self.btn_view_fwd.sizeHint().height() + 2)
            b2w = max(56, self.btn_view_back.sizeHint().width() + 4)
            b2h = max(26, self.btn_view_back.sizeHint().height() + 2)
            b3w = max(36, self.btn_view_zoom_in.sizeHint().width() + 6)
            b3h = max(26, self.btn_view_zoom_in.sizeHint().height() + 2)
            b4w = max(36, self.btn_view_zoom_out.sizeHint().width() + 6)
            b4h = max(26, self.btn_view_zoom_out.sizeHint().height() + 2)
            row1h = max(b1h, b2h, b3h, b4h)
            x1 = m
            self.btn_view_fwd.setGeometry(x1, y_cursor + (row1h - b1h) // 2, b1w, b1h)
            self.btn_view_fwd.raise_()
            x2 = x1 + b1w + gap
            self.btn_view_back.setGeometry(x2, y_cursor + (row1h - b2h) // 2, b2w, b2h)
            self.btn_view_back.raise_()
            x3 = x2 + b2w + gap
            self.btn_view_zoom_in.setGeometry(x3, y_cursor + (row1h - b3h) // 2, b3w, b3h)
            self.btn_view_zoom_in.raise_()
            x4 = x3 + b3w + gap
            self.btn_view_zoom_out.setGeometry(x4, y_cursor + (row1h - b4h) // 2, b4w, b4h)
            self.btn_view_zoom_out.raise_()
            y_cursor += row1h + 6
        # Row 2: playback icons (same look as global)
        if hasattr(self, "btn_view_play_back") and hasattr(self, "btn_view_play_pause") and hasattr(self, "btn_view_stop"):
            gap = 6
            iw = 28
            ih = 24
            x = m
            self.btn_view_play_back.setGeometry(x, y_cursor, iw, ih)
            self.btn_view_play_back.raise_()
            x += iw + gap
            self.btn_view_play_pause.setGeometry(x, y_cursor, iw, ih)
            self.btn_view_play_pause.raise_()
            x += iw + gap
            self.btn_view_stop.setGeometry(x, y_cursor, iw, ih)
            self.btn_view_stop.raise_()
            y_cursor += ih + 6
        # Row 3: speed presets
        if hasattr(self, "btn_view_speed_x1") and hasattr(self, "btn_view_speed_x2") and hasattr(self, "btn_view_speed_x4"):
            speed_btns = [self.btn_view_speed_x1, self.btn_view_speed_x2, self.btn_view_speed_x4]
            gap_s = 4
            sx = m
            sy = y_cursor
            max_h = 0
            for sb in speed_btns:
                sw = max(34, sb.sizeHint().width() + 2)
                sh = max(22, sb.sizeHint().height())
                max_h = max(max_h, sh)
                sb.setGeometry(sx, sy, sw, sh)
                sb.raise_()
                sx += sw + gap_s
            y_cursor += max_h + 8
        # Row 4: view mode and step label toggles
        if hasattr(self, "btn_view_mode_step") and hasattr(self, "btn_view_mode_overview") and hasattr(self, "btn_view_show_steps"):
            mode_btns = [self.btn_view_mode_step, self.btn_view_mode_overview, self.btn_view_show_steps]
            gap_m = 4
            mx = m
            my = y_cursor
            max_h2 = 0
            for mb in mode_btns:
                mw = max(74, mb.sizeHint().width() + 6)
                mh = max(22, mb.sizeHint().height())
                max_h2 = max(max_h2, mh)
                mb.setGeometry(mx, my, mw, mh)
                mb.raise_()
                mx += mw + gap_m
            y_cursor += max_h2 + 8
        if hasattr(self, "lbl_view_tail") and hasattr(self, "btn_view_tail_3") and hasattr(self, "btn_view_tail_10") and hasattr(self, "btn_view_tail_inf"):
            tx = m
            ty = y_cursor
            lw = max(42, self.lbl_view_tail.sizeHint().width() + 4)
            lh = max(22, self.lbl_view_tail.sizeHint().height() + 2)
            self.lbl_view_tail.setGeometry(tx, ty, lw, lh)
            self.lbl_view_tail.raise_()
            tx += lw + 4
            for tb in (self.btn_view_tail_3, self.btn_view_tail_10, self.btn_view_tail_inf):
                twb = max(32, tb.sizeHint().width() + 2)
                thb = max(22, tb.sizeHint().height())
                tb.setGeometry(tx, ty, twb, thb)
                tb.raise_()
                tx += twb + 4
            y_cursor += max(lh, 22) + 8
        ew = eh = 0
        tw = th = 0
        pw = ph = 0
        gw = gh = 0
        if hasattr(self, "elapsed_stamp") and (self.elapsed_stamp is not None):
            ew = self.elapsed_stamp.sizeHint().width() + 2
            eh = self.elapsed_stamp.sizeHint().height() + 2
        if hasattr(self, "chk_top_view_overlay") and (self.chk_top_view_overlay is not None):
            tw = self.chk_top_view_overlay.sizeHint().width() + 4
            th = self.chk_top_view_overlay.sizeHint().height()
        if hasattr(self, "chk_plan_view_overlay") and (self.chk_plan_view_overlay is not None):
            pw = self.chk_plan_view_overlay.sizeHint().width() + 4
            ph = self.chk_plan_view_overlay.sizeHint().height()
        if hasattr(self, "grid_spacing_combo") and (self.grid_spacing_combo is not None):
            gw = self.grid_spacing_combo.sizeHint().width() + 4
            gh = self.grid_spacing_combo.sizeHint().height()
        panel_w = max(tw, pw, gw, 1)
        right_margin = 2
        panel_x = max(right_margin, self.view.width() - panel_w - right_margin)
        if hasattr(self, "compass_rose") and (self.compass_rose is not None):
            cw = 146
            ch = 146
            c_x = max(2, panel_x - cw - 10)
            c_y = 10
            self.compass_rose.setGeometry(c_x, c_y, cw, ch)
            self.compass_rose.raise_()
        if hasattr(self, "step_center_stamp") and (self.step_center_stamp is not None):
            sw = self.step_center_stamp.sizeHint().width() + 10
            sh = self.step_center_stamp.sizeHint().height() + 6
            sx = max(m, (self.view.width() - sw) // 2)
            sy = m + 4
            self.step_center_stamp.setGeometry(sx, sy, sw, sh)
            self.step_center_stamp.raise_()
            if hasattr(self, "btn_view_bookmark") and (self.btn_view_bookmark is not None):
                bw = max(30, self.btn_view_bookmark.sizeHint().width() + 2)
                bh = max(24, self.btn_view_bookmark.sizeHint().height())
                bx = int(sx + sw + 6)
                by = int(sy + (sh - bh) // 2)
                bx = max(m, min(int(self.view.width()) - bw - m, bx))
                self.btn_view_bookmark.setGeometry(bx, by, bw, bh)
                self.btn_view_bookmark.raise_()
            if hasattr(self, "elapsed_stamp") and (self.elapsed_stamp is not None):
                tw2 = self.elapsed_stamp.sizeHint().width() + 10
                th2 = self.elapsed_stamp.sizeHint().height() + 6
                tx = max(m, (self.view.width() - tw2) // 2)
                ty = sy + sh + 4
                self.elapsed_stamp.setGeometry(tx, ty, tw2, th2)
                self.elapsed_stamp.raise_()
        y_after_time = 4
        if hasattr(self, "chk_top_view_overlay") and (self.chk_top_view_overlay is not None):
            self.chk_top_view_overlay.setGeometry(panel_x, y_after_time, tw, th)
            self.chk_top_view_overlay.raise_()
            y_after_time += th + 4
        if hasattr(self, "chk_plan_view_overlay") and (self.chk_plan_view_overlay is not None):
            self.chk_plan_view_overlay.setGeometry(panel_x, y_after_time, pw, ph)
            self.chk_plan_view_overlay.raise_()
            y_after_time += ph + 4
        self._position_left_panel_toggle()
        w = gw if gw > 0 else self.grid_spacing_combo.sizeHint().width() + 4
        h = gh if gh > 0 else self.grid_spacing_combo.sizeHint().height()
        x = panel_x
        y = max(2, y_after_time + 3)
        self.grid_spacing_combo.setGeometry(x, y, w, h)
        self.grid_spacing_combo.raise_()
        if hasattr(self, "los_map_panel") and (self.los_map_panel is not None):
            panel_w = 248
            panel_h = 218
            px = 8
            py = max(6, int(self.view.height()) - panel_h - 8)
            self.los_map_panel.setGeometry(px, py, panel_w, panel_h)
            self._refresh_relation_map_overlay()
        if hasattr(self, "bookmark_panel") and (self.bookmark_panel is not None):
            panel_w_b = 336
            bm_count = max(1, int(len(getattr(self, "step_bookmarks", {}))))
            row_h = 36
            panel_h_b = max(44, min(int(self.view.height()) - 24, 8 + (bm_count * row_h) + 8))
            brand_h = 0
            if hasattr(self, "brand_stamp") and (self.brand_stamp is not None):
                try:
                    brand_h = int(self.brand_stamp.sizeHint().height() + 2)
                except Exception:
                    brand_h = 0
            bx = max(6, int(self.view.width()) - panel_w_b - 8)
            by = max(6, int(self.view.height()) - brand_h - 6 - panel_h_b)
            self.bookmark_panel.setGeometry(bx, by, panel_w_b, panel_h_b)
            self.bookmark_panel.raise_()
        if hasattr(self, "brand_stamp") and (self.brand_stamp is not None):
            bw = self.brand_stamp.sizeHint().width() + 2
            bh = self.brand_stamp.sizeHint().height() + 2
            bx = max(right_margin, self.view.width() - bw - right_margin)
            by = max(2, self.view.height() - bh - 2)
            self.brand_stamp.setGeometry(bx, by, bw, bh)
            self.brand_stamp.raise_()

    def _on_view_camera_changed(self):
        # Camera move must immediately rebuild arrow-attached number geometry.
        if bool(getattr(self, "_camera_refresh_guard", False)):
            return
        try:
            self._camera_refresh_guard = True
            self.refresh_ui()
        except Exception:
            pass
        finally:
            self._camera_refresh_guard = False

    def _adjust_view_zoom(self, scale: float):
        if (not hasattr(self, "view")) or (self.view is None):
            return
        try:
            cur = float(self.view.opts.get("distance", 40000.0))
        except Exception:
            cur = 40000.0
        s = float(scale)
        if (not np.isfinite(s)) or (s <= 0.0):
            return
        nxt = max(500.0, min(300000.0, cur * s))
        self.view.setCameraPosition(distance=float(nxt))
        self._position_view_overlays()

    def _elapsed_seconds_to_step(self, step: int) -> float:
        step_i = max(0, int(step))
        if step_i <= 0:
            return 0.0
        if self.fixed_dt is not None:
            return float(self.fixed_dt) * float(step_i)
        default_dt = float(max(1.0, self.dt_sec.value()))
        total = 0.0
        for s in range(step_i):
            pkg = self.step_cmds.get(s)
            total += float(pkg.get("_dt", default_dt)) if isinstance(pkg, dict) else default_dt
        return total

    @staticmethod
    def _format_mmss(total_sec: float) -> str:
        sec = max(0, int(round(float(total_sec))))
        mm = sec // 60
        ss = sec % 60
        return f"{mm:02d}:{ss:02d}"

    def _lw(self, base_width: float) -> float:
        return float(base_width) * float(getattr(self, "aircraft_line_width_scale", 1.0))

    def _aircraft_color(self, aid: str) -> Tuple[float, float, float, float]:
        return tuple(self.aircraft_colors.get(aid, COLORS.get(aid, (1.0, 1.0, 1.0, 1.0))))

    def _ensure_step_label_pool(self, aid: str, n: int):
        # Legacy QLabel path is intentionally disabled.
        return

    def _hide_all_step_number_labels(self):
        self.step_number_draw_cache = []
        for arr in self.step_num_labels.values():
            for lbl in arr:
                lbl.hide()

    def _overview_sampled_steps(self) -> List[int]:
        if self.current_step <= 0:
            return [0]
        out = list(range(0, self.current_step, 2))
        if out[-1] != self.current_step:
            out.append(self.current_step)
        return out

    def _step_label_anchor_world(self, aid: str, step_idx: int, step_mode: bool) -> Optional[np.ndarray]:
        # Strictly lock number to the rendered arrow-head apex for this step.
        cache = getattr(self, "step_label_anchor_cache", None)
        if not isinstance(cache, dict):
            return None
        v = cache.get((str(aid), int(step_idx)))
        if v is None:
            return None
        return np.array(v, dtype=float)

    def _draw_step_number_labels_for_aircraft(self, aid: str, step_indices: List[int], step_mode: bool):
        return

    def update_step_number_labels(self, step_mode: Optional[bool] = None):
        self.step_number_draw_cache = []
        return

    def _paint_step_number_overlay(self, painter: QPainter):
        return

    def _on_grid_spacing_changed(self):
        txt = self.grid_spacing_combo.currentText()
        if "OFF" in txt.upper():
            self.grid_enabled = False
        else:
            self.grid_enabled = True
        if "1000" in txt:
            self.grid_spacing_ft = 1000.0
        elif "6000" in txt:
            self.grid_spacing_ft = 6000.0
        else:
            self.grid_spacing_ft = 3000.0
        self._build_or_update_dashed_grids(force=True)
        self.refresh_ui()

    @staticmethod
    def _circle_points(center: np.ndarray, radius_ft: float = 1100.0, n: int = 48) -> np.ndarray:
        c = np.array(center, dtype=float)
        pts = []
        for i in range(n + 1):
            th = (2.0 * math.pi * i) / float(n)
            x = c[0] + radius_ft * math.cos(th)
            y = c[1] + radius_ft * math.sin(th)
            z = c[2]
            pts.append([x, y, z])
        return np.array(pts, dtype=float)

    def _pick_aircraft_by_screen(self, sx: float, sy: float, max_dist_px: float = 26.0) -> Optional[str]:
        best_aid = None
        best_dist = float("inf")
        click = np.array([sx, sy], dtype=float)
        for aid in self._active_aircraft_ids():
            pick = self.current_arrow_pick.get(aid)
            if not pick:
                continue
            apex = pick.get("apex")
            if apex is None:
                continue
            sp = self.view._project_point(np.array(apex, dtype=float))
            if sp is None:
                continue
            d = float(np.linalg.norm(sp - click))
            if d < best_dist:
                best_dist = d
                best_aid = aid
        if best_aid is None or best_dist > float(max_dist_px):
            return None
        return best_aid

    def _step_points_for_linking(self) -> List[Tuple[str, int, np.ndarray]]:
        out: List[Tuple[str, int, np.ndarray]] = []
        if not self.state_history:
            return out
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active))
        active = set(self._active_aircraft_ids())
        if step_mode:
            steps = list(range(max(0, self.current_step - 10), self.current_step + 1))
            for aid in AIRCRAFT_IDS:
                if aid not in active:
                    continue
                for s in steps:
                    if s < 0 or s >= len(self.state_history):
                        continue
                    st = self.state_history[s][aid]
                    p = np.array([float(st["x_ft"]), float(st["y_ft"]), float(st["z_ft"])], dtype=float)
                    out.append((aid, int(s), p))
        else:
            # Overview LOS authoring: snap to on-screen arrow-head anchors only.
            s = int(max(0, min(self.current_step, len(self.state_history) - 1)))
            for aid in AIRCRAFT_IDS:
                if aid not in active:
                    continue
                p = self._los_anchor_world(aid, s, step_mode=False)
                if p is None:
                    continue
                out.append((aid, s, np.array(p, dtype=float)))
        return out

    def _pick_step_point_by_screen(self, sx: float, sy: float, max_dist_px: float = 18.0) -> Optional[Tuple[str, int, np.ndarray]]:
        click = np.array([sx, sy], dtype=float)
        best = None
        best_d = float("inf")
        for aid, step_idx, p in self._step_points_for_linking():
            sp = self.view._project_point(p) if hasattr(self.view, "_project_point") else None
            if sp is None:
                continue
            d = float(np.linalg.norm(sp - click))
            if d < best_d:
                best_d = d
                best = (aid, step_idx, p)
        if best is None or best_d > float(max_dist_px):
            return None
        return best

    def _los_anchor_world(self, aid: str, step_i: int, step_mode: bool) -> Optional[np.ndarray]:
        if (step_i < 0) or (step_i >= len(self.state_history)):
            return None
        st = self.state_history[step_i][str(aid)]
        start = np.array([float(st["x_ft"]), float(st["y_ft"]), float(st["z_ft"])], dtype=float)
        if bool(step_mode):
            return start
        # Overview LOS anchors to displayed arrow-head apex.
        cache = getattr(self, "step_label_anchor_cache", None)
        if isinstance(cache, dict):
            v = cache.get((str(aid), int(step_i)))
            if v is not None:
                return np.array(v, dtype=float)
        next_pos = None
        if (step_i + 1) <= self.current_step and (step_i + 1) < len(self.state_history):
            nst = self.state_history[step_i + 1][str(aid)]
            next_pos = np.array([float(nst["x_ft"]), float(nst["y_ft"]), float(nst["z_ft"])], dtype=float)
        tip_len = float(self._arrow_len_for_aircraft(str(aid), step_idx=int(step_i), step_mode=False))
        draw_hdg = self._overview_arrow_hdg_deg(str(aid), int(step_i), float(st.get("hdg_deg", 0.0)))
        _tail, apex, _wing_l, _wing_r = self._attached_tip_geometry(
            start,
            draw_hdg,
            float(st.get("pitch_deg", 0.0)),
            tip_len,
            next_pos=next_pos,
        )
        return np.array(apex, dtype=float)

    def _pick_overview_aircraft_point_by_screen(self, sx: float, sy: float, max_dist_px: float = 52.0) -> Optional[Tuple[str, int, np.ndarray]]:
        # Overview LOS authoring: 2D nearest pick against displayed arrow-head anchors.
        if not self.state_history:
            return None
        s = int(max(0, min(self.current_step, len(self.state_history) - 1)))
        click = np.array([float(sx), float(sy)], dtype=float)
        best_aid = None
        best_pos = None
        best_d = float("inf")
        for aid in self._active_aircraft_ids():
            p = self._los_anchor_world(str(aid), s, step_mode=False)
            if p is None:
                continue
            sp = self.view._project_point(np.array(p, dtype=float)) if hasattr(self.view, "_project_point") else None
            if sp is None:
                continue
            d = float(np.linalg.norm(sp - click))
            if d < best_d:
                best_d = d
                best_aid = str(aid)
                best_pos = np.array(p, dtype=float)
        if (best_aid is None) or (best_pos is None) or (best_d > float(max_dist_px)):
            return None
        return (best_aid, s, best_pos)

    def _pick_same_step_target_by_proximity(
        self,
        sx: float,
        sy: float,
        src_step: int,
        src_aid: str,
        max_dist_px: float = 72.0,
    ) -> Optional[Tuple[str, int, np.ndarray]]:
        # Lenient snap: if cursor is near any displayed point of an aircraft, snap to that aircraft's src_step point.
        click = np.array([sx, sy], dtype=float)
        best_aid = None
        best_d = float("inf")
        for aid, step_idx, p in self._step_points_for_linking():
            if aid == src_aid:
                continue
            sp = self.view._project_point(p) if hasattr(self.view, "_project_point") else None
            if sp is None:
                continue
            d = float(np.linalg.norm(sp - click))
            if d < best_d:
                best_d = d
                best_aid = aid
        if best_aid is None or best_d > float(max_dist_px):
            return None
        if src_step < 0 or src_step >= len(self.state_history):
            return None
        st = self.state_history[src_step][best_aid]
        p = np.array([float(st["x_ft"]), float(st["y_ft"]), float(st["z_ft"])], dtype=float)
        return (str(best_aid), int(src_step), p)

    @staticmethod
    def _place_overlay_label_xy(
        sp: np.ndarray,
        lw: int,
        lh: int,
        vw: int,
        vh: int,
        occupied_rects: List[Tuple[int, int, int, int]],
        base_x: int = 6,
        base_y: int = 6,
    ) -> Tuple[int, int]:
        if vw <= 0 or vh <= 0 or lw <= 0 or lh <= 0:
            return 0, 0
        max_x = max(0, vw - lw)
        max_y = max(0, vh - lh)
        x0 = max(0, min(int(sp[0]) + int(base_x), max_x))
        y0 = max(0, min(int(sp[1]) + int(base_y), max_y))

        pad = 4
        dx = max(10, lw // 4)
        dy = max(12, lh + 2)
        offsets = [(0, 0)]
        for r in range(1, 6):
            for ox in range(-r, r + 1):
                offsets.append((ox, -r))
                offsets.append((ox, r))
            for oy in range(-r + 1, r):
                offsets.append((-r, oy))
                offsets.append((r, oy))

        for ox, oy in offsets:
            x = max(0, min(x0 + ox * dx, max_x))
            y = max(0, min(y0 + oy * dy, max_y))
            overlap = False
            for rx, ry, rw, rh in occupied_rects:
                if (x < (rx + rw + pad)) and ((x + lw + pad) > rx) and (y < (ry + rh + pad)) and ((y + lh + pad) > ry):
                    overlap = True
                    break
            if not overlap:
                return x, y
        return x0, y0

    def _map_mode_enabled(self) -> bool:
        # LOS relation-map authoring is allowed even during playback.
        # (User requested playback-time LOS creation through the LOS panel.)
        return True

    @staticmethod
    def _forced_step_default_pairs_by_mode(mode_key: str) -> List[Tuple[str, str]]:
        mk = str(mode_key).strip()
        if mk == "1vs1":
            # 1vs1 has only #1/#2 active; apply #1-origin orientation.
            base = [("#1", "#2")]
        elif mk == "2vs1":
            # Keep existing pairs, but 1-2 uses #2-origin.
            base = [("#1", "#3"), ("#2", "#3"), ("#2", "#1")]
        elif mk == "2vs2":
            # Keep existing pairs, but 1-2 uses #2-origin and 3-4 uses #4-origin.
            base = [("#1", "#3"), ("#1", "#4"), ("#2", "#3"), ("#2", "#4"), ("#2", "#1"), ("#4", "#3")]
        else:
            base = []
        return list(base)

    def _relation_map_effective_step(self) -> int:
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active))
        if step_mode:
            return int(self.current_step)
        txt = str(self.edt_los_step.text()).strip() if hasattr(self, "edt_los_step") else ""
        if txt == "":
            return int(self.current_step)
        try:
            s = int(float(txt))
        except Exception:
            return int(self.current_step)
        return max(0, min(s, len(self.state_history) - 1 if self.state_history else 0))

    def _toggle_custom_los_pair(self, a: str, b: str, step_i: int, src_aid: str, origin: str):
        a = str(a)
        b = str(b)
        if a == b:
            return
        exists_idx = None
        for i, lk in enumerate(self.custom_los_links):
            if (
                int(lk.get("step", -1)) == int(step_i)
                and str(lk.get("origin", "overview")) == str(origin)
                and str(lk.get("a")) == a
                and str(lk.get("b")) == b
            ):
                exists_idx = i
                break
        if exists_idx is not None:
            del self.custom_los_links[exists_idx]
            return
        st = self._custom_link_style_by_source(a, b, src_aid)
        self.custom_los_links.append(
            {
                "a": a,
                "b": b,
                "step": int(step_i),
                "origin": str(origin),
                "src_aid": str(src_aid),
                "color": st["color"],
                "text_color": st["text_color"],
            }
        )

    def _on_relation_map_pair_drawn(self, a: str, b: str):
        if not self._map_mode_enabled():
            return
        active = set(self._active_aircraft_ids())
        if (a not in active) or (b not in active):
            return
        step_i = self._relation_map_effective_step()
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active))
        mk = str(getattr(self, "current_mode_key", "")).strip()
        forced_pairs = self._forced_step_default_pairs_by_mode(mk)
        if step_mode and (mk in {"1vs1", "2vs1", "2vs2"}) and ((a, b) in forced_pairs):
            hkey = (mk, int(step_i))
            hidden = self.default_step_los_hidden.setdefault(hkey, set())
            if (a, b) in hidden:
                hidden.remove((a, b))
            else:
                hidden.add((a, b))
            self.refresh_ui()
            return
        origin = "step" if step_mode else "overview"
        self._toggle_custom_los_pair(a, b, step_i, src_aid=a, origin=origin)
        self.refresh_ui()

    def _refresh_relation_map_overlay(self):
        if not hasattr(self, "los_relation_map"):
            return
        enabled = bool(self._map_mode_enabled())
        active = list(self._active_aircraft_ids())
        mk = str(getattr(self, "current_mode_key", "")).strip()
        self.los_relation_map.set_mode_and_active(mk, active)
        cdict: Dict[str, Tuple[int, int, int]] = {}
        for aid in active:
            c = self._aircraft_color(aid)
            cdict[str(aid)] = (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))
        self.los_relation_map.set_node_colors(cdict)
        step_i = self._relation_map_effective_step()
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active))
        want_origin = "step" if step_mode else "overview"
        show_links: List[Tuple[str, str]] = []
        # Mirror forced default LOS set in Step View (1vs1/2vs1/2vs2) on the relation map.
        if step_mode and (mk in {"1vs1", "2vs1", "2vs2"}):
            hidden = self.default_step_los_hidden.get((mk, int(step_i)), set())
            for a, b in self._forced_step_default_pairs_by_mode(mk):
                if (a in active) and (b in active):
                    if (a, b) not in hidden:
                        show_links.append((a, b))
        for lk in self.custom_los_links:
            try:
                if str(lk.get("origin", "overview")) != want_origin:
                    continue
                if int(lk.get("step", -1)) != int(step_i):
                    continue
                a = str(lk.get("a"))
                b = str(lk.get("b"))
            except Exception:
                continue
            if (a in active) and (b in active):
                if (a, b) not in show_links and (b, a) not in show_links:
                    show_links.append((a, b))
        self.los_relation_map.set_links(show_links)
        self.los_map_panel.setEnabled(enabled)
        self.los_map_panel.setStyleSheet(
            "QWidget { background: rgba(255,255,255,210); border: 1px solid rgba(20,20,20,120); border-radius: 6px; }"
            if enabled
            else
            "QWidget { background: rgba(255,255,255,170); border: 1px solid rgba(20,20,20,80); border-radius: 6px; }"
        )
        self.los_map_panel.show()
        self.los_map_panel.raise_()

    def _ensure_custom_los_render_capacity(self):
        n = len(self.custom_los_links)
        while len(self.custom_los_line_items) < n:
            item = gl.GLLinePlotItem(
                pos=np.zeros((2, 3), dtype=float),
                color=(0.0, 0.0, 0.0, 0.35),
                width=1.0,
                antialias=True,
                mode="lines",
            )
            self.view.addItem(item)
            self.custom_los_line_items.append(item)
            lbl = QLabel(self.view)
            lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            lbl.setStyleSheet(
                "QLabel {"
                " font-size: 10pt;"
                " color: #111111;"
                " background-color: rgba(255, 255, 255, 0);"
                " border: none;"
                " padding: 0px;"
                "}"
            )
            lbl.hide()
            self.custom_los_link_labels.append(lbl)

    def _clear_custom_los_links(self):
        self.custom_los_links = []
        self.custom_link_drag_src = None
        self.custom_los_drag_line.setVisible(False)
        for it in self.custom_los_line_items:
            it.setVisible(False)
        for lbl in self.custom_los_link_labels:
            lbl.hide()

    def _on_clear_los_clicked(self):
        self._clear_custom_los_links()
        self.default_step_los_hidden = {}
        self.refresh_ui()

    def _show_guide_dialog(self):
        guide_name_ko = "FA50_GUIDEBOOK.md"
        guide_candidates = [guide_name_ko, "FA50_USER_GUIDE_0.2.15_KO.md", "FA50_USER_GUIDE_0.2.15.md"]
        search_dirs = []
        try:
            search_dirs.append(os.path.dirname(os.path.abspath(sys.executable)))
        except Exception:
            pass
        try:
            search_dirs.append(os.getcwd())
        except Exception:
            pass
        try:
            search_dirs.append(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass
        text = ""
        for d in search_dirs:
            for name in guide_candidates:
                p = os.path.join(d, name)
                if os.path.exists(p):
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            text = f.read().strip()
                        break
                    except Exception:
                        text = ""
            if text:
                break
        if not text:
            text = f"{guide_name_ko} 파일을 찾을 수 없습니다."
        dlg = QDialog(self)
        dlg.setWindowTitle("FA50 사용자 가이드")
        dlg.resize(980, 760)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(10, 10, 10, 10)
        view = QTextEdit(dlg)
        view.setReadOnly(True)
        view.setPlainText(text)
        view.setStyleSheet(
            "QTextEdit {"
            " background: #ffffff;"
            " color: #111111;"
            " border: 1px solid #c7c7c7;"
            " font-size: 10pt;"
            "}"
        )
        lay.addWidget(view)
        row = QHBoxLayout()
        row.addStretch(1)
        btn_close = QPushButton("닫기", dlg)
        btn_close.clicked.connect(dlg.accept)
        row.addWidget(btn_close)
        lay.addLayout(row)
        dlg.exec()

    @staticmethod
    def _pair_key(a: str, b: str) -> frozenset:
        return frozenset([str(a), str(b)])

    @staticmethod
    def _rgba_to_csv(color: Tuple[float, float, float, float]) -> str:
        try:
            return ",".join(f"{float(c):.4f}" for c in color[:4])
        except Exception:
            return ""

    @staticmethod
    def _parse_rgba_csv(s: str) -> Optional[Tuple[float, float, float, float]]:
        try:
            parts = [p.strip() for p in str(s).split(",")]
            if len(parts) != 4:
                return None
            vals = tuple(float(x) for x in parts)
            return (vals[0], vals[1], vals[2], vals[3])
        except Exception:
            return None

    def _custom_link_style_by_source(self, a: str, b: str, src_aid: str) -> Dict[str, object]:
        c = self._aircraft_color(str(src_aid))
        return {"color": (c[0], c[1], c[2], 0.35), "text_color": self._hex_from_rgb01((c[0], c[1], c[2]))}

    def _batch_pairs_for_custom_los(self, src_aid: str, dst_aid: str) -> List[Tuple[str, str]]:
        src = str(src_aid)
        dst = str(dst_aid)
        active = set(self._active_aircraft_ids())
        out: List[Tuple[str, str]] = []
        mk = str(getattr(self, "current_mode_key", "")).strip()
        if mk in {"4vs2", "4vs4"}:
            out.append((src, dst))
        elif (src in TEAM_A) and (dst in TEAM_B):
            out.extend([("#1", dst), ("#2", dst), ("#1", "#2")])
        elif (src in TEAM_B) and (dst in TEAM_A):
            for b in sorted(TEAM_B):
                out.extend([(b, "#1"), (b, "#2")])
            out.append(("#1", "#2"))
        else:
            out.append((src, dst))
        # keep only active and non-self pairs; dedup unordered
        seen = set()
        kept: List[Tuple[str, str]] = []
        for a, b in out:
            if a == b or (a not in active) or (b not in active):
                continue
            k = self._pair_key(a, b)
            if k in seen:
                continue
            seen.add(k)
            kept.append((a, b))
        return kept

    def _on_add_bookmark_clicked(self):
        step_now = int(self.current_step)
        entry = self.step_bookmarks.get(step_now, {})
        default_text = str(entry.get("note", "")) if isinstance(entry, dict) else ""
        text, ok = QInputDialog.getText(
            self,
            "북마크 추가",
            f"Step {step_now} 북마크 내용을 입력하세요",
            text=default_text,
        )
        if not bool(ok):
            return
        note = str(text).strip()
        if note:
            self.step_bookmarks[step_now] = {
                "note": note,
                "camera": self._bookmark_camera_snapshot(),
            }
            self.bookmark_selected_step = int(step_now)
        else:
            self.step_bookmarks.pop(step_now, None)
            if self.bookmark_selected_step == int(step_now):
                self.bookmark_selected_step = None
        self._refresh_bookmark_panel()
        self._position_view_overlays()

    def _bookmark_card_style(self, active: bool) -> str:
        if active:
            return (
                "QPushButton {"
                " text-align: left;"
                " font-size: 8.5pt;"
                " font-weight: 800;"
                " color: #0b1a33;"
                " background: rgba(191,219,254,205);"
                " border: 1px solid rgba(58,110,180,170);"
                " border-radius: 6px;"
                " padding: 4px 8px;"
                "}"
            )
        return (
            "QPushButton {"
            " text-align: left;"
            " font-size: 8.5pt;"
            " font-weight: 700;"
            " color: #0f172a;"
            " background: rgba(255,255,255,240);"
            " border: 1px solid rgba(50,60,90,85);"
            " border-radius: 6px;"
            " padding: 4px 8px;"
            "}"
            "QPushButton:hover { background: rgba(219,234,254,170); }"
        )

    @staticmethod
    def _bookmark_icon_btn_style(tone: str) -> str:
        if tone == "edit":
            return (
                "QPushButton {"
                " font-size: 9pt;"
                " font-weight: 800;"
                " color: #1f4f8a;"
                " background: rgba(255,255,255,220);"
                " border: 1px solid rgba(60,110,170,130);"
                " border-radius: 6px;"
                " padding: 0px;"
                "}"
                "QPushButton:hover { background: rgba(224,236,255,235); }"
            )
        return (
            "QPushButton {"
            " font-size: 9pt;"
            " font-weight: 800;"
            " color: #8a1f1f;"
            " background: rgba(255,255,255,220);"
            " border: 1px solid rgba(170,70,70,130);"
            " border-radius: 6px;"
            " padding: 0px;"
            "}"
            "QPushButton:hover { background: rgba(255,230,230,235); }"
        )

    def _refresh_bookmark_panel(self):
        if not hasattr(self, "bookmark_cards_layout") or (self.bookmark_cards_layout is None):
            return
        while self.bookmark_cards_layout.count():
            item = self.bookmark_cards_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        selected = self.bookmark_selected_step
        if selected is None and int(self.current_step) in self.step_bookmarks:
            selected = int(self.current_step)
            self.bookmark_selected_step = selected
        if not self.step_bookmarks:
            self.bookmark_cards_layout.addStretch(1)
            return
        for step_idx, payload in sorted(self.step_bookmarks.items(), key=lambda kv: int(kv[0])):
            note = ""
            if isinstance(payload, dict):
                note = str(payload.get("note", "")).strip()
            else:
                note = str(payload).strip()
            line = f"STEP {int(step_idx):03d}  |  {note if note else '(no note)'}"
            row = QWidget(self.bookmark_cards)
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(4)
            btn = QPushButton(line, self.bookmark_cards)
            btn.setMinimumHeight(26)
            active = (selected is not None) and (int(step_idx) == int(selected))
            btn.setStyleSheet(self._bookmark_card_style(active))
            btn.setToolTip(f"STEP {int(step_idx)} 이동")
            btn.clicked.connect(lambda _checked=False, s=int(step_idx): self._on_bookmark_card_clicked(s))
            row_lay.addWidget(btn, 1)
            btn_edit = QPushButton("✎", row)
            btn_edit.setFixedSize(24, 24)
            btn_edit.setToolTip(f"STEP {int(step_idx)} 북마크 편집")
            btn_edit.setStyleSheet(self._bookmark_icon_btn_style("edit"))
            btn_edit.clicked.connect(lambda _checked=False, s=int(step_idx): self._on_edit_bookmark_clicked(s))
            row_lay.addWidget(btn_edit, 0)
            btn_del = QPushButton("✕", row)
            btn_del.setFixedSize(24, 24)
            btn_del.setToolTip(f"STEP {int(step_idx)} 북마크 삭제")
            btn_del.setStyleSheet(self._bookmark_icon_btn_style("delete"))
            btn_del.clicked.connect(lambda _checked=False, s=int(step_idx): self._on_delete_bookmark_for_step(s))
            row_lay.addWidget(btn_del, 0)
            self.bookmark_cards_layout.addWidget(row)
        self.bookmark_cards_layout.addStretch(1)

    def _bookmark_camera_snapshot(self) -> Dict[str, float]:
        cam = self._capture_camera_state()
        c = cam.get("center", QVector3D(0.0, 0.0, 0.0))
        return {
            "distance": float(cam.get("distance", self.view.opts.get("distance", 40000.0))),
            "elevation": float(cam.get("elevation", self.view.opts.get("elevation", 22.0))),
            "azimuth": float(cam.get("azimuth", self.view.opts.get("azimuth", 45.0))),
            "center_x": float(c.x()),
            "center_y": float(c.y()),
            "center_z": float(c.z()),
        }

    def _apply_bookmark_camera(self, camera: Optional[Dict[str, object]]):
        if not isinstance(camera, dict):
            return
        try:
            cx = float(camera.get("center_x", float(self.view.opts["center"].x())))
            cy = float(camera.get("center_y", float(self.view.opts["center"].y())))
            cz = float(camera.get("center_z", float(self.view.opts["center"].z())))
            dist = float(camera.get("distance", float(self.view.opts["distance"])))
            elev = float(camera.get("elevation", float(self.view.opts["elevation"])))
            az = float(camera.get("azimuth", float(self.view.opts["azimuth"])))
            self.view.opts["center"] = QVector3D(cx, cy, cz)
            self.view.setCameraPosition(distance=dist, elevation=elev, azimuth=az)
            self._update_view_mode_from_camera()
            self._sync_view_mode_controls()
        except Exception:
            return

    def _go_to_bookmark_step(self, step_idx: int):
        target = max(0, int(step_idx))
        if self.playback_running:
            self._pause_playback()
        self.playback_active = False
        self.view_mode.setCurrentText("Step View")
        self._sync_view_mode_overlay_buttons()
        if self.current_step != target:
            self._replay_to_step(target)
            self.current_step = max(0, min(target, len(self.state_history) - 1))
            self.playback_step_float = float(self.current_step)
            self._restore_cmd_ui_for_step(self.current_step)
            self._restore_hold_ui_for_step(self.current_step)
        payload = self.step_bookmarks.get(int(step_idx), {})
        camera = payload.get("camera", None) if isinstance(payload, dict) else None
        self._apply_bookmark_camera(camera)
        self.refresh_ui()

    def _on_bookmark_card_clicked(self, step_idx: int):
        self.bookmark_selected_step = int(step_idx)
        self._refresh_bookmark_panel()
        self._go_to_bookmark_step(int(step_idx))

    def _on_edit_bookmark_clicked(self, step_idx: int):
        entry = self.step_bookmarks.get(int(step_idx), {})
        default_text = str(entry.get("note", "")) if isinstance(entry, dict) else ""
        text, ok = QInputDialog.getText(
            self,
            "북마크 편집",
            f"Step {int(step_idx)} 북마크 내용을 입력하세요",
            text=default_text,
        )
        if not bool(ok):
            return
        note = str(text).strip()
        if not note:
            self._on_delete_bookmark_for_step(int(step_idx))
            return
        payload = self.step_bookmarks.get(int(step_idx), {})
        cam = payload.get("camera", None) if isinstance(payload, dict) else None
        self.step_bookmarks[int(step_idx)] = {"note": note, "camera": cam}
        self.bookmark_selected_step = int(step_idx)
        self._refresh_bookmark_panel()
        self._position_view_overlays()

    def _on_delete_bookmark_for_step(self, step_idx: int):
        if int(step_idx) not in self.step_bookmarks:
            return
        self.step_bookmarks.pop(int(step_idx), None)
        if self.bookmark_selected_step == int(step_idx):
            self.bookmark_selected_step = None
        self._refresh_bookmark_panel()
        self._position_view_overlays()

    def _on_view_click(self, sx: float, sy: float) -> bool:
        # Arrow selection toggle works in Step View only.
        step_mode_selected = self.view_mode.currentText() == "Step View"
        if (not step_mode_selected) or bool(self.playback_active):
            return False
        best_aid = self._pick_aircraft_by_screen(sx, sy, max_dist_px=26.0)
        if best_aid is None:
            return False
        if self.selected_orbit_aid == best_aid:
            self.selected_orbit_aid = None
            self.selected_ring.setData(pos=np.zeros((0, 3), dtype=float), color=(1.0, 0.92, 0.20, 0.92), width=2.6, antialias=True, mode="lines")
        else:
            self.selected_orbit_aid = best_aid
        self.refresh_ui()
        return True

    def _on_view_right_press(self, sx: float, sy: float) -> bool:
        # Start web-like drag when pressing on a step point (Step/Overview, except playback).
        if self._map_mode_enabled():
            return False
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active)) and (not bool(self.playback_running))
        if step_mode:
            pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=36.0)
        else:
            pick = self._pick_overview_aircraft_point_by_screen(sx, sy, max_dist_px=56.0)
            if pick is None:
                pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=42.0)
        if pick is None:
            return False
        aid, step_idx, pos = pick
        self.custom_link_drag_src = {"aid": aid, "step": int(step_idx), "pos": np.array(pos, dtype=float)}
        seg = np.array([pos, pos], dtype=float)
        self.custom_los_drag_line.setData(pos=seg, color=(0.0, 0.0, 0.0, 0.30), width=1.0, antialias=True, mode="lines")
        self.custom_los_drag_line.setVisible(True)
        return True

    def _on_view_right_move(self, sx: float, sy: float) -> bool:
        if self._map_mode_enabled():
            return False
        if self.custom_link_drag_src is None:
            return False
        src_pos = np.array(self.custom_link_drag_src["pos"], dtype=float)
        src_step = int(self.custom_link_drag_src["step"])
        src_aid = str(self.custom_link_drag_src["aid"])
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active)) and (not bool(self.playback_running))
        end_pos = None
        if step_mode:
            pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=40.0)
        else:
            pick = self._pick_overview_aircraft_point_by_screen(sx, sy, max_dist_px=64.0)
            if pick is None:
                pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=46.0)
        if pick is not None:
            _aid_t, step_t, pos_t = pick
            if int(step_t) == int(self.custom_link_drag_src["step"]):
                end_pos = np.array(pos_t, dtype=float)
        if end_pos is None:
            soft = self._pick_same_step_target_by_proximity(sx, sy, src_step=src_step, src_aid=src_aid, max_dist_px=72.0)
            if soft is not None:
                _aid_t, _step_t, pos_t = soft
                end_pos = np.array(pos_t, dtype=float)
        if end_pos is None:
            end_pos = np.array(src_pos, dtype=float)
        seg = np.array([src_pos, np.array(end_pos, dtype=float)], dtype=float)
        self.custom_los_drag_line.setData(pos=seg, color=(0.0, 0.0, 0.0, 0.30), width=1.0, antialias=True, mode="lines")
        self.custom_los_drag_line.setVisible(True)
        return True

    def _on_view_right_release(self, sx: float, sy: float) -> bool:
        if self._map_mode_enabled():
            return False
        if self.custom_link_drag_src is None:
            return False
        src_aid = str(self.custom_link_drag_src["aid"])
        src_step = int(self.custom_link_drag_src["step"])
        step_mode_selected = self.view_mode.currentText() == "Step View"
        step_mode = step_mode_selected and (not bool(self.playback_active)) and (not bool(self.playback_running))
        origin = "step" if step_mode else "overview"
        if step_mode:
            pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=38.0)
        else:
            pick = self._pick_overview_aircraft_point_by_screen(sx, sy, max_dist_px=60.0)
            if pick is None:
                pick = self._pick_step_point_by_screen(sx, sy, max_dist_px=44.0)
        if (pick is None) or (int(pick[1]) != src_step) or (str(pick[0]) == src_aid):
            pick = self._pick_same_step_target_by_proximity(sx, sy, src_step=src_step, src_aid=src_aid, max_dist_px=80.0)
        if pick is not None:
            dst_aid, dst_step, _dst_pos = pick
            if (int(dst_step) == src_step) and (str(dst_aid) != src_aid):
                batch_pairs = self._batch_pairs_for_custom_los(src_aid, str(dst_aid))
                pair_sets = [self._pair_key(a, b) for (a, b) in batch_pairs]

                def _has_pair_at_step(ps: frozenset) -> bool:
                    return any(
                        int(lk.get("step", -1)) == src_step
                        and str(lk.get("origin", "overview")) == origin
                        and self._pair_key(str(lk.get("a")), str(lk.get("b"))) == ps
                        for lk in self.custom_los_links
                    )
                all_present = bool(batch_pairs) and all(_has_pair_at_step(ps) for ps in pair_sets)
                if all_present:
                    self.custom_los_links = [
                        lk for lk in self.custom_los_links
                        if not (
                            int(lk.get("step", -1)) == src_step
                            and str(lk.get("origin", "overview")) == origin
                            and self._pair_key(str(lk.get("a")), str(lk.get("b"))) in pair_sets
                        )
                    ]
                else:
                    for (a_new, b_new), ps in zip(batch_pairs, pair_sets):
                        if not _has_pair_at_step(ps):
                            st = self._custom_link_style_by_source(a_new, b_new, src_aid)
                            self.custom_los_links.append(
                                {
                                    "a": str(a_new),
                                    "b": str(b_new),
                                    "step": int(src_step),
                                    "origin": origin,
                                    "src_aid": str(src_aid),
                                    "color": st["color"],
                                    "text_color": st["text_color"],
                                }
                            )
        self.custom_link_drag_src = None
        self.custom_los_drag_line.setVisible(False)
        self.refresh_ui()
        return True

    def _grid_extent_target(self) -> float:
        # Default: fixed 100nm x 100nm.
        # DCA setup active: grow extent to include full mission-area footprint.
        if self._has_dca_mission_area():
            pts = np.array(self.dca_mission_rect_pts_ft, dtype=float)
            m = float(np.max(np.abs(pts[:, :2]))) if len(pts) > 0 else (10.0 * NM_TO_FT)
            target = max(1000.0, m + 1000.0)
            target = math.ceil(target / 1000.0) * 1000.0
            return float(target)
        return float(GROUND_MIN_EXTENT_FT)

    def _has_dca_mission_area(self) -> bool:
        pts = getattr(self, "dca_mission_rect_pts_ft", None)
        if not isinstance(pts, np.ndarray) or len(pts) < 5:
            return False
        try:
            w = float(np.linalg.norm(np.array(pts[1], dtype=float) - np.array(pts[0], dtype=float)))
            h = float(np.linalg.norm(np.array(pts[3], dtype=float) - np.array(pts[0], dtype=float)))
            return (w > 1.0) and (h > 1.0)
        except Exception:
            return False

    def _build_mission_xy_grid_points(self, spacing_ft: float) -> np.ndarray:
        if not self._has_dca_mission_area():
            return np.zeros((0, 3), dtype=float)
        pts = np.array(self.dca_mission_rect_pts_ft[:4], dtype=float)
        rear_left = pts[0]
        rear_right = pts[1]
        front_left = pts[3]
        right_vec = rear_right - rear_left
        fwd_vec = front_left - rear_left
        w_len = float(np.linalg.norm(right_vec))
        h_len = float(np.linalg.norm(fwd_vec))
        if w_len <= 1e-6 or h_len <= 1e-6:
            return np.zeros((0, 3), dtype=float)
        right_u = right_vec / w_len
        fwd_u = fwd_vec / h_len
        spacing = max(100.0, float(spacing_ft))
        u_coords = np.arange(0.0, w_len + 0.1, spacing, dtype=float)
        v_coords = np.arange(0.0, h_len + 0.1, spacing, dtype=float)
        lines: List[List[float]] = []
        # Width-wise slices (parallel to forward axis)
        for u in u_coords:
            p0 = rear_left + (right_u * float(u))
            p1 = p0 + (fwd_u * h_len)
            lines.extend([[float(p0[0]), float(p0[1]), 0.0], [float(p1[0]), float(p1[1]), 0.0]])
        # Height-wise slices (parallel to right axis)
        for v in v_coords:
            q0 = rear_left + (fwd_u * float(v))
            q1 = q0 + (right_u * w_len)
            lines.extend([[float(q0[0]), float(q0[1]), 0.0], [float(q1[0]), float(q1[1]), 0.0]])
        return np.array(lines, dtype=float) if lines else np.zeros((0, 3), dtype=float)

    def _build_mission_vertical_grid_points(self, spacing_ft: float) -> np.ndarray:
        if not self._has_dca_mission_area():
            return np.zeros((0, 3), dtype=float)
        pts = np.array(self.dca_mission_rect_pts_ft[:4], dtype=float)
        rear_left = pts[0]
        rear_right = pts[1]
        front_left = pts[3]
        right_vec = rear_right - rear_left
        fwd_vec = front_left - rear_left
        w_len = float(np.linalg.norm(right_vec))
        h_len = float(np.linalg.norm(fwd_vec))
        if w_len <= 1e-6 or h_len <= 1e-6:
            return np.zeros((0, 3), dtype=float)
        right_u = right_vec / w_len
        fwd_u = fwd_vec / h_len
        spacing = max(100.0, float(spacing_ft))
        u_coords = np.arange(0.0, w_len + 0.1, spacing, dtype=float)
        v_coords = np.arange(0.0, h_len + 0.1, spacing, dtype=float)
        lines: List[List[float]] = []
        z0 = 0.0
        z1 = float(GRID_VERTICAL_MAX_FT)
        for u in u_coords:
            for v in v_coords:
                p = rear_left + (right_u * float(u)) + (fwd_u * float(v))
                lines.extend([[float(p[0]), float(p[1]), z0], [float(p[0]), float(p[1]), z1]])
        return np.array(lines, dtype=float) if lines else np.zeros((0, 3), dtype=float)

    def _preferred_yz_plane_x_ft(self, extent: float, spacing: float) -> float:
        spacing_ft = max(100.0, float(spacing))
        target_x = 0.0
        if self._has_dca_mission_area():
            try:
                pts = np.array(self.dca_mission_rect_pts_ft[:4], dtype=float)
                target_x = float(np.mean(pts[:, 0]))
            except Exception:
                target_x = 0.0
        snapped = round(float(target_x) / spacing_ft) * spacing_ft
        return float(max(-float(extent), min(float(extent), snapped)))

    def _build_plane_solid_points(self, plane: str, extent: float, spacing: float):
        pts = []
        if plane == "XY":
            coords = np.arange(-extent, extent + 0.1, spacing, dtype=float)
            for c in coords:
                pts.extend([[-extent, c, 0.0], [extent, c, 0.0], [c, -extent, 0.0], [c, extent, 0.0]])
        elif plane == "XZ":
            x_coords = np.arange(-extent, extent + 0.1, spacing, dtype=float)
            z_coords = np.arange(0.0, float(GRID_VERTICAL_MAX_FT) + 0.1, spacing, dtype=float)
            for z in z_coords:
                pts.extend([[-extent, 0.0, z], [extent, 0.0, z]])
            for x in x_coords:
                pts.extend([[x, 0.0, 0.0], [x, 0.0, float(GRID_VERTICAL_MAX_FT)]])
        else:  # YZ
            x_plane = self._preferred_yz_plane_x_ft(extent=extent, spacing=spacing)
            y_coords = np.arange(-extent, extent + 0.1, spacing, dtype=float)
            z_coords = np.arange(0.0, float(GRID_VERTICAL_MAX_FT) + 0.1, spacing, dtype=float)
            for z in z_coords:
                pts.extend([[x_plane, -extent, z], [x_plane, extent, z]])
            for y in y_coords:
                pts.extend([[x_plane, y, 0.0], [x_plane, y, float(GRID_VERTICAL_MAX_FT)]])
        return np.array(pts, dtype=float) if pts else np.zeros((0, 3), dtype=float)

    def _build_or_update_dashed_grids(self, force: bool = False):
        extent = self._grid_extent_target()
        if not force and abs(extent - self.grid_extent_ft) < 1000.0:
            return
        self.grid_extent_ft = extent
        self._build_or_update_ground_plane()
        for it in self.grid_items:
            self.view.removeItem(it)
        self.grid_items = []
        self.grid_items_by_plane = {}
        if not bool(getattr(self, "grid_enabled", True)):
            return
        # Solid grid on XY/XZ/YZ planes (semi-transparent), user-selectable spacing.
        plane_colors = {
            "XY": (0.58, 0.58, 0.58, 0.34),
            "XZ": (0.58, 0.58, 0.58, 0.24),
            "YZ": (0.58, 0.58, 0.58, 0.24),
        }
        # Always derive spacing from current UI selection so vertical/horizontal grids stay in sync.
        txt = str(self.grid_spacing_combo.currentText()) if hasattr(self, "grid_spacing_combo") else ""
        if "1000" in txt:
            spacing = 1000.0
        elif "6000" in txt:
            spacing = 6000.0
        else:
            spacing = 3000.0
        self.grid_spacing_ft = float(spacing)
        use_mission_only = bool(self._has_dca_mission_area())
        for plane in ["XY", "XZ", "YZ"]:
            if use_mission_only:
                if plane == "XY":
                    pos = self._build_mission_xy_grid_points(spacing_ft=spacing)
                elif plane == "XZ":
                    pos = self._build_plane_solid_points("XZ", extent, spacing=spacing)
                else:
                    # YZ vertical plane snapped to XY lattice for cleaner intersection.
                    pos = self._build_plane_solid_points("YZ", extent, spacing=spacing)
            else:
                pos = self._build_plane_solid_points(plane, extent, spacing=spacing)
            item = gl.GLLinePlotItem(pos=pos, color=plane_colors[plane], width=1.35, antialias=True, mode="lines")
            self.view.addItem(item)
            self.grid_items.append(item)
            self.grid_items_by_plane[plane] = item
        self._apply_grid_visibility_for_view(self._detect_camera_view_kind())

    @staticmethod
    def _angle_diff_deg(a: float, b: float) -> float:
        return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)

    def _detect_camera_view_kind(self) -> str:
        elev = float(self.view.opts.get("elevation", 0.0))
        az = float(self.view.opts.get("azimuth", 0.0)) % 360.0
        if elev >= 80.0:
            return "top"
        plan_axis_left = self._angle_diff_deg(az, 0.0) <= 18.0
        plan_axis_right = self._angle_diff_deg(az, 180.0) <= 18.0
        if abs(elev) <= 8.0 and (plan_axis_left or plan_axis_right):
            return "plan"
        return "free"

    def _apply_grid_visibility_for_view(self, view_kind: str):
        items = getattr(self, "grid_items_by_plane", {})
        if not items:
            return
        if view_kind == "top":
            if "XY" in items:
                items["XY"].setVisible(True)
            if "XZ" in items:
                items["XZ"].setVisible(False)
            if "YZ" in items:
                items["YZ"].setVisible(False)
            return
        if view_kind == "plan":
            if "XY" in items:
                items["XY"].setVisible(False)
            if "XZ" in items:
                items["XZ"].setVisible(False)
            if "YZ" in items:
                items["YZ"].setVisible(True)
            return
        # Free view: keep only Y-axis vertical plane (YZ on x=0) plus XY.
        if "XY" in items:
            items["XY"].setVisible(True)
        if "XZ" in items:
            items["XZ"].setVisible(False)
        if "YZ" in items:
            items["YZ"].setVisible(True)

    def _capture_camera_state(self) -> Dict[str, object]:
        return {
            "distance": float(self.view.opts["distance"]),
            "elevation": float(self.view.opts["elevation"]),
            "azimuth": float(self.view.opts["azimuth"]),
            "center": QVector3D(self.view.opts["center"]),
        }

    def _restore_saved_camera(self):
        if self.saved_camera is None:
            return
        self.view.opts["center"] = self.saved_camera["center"]
        self.view.setCameraPosition(
            distance=float(self.saved_camera["distance"]),
            elevation=float(self.saved_camera["elevation"]),
            azimuth=float(self.saved_camera["azimuth"]),
        )

    def _sync_view_mode_controls(self):
        top_on = (self.camera_mode == "top")
        plan_on = (self.camera_mode == "plan")
        self.top_view_enabled = bool(top_on)
        if hasattr(self, "chk_top_view_overlay") and (self.chk_top_view_overlay is not None):
            self.chk_top_view_overlay.blockSignals(True)
            self.chk_top_view_overlay.setChecked(top_on)
            self.chk_top_view_overlay.blockSignals(False)
        if hasattr(self, "chk_plan_view_overlay") and (self.chk_plan_view_overlay is not None):
            self.chk_plan_view_overlay.blockSignals(True)
            self.chk_plan_view_overlay.setChecked(plan_on)
            self.chk_plan_view_overlay.blockSignals(False)

    def _update_view_mode_from_camera(self):
        kind = self._detect_camera_view_kind()
        az = float(self.view.opts.get("azimuth", 0.0)) % 360.0
        if kind == "top":
            self.camera_mode = "top"
        elif kind == "plan":
            self.camera_mode = "plan"
            self.plan_view_axis_idx = 0 if self._angle_diff_deg(az, 0.0) <= self._angle_diff_deg(az, 180.0) else 1
        else:
            self.camera_mode = "free"
        self._sync_view_mode_controls()
        self._apply_grid_visibility_for_view(kind)

    def _apply_top_view_camera(self):
        self.view.setCameraPosition(elevation=89.5, azimuth=0.0)

    def _apply_plan_view_camera(self):
        # idx=0/1: XZ side views only.
        az = 0.0 if int(self.plan_view_axis_idx) == 0 else 180.0
        self.view.setCameraPosition(elevation=1.5, azimuth=az)

    def _set_camera_mode(self, mode: str):
        mode = str(mode).strip().lower()
        if mode not in {"free", "top", "plan"}:
            return
        if mode == self.camera_mode:
            return
        if self.camera_mode == "free" and mode in {"top", "plan"}:
            self.saved_camera = self._capture_camera_state()
        self.camera_mode = mode
        if mode == "free":
            self._restore_saved_camera()
        elif mode == "top":
            self._apply_top_view_camera()
        elif mode == "plan":
            self._apply_plan_view_camera()
        self._sync_view_mode_controls()
        self.update_ata_labels()

    def _on_top_view_checkbox_toggled(self, checked: bool):
        if checked:
            self._set_camera_mode("top")
        else:
            if self.camera_mode == "top":
                self._set_camera_mode("free")

    def _on_plan_view_checkbox_toggled(self, checked: bool):
        if checked:
            self._set_camera_mode("plan")
        else:
            if self.camera_mode == "plan":
                self._set_camera_mode("free")

    def toggle_top_view(self):
        if self.camera_mode == "top":
            self._set_camera_mode("free")
        else:
            self._set_camera_mode("top")

    def toggle_plan_view(self):
        if self.camera_mode == "plan":
            self.plan_view_axis_idx = (int(self.plan_view_axis_idx) + 1) % 2
            self._apply_plan_view_camera()
            self._sync_view_mode_controls()
            self.update_ata_labels()
        else:
            self._set_camera_mode("plan")

    def refresh_ui(self):
        self.view._clamp_elevation()
        self._update_view_mode_from_camera()
        self._sync_view_mode_overlay_buttons()
        self._sync_compass_overlay()
        self._debug_cmd_g_binding_once()
        self.step_label.setText(f"step: {self.current_step}")
        self._refresh_bookmark_panel()
        self.step_big_label.setText(f"STEP: {self.current_step}")
        if hasattr(self, "step_center_stamp") and (self.step_center_stamp is not None):
            self.step_center_stamp.setText(f"STEP {self.current_step}")
            self.step_center_stamp.adjustSize()
        if hasattr(self, "elapsed_stamp") and (self.elapsed_stamp is not None):
            elapsed_txt = self._format_mmss(self._elapsed_seconds_to_step(self.current_step))
            self.elapsed_stamp.setText(f"TIME {elapsed_txt}")
            self.elapsed_stamp.adjustSize()
            self._position_view_overlays()
        self._hide_all_step_number_labels()
        self._update_dt_lock_ui()
        self._apply_dca_ra_ui_lock()
        self._restore_hold_ui_for_step(self.current_step)
        self._build_or_update_dashed_grids()
        self.step_label_anchor_cache = {}
        step_mode_selected = self.view_mode.currentText() == "Step View"
        overview_like_mode = (not step_mode_selected) or bool(self.playback_active)
        step_mode = not overview_like_mode
        latest_step = max(0, len(self.state_history) - 1)
        overview_force_latest = (not step_mode_selected) and (not bool(self.playback_active)) and (not bool(self.playback_running))
        render_step = int(latest_step if overview_force_latest else self.current_step)
        cur_states_int = self.state_history[render_step]
        cur_states = dict(cur_states_int) if overview_force_latest else self._get_display_states(cur_states_int)
        initial_editable = self.current_step == 0
        self.current_arrow_pick = {}

        active_ids = set(self._active_aircraft_ids())
        if self.selected_orbit_aid is not None and self.selected_orbit_aid not in active_ids:
            self.selected_orbit_aid = None
        for aid in AIRCRAFT_IDS:
            color = self._aircraft_color(aid)
            self.controls[aid].set_participation_enabled(aid in active_ids)
            self.controls[aid].set_initial_editable(initial_editable)
            if aid not in active_ids:
                self._set_mode_visibility(aid, step_mode)
                self.plot_items[aid]["trail_dashed"].setData(pos=np.zeros((0, 3), dtype=float), color=color, width=self._lw(1.0), antialias=True, mode="lines")
                self.plot_items[aid]["trail_recent"].setData(pos=np.zeros((0, 3), dtype=float), color=color, width=self._lw(1.0), antialias=True, mode="lines")
                self.plot_items[aid]["overview_line"].setData(pos=np.zeros((0, 3), dtype=float), color=color, width=self._lw(1.0), antialias=True, mode="lines")
                self.plot_items[aid]["overview_scatter"].setData(pos=np.zeros((0, 3), dtype=float), color=color, size=7.5, pxMode=True)
                self._clear_step_arrow_items(aid)
                self.plot_items[aid]["vertical_markers"].setVisible(False)
                continue
            self._set_mode_visibility(aid, step_mode)
            cur = cur_states[aid]
            cur_step_state = self.state_history[render_step][aid]
            self.controls[aid].set_current_state(float(cur["cas_kt"]), float(cur["z_ft"]), float(cur["hdg_deg"]))
            g_user = float(cur_step_state.get("g_cmd", np.nan))
            g_used = float(cur_step_state.get("g_used", np.nan))
            self.controls[aid].set_applied_g(g_used)
            clamped = bool(cur_step_state.get("clamped", False))
            if clamped and (not np.isnan(g_user)) and (not np.isnan(g_used)) and (g_used < (g_user - 1e-9)):
                self.controls[aid].set_g_limit_indicator(g_user, g_used)
            else:
                self.controls[aid].clear_g_limit_indicator()
            clamp_text = str(cur.get("clamp_note", "")).strip()
            if clamp_text.startswith("G limited:") or clamp_text.startswith("No feasible turn G"):
                self.controls[aid].status.setText(clamp_text)
                self.controls[aid].status.setVisible(True)
            else:
                self.controls[aid].status.setText("")
                self.controls[aid].status.setVisible(False)
            cur_pt = np.array([cur["x_ft"], cur["y_ft"], cur["z_ft"]], dtype=float)
            if step_mode:
                tail_states = self._step_tail_states(aid)
                hist_steps = list(range(self._tail_start_step(), self.current_step))
            else:
                # Overview: always render from step 0 to latest created step.
                # Playback: keep current behavior driven by current_step.
                hist_steps = list(range(0, render_step))
                tail_states = [self.state_history[k][aid] for k in hist_steps]

            # Use local step separation (not global history extent) so tip size stays stable over FWD progression.
            tip_len_by_step: Dict[int, float] = {}
            tip_steps = list(hist_steps) + [render_step]
            prev_tip_len = None
            for k in tip_steps:
                sep_ft = np.nan
                if (k + 1) <= render_step:
                    st_k = self.state_history[k][aid]
                    st_n = self.state_history[k + 1][aid]
                    sep_ft = float(
                        np.linalg.norm(
                            np.array([st_n["x_ft"] - st_k["x_ft"], st_n["y_ft"] - st_k["y_ft"], st_n["z_ft"] - st_k["z_ft"]], dtype=float)
                        )
                    )
                elif k > 0:
                    st_p = self.state_history[k - 1][aid]
                    st_k = self.state_history[k][aid]
                    sep_ft = float(
                        np.linalg.norm(
                            np.array([st_k["x_ft"] - st_p["x_ft"], st_k["y_ft"] - st_p["y_ft"], st_k["z_ft"] - st_p["z_ft"]], dtype=float)
                        )
                    )
                if np.isnan(sep_ft):
                    sep_ft = 800.0
                target_tip_len = float(np.clip(sep_ft * 0.22, 90.0, 220.0))
                if prev_tip_len is None:
                    tip_len = target_tip_len
                else:
                    max_delta = 35.0
                    tip_len = prev_tip_len + float(np.clip(target_tip_len - prev_tip_len, -max_delta, max_delta))
                tip_len_by_step[int(k)] = float(tip_len)
                prev_tip_len = float(tip_len)
            hlen_cur = float(tip_len_by_step.get(render_step, 420.0))

            self._clear_step_arrow_items(aid)
            self.plot_items[aid]["arrows_dashed"].setData(pos=np.zeros((0, 3), dtype=float), color=(0, 0, 0, 0), width=self._lw(1.0), antialias=True, mode="lines")
            self.plot_items[aid]["arrow_current"].setData(pos=np.zeros((0, 3), dtype=float), color=(0, 0, 0, 0), width=self._lw(1.0), antialias=True, mode="lines")

            if step_mode:
                # Pass A: previous steps are tip-only (no shaft).
                for step_idx, st in zip(hist_steps, tail_states):
                    st_pt = np.array([st["x_ft"], st["y_ft"], st["z_ft"]], dtype=float)
                    next_pt = None
                    if (step_idx + 1) <= self.current_step:
                        nst = self.state_history[step_idx + 1][aid]
                        next_pt = np.array([nst["x_ft"], nst["y_ft"], nst["z_ft"]], dtype=float)
                    turn_dir = self._turn_dir_for_state(aid, step_idx)
                    hlen_hist = float(tip_len_by_step.get(step_idx, 420.0))
                    self._draw_arrow_dashed(aid, st_pt, st["hdg_deg"], float(st.get("pitch_deg", 0.0)), hlen_hist, turn_dir, next_pt, (color[0], color[1], color[2], 0.58))
                    _tail_l, _apex_l, _wing_l_l, _wing_r_l = self._attached_tip_geometry(
                        st_pt,
                        float(st.get("hdg_deg", 0.0)),
                        float(st.get("pitch_deg", 0.0)),
                        hlen_hist,
                        next_pos=next_pt,
                    )
                    self.step_label_anchor_cache[(aid, int(step_idx))] = np.array(_apex_l, dtype=float)
                    self._draw_step_number_attached(aid, int(step_idx), np.array(_apex_l, dtype=float), float(st.get("hdg_deg", 0.0)), float(hlen_hist), (color[0], color[1], color[2], 0.92))

                # Pass B: current step only is tip-only.
                cur_turn = self._turn_dir_for_state(aid, render_step)
                next_cur = None
                if (render_step + 1) < len(self.state_history):
                    nst_cur = self.state_history[render_step + 1][aid]
                    next_cur = np.array([nst_cur["x_ft"], nst_cur["y_ft"], nst_cur["z_ft"]], dtype=float)
                self._draw_arrow_solid(aid, cur_pt, cur["hdg_deg"], float(cur.get("pitch_deg", 0.0)), hlen_cur, cur_turn, next_cur, (color[0], color[1], color[2], 1.0))
                tip_base_pick, shaft_end_pick, _wing_l_pick, _wing_r_pick = self._attached_tip_geometry(
                    cur_pt,
                    cur["hdg_deg"],
                    float(cur.get("pitch_deg", 0.0)),
                    hlen_cur,
                    next_pos=next_cur,
                )
                self.step_label_anchor_cache[(aid, int(render_step))] = np.array(shaft_end_pick, dtype=float)
                self._draw_step_number_attached(aid, int(render_step), np.array(shaft_end_pick, dtype=float), float(cur.get("hdg_deg", 0.0)), float(hlen_cur), (color[0], color[1], color[2], 1.0))
                self.current_arrow_pick[aid] = {
                    "start": tip_base_pick,
                    "apex": shaft_end_pick,
                    "center": 0.5 * (tip_base_pick + shaft_end_pick),
                    "pos": cur_pt,
                }
            else:
                # Overview/playback: draw step-separated arrow heads instead of point markers.
                # Strongly separate arrow layer from overview trail layer to avoid
                # apparent per-step shaft drop on some aircraft/colors (e.g. #4 green).
                z_lift_ft = 120.0
                for step_idx, st in zip(hist_steps, tail_states):
                    st_pt = np.array([st["x_ft"], st["y_ft"], st["z_ft"]], dtype=float)
                    st_pt[2] = float(st_pt[2]) + z_lift_ft
                    next_pt = None
                    sep_ft_hist = np.nan
                    if (step_idx + 1) <= render_step:
                        nst = self.state_history[step_idx + 1][aid]
                        next_pt = np.array([nst["x_ft"], nst["y_ft"], nst["z_ft"]], dtype=float)
                        next_pt[2] = float(next_pt[2]) + z_lift_ft
                        sep_ft_hist = float(np.linalg.norm(next_pt - st_pt))
                    turn_dir = self._turn_dir_for_state(aid, step_idx)
                    hlen_hist = float(tip_len_by_step.get(step_idx, 420.0))
                    draw_hdg = self._overview_arrow_hdg_deg(aid, int(step_idx), float(st.get("hdg_deg", 0.0)))
                    if (next_pt is not None) and np.isfinite(sep_ft_hist) and (sep_ft_hist > 1e-6):
                        # Use true step segment as shaft so each step contributes exactly one visible shaft.
                        self._draw_overview_step_arrow_from_pair(
                            aid,
                            st_pt,
                            next_pt,
                            turn_dir,
                            (color[0], color[1], color[2], 0.58),
                            self._lw(3.60),
                        )
                        _apex_l = np.array(next_pt, dtype=float)
                    else:
                        self._draw_arrow_dashed(
                            aid,
                            st_pt,
                            draw_hdg,
                            float(st.get("pitch_deg", 0.0)),
                            hlen_hist,
                            turn_dir,
                            None,
                            (color[0], color[1], color[2], 0.58),
                        )
                        _tail_l, _apex_l, _wing_l_l, _wing_r_l = self._attached_tip_geometry(
                            st_pt,
                            float(draw_hdg),
                            float(st.get("pitch_deg", 0.0)),
                            hlen_hist,
                            next_pos=None,
                        )
                    self.step_label_anchor_cache[(aid, int(step_idx))] = np.array(_apex_l, dtype=float)
                    self._draw_step_number_attached(aid, int(step_idx), np.array(_apex_l, dtype=float), float(draw_hdg), float(hlen_hist), (color[0], color[1], color[2], 0.90))

                cur_turn = self._turn_dir_for_state(aid, render_step)
                next_cur = None
                cur_pt_over = np.array(cur_pt, dtype=float)
                cur_pt_over[2] = float(cur_pt_over[2]) + z_lift_ft
                sep_ft_cur = np.nan
                if (render_step + 1) < len(self.state_history):
                    nst_cur = self.state_history[render_step + 1][aid]
                    next_cur = np.array([nst_cur["x_ft"], nst_cur["y_ft"], nst_cur["z_ft"]], dtype=float)
                    next_cur[2] = float(next_cur[2]) + z_lift_ft
                    sep_ft_cur = float(np.linalg.norm(next_cur - cur_pt_over))
                hlen_cur_draw = float(hlen_cur)
                if np.isfinite(sep_ft_cur):
                    hlen_cur_draw = min(hlen_cur_draw, max(55.0, 0.72 * sep_ft_cur))
                prev_cur = None
                if render_step > 0:
                    pst = self.state_history[render_step - 1][aid]
                    prev_cur = np.array([pst["x_ft"], pst["y_ft"], pst["z_ft"]], dtype=float)
                    prev_cur[2] = float(prev_cur[2]) + z_lift_ft
                if prev_cur is not None:
                    self._draw_overview_step_arrow_from_pair(
                        aid,
                        prev_cur,
                        cur_pt_over,
                        cur_turn,
                        (color[0], color[1], color[2], 0.98),
                        self._lw(5.20),
                    )
                    _apex_c = np.array(cur_pt_over, dtype=float)
                else:
                    self._draw_arrow_solid(aid, cur_pt_over, cur["hdg_deg"], float(cur.get("pitch_deg", 0.0)), hlen_cur_draw, cur_turn, next_cur, (color[0], color[1], color[2], 0.98))
                    _tail_c, _apex_c, _wing_l_c, _wing_r_c = self._attached_tip_geometry(
                        cur_pt_over,
                        float(cur.get("hdg_deg", 0.0)),
                        float(cur.get("pitch_deg", 0.0)),
                        hlen_cur_draw,
                        next_pos=next_cur,
                    )
                self.step_label_anchor_cache[(aid, int(render_step))] = np.array(_apex_c, dtype=float)
                self._draw_step_number_attached(aid, int(render_step), np.array(_apex_c, dtype=float), float(cur.get("hdg_deg", 0.0)), float(hlen_cur_draw), (color[0], color[1], color[2], 0.95))

            if step_mode:
                path_dash_parts = []
                path_pts = [np.array([st["x_ft"], st["y_ft"], st["z_ft"]], dtype=float) for st in tail_states] + [cur_pt]
                if (self.current_step == 0) and (len(path_pts) < 2):
                    path_pts = [self._step0_virtual_prev_point(aid, cur), cur_pt]
                if len(path_pts) >= 3:
                    for i in range(len(path_pts) - 2):
                        seg = self._build_dashed_line_points(path_pts[i], path_pts[i + 1], 200.0, 200.0)
                        if len(seg) > 0:
                            path_dash_parts.append(seg)
                dash_path = np.vstack(path_dash_parts) if path_dash_parts else np.zeros((0, 3), dtype=float)
                self.plot_items[aid]["trail_dashed"].setData(
                    pos=dash_path,
                    color=(color[0], color[1], color[2], 0.52),
                    width=self._lw(2.52),
                    antialias=True,
                    mode="lines",
                )

                if len(path_pts) >= 2:
                    recent = np.vstack([path_pts[-2], path_pts[-1]])
                else:
                    recent = np.vstack([cur_pt, cur_pt])
                self.plot_items[aid]["trail_recent"].setData(
                    pos=recent,
                    color=(color[0], color[1], color[2], 0.92),
                    width=self._lw(4.62),
                    antialias=True,
                    mode="lines",
                )
            else:
                full_pts = np.array(
                    [
                        [self.state_history[s][aid]["x_ft"], self.state_history[s][aid]["y_ft"], self.state_history[s][aid]["z_ft"]]
                        for s in range(0, render_step + 1)
                    ],
                    dtype=float,
                )
                # Push overview trail slightly below arrows in Z so shafts remain visible.
                full_pts[:, 2] = full_pts[:, 2] - 80.0
                if len(full_pts) == 0:
                    full_pts = np.array([cur_pt], dtype=float)
                elif float(np.linalg.norm(full_pts[-1] - cur_pt)) > 1e-6:
                    full_pts = np.vstack([full_pts, cur_pt])
                if len(full_pts) >= 2:
                    self.plot_items[aid]["overview_line"].setData(pos=full_pts, color=(color[0], color[1], color[2], 0.40), width=self._lw(1.2), antialias=True)
                else:
                    self.plot_items[aid]["overview_line"].setData(pos=np.vstack([full_pts, full_pts]), color=(color[0], color[1], color[2], 0.40), width=self._lw(1.2), antialias=True)
                self.plot_items[aid]["overview_scatter"].setData(pos=np.zeros((0, 3), dtype=float), color=np.zeros((0, 4), dtype=float), size=0.0, pxMode=True)

            marker_pts = self._vertical_transition_markers(aid, step_mode, hlen_cur)
            self.plot_items[aid]["vertical_markers"].setData(
                pos=marker_pts,
                color=(color[0], color[1], color[2], 0.60),
                width=self._lw(1.4),
                antialias=True,
                mode="lines",
            )
            self.plot_items[aid]["vertical_markers"].setVisible(len(marker_pts) > 0)
            # Keep compact one-line G-limit status visible when clamping occurs.
        if step_mode and (self.selected_orbit_aid in self.current_arrow_pick):
            sel = self.current_arrow_pick[self.selected_orbit_aid]
            center = np.array(sel["center"], dtype=float)
            ring_pts = self._circle_points(center, radius_ft=950.0, n=56)
            self.selected_ring.setData(
                pos=ring_pts,
                color=(1.0, 0.92, 0.20, 0.92),
                width=2.6,
                antialias=True,
                mode="lines",
            )
            self.view.opts["center"] = QVector3D(float(center[0]), float(center[1]), float(center[2]))
            self._set_pivot_marker(center)
        else:
            self.selected_ring.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(1.0, 0.92, 0.20, 0.92),
                width=2.6,
                antialias=True,
                mode="lines",
            )
        if self.dca_be_center_ft is not None:
            outer_r_ft = 0.5 * float(self.dca_be_outer_diam_ft)
            inner_r_ft = 0.5 * float(self.dca_be_inner_diam_ft)
            outer_pts = self._circle_points(self.dca_be_center_ft, radius_ft=outer_r_ft, n=72)
            inner_pts = self._circle_points(self.dca_be_center_ft, radius_ft=inner_r_ft, n=72)
            self.dca_be_outer_ring.setData(
                pos=outer_pts,
                color=(0.10, 0.45, 0.98, 0.95),
                width=2.2,
                antialias=True,
                mode="lines",
            )
            self.dca_be_inner_ring.setData(
                pos=inner_pts,
                color=(0.10, 0.45, 0.98, 0.95),
                width=2.2,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_be_outer_ring.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.10, 0.45, 0.98, 0.95),
                width=2.2,
                antialias=True,
                mode="lines",
            )
            self.dca_be_inner_ring.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.10, 0.45, 0.98, 0.95),
                width=2.2,
                antialias=True,
                mode="lines",
            )
        if self.dca_asset_center_ft is not None:
            self.dca_asset_disc.setData(
                pos=np.array([self.dca_asset_center_ft], dtype=float),
                color=(1.0, 0.0, 0.0, 1.0),
                size=np.array([float(self.dca_asset_diam_ft)], dtype=float),
                pxMode=False,
            )
        else:
            self.dca_asset_disc.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(1.0, 0.0, 0.0, 1.0),
                size=0.0,
                pxMode=False,
            )
        if (self.dca_ra_zone_center_ft is not None) and (str(getattr(self, "dca_ra_zone_mode", "radius")).lower() == "radius"):
            zone_r_ft = max(50.0, float(self.dca_ra_zone_radius_nm) * NM_TO_FT)
            zone_pts = self._circle_points(self.dca_ra_zone_center_ft, radius_ft=zone_r_ft, n=72)
            self.dca_ra_zone_ring.setData(
                pos=zone_pts,
                color=(0.95, 0.12, 0.12, 0.95),
                width=1.8,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_ra_zone_ring.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.95, 0.12, 0.12, 0.95),
                width=1.8,
                antialias=True,
                mode="lines",
            )
        if (
            str(getattr(self, "dca_ra_zone_mode", "radius")).lower() == "line"
            and isinstance(self.dca_ra_line_pts_ft, np.ndarray)
            and (len(self.dca_ra_line_pts_ft) >= 2)
        ):
            self.dca_ra_line.setData(
                pos=np.array(self.dca_ra_line_pts_ft, dtype=float),
                color=(0.95, 0.12, 0.12, 0.95),
                width=2.1,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_ra_line.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.95, 0.12, 0.12, 0.95),
                width=2.1,
                antialias=True,
                mode="lines",
            )
        if isinstance(self.dca_mission_rect_pts_ft, np.ndarray) and (len(self.dca_mission_rect_pts_ft) >= 5):
            self.dca_mission_rect.setData(
                pos=np.array(self.dca_mission_rect_pts_ft, dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=2.0,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_mission_rect.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=2.0,
                antialias=True,
                mode="lines",
            )
        if isinstance(self.dca_mission_diag1_pts_ft, np.ndarray) and (len(self.dca_mission_diag1_pts_ft) >= 2):
            self.dca_mission_diag1.setData(
                pos=np.array(self.dca_mission_diag1_pts_ft, dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=1.4,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_mission_diag1.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=1.4,
                antialias=True,
                mode="lines",
            )
        if isinstance(self.dca_mission_diag2_pts_ft, np.ndarray) and (len(self.dca_mission_diag2_pts_ft) >= 2):
            self.dca_mission_diag2.setData(
                pos=np.array(self.dca_mission_diag2_pts_ft, dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=1.4,
                antialias=True,
                mode="lines",
            )
        else:
            self.dca_mission_diag2.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(1.0, 0.92, 0.10, 0.95),
                width=1.4,
                antialias=True,
                mode="lines",
            )
        if bool(getattr(self, "dca_cap_pair_enabled_default", False)) and isinstance(self.dca_cap_front_split_centers_ft, np.ndarray) and isinstance(self.dca_cap_rear_split_centers_ft, np.ndarray) and (len(self.dca_cap_front_split_centers_ft) >= 2) and (len(self.dca_cap_rear_split_centers_ft) >= 2):
            cap_pts = np.vstack([np.array(self.dca_cap_front_split_centers_ft, dtype=float), np.array(self.dca_cap_rear_split_centers_ft, dtype=float)])
            self.dca_cap_split_dots.setData(
                pos=np.array(cap_pts, dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=np.full((len(cap_pts),), float(self.dca_asset_diam_ft) * 0.5, dtype=float),
                pxMode=False,
            )
        else:
            self.dca_cap_split_dots.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=0.0,
                pxMode=False,
            )
        if (self.dca_cap_front_center_ft is not None) and (not bool(getattr(self, "dca_cap_pair_enabled_default", False))):
            self.dca_cap_front_dot.setData(
                pos=np.array([self.dca_cap_front_center_ft], dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=np.array([float(self.dca_asset_diam_ft) * 0.5], dtype=float),
                pxMode=False,
            )
        else:
            self.dca_cap_front_dot.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=0.0,
                pxMode=False,
            )
        if (self.dca_cap_rear_center_ft is not None) and (not bool(getattr(self, "dca_cap_pair_enabled_default", False))):
            self.dca_cap_rear_dot.setData(
                pos=np.array([self.dca_cap_rear_center_ft], dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=np.array([float(self.dca_asset_diam_ft) * 0.5], dtype=float),
                pxMode=False,
            )
        else:
            self.dca_cap_rear_dot.setData(
                pos=np.zeros((0, 3), dtype=float),
                color=(0.0, 0.0, 0.0, 1.0),
                size=0.0,
                pxMode=False,
            )
        if isinstance(self.dca_hmrl_pts_ft, np.ndarray) and (len(self.dca_hmrl_pts_ft) >= 2):
            self.dca_hmrl_line.setData(pos=np.array(self.dca_hmrl_pts_ft, dtype=float), color=(0.95, 0.12, 0.12, 0.95), width=2.0, antialias=True, mode="lines")
        else:
            self.dca_hmrl_line.setData(pos=np.zeros((0, 3), dtype=float), color=(0.95, 0.12, 0.12, 0.95), width=2.0, antialias=True, mode="lines")
        if isinstance(self.dca_ldez_pts_ft, np.ndarray) and (len(self.dca_ldez_pts_ft) >= 2):
            self.dca_ldez_line.setData(pos=np.array(self.dca_ldez_pts_ft, dtype=float), color=(0.0, 0.95, 0.95, 0.95), width=2.0, antialias=True, mode="lines")
        else:
            self.dca_ldez_line.setData(pos=np.zeros((0, 3), dtype=float), color=(0.0, 0.95, 0.95, 0.95), width=2.0, antialias=True, mode="lines")
        if isinstance(self.dca_hdez_pts_ft, np.ndarray) and (len(self.dca_hdez_pts_ft) >= 2):
            self.dca_hdez_line.setData(pos=np.array(self.dca_hdez_pts_ft, dtype=float), color=(0.0, 0.95, 0.95, 0.95), width=2.0, antialias=True, mode="lines")
        else:
            self.dca_hdez_line.setData(pos=np.zeros((0, 3), dtype=float), color=(0.0, 0.95, 0.95, 0.95), width=2.0, antialias=True, mode="lines")
        if isinstance(self.dca_commit_pts_ft, np.ndarray) and (len(self.dca_commit_pts_ft) >= 2):
            self.dca_commit_line.setData(pos=np.array(self.dca_commit_pts_ft, dtype=float), color=(0.95, 0.12, 0.12, 0.95), width=2.0, antialias=True, mode="lines")
        else:
            self.dca_commit_line.setData(pos=np.zeros((0, 3), dtype=float), color=(0.95, 0.12, 0.12, 0.95), width=2.0, antialias=True, mode="lines")
        self._update_dca_point_labels()
        los_states = cur_states_int if bool(getattr(self, "playback_running", False)) else cur_states
        self.update_ata_labels(cur_states=los_states, step_mode=step_mode_selected, verbose=False)
        self._refresh_relation_map_overlay()
    def export_csv(self):
        if len(self.state_history) <= 1:
            QMessageBox.information(self, "Info", "No state history to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export States CSV", "fa50_states.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            rows = []
            t = 0.0
            for step in range(self.current_step):
                pkg = self.step_cmds.get(step)
                if pkg is None:
                    continue
                dt = float(pkg["_dt"])
                t += dt
                for aid in AIRCRAFT_IDS:
                    st = self.state_history[step + 1][aid]
                    rows.append(
                        {
                            "step": step + 1,
                            "t_sec": t,
                            "id": aid,
                            "x_ft": st["x_ft"],
                            "y_ft": st["y_ft"],
                            "z_ft": st["z_ft"],
                            "cas_kt": st["cas_kt"],
                            "tas_kt": st["tas_kt"],
                            "hdg_deg": st["hdg_deg"],
                            "power": st["power"],
                            "turn": st["turn"],
                            "turn_cmd_user": st.get("turn_cmd_user", st["turn"]),
                            "turn_effective": st.get("turn_effective", st["turn"]),
                            "g_cmd": st["g_cmd"],
                            "g_cmd_effective": st.get("g_cmd_effective", st["g_cmd"]),
                            "g_used": st["g_used"],
                            "g_max": st.get("g_max", np.nan),
                            "pull_mode": st.get("pull_mode", "NONE"),
                            "bank_cmd_user": st.get("bank_cmd_user", np.nan),
                            "bank_used": st.get("bank_used", st.get("bank_deg", np.nan)),
                            "ps_fps": st["ps_fps"],
                            "ps_primary": st.get("ps_primary", np.nan),
                            "ps_fallback_1g_straight": st.get("ps_fallback_1g_straight", np.nan),
                            "ps_final": st.get("ps_final", st["ps_fps"]),
                            "cas_before": st["cas_before"],
                            "dV_ktsps": st["dV_ktsps"],
                            "cas_after": st["cas_after"],
                            "tan_bank": st.get("tan_bank", np.nan),
                            "bank_deg": st.get("bank_deg", np.nan),
                            "radius_nm": st.get("radius_nm", np.nan),
                            "radius_ft": st.get("radius_ft", np.nan),
                            "turn_rate_degps": st.get("turn_rate_degps", np.nan),
                            "clamp_note": st.get("clamp_note", ""),
                            "turn_note": st.get("turn_note", ""),
                            "clamped": st["clamped"],
                            "feasible": st["feasible"],
                        }
                    )
            fieldnames = list(rows[0].keys()) if rows else ["step", "t_sec", "id"]
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            QMessageBox.information(self, "Done", f"Saved to: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed: {e}")

    def export_scenario_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Scenario CSV", "fa50_scenario.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            rows = []
            rows.append({"row_type": "META", "key": "fixed_dt", "value": float(self.fixed_dt if self.fixed_dt is not None else self.dt_sec.value())})
            rows.append({"row_type": "META", "key": "current_step", "value": int(self.current_step)})
            rows.append({"row_type": "META", "key": "mode_key", "value": str(self.current_mode_key)})
            rows.append({"row_type": "META", "key": "setup_key", "value": str(self.current_setup_key)})
            rows.append({"row_type": "META", "key": "active_ids", "value": ",".join(self._active_aircraft_ids())})
            rows.append({"row_type": "META", "key": "enabled_ids", "value": ",".join(self._enabled_aircraft_ids_for_save())})
            dca_enabled = bool(self._is_dca_active())
            rows.append({"row_type": "META", "key": "dca_enabled", "value": int(dca_enabled)})
            rows.append({"row_type": "META", "key": "dca_be_bearing_deg", "value": float(self.dca_be_default_bearing_deg)})
            rows.append({"row_type": "META", "key": "dca_be_range_nm", "value": float(self.dca_be_default_range_nm)})
            rows.append({"row_type": "META", "key": "dca_asset_bearing_from_be_deg", "value": float(self.dca_asset_default_bearing_from_be_deg)})
            rows.append({"row_type": "META", "key": "dca_asset_range_from_be_nm", "value": float(self.dca_asset_default_range_from_be_nm)})
            rows.append({"row_type": "META", "key": "dca_asset_same_as_be", "value": int(bool(self.dca_asset_same_as_be_default))})
            rows.append({"row_type": "META", "key": "dca_ba_from_asset_nm", "value": float(self.dca_ba_from_asset_nm_default)})
            rows.append({"row_type": "META", "key": "dca_ra_from_asset_nm", "value": float(self.dca_ra_from_asset_nm_default)})
            rows.append({"row_type": "META", "key": "dca_ba_heading_deg", "value": float(self.dca_ba_heading_deg_default)})
            rows.append({"row_type": "META", "key": "dca_ra_heading_deg", "value": float(self.dca_ra_heading_deg_default)})
            rows.append({"row_type": "META", "key": "dca_ra_zone_radius_nm", "value": float(self.dca_ra_zone_radius_nm_default)})
            rows.append({"row_type": "META", "key": "dca_ra_line_forward_nm", "value": float(self.dca_ra_line_forward_nm_default)})
            rows.append({"row_type": "META", "key": "dca_ra_zone_mode", "value": str(self.dca_ra_zone_mode_default)})
            rows.append({"row_type": "META", "key": "dca_mission_width_nm", "value": float(self.dca_mission_width_nm_default)})
            rows.append({"row_type": "META", "key": "dca_mission_height_nm", "value": float(self.dca_mission_height_nm_default)})
            rows.append({"row_type": "META", "key": "dca_cap_front_nm", "value": float(self.dca_cap_front_nm_default)})
            rows.append({"row_type": "META", "key": "dca_cap_rear_nm", "value": float(self.dca_cap_rear_nm_default)})
            rows.append({"row_type": "META", "key": "dca_cap_pair_enabled", "value": int(bool(self.dca_cap_pair_enabled_default))})
            rows.append({"row_type": "META", "key": "dca_cap_pair_half_sep_nm", "value": float(self.dca_cap_pair_half_sep_nm_default)})
            rows.append({"row_type": "META", "key": "dca_hmrl_nm", "value": float(self.dca_hmrl_nm_default)})
            rows.append({"row_type": "META", "key": "dca_ldez_nm", "value": float(self.dca_ldez_nm_default)})
            rows.append({"row_type": "META", "key": "dca_hdez_nm", "value": float(self.dca_hdez_nm_default)})
            rows.append({"row_type": "META", "key": "dca_commit_nm", "value": float(self.dca_commit_nm_default)})
            for aid in AIRCRAFT_IDS:
                rows.append({"row_type": "META", "key": f"color_{aid.replace('#', '')}", "value": str(self.controls[aid].current_color_key())})
            init_states = self.state_history[0] if self.state_history else {}
            for aid in AIRCRAFT_IDS:
                ac = self.controls[aid]
                st0 = init_states.get(aid, {})
                alt0 = float(st0.get("z_ft", ac.alt_ft.value()))
                hdg0 = float(st0.get("hdg_deg", ac.hdg_deg.value()))
                cas0 = float(st0.get("cas_kt", ac.cas_kt.value()))
                rows.append({"row_type": "INIT", "id": aid, "field": "range_nm", "value": float(ac.range_nm.value())})
                rows.append({"row_type": "INIT", "id": aid, "field": "bearing_deg", "value": float(ac.bearing_deg.value())})
                rows.append({"row_type": "INIT", "id": aid, "field": "alt_ft", "value": alt0})
                rows.append({"row_type": "INIT", "id": aid, "field": "hdg_deg", "value": hdg0})
                rows.append({"row_type": "INIT", "id": aid, "field": "cas_kt", "value": cas0})
            for step, pkg in sorted(self.step_cmds.items()):
                cmds = pkg.get("cmds", {})
                rows.append({"row_type": "META_STEP", "step": int(step), "dt": float(pkg.get("_dt", self.fixed_dt if self.fixed_dt is not None else 1.0))})
                for aid in AIRCRAFT_IDS:
                    c = cmds.get(aid, self._default_cmd_for_aircraft())
                    rows.append(
                        {
                            "row_type": "CMD",
                            "step": int(step),
                            "id": aid,
                            "turn": c.get("turn", "S"),
                            "power": c.get("power", "M"),
                            "g_cmd": float(c.get("g_cmd", 1.0)),
                            "g_use_max": int(bool(c.get("g_use_max", False))),
                            "pitch_deg": float(c.get("pitch_deg", 0.0)),
                            "pitch_hold": int(bool(c.get("pitch_hold", False))),
                            "pitch_user_set": int(bool(c.get("pitch_user_set", False))),
                            "bank_deg": float(c.get("bank_deg", 0.0)),
                            "bank_user_set": int(bool(c.get("bank_user_set", False))),
                            "pull_mode": str(c.get("pull_mode", "NONE")),
                            "level_hold": int(bool(c.get("level_hold", False))),
                        }
                    )
            for step, hold_map in sorted(self.hold_state_by_step.items()):
                if isinstance(hold_map, dict):
                    for aid in AIRCRAFT_IDS:
                        rows.append({"row_type": "HOLD", "step": int(step), "id": aid, "hold": bool(hold_map.get(aid, False))})
                else:
                    # Backward compatibility path.
                    for aid in AIRCRAFT_IDS:
                        rows.append({"row_type": "HOLD", "step": int(step), "id": aid, "hold": bool(hold_map)})
            for link in self.custom_los_links:
                try:
                    a = str(link.get("a", "")).strip()
                    b = str(link.get("b", "")).strip()
                    s = int(link.get("step", -1))
                    color = link.get("color", None)
                    text_color = link.get("text_color", None)
                except Exception:
                    continue
                if (a in AIRCRAFT_IDS) and (b in AIRCRAFT_IDS) and (a != b) and (s >= 0):
                    rows.append(
                        {
                            "row_type": "CUSTOM_LOS",
                            "a": a,
                            "b": b,
                            "step": int(s),
                            "src_aid": str(link.get("src_aid", "")).strip(),
                            "color_rgba": self._rgba_to_csv(color) if color is not None else "",
                            "text_color": str(text_color) if text_color is not None else "",
                        }
                    )
            for step_idx, payload in sorted(self.step_bookmarks.items(), key=lambda kv: int(kv[0])):
                note = ""
                cam = {}
                if isinstance(payload, dict):
                    note = str(payload.get("note", "")).strip()
                    cam = payload.get("camera", {}) if isinstance(payload.get("camera", {}), dict) else {}
                else:
                    note = str(payload).strip()
                rows.append(
                    {
                        "row_type": "BOOKMARK",
                        "step": int(step_idx),
                        "note": str(note),
                        "cam_distance": float(cam.get("distance", np.nan)) if cam else np.nan,
                        "cam_elevation": float(cam.get("elevation", np.nan)) if cam else np.nan,
                        "cam_azimuth": float(cam.get("azimuth", np.nan)) if cam else np.nan,
                        "cam_center_x": float(cam.get("center_x", np.nan)) if cam else np.nan,
                        "cam_center_y": float(cam.get("center_y", np.nan)) if cam else np.nan,
                        "cam_center_z": float(cam.get("center_z", np.nan)) if cam else np.nan,
                    }
                )
            fieldnames = sorted({k for row in rows for k in row.keys()})
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
            QMessageBox.information(self, "Done", f"Saved to: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed: {e}")

    def import_scenario_csv(self) -> bool:
        path, _ = QFileDialog.getOpenFileName(self, "Import Scenario CSV", "", "CSV Files (*.csv)")
        if not path:
            return False
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.playback_running = False
            self.playback_timer.stop()
            self._sync_play_button_icon()
            self._set_inputs_enabled(True)

            self.step_cmds.clear()
            self.hold_state_by_step.clear()
            self.lock_speed_value_by_step.clear()
            self.lock_ps_value_by_step.clear()
            self.warning_shown = {"impl": False, "mach": False}
            self._clear_custom_los_links()
            self.step_bookmarks = {}
            self.bookmark_selected_step = None

            def _f(x, default=0.0):
                try:
                    if x is None or x == "":
                        return float(default)
                    return float(x)
                except Exception:
                    return float(default)

            def _i(x, default=0):
                try:
                    if x is None or x == "":
                        return int(default)
                    return int(float(x))
                except Exception:
                    return int(default)

            def _b(x):
                if isinstance(x, bool):
                    return x
                s = str(x).strip().lower()
                return s in {"1", "true", "yes", "y", "on"}

            meta_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "META"]
            meta_map: Dict[str, str] = {}
            for r in meta_rows:
                k = str(r.get("key", "")).strip()
                if k:
                    meta_map[k] = str(r.get("value", ""))

            mode_from_file = str(meta_map.get("mode_key", "")).strip()
            setup_from_file = str(meta_map.get("setup_key", "")).strip()
            if mode_from_file not in MODE_KEYS:
                raw_active = str(meta_map.get("active_ids", "")).strip()
                parsed_active = [x.strip() for x in raw_active.split(",") if x.strip() in AIRCRAFT_IDS]
                active_key = tuple(parsed_active)
                mode_by_active = {
                    tuple(MODE_ACTIVE_IDS["1vs1"]): "1vs1",
                    tuple(MODE_ACTIVE_IDS["2vs1"]): "2vs1",
                    tuple(MODE_ACTIVE_IDS["2vs2"]): "2vs2",
                    tuple(MODE_ACTIVE_IDS["4vs2"]): "4vs2",
                    tuple(MODE_ACTIVE_IDS["4vs4"]): "4vs4",
                }
                mode_from_file = mode_by_active.get(active_key, mode_from_file)
            if mode_from_file in MODE_KEYS:
                self._suppress_dca_prompt = True
                try:
                    self.apply_startup_profile(mode_from_file, setup_from_file if setup_from_file else "DEFAULT")
                finally:
                    self._suppress_dca_prompt = False
            enabled_ids_raw = str(meta_map.get("enabled_ids", "")).strip()
            if enabled_ids_raw and bool(getattr(self, "aircraft_enable_checks", {})):
                enabled_set = {x.strip() for x in enabled_ids_raw.split(",") if x.strip() in AIRCRAFT_IDS}
                mk_loaded = str(getattr(self, "current_mode_key", "")).strip()
                mode_ids_loaded = set(MODE_ACTIVE_IDS.get(mk_loaded, MODE_ACTIVE_IDS["2vs1"]))
                for aid, cb in self.aircraft_enable_checks.items():
                    if (aid in AIRCRAFT_IDS) and (aid in mode_ids_loaded):
                        cb.setChecked(aid in enabled_set)

            fixed_dt_row = next((r for r in meta_rows if str(r.get("key", "")).strip() == "fixed_dt"), None)
            if fixed_dt_row is not None:
                self.fixed_dt = _f(fixed_dt_row.get("value"), self.dt_sec.value())
                self.dt_sec.setValue(self.fixed_dt)
            else:
                self.fixed_dt = float(self.dt_sec.value())
            current_step_row = next((r for r in meta_rows if str(r.get("key", "")).strip() == "current_step"), None)
            target_step_meta = _i(current_step_row.get("value"), 0) if current_step_row is not None else None
            for aid in AIRCRAFT_IDS:
                color_row = next((r for r in meta_rows if str(r.get("key", "")).strip() == f"color_{aid.replace('#', '')}"), None)
                if color_row is not None:
                    self.controls[aid].set_color_key(str(color_row.get("value", self.controls[aid].current_color_key())))
            self.aircraft_colors = {aid: tuple(self.controls[aid].current_color_rgba()) for aid in AIRCRAFT_IDS}

            init_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "INIT"]
            for r in init_rows:
                aid = str(r.get("id", "")).strip()
                if aid not in AIRCRAFT_IDS:
                    continue
                ac = self.controls[aid]
                field = str(r.get("field", "")).strip()
                val = _f(r.get("value"), 0.0)
                if hasattr(ac, field):
                    w = getattr(ac, field)
                    if isinstance(w, QDoubleSpinBox):
                        w.setValue(val)
            # Important: rebase replay on imported INIT, not on previous scenario snapshot.
            self.state_history = [self._initial_states()]
            self.transition_history = []

            meta_step_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "META_STEP"]
            for r in meta_step_rows:
                step = _i(r.get("step"), 0)
                dt = _f(r.get("dt"), self.fixed_dt if self.fixed_dt is not None else 1.0)
                if step not in self.step_cmds:
                    self.step_cmds[step] = {"_dt": float(dt), "cmds": self._default_step_cmds()}
                else:
                    self.step_cmds[step]["_dt"] = float(dt)

            cmd_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "CMD"]
            for r in cmd_rows:
                step = _i(r.get("step"), 0)
                aid = str(r.get("id", "")).strip()
                if aid not in AIRCRAFT_IDS:
                    continue
                if step not in self.step_cmds:
                    self.step_cmds[step] = {"_dt": float(self.fixed_dt), "cmds": self._default_step_cmds()}
                self.step_cmds[step]["cmds"][aid] = {
                    "turn": str(r.get("turn", "S")).strip() or "S",
                    "power": str(r.get("power", "M")).strip() or "M",
                    "g_cmd": _f(r.get("g_cmd"), 1.0),
                    "g_use_max": _b(r.get("g_use_max")),
                    "pitch_deg": _f(r.get("pitch_deg"), 0.0),
                    "pitch_hold": _b(r.get("pitch_hold")),
                    "pitch_user_set": _b(r.get("pitch_user_set")),
                    "bank_deg": _f(r.get("bank_deg"), 0.0),
                    "bank_user_set": _b(r.get("bank_user_set")),
                    "pull_mode": str(r.get("pull_mode", "NONE")).strip().upper() or "NONE",
                    "level_hold": _b(r.get("level_hold")),
                }

            hold_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "HOLD"]
            for r in hold_rows:
                step = _i(r.get("step"), 0)
                aid = str(r.get("id", "")).strip()
                if aid in AIRCRAFT_IDS:
                    if step not in self.hold_state_by_step:
                        self.hold_state_by_step[step] = {a: False for a in AIRCRAFT_IDS}
                    self.hold_state_by_step[step][aid] = _b(r.get("hold"))
                else:
                    # Backward compatibility: one bool for all aircraft.
                    self.hold_state_by_step[step] = {a: _b(r.get("hold")) for a in AIRCRAFT_IDS}

            custom_los_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "CUSTOM_LOS"]
            loaded_links: List[Dict[str, object]] = []
            for r in custom_los_rows:
                a = str(r.get("a", "")).strip()
                b = str(r.get("b", "")).strip()
                s = _i(r.get("step"), -1)
                if (a not in AIRCRAFT_IDS) or (b not in AIRCRAFT_IDS) or (a == b) or (s < 0):
                    continue
                pair_set = self._pair_key(a, b)
                duplicate = any(
                    (int(lk.get("step", -1)) == int(s))
                    and (self._pair_key(str(lk.get("a")), str(lk.get("b"))) == pair_set)
                    for lk in loaded_links
                )
                if not duplicate:
                    link_obj: Dict[str, object] = {"a": a, "b": b, "step": int(s)}
                    src_aid = str(r.get("src_aid", "")).strip()
                    if src_aid in AIRCRAFT_IDS:
                        link_obj["src_aid"] = src_aid
                    c = self._parse_rgba_csv(r.get("color_rgba", ""))
                    if c is not None:
                        link_obj["color"] = c
                    tc = str(r.get("text_color", "")).strip()
                    if tc:
                        link_obj["text_color"] = tc
                    loaded_links.append(link_obj)
            self.custom_los_links = loaded_links
            bookmark_rows = [r for r in rows if str(r.get("row_type", "")).strip() == "BOOKMARK"]
            for r in bookmark_rows:
                s = _i(r.get("step"), -1)
                note = str(r.get("note", "")).strip()
                if s >= 0 and note:
                    cam_distance = _f(r.get("cam_distance"), np.nan)
                    cam_elevation = _f(r.get("cam_elevation"), np.nan)
                    cam_azimuth = _f(r.get("cam_azimuth"), np.nan)
                    cam_center_x = _f(r.get("cam_center_x"), np.nan)
                    cam_center_y = _f(r.get("cam_center_y"), np.nan)
                    cam_center_z = _f(r.get("cam_center_z"), np.nan)
                    cam_obj = None
                    if all(np.isfinite(v) for v in [cam_distance, cam_elevation, cam_azimuth, cam_center_x, cam_center_y, cam_center_z]):
                        cam_obj = {
                            "distance": float(cam_distance),
                            "elevation": float(cam_elevation),
                            "azimuth": float(cam_azimuth),
                            "center_x": float(cam_center_x),
                            "center_y": float(cam_center_y),
                            "center_z": float(cam_center_z),
                        }
                    self.step_bookmarks[int(s)] = {"note": note, "camera": cam_obj}

            dca_enabled = _b(meta_map.get("dca_enabled", "0"))
            if dca_enabled:
                self._apply_dca_from_saved_meta(meta_map)
            else:
                self._clear_dca_be()

            max_step = max(self.step_cmds.keys()) if self.step_cmds else 0
            if target_step_meta is None:
                target_step = max_step
            else:
                target_step = max(0, min(int(target_step_meta), int(max_step)))
            self.current_step = target_step
            self.playback_step_float = float(self.current_step)
            self._replay_to_step(self.current_step)
            self._restore_cmd_ui_for_step(self.current_step)
            self._restore_hold_ui_for_step(self.current_step)
            self.refresh_ui()
            QMessageBox.information(self, "Done", f"Loaded from: {path}")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Load failed: {e}")
            return False


def main():
    print(f"[fa50 v{APP_VERSION}] Using NPZ Ps database (fa50_psdb_0p1_strict2_v0.npz)")
    print("G clamp step = 0.1g")
    args = list(sys.argv[1:])
    auto_visual_probe = any(str(a).strip().lower() == "--auto-visual-probe" for a in args)
    if (not auto_visual_probe) and (not acquire_single_instance_lock()):
        print("[FA50] Another instance is already running. Exiting.")
        return
    probe_prefix = "visual_probe_4vs2_fwd5_top"
    open_probe_files = True
    for a in args:
        s = str(a).strip()
        if s.lower().startswith("--probe-prefix="):
            v = s.split("=", 1)[1].strip()
            if v:
                probe_prefix = v
        elif s.lower() == "--no-open-probe":
            open_probe_files = False
    base_dir = os.path.dirname(os.path.abspath(__file__))
    probe_dir_env = str(os.environ.get("FA50_PROBE_DIR", "")).strip()
    if probe_dir_env:
        out_dir = probe_dir_env
    else:
        # Use ASCII-safe temp path by default to avoid Unicode-path save issues.
        out_dir = os.path.join(os.environ.get("TEMP", base_dir), "fa50_visual_probes")
    overview_png = os.path.join(out_dir, f"{probe_prefix}_overview.png")
    play_png = os.path.join(out_dir, f"{probe_prefix}_play.png")
    log_txt = os.path.join(out_dir, f"{probe_prefix}.txt")
    probe_lines: List[str] = []
    if auto_visual_probe:
        os.makedirs(out_dir, exist_ok=True)
        probe_lines.extend(
            [
                f"time={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}",
                f"python={sys.executable}",
                f"script={os.path.abspath(__file__)}",
                f"args={' '.join(args)}",
                "mode=auto_visual_probe",
                f"out_dir={out_dir}",
            ]
        )
        # Always create a starter log immediately so failures/hangs are diagnosable.
        with open(log_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(probe_lines) + "\n")
        try:
            from OpenGL import GL as _GL
            _orig_gl_clear_color = _GL.glClearColor

            def _safe_gl_clear_color(*a, **k):
                try:
                    return _orig_gl_clear_color(*a, **k)
                except Exception as e_glcc:
                    probe_lines.append(f"warn=glClearColor_ignored:{e_glcc}")
                    return None

            _GL.glClearColor = _safe_gl_clear_color
            probe_lines.append("patch=glClearColor_safe_wrapper_enabled")
        except Exception as e_patch:
            probe_lines.append(f"warn=glClearColor_patch_failed:{e_patch}")
        with open(log_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(probe_lines) + "\n")
    if not auto_visual_probe:
        run_sanity_tests()
    else:
        print("Sanity tests skipped in auto-visual-probe mode.")
    # Compatibility-first default for restricted/old PCs.
    gl_mode = str(os.environ.get("FA50_GL_MODE", "hardware")).strip().lower()
    force_sw = (os.environ.get("FA50_FORCE_SOFTWARE_GL", "0") == "1") or (gl_mode in ("compat", "software", "sw", "cpu"))
    if force_sw:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
        print("GL mode: software (compat)")
    else:
        os.environ["QT_OPENGL"] = "desktop"
        print("GL mode: hardware")
    if gl is None:
        if auto_visual_probe:
            probe_lines.append(f"error=OpenGL import failed: {OPENGL_IMPORT_ERROR}")
            with open(log_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(probe_lines) + "\n")
            print(f"[AUTO_PROBE] failed before app init. log: {log_txt}")
            return
        raise RuntimeError(
            "OpenGL import failed. Install dependencies first:\n"
            "  python -m pip install PyOpenGL PyOpenGL_accelerate\n"
            f"Original error: {OPENGL_IMPORT_ERROR}"
        )
    app = QApplication(sys.argv)
    available_fonts = set(QFontDatabase.families())
    candidate_fonts = [
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Noto Sans CJK KR",
        "Noto Sans KR",
    ]
    chosen_font = None
    font_source = "system"
    for family in candidate_fonts:
        if family in available_fonts:
            chosen_font = family
            break
    if chosen_font is None:
        chosen_font = app.font().family()
        font_source = "default"
    app.setFont(QFont(chosen_font, 9))
    print(f"UI Font: {chosen_font} ({font_source})")
    print("Layout rebuilt: no overlap")
    print("CAS/ALT continuous interpolation enabled (g on 0.1 NPZ grid).")
    npz_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fa50_psdb_0p1_strict2_v0.npz")
    if not os.path.exists(npz_path):
        if auto_visual_probe:
            probe_lines.append(f"error=missing npz: {npz_path}")
            with open(log_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(probe_lines) + "\n")
            print(f"[AUTO_PROBE] failed missing npz. log: {log_txt}")
            return
        QMessageBox.critical(
            None,
            "Missing File",
            "Missing fa50_psdb_0p1_strict2_v0.npz. Run: python fa50_build_psdb_0p1_strict2.py --xlsx DATABASE.xlsx --out fa50_psdb_0p1_strict2_v0.npz",
        )
        return

    try:
        win = MainWindow(npz_path, startup_mode="2vs1", startup_setup="DEFAULT")
    except Exception as e:
        if auto_visual_probe:
            probe_lines.append(f"error=MainWindow init failed: {e}")
            with open(log_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(probe_lines) + "\n")
            print(f"[AUTO_PROBE] failed at MainWindow init. log: {log_txt}")
            return
        QMessageBox.critical(None, "Startup Error", str(e))
        raise
    scr = app.primaryScreen()
    if scr is not None:
        rect = scr.availableGeometry()
        win.setGeometry(rect)
    max_state = (win.windowState() & ~Qt.WindowState.WindowFullScreen) | Qt.WindowState.WindowMaximized
    win.setWindowState(max_state)
    win.show()
    QTimer.singleShot(0, lambda: win.setWindowState(max_state))
    if not auto_visual_probe:
        QTimer.singleShot(1200, win.check_updates_on_startup)

    if auto_visual_probe:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        probe_lines.append(f"probe_start={ts}")
        def _probe_prepare_gl_context():
            # In some environments, GL context is not fully ready at first refresh call.
            # Prime the widget/context before running heavy UI updates.
            for _ in range(4):
                app.processEvents()
            try:
                if hasattr(win, "view") and (win.view is not None) and hasattr(win.view, "makeCurrent"):
                    win.view.makeCurrent()
            except Exception as e_ctx:
                probe_lines.append(f"warn=makeCurrent_failed:{e_ctx}")
            for _ in range(4):
                app.processEvents()

        def _probe_call_with_gl_retry(label: str, fn):
            last_err = None
            for attempt in range(1, 4):
                try:
                    fn()
                    if attempt > 1:
                        probe_lines.append(f"{label}_retry_success_attempt={attempt}")
                    return
                except Exception as e_call:
                    last_err = e_call
                    msg = str(e_call)
                    probe_lines.append(f"{label}_attempt_{attempt}_error={msg}")
                    lower_msg = msg.lower()
                    if ("glclearcolor" in lower_msg) or ("invalid operation" in lower_msg):
                        _probe_prepare_gl_context()
                        continue
                    break
            raise last_err

        def _probe_frame_ba_arrows(step_i: int):
            # Fit camera to BA group (#1~#4) so arrows are guaranteed visible in probe PNGs.
            try:
                ba_ids = ["#1", "#2", "#3", "#4"]
                pts = []
                s = int(max(0, min(step_i, len(win.state_history) - 1)))
                for aid in ba_ids:
                    st = win.state_history[s].get(aid)
                    if isinstance(st, dict):
                        pts.append(np.array([float(st["x_ft"]), float(st["y_ft"]), float(st["z_ft"])], dtype=float))
                if not pts:
                    return
                arr = np.vstack(pts)
                ctr = arr.mean(axis=0)
                dx = float(np.max(arr[:, 0]) - np.min(arr[:, 0]))
                dy = float(np.max(arr[:, 1]) - np.min(arr[:, 1]))
                span = max(6000.0, math.hypot(dx, dy))
                dist = float(np.clip(span * 1.55, 9000.0, 90000.0))
                win.view.opts["center"] = QVector3D(float(ctr[0]), float(ctr[1]), float(ctr[2]))
                # Top-view but keep a slight angle for arrow readability.
                win.view.setCameraPosition(distance=dist, elevation=86.0, azimuth=0.0)
                win.refresh_ui()
                for _ in range(6):
                    app.processEvents()
            except Exception as e_cam:
                probe_lines.append(f"warn=probe_frame_ba_arrows_failed:{e_cam}")

        try:
            probe_lines.append("checkpoint=prepare_gl_context_initial")
            _probe_prepare_gl_context()
            probe_lines.append("checkpoint=apply_startup_profile")
            _probe_call_with_gl_retry(
                "apply_startup_profile",
                lambda: win.apply_startup_profile("4vs2", "4vs2 BA OFFSET BOX + RA RANGE"),
            )
            probe_lines.append("checkpoint=advance_steps_5")
            _probe_call_with_gl_retry("advance_steps_5", lambda: win.advance_steps(5))
            probe_lines.append("checkpoint=set_overview_top")
            win.view_mode.setCurrentText("Overview View")
            win._set_camera_mode("top")
            _probe_call_with_gl_retry("refresh_overview_top", lambda: win.refresh_ui())
            _probe_frame_ba_arrows(step_i=win.current_step)
            for _ in range(8):
                app.processEvents()
            pix_over = win.grab()
            save_over_ok = bool(pix_over.save(overview_png))
            probe_lines.append(f"save_overview={save_over_ok} path={overview_png}")

            # Playback-like overview frame (interpolated)
            probe_lines.append("checkpoint=playback_like_frame")
            win.playback_active = True
            win.playback_running = False
            win.playback_step_float = 3.4
            win.current_step = 3
            _probe_call_with_gl_retry("refresh_playback_like", lambda: win.refresh_ui())
            _probe_frame_ba_arrows(step_i=win.current_step)
            for _ in range(8):
                app.processEvents()
            pix_play = win.grab()
            save_play_ok = bool(pix_play.save(play_png))
            probe_lines.append(f"save_play={save_play_ok} path={play_png}")

            active_ids = win._active_aircraft_ids()
            arrow_counts = {aid: len(win.step_arrow_items.get(aid, [])) for aid in active_ids}
            lines = [
                f"time={ts}",
                "scenario=4vs2 BA OFFSET BOX + RA RANGE",
                "action=fwd 5, top view, overview/play capture",
                f"current_step={int(win.current_step)}",
                f"playback_step_float={float(win.playback_step_float):.2f}",
                f"save_overview={save_over_ok} path={overview_png}",
                f"save_play={save_play_ok} path={play_png}",
                "step_arrow_items_count_by_aid:",
            ]
            for aid in active_ids:
                lines.append(f"  {aid}: {arrow_counts.get(aid, 0)}")
            probe_lines.extend(lines)
            with open(log_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(probe_lines) + "\n")
            print(f"[AUTO_PROBE] saved: {overview_png}")
            print(f"[AUTO_PROBE] saved: {play_png}")
            print(f"[AUTO_PROBE] log:   {log_txt}")
            if open_probe_files:
                try:
                    if save_over_ok:
                        os.startfile(overview_png)
                    if save_play_ok:
                        os.startfile(play_png)
                    os.startfile(log_txt)
                except Exception as e_open:
                    print(f"[AUTO_PROBE] open-file warning: {e_open}")
        except Exception as e:
            probe_lines.append(f"error={e}")
            with open(log_txt, "w", encoding="utf-8") as f:
                f.write("\n".join(probe_lines) + "\n")
            print(f"[AUTO_PROBE] failed: {e}")
        finally:
            win.close()
            app.quit()
        return

    QTimer.singleShot(120, win.prompt_startup_selection)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
