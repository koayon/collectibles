from dataclasses import fields, is_dataclass
from typing import Generic, Optional, Self, Sequence, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListCollection(list[T], Generic[T]):
    def __init__(self, items: Sequence[T]):
        self.underlying_type: Optional[Type] = None
        if items:
            self.underlying_type = type(items[0])
            if is_dataclass(self.underlying_type):
                self._check_consistent_types_for_dataclass_list(items)
            elif isinstance(self.underlying_type, BaseModel):
                raise NotImplementedError("Pydantic models are not supported yet")
            else:
                raise TypeError(
                    f"""The ListCollection must be of dataclasses or Pydantic models."""
                )

        super().__init__(items)
        self._add_properties()

    def _check_consistent_types_for_dataclass_list(self, items):
        self.underlying_type = type(items[0])
        for item in items:
            if not isinstance(item, self.underlying_type):
                raise TypeError(
                    f"""All elements in the ListCollection must be instances of the same type.
    This collection is of type {self.underlying_type}, but there's an element of type {type(item)}"""
                )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({super().__str__()})"

    ### ADD PROPERTIES ###

    def _add_properties(self) -> None:
        cls = self.__class__
        if is_dataclass(self.underlying_type):
            dataclass_type = self.__orig_bases__[0].__args__[0]  # type: ignore

            for field in fields(self.underlying_type):
                # for field in fields(dataclass_type):

                name = field.name
                field_type = field.type
                property_type = list[field_type]
                setattr(cls, name, self._make_property(name, field_type, property_type))

            # Attempting to add custom properties and methods
            potential_properties = [
                prop
                for prop in dir(self.underlying_type)
                if isinstance(getattr(self.underlying_type, prop), property)
                or callable(getattr(self.underlying_type, prop))
            ]
            for prop in potential_properties:
                if not hasattr(self.__class__, prop):
                    field_type = type(getattr(self.underlying_type, prop))
                    property_type = list[field_type]
                    setattr(
                        cls,
                        prop,
                        self._make_dynamic_property(prop, field_type, property_type),
                    )

            setattr(cls, "_ATTRS", [field.name for field in fields(dataclass_type)])

        elif isinstance(self.underlying_type, BaseModel):
            raise NotImplementedError("Pydantic models are not supported yet")
        elif self.underlying_type is None:
            pass
        else:
            raise TypeError(f"""The ListCollection must be of dataclasses""")

    @staticmethod
    def _make_property(name: str, field_type: type, property_type: type) -> property:
        def prop(self) -> list[field_type]:
            # Intuitively [item.name for item in self]
            # But the following is a little nicer
            return [getattr(item, name) for item in self]

        prop.__name__ = name
        prop.__annotations__ = {"return": property_type}
        return property(prop)

    @staticmethod
    def _make_dynamic_property(name: str, field_type: type, property_type: type) -> property:
        def dynamic_prop(self) -> list[field_type]:
            return [
                (
                    getattr(item, name)()
                    if callable(getattr(item, name))
                    else getattr(item, name)
                )
                for item in self
            ]

        dynamic_prop.__name__ = name
        dynamic_prop.__annotations__ = {"return": property_type}
        return property(dynamic_prop)

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

    def __add__(self, other: list[T]) -> Self:
        if len(self) == 0:
            if isinstance(other, type(self)):
                return other
            elif isinstance(other, list):
                self_type = type(self)
                return self_type(other)
            else:
                raise TypeError(
                    f"""The ListCollection can only be added to another ListCollection or a list."""
                )

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

    def _add_list_collections(self, other: "ListCollection[T]") -> Self:
        if self.underlying_type == other.underlying_type:
            concatted_collections = super().__add__(other)

            self_type = type(self)
            out = self_type(concatted_collections)
            return out
        else:
            raise TypeError(
                f"""Both ListCollections must be of the same type to be added together.
This collection is of type {self.underlying_type} and the other collection is of type {other.underlying_type}"""
            )
