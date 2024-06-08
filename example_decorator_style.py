from dataclasses import dataclass

from dataclass_collections.list_decorator import list_collection


@dataclass
class Dataclass:
    val1: int
    val2: str


@list_collection(Dataclass)
class DataclassCollection:
    val1: list[int]
    val2: list[str]

    @property
    def val3(self) -> list[str]:
        return [f"{val1}: {val2}" for val1, val2 in zip(self.val1, self.val2)]


_dataclasses = [Dataclass(1, "a"), Dataclass(2, "b"), Dataclass(3, "c")]
collection = DataclassCollection(_dataclasses)

element = collection[0]

# Accessing properties
print(collection.val1)  # Output: [1, 2, 3]
print(collection.val2)  # Output: ["a", "b", "c"]
print(collection.val3)
