from typing import Sequence, Tuple, Callable
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import seaborn

from ._qt import (
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
    QSizePolicy,
    QSpinBox,
    QPushButton,
    QFrame,
    QIcon,
    Qt,
    FigureCanvasQTAgg,
)
from ..ir import Colleciton, Tiles
from .. import release


class HeatmapApp(QApplication):
    def __init__(
        self,
        *args,
        collection: Colleciton,
        array: Tuple[int, int] = (10, 10),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setStyle("Fusion")
        self.window = HeatmapWindow(collection)
        self.window.array = array
        self.window.init()

    def show(self):
        self.window.show()


class HeatmapWindow(QMainWindow):
    def __init__(
        self,
        collection: Colleciton,
        array: Tuple[int, int] = (10, 10),
    ) -> None:
        super().__init__()
        self.collection = collection
        self.array = array
        self.inited: bool = False
        self.__ui()

    @property
    def collection(self) -> Colleciton:
        return self.__collection

    @collection.setter
    def collection(self, value: Colleciton) -> None:
        self.__collection = value
        self.inited = False

    @property
    def array(self) -> Tuple[int, int]:
        return self.__array

    @array.setter
    def array(self, value: Tuple[int, int]) -> None:
        col, row = tuple(map(int, value[:2]))
        self.__array = (col, row)

    @property
    def value_array(self):
        return self.__value_array

    @property
    def tiles(self) -> Tiles:
        return self.__tiles

    def update_tiles(self, col: int, row: int):
        self.__tiles = self.collection.make_tiles(col, row)

    def init(self) -> None:
        if self.collection is None:
            raise ValueError("Collection undefined")
        self.update_tiles(*self.array)
        nets = [""] + list(self.collection.keys())
        self.inited = False
        for sel in self.net_selector1, self.net_selector2:
            sel.clear()
            sel.addItems(nets)
            sel.setCurrentIndex(0)
        self.inited = True

    def __net_selector_cb(self) -> None:
        """切换网络时回调"""
        if not self.inited:
            return
        net1 = self.net_selector1.currentText()
        net2 = self.net_selector2.currentText()
        self.clear_all()
        if net1 == "" or net2 == "":
            pass
        elif net1 == net2:
            pass
        else:
            self.__refresh_heatmap(net1, net2)
            self.__refresh_heatmap_table(net1, net2)

    def clear_all(self) -> None:
        """清空所有内容"""
        self.clear_heatmap()
        self.clear_heatmap_table()
        self.clear_net_table()

    def clear_heatmap_table(self) -> None:
        clear_table_items(self.heatmap_table)

    def __refresh_heatmap_table(self, net1: str, net2: str) -> None:
        for pos, collection in self.tiles.items():
            value = collection.calc_drop(net1, net2)
            add_strings_to_table(
                self.heatmap_table, [f"{pos[0]}", f"{pos[1]}", f"{value:.2f}"]
            )
        self.heatmap_table.sortItems(2, order=Qt.SortOrder.DescendingOrder)

    def clear_net_table(self) -> None:
        clear_table_items(self.net_table1)
        clear_table_items(self.net_table2)

    def __heatmap_table_click_cb(self, item: "AlphaNumCmpItem") -> None:
        col, row = (
            int(self.heatmap_table.item(item.row(), 0).text()),
            int(self.heatmap_table.item(item.row(), 1).text()),
        )
        self.__refresh_net_table(col, row)
        self.__update_heatmap_hilight(col, row)

    def __refresh_net_table(self, col: int, row: int) -> None:
        self.clear_net_table()
        net1 = self.net_selector1.currentText()
        net2 = self.net_selector2.currentText()
        for net, table in zip([net1, net2], [self.net_table1, self.net_table2]):
            for item in self.tiles[col, row][net]:
                add_strings_to_table(
                    table,
                    [f"{item.x:.2f}", f"{item.y:.2f}", f"{item.value:.2f}", item.path],
                )
            table.sortItems(2, order=Qt.SortOrder.DescendingOrder)

    def clear_heatmap(self) -> None:
        self.heatmap_figure.clear()
        self.heatmap_canvas.draw()

    def __heatmap_canvas_cb(self, event) -> None:
        if event.inaxes == self.heatmap_axes:
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            col, row = int(x), int(y)
            self.__refresh_net_table(col, row)
            self.__update_heatmap_hilight(col, row)

    def __refresh_heatmap(self, net1: str, net2: str) -> None:
        self.heatmap_axes = self.heatmap_figure.add_subplot(111)
        info = self.tiles.array_info(net1, net2)
        self.__value_array = info.ndarray
        seaborn.heatmap(
            self.value_array.transpose(),
            # annot=True,
            # fmt=".2f",
            cmap="coolwarm",
            ax=self.heatmap_axes,
            linewidths=0.5,
            linecolor="#000000",
        )
        cell_drop = self.collection.calc_drop(net1, net2)
        self.heatmap_axes.set_title(f"{net1} - {net2} - {cell_drop:.2f}")
        self.heatmap_axes.set_xlabel("Columns")
        self.heatmap_axes.set_ylabel("Rows")
        self.heatmap_axes.invert_yaxis()

        # append text
        mid_value = (info.max + info.min) / 2
        qtr_value = (info.max - info.min) / 4
        for col in range(self.array[0]):
            for row in range(self.array[1]):
                value = self.value_array[col, row]
                if abs(value - mid_value) > qtr_value:
                    color = "#FFFFFF"
                else:
                    color = "#000000"
                self.heatmap_axes.text(
                    col + 0.5,
                    row + 0.5,
                    f"{value:.2f}",
                    ha="center",
                    va="center",
                    color=color,
                    fontsize=10,
                )

        self.heatmap_canvas.draw()
        self.heatmap_canvas.mpl_connect("button_press_event", self.__heatmap_canvas_cb)

    def __update_heatmap_hilight(self, col: int, row: int) -> None:
        if hasattr(self, "heatmap_hilight_rect"):
            self.heatmap_hilight_rect.remove()
        self.heatmap_hilight_rect = Rectangle(
            xy=(col, row),
            width=1,
            height=1,
            linewidth=3,
            edgecolor="#F5D83E",
            facecolor="none",
        )
        self.heatmap_axes.add_patch(self.heatmap_hilight_rect)
        self.heatmap_canvas.draw()

    def __array_btn_cb(self) -> None:
        net1 = self.net_selector1.currentText()
        net2 = self.net_selector2.currentText()
        self.array = (self.arr_col_input.value(), self.arr_row_input.value())
        self.init()
        self.net_selector1.setCurrentText(net1)
        self.net_selector2.setCurrentText(net2)
        self.__net_selector_cb()

    def __ui(self) -> None:
        self.setWindowTitle(f"IR-Drop Heatmap - {release.version}")
        icon = Path(__file__).parent / "icon.png"
        if icon.exists():
            self.setWindowIcon(QIcon(str(icon)))
        self.setGeometry(100, 100, 1600, 800)

        self.setCentralWidget(main_widget := QWidget())
        main_widget.setLayout(main_layout := QHBoxLayout())
        main_splitter = QSplitter(Qt.Orientation.Horizontal)  # 顶层水平分割窗
        main_layout.addWidget(main_splitter)

        # 左侧
        left_region = QWidget()
        left_region.setLayout(left_layout := QVBoxLayout())
        # 左侧 heatmap 信息表格
        self.heatmap_table = QTableWidget()
        self.heatmap_table.setColumnCount(3)
        self.heatmap_table.setHorizontalHeaderLabels(["Col", "Row", "Value"])
        self.heatmap_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.heatmap_table.setSortingEnabled(True)
        self.heatmap_table.clicked.connect(self.__heatmap_table_click_cb)
        left_layout.addWidget(self.heatmap_table)

        # 中间
        middle_region = QSplitter(Qt.Orientation.Vertical)  # 中间垂直分割窗
        # 中间 heatmap
        self.heatmap_figure = Figure(facecolor="#DFDFDF")
        self.heatmap_canvas = FigureCanvasQTAgg(self.heatmap_figure)
        middle_region.addWidget(self.heatmap_canvas)
        self.heatmap_canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # 中间底部表格分区
        bottom_region = QSplitter(Qt.Orientation.Horizontal)  # 中间底部水平分割窗
        middle_region.addWidget(bottom_region)
        self.net_selector1, self.net_table1 = create_selector(
            parent=bottom_region,
            callback=self.__net_selector_cb,
        )
        self.net_selector2, self.net_table2 = create_selector(
            parent=bottom_region,
            callback=self.__net_selector_cb,
        )

        # 右侧
        right_region = QWidget()
        right_region.setLayout(right_layout := QVBoxLayout())
        # array inputter
        # array_region = QSplitter(Qt.Orientation.Horizontal)
        array_region = QWidget()
        array_region.setLayout(array_layout := QHBoxLayout())
        self.arr_col_input = QSpinBox()
        self.arr_col_input.setRange(1, 100)
        self.arr_col_input.setValue(self.array[0])
        self.arr_row_input = QSpinBox()
        self.arr_row_input.setRange(1, 100)
        self.arr_row_input.setValue(self.array[1])
        array_btn = QPushButton("Refresh")
        array_btn.clicked.connect(self.__array_btn_cb)
        array_prompt = QLabel("Array Size:")
        array_prompt.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        array_x_label = QLabel("X")
        array_x_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for i, field in enumerate(
            (
                array_prompt,
                self.arr_col_input,
                array_x_label,
                self.arr_row_input,
                array_btn,
            )
        ):
            array_layout.addWidget(field)
            array_layout.setStretch(i, 1)
        array_region_line = QFrame()
        array_region_line.setFrameShape(QFrame.Shape.HLine)
        array_region_line.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(array_region)
        right_layout.addWidget(array_region_line)
        right_layout.addStretch()

        main_splitter.addWidget(left_region)
        main_splitter.addWidget(middle_region)
        main_splitter.addWidget(right_region)


class AlphaNumCmpItem(QTableWidgetItem):
    def __lt__(self, other: "AlphaNumCmpItem") -> bool:
        try:
            return float(self.text()) < float(other.text())
        except ValueError:
            return self.text() < other.text()


def add_strings_to_table(table: QTableWidget, strings: Sequence[str]) -> None:
    """向表格中添加一行，items 代表这一行的每一列内容"""
    table.setSortingEnabled(False)
    row_num = table.rowCount()
    table.insertRow(row_num)
    for i, s in enumerate(strings):
        table.setItem(row_num, i, AlphaNumCmpItem(s))
    table.setSortingEnabled(True)


def clear_table_items(table: QTableWidget) -> None:
    """清空表格内容"""
    for _ in range(table.rowCount()):
        table.removeRow(0)


def create_selector(
    parent: QSplitter,
    callback: Callable,
) -> Tuple[QComboBox, QTableWidget]:
    region = QWidget()
    parent.addWidget(region)
    region.setLayout(layout := QVBoxLayout())

    selector_region = QWidget()
    selector_region.setLayout(selector_layout := QHBoxLayout())
    selector_prompt = QLabel("Select Net:")
    selector_prompt.setAlignment(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    selector_layout.addWidget(selector_prompt)
    selector_layout.addWidget(selector := QComboBox())
    selector.currentIndexChanged.connect(callback)
    layout.addWidget(selector_region)

    table = QTableWidget()
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["X", "Y", "Value", "Path"])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)
    return selector, table
