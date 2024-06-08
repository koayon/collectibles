from dataclasses import fields, is_dataclass
from typing import Any, Callable, Sequence, Type, TypeVar, get_type_hints

from pydantic import BaseModel

from dataclass_collections.list_collection import ListCollection

T = TypeVar("T")


# Define the decorator
def list_collection(
    base_dataclass: Type[T],
) -> Callable[[Type[Any]], Type[ListCollection[T]]]:
    def decorator(cls: Type[Any]) -> Type[ListCollection[T]]:
        base_annotations = get_type_hints(base_dataclass)

        # Define a new class that inherits from ListCollection and the user-defined class
        class ListCollectionSubClass(ListCollection[base_dataclass], cls):
            def __init__(self, items: Sequence[base_dataclass]):
                # Initialize the ListCollection with the items
                super().__init__(items)
                self.underlying_type = base_dataclass
                self._add_properties()

        # Transfer attributes and methods from the original class to the new class
        for name, value in vars(cls).items():
            if not name.startswith("__"):
                setattr(ListCollectionSubClass, name, value)

        # Transfer annotations for better type checking and editor support
        if is_dataclass(base_dataclass):
            # _fields = dataclasses.fields(base_dataclass)
            # cls_annotations = {field.name: list[field.type] for field in _fields}
            # cls_annotations.update(getattr(cls, "__annotations__", {}))
            cls_annotations = get_type_hints(cls)
        elif isinstance(base_dataclass, BaseModel):
            raise NotImplementedError("Pydantic models are not supported yet")
        else:
            raise TypeError("The ListCollection must be of dataclasses or Pydantic models.")

        # Ensure list types for collection fields
        for field in fields(base_dataclass):
            field_type = getattr(base_dataclass, field.type.__name__, field.type)
            cls_annotations[field.name] = list[field_type]

        # Combine annotations from base_dataclass and cls
        combined_annotations = {**base_annotations, **cls_annotations}
        setattr(ListCollectionSubClass, "__annotations__", combined_annotations)

        # Copy docstring and other attributes if needed
        ListCollectionSubClass.__doc__ = cls.__doc__

        return ListCollectionSubClass

    return decorator
