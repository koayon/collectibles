from dataclasses import dataclass

import pytest

from dataclass_collections import ListCollection


# Define test dataclasses
@dataclass
class TestDataclass:
    val1: int
    val2: str

    @property
    def val3(self) -> str:
        return f"{self.val1}: {self.val2}"


@dataclass
class RogueDataclass:
    val1: int
    val2: int


class DataclassCollection(ListCollection[TestDataclass]):
    val1: list[int]
    val2: list[str]
    val3: list[str]

    @property
    def agg(self) -> str:
        return f"{sum(self.val1)}: {''.join(self.val2)}"


# Test initialization
def test_initialization_valid():
    items = [TestDataclass(1, "a"), TestDataclass(2, "b")]
    collection = DataclassCollection(items)
    assert len(collection) == 2
    assert collection.val1 == [1, 2]
    assert collection.val2 == ["a", "b"]
    assert collection.val3 == ["1: a", "2: b"]


def test_initialization_invalid():
    items = [TestDataclass(1, "a"), RogueDataclass(1, 2)]
    with pytest.raises(TypeError):
        DataclassCollection(items)


# Test property access
def test_dynamic_properties():
    items = [TestDataclass(1, "a"), TestDataclass(2, "b")]
    collection = DataclassCollection(items)
    assert collection.val1 == [1, 2]
    assert collection.agg == "3: ab"


# Test appending valid and invalid items
def test_append_valid():
    collection = DataclassCollection([TestDataclass(1, "a")])
    collection.append(TestDataclass(2, "b"))
    assert len(collection) == 2


def test_append_invalid():
    collection = DataclassCollection([TestDataclass(1, "a")])
    with pytest.raises(TypeError):
        collection.append(RogueDataclass(2, 3))  # type: ignore


# Test __setitem__
def test_setitem_valid():
    collection = DataclassCollection([TestDataclass(1, "a")])
    collection[0] = TestDataclass(2, "b")
    assert collection.val1 == [2]


def test_setitem_invalid():
    collection = DataclassCollection([TestDataclass(1, "a")])
    with pytest.raises(TypeError):
        collection[0] = RogueDataclass(2, 3)  # type: ignore


# Test list operations: addition and slicing
def test_list_addition():
    collection1 = DataclassCollection([TestDataclass(1, "a")])
    collection2 = DataclassCollection([TestDataclass(2, "b")])
    new_collection = collection1 + collection2
    assert len(new_collection) == 2
    assert new_collection.val1 == [1, 2]


def test_list_slicing():
    collection = DataclassCollection(
        [TestDataclass(1, "a"), TestDataclass(2, "b"), TestDataclass(3, "c")]
    )
    sliced = collection[1:3]
    assert isinstance(
        sliced, list
    )  # Or assert isinstance(sliced, type(collection)) if returning wrapped list
    assert len(sliced) == 2


# Test invalid addition
def test_invalid_addition():
    collection1 = DataclassCollection([TestDataclass(1, "a")])
    with pytest.raises(TypeError):
        _ = collection1 + [1, 2, 3]  # type: ignore
