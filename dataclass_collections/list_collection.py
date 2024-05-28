from dataclasses import fields, is_dataclass
from typing import Generic, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel
from typeguard import check_type

T = TypeVar("T")


class ListCollection(list[T], Generic[T]):
    def __init__(self, args: Sequence[T]):
        self.underlying_type: Optional[Type] = None
        if args:
            self.underlying_type = type(args[0])
            if is_dataclass(self.underlying_type):
                for item in args:
                    if not isinstance(item, self.underlying_type):
                        raise TypeError(
                            f"""All elements in the ListCollection must be instances of the same type.
    This collection is of type {self.underlying_type}, but there's an element of type {type(item)}"""
                        )
                check_type("args", args, Sequence[self.underlying_type])
            elif isinstance(self.underlying_type, BaseModel):
                raise NotImplementedError("Pydantic models are not supported yet")
            else:
                raise TypeError(
                    f"""The ListCollection must be of dataclasses or Pydantic models."""
                )

        super().__init__(args)
        self._add_properties()

    ### ADD PROPERTIES ###

    def _add_properties(self) -> None:
        cls = self.__class__
        if is_dataclass(self.underlying_type):
            dataclass_type = self.__orig_bases__[0].__args__[0]  # type: ignore
            for field in fields(dataclass_type):
                name = field.name
                property_type = list[field.type]
                setattr(cls, name, self._make_property(name, property_type))
        elif isinstance(self.underlying_type, BaseModel):
            raise NotImplementedError("Pydantic models are not supported yet")
        elif self.underlying_type is None:
            pass
        else:
            raise TypeError(f"""The ListCollection must be of dataclasses""")

    def _make_property(self, name: str, property_type: type) -> property:
        def prop(self) -> list[property_type]:
            # Intuitively [item.name for item in self]
            # But the following is a little nicer
            return [getattr(item, name) for item in self]

        prop.__name__ = name
        return property(prop)

    ### ENABLE TYPE-CHECKED LIST OPS ###

    def append(self, object: T) -> None:
        self.underlying_type = self.underlying_type or type(object)
        if isinstance(object, self.underlying_type):
            super().append(object)
        else:
            raise TypeError(
                f"""All elements in the ListCollection must be instances of the same type.
This collection is of type {self.underlying_type} and an object of type {type(object)} is being appended."""
            )
        # Note that extend uses append under the hood so this covers that case.

    def __setitem__(self, key: int, value: T) -> None:
        self.underlying_type = self.underlying_type or type(value)
        if isinstance(value, self.underlying_type):
            super().__setitem__(key, value)
        else:
            raise TypeError(
                f"""All elements in the ListCollection must be instances of the same type.
This collection is of type {self.underlying_type} and an object of type {type(value)} is being assigned."""
            )
        # Note that insert uses __setitem__ under the hood so this covers that case.

    def __add__(self, other: Union["ListCollection[T]", list[T]]) -> "ListCollection[T]":
        if len(self) == 0:
            return ListCollection(other)

        elif isinstance(other, ListCollection):
            return self._add_list_collections(other)

        elif isinstance(other, list):
            assert self.underlying_type is not None
            other_list_collection = ListCollection(other)
            return self._add_list_collections(other_list_collection)

        else:
            raise TypeError(
                f"""The ListCollection can only be added to another ListCollection."""
            )

    def _add_list_collections(self, other: "ListCollection[T]") -> "ListCollection[T]":
        if self.underlying_type == other.underlying_type:
            out = ListCollection(super().__add__(other))
            return out
        else:
            raise TypeError(
                f"""Both ListCollections must be of the same type to be added together.
This collection is of type {self.underlying_type} and the other collection is of type {other.underlying_type}"""
            )
