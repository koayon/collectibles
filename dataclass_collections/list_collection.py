from dataclasses import fields, is_dataclass
from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel
from typeguard import check_type

T = TypeVar("T")


class ListCollection(list[T], Generic[T]):
    def __init__(self, args: list[T]):
        self.underlying_type: Optional[Type] = None
        if args:
            self.underlying_type = type(args[0])
            assert is_dataclass(
                self.underlying_type
            ), "The ListCollection must be of dataclasses"

            for item in args:
                if not isinstance(item, self.underlying_type):
                    raise TypeError(
                        f"""All elements in the ListCollection must be instances of the same type.
This collection is of type {self.underlying_type}, but there's an element of type {type(item)}"""
                    )
            check_type("args", args, list[self.underlying_type])

        super().__init__(args)
        self._add_properties()

    def _add_properties(self):
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

    def _make_property(self, name: str, typ: type):
        def prop(self):
            # Intuitively [item.name for item in self]
            # But the following is a little nicer
            return [getattr(item, name) for item in self]

        prop.__name__ = name
        return property(prop)

    def append(self, object: T) -> None:
        self.underlying_type = self.underlying_type or type(object)
        if isinstance(object, self.underlying_type):
            super().append(object)
        else:
            raise TypeError(
                f"""All elements in the ListCollection must be instances of the same type.
This collection is of type {self.underlying_type} and an object of type {type(object)} is being appended."""
            )

    def __setitem__(self, key: int, value: T) -> None:
        self.underlying_type = self.underlying_type or type(value)
        if not isinstance(value, self.underlying_type):
            raise TypeError(
                f"""All elements in the ListCollection must be instances of the same type.
This collection is of type {self.underlying_type} and an object of type {type(value)} is being assigned."""
            )
        super().__setitem__(key, value)
