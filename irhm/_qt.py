from importlib.util import find_spec

__all__ = [
    "QApplication",
    "QMainWindow",
    "QWidget",
    "QVBoxLayout",
    "QTableWidget",
    "QTableWidgetItem",
    "QHeaderView",
    "QSplitter",
    "QLabel",
    "QComboBox",
    "QHBoxLayout",
    "QMenu",
    "QMessageBox",
    "QSizePolicy",
    "QSpinBox",
    "QPushButton",
    "QFrame",
    "QAction",
    "QIcon",
    "Qt",
    "FigureCanvasQTAgg",
]

if find_spec("PyQt5"):
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTableWidget,
        QTableWidgetItem,
        QHeaderView,
        QSplitter,
        QLabel,
        QComboBox,
        QMenu,
        QMessageBox,
        QSizePolicy,
        QSpinBox,
        QPushButton,
        QFrame,
        QAction,
    )
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import Qt
else:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTableWidget,
        QTableWidgetItem,
        QHeaderView,
        QSplitter,
        QLabel,
        QComboBox,
        QMenu,
        QMessageBox,
        QSizePolicy,
        QSpinBox,
        QPushButton,
        QFrame,
    )
    from PySide6.QtGui import QAction, QIcon
    from PySide6.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
