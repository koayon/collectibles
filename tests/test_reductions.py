from dataclasses import dataclass
from typing import Optional

import pytest

from dataclass_collections import ListCollection


# Define test dataclasses
@dataclass
class TestDataclass:
    val1: int
    val2: Optional[float]


class DataclassCollection(ListCollection[TestDataclass]):
    val1: list[int]
    val2: list[str]


def test_reduce_mean():
    collection = DataclassCollection([TestDataclass(1, 0.5), TestDataclass(2, 1.5)])
    reduced = collection.reduce(func="mean")
    assert reduced.val1 == 1.5
    assert reduced.val2 == 1.0


def test_reduce_mean_without_nones():
    collection = DataclassCollection([TestDataclass(1, None), TestDataclass(2, 1.5)])
    reduced = collection.reduce(func="mean_without_nones")
    assert reduced.val1 == 1.5
    assert reduced.val2 == 1.5
