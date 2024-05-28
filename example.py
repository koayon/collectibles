from dataclasses import dataclass

from dataclass_collections.list_collection import ListCollection


@dataclass
class Dataclass:
    val1: int
    val2: str


@dataclass
class RogueDataclass:
    val1: int
    val2: int


class DataclassCollection(ListCollection[Dataclass]):
    val1: list[int]
    val2: list[str]

    @property
    def val3(self) -> list[str]:
        return [f"{val1}: {val2}" for val1, val2 in zip(self.val1, self.val2)]


# Usage
dataclasses_with_rogue = [Dataclass(1, "a"), RogueDataclass(2, 3), Dataclass(3, "c")]
try:
    collection = DataclassCollection(dataclasses_with_rogue)
except TypeError as e:
    print(e)

dataclasses = [Dataclass(1, "a"), Dataclass(2, "b"), Dataclass(3, "c")]
collection = DataclassCollection(dataclasses)

a = collection[0]

# Accessing properties
print(collection.val1)  # Output: [1, 2, 3]
print(collection.val2)  # Output: ["a", "b", "c"]
print(collection.val3)

collection.append(Dataclass(4, "d"))
print(collection.val1)  # Output: [1, 2, 3, 4]
