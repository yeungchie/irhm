from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np

__all__ = [
    "Item",
    "Items",
    "ArrayInfo",
    "Tiles",
    "Colleciton",
    "from_file",
]


@dataclass
class Item:
    net: str
    value: float
    x: float
    y: float
    path: Optional[str] = field(default=None, repr=False)
    raw: Optional[str] = field(default=None, repr=False, compare=False)


class Items(list):
    def get_max(self) -> float:
        values = [item.value for item in self]
        if len(values) == 0:
            return 0.0
        else:
            return max(values)


@dataclass
class ArrayInfo:
    max: float
    min: float
    ndarray: np.ndarray


class Tiles(defaultdict):
    def __init__(self) -> None:
        super().__init__(Colleciton)

    def __getitem__(self, *args, **kwargs) -> "Colleciton":
        return super().__getitem__(*args, **kwargs)

    def array_info(self, net1: str, net2: str) -> ArrayInfo:
        x_size, y_size = 0, 0
        for x, y in self:
            x_size = max(x_size, x)
            y_size = max(y_size, y)
        max_v = None
        min_v = None
        array = np.zeros((x_size + 1, y_size + 1))
        for xy, c in self.items():
            value = c.calc_drop(net1, net2)
            array[xy] = value
            if max_v is None or value > max_v:
                max_v = value
            if min_v is None or value < min_v:
                min_v = value
        return ArrayInfo(
            max=max_v,
            min=min_v,
            ndarray=array,
        )


class Colleciton(defaultdict):
    def __init__(self) -> None:
        super().__init__(Items)

    def append(self, item: Item) -> None:
        self[item.net].append(item)

    def __getitem__(self, key: str) -> Items:
        return super().__getitem__(key)

    def all_items(self) -> list:
        items = []
        for x in self.values():
            items.extend(x)
        return items

    def calc_drop(self, net1: str, net2: str) -> float:
        return self[net1].get_max() + self[net2].get_max()

    def get_box(
        self,
        origin: Optional[Tuple[float, float]] = None,
        expand: float = 1.0,
    ) -> tuple:
        x_min, x_max = None, None
        y_min, y_max = None, None
        if origin is not None:
            x_min, y_min = origin
        for item in self.all_items():
            if origin is None:
                if x_min is None or item.x < x_min:
                    x_min = item.x
                if x_max is None or item.x > x_max:
                    x_max = item.x
            if y_min is None or item.y < y_min:
                y_min = item.y
            if y_max is None or item.y > y_max:
                y_max = item.y
        x_min -= expand
        y_min -= expand
        x_max += expand
        y_max += expand
        return (x_min, y_min), (x_max, y_max)

    def make_tiles(self, cols: int, rows: int, **kwargs) -> Tiles:
        box = self.get_box(
            origin=kwargs.get("origin"),
            expand=kwargs.get("expand", 1.0),
        )
        x_min, y_min = box[0]
        x_max, y_max = box[1]
        x_size = (x_max - x_min) / cols
        y_size = (y_max - y_min) / rows
        tiles = Tiles()
        for col in range(cols):
            for row in range(rows):
                x_start = x_min + col * x_size
                y_start = y_min + row * y_size
                x_end = x_start + x_size
                y_end = y_start + y_size
                colleciton = Colleciton()
                for item in self.all_items():
                    if x_start <= item.x < x_end and y_start <= item.y < y_end:
                        colleciton.append(item)
                tiles[(col, row)] = colleciton
        return tiles

    def make_tiles_by_size(
        self,
        width: float,
        height: float,
        origin: Optional[Tuple[float, float]] = None,
        expand: float = 0.0,
    ) -> Tiles:
        box = self.get_box(origin=origin, expand=expand)
        x_min, y_min = box[0]
        x_max, y_max = box[1]
        cols = int((x_max - x_min) // width) + 1
        rows = int((y_max - y_min) // height) + 1
        tiles = Tiles()
        for col in range(cols):
            for row in range(rows):
                x_start = x_min + col * width
                y_start = y_min + row * height
                x_end = x_start + width
                y_end = y_start + height
                colleciton = Colleciton()
                for item in self.all_items():
                    if x_start <= item.x < x_end and y_start <= item.y < y_end:
                        colleciton.append(item)
                tiles[(col, row)] = colleciton
        return tiles


def from_file(file: Union[str, Path]) -> Colleciton:
    """file format:
    ```
    #net  value  x      y      path
    VCC   17.77  91.36  61.24  X14/X45
    VSS   26.17  30.78  62.44  X10/X27
    VCCA  13.97  13.72  13.73  X18/X47/X28/X35
    VSSA  40.02  74.70  88.81  X47/X39
    VCCD  28.10  84.42  38.62  X24/X34/X30/X38
    VSSD  14.63  25.73  15.37  X3/X4
    ```
    """
    collection = Colleciton()
    for line in Path(file).read_text().splitlines():
        tokens = line.partition("#")[0].split()
        if not tokens:
            continue
        net, value, x, y, path = tokens
        collection.append(
            Item(
                net=net,
                value=float(value),
                x=float(x),
                y=float(y),
                path=path,
                raw=line,
            )
        )
    return collection
