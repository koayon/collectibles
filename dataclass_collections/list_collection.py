from dataclasses import fields, is_dataclass
from typing import Any, Generic, Optional, Type, TypeVar

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
Here, the first element is of type {self.underlying_type}, but there's an element of type {type(item)}"""
                    )
            check_type("args", args, list[self.underlying_type])

        super().__init__(args)
        self._add_properties()

    def _add_properties(self):
        cls = self.__class__
        dataclass_type = self.__orig_bases__[0].__args__[0]  # type: ignore
        # TODO: ^Can we switch this with self.underlying_type?
        for field in fields(dataclass_type):
            name = field.name
            property_type = list[field.type]
            setattr(cls, name, self._make_property(name, property_type))

    def _make_property(self, name: str, typ: type):
        def prop(self):
            # Intuitively [item.name for item in self]
            # But the following is a little nicer
            return [getattr(item, name) for item in self]

        prop.__name__ = name
        return property(prop)
