# This file is just for internal testing of certain functionality NOT FOR A TEST OF THE TOOL
from typing import Optional
import numpy as np
import pickle
from PyQt5.QtCore import QSize, QPointF
import time


class Test:
    def __init__(self):
        self._val = 0

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value


def qt_method(points, displacement):
    return [_pt - displacement for _pt in points]


def for_loop(lst, value):
    for _l in lst:
        _l.val = value


def add_value(a, displacement):
    return a + displacement


def set_class_attribute(element: Test, value):
    element.val = value
    return element


def main():
    a = np.random.rand(500, 2)
    lst = a.tolist()
    displacement = QPointF(1, 1)
    points = [QPointF(_pt[0], _pt[1]) for _pt in lst]

    clock = time.CLOCK_REALTIME
    """
    start = time.clock_gettime_ns(clock)
    a = map(add_value, points, [displacement]*len(points))
    a_time = time.clock_gettime_ns(clock) - start
    start = time.clock_gettime_ns(clock)
    b = qt_method(points, displacement)
    b_time = time.clock_gettime_ns(clock) - start

    print(f"Map: \t\t {a_time}")  # 3314
    print(f"QT: \t\t {b_time}")  # 242590
    """
    inst = [Test() for _ in range(10)]

    start = time.clock_gettime_ns(clock)
    b = list(map(lambda test: test.val, inst))
    b_time = time.clock_gettime_ns(clock) - start

    start = time.clock_gettime_ns(clock)
    a = list(map(set_class_attribute, inst, [1] * len(points)))
    a_time = time.clock_gettime_ns(clock) - start

    print(f"Map: \t\t {a_time}")  # 2426
    print(f"Loop: \t\t {b_time}")   # 47778


if __name__ == "__main__":
    main()
