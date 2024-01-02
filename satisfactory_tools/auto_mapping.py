from typing import Generic, TypeVar, Iterable, Any, get_args
from collections.abc import Mapping

T = TypeVar("T")
S = TypeVar("S")


MISSING = object()

class AutoMapping(Generic[T]):
    """
    Automatically treat a collection of models as a dictionary keyed by any of the model fields.
    Should not be used in performance critical code, as mappings are generated on demand or
    iterate over the collection. In other words, does not promise O(1) lookup.
    """

    # TODO: bind S to T
    class _Indexer(Generic[S]):
        def __init__(self, field_name: str, items: Iterable[S]):
            self.field_name = field_name
            self._items = items

        def __getitem__(self, k: Any) -> "AutoMapping[S]":
            return AutoMapping([item for item in self._items if getattr(item, self.field_name, MISSING) == k])

        def __iter__(self):
            yield from (getattr(item, self.field_name) for item in self._items)

        def __len__(self):
            return len(self.items)

    def __init__(self, values: Iterable[T]):
        self.values = list(values)

    def __getattr__(self, name: str):
        # Not checking whether the attr exists--non existent attributes will just return no results
        return self._Indexer(name, self.values)

    def __iter__(self):
        yield from self.values

    def __getitem__(self, k: int) -> T:
        return self.values[k]
