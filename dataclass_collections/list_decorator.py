import dataclasses
from dataclasses import is_dataclass
from typing import Sequence, Type, TypeVar

from pydantic import BaseModel

from dataclass_collections.list_collection import ListCollection


# Define the decorator
def list_collection(base_dataclass: Type):
    def decorator(cls):
        # Define a new class that inherits from ListCollection and the user-defined class
        class ListCollectionSubClass(ListCollection[base_dataclass]):
            def __init__(self, items: Sequence[base_dataclass]):
                # Initialize the ListCollection with the items
                super().__init__(items)
                self.underlying_type = base_dataclass
                self._add_properties()

            # def _add_properties(self) -> None:
            #     cls = self.__class__
            #     if is_dataclass(base_dataclass):
            #         dataclass_type = self.__orig_bases__[0].__args__[0]  # type: ignore
            #         for field in fields(dataclass_type):
            #             name = field.name
            #             field_type = field.type
            #             setattr(cls, name, self._make_property(name, field_type))

            #         setattr(cls, "_ATTRS", [field.name for field in fields(dataclass_type)])

            #     elif isinstance(self.underlying_type, BaseModel):
            #         raise NotImplementedError("Pydantic models are not supported yet")
            #     elif self.underlying_type is None:
            #         pass
            #     else:
            #         raise TypeError(f"""The ListCollection must be of dataclasses""")

            # def _make_property(self, name: str, field_type: type) -> property:
            #     def prop(self) -> list[field_type]:
            #         # Intuitively [item.name for item in self]
            #         # But the following is a little nicer
            #         return [getattr(item, name) for item in self]

            #     prop.__name__ = name
            #     return property(prop)

            # # Adding properties dynamically if not present in the user-defined class
            # for field in dataclasses.fields(base_dataclass):
            #     if not hasattr(cls, field.name):
            #         # Create a property that collects values of this field from all items
            #         prop = property(
            #             lambda self, field_name=field.name: [
            #                 getattr(item, field_name) for item in self
            #             ]
            #         )
            #         setattr(cls, field.name, prop)

        # Transfer annotations for better type checking and editor support
        if is_dataclass(base_dataclass):
            _fields = dataclasses.fields(base_dataclass)
            cls_annotations = {field.name: list[field.type] for field in _fields}
            cls_annotations.update(getattr(cls, "__annotations__", {}))
        elif isinstance(base_dataclass, BaseModel):
            raise NotImplementedError("Pydantic models are not supported yet")
        else:
            raise TypeError(
                f"""The ListCollection must be of dataclasses or Pydantic models."""
            )
        setattr(ListCollectionSubClass, "__annotations__", cls_annotations)

        # Copy docstring and other attributes if needed
        ListCollectionSubClass.__doc__ = cls.__doc__

        return ListCollectionSubClass

    return decorator
