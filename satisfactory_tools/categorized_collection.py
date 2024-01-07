from collections import defaultdict
from typing import Generic, Iterable, TypeVar

from typing_extensions import Self

K = TypeVar("K")
V = TypeVar("V")


class CategorizedCollection(Generic[K, V]):
    """
    Class  that stores a dictionary and categories for each of its items. This allows
    access to items directly, as well as by category.
    """
    _values: dict[K, V]
    # tags maps tags to keys, inverse maps keys to tags
    _tags: dict[str, set[K]]
    _inverse_tags: dict[K, set[str]]

    def __init__(self, items: dict[K, V] | None = None, tags: dict[str, set[K]] | None = None):
        self._tags = defaultdict(set)
        self._inverse_tags = defaultdict(set)
        if tags is not None:
            self._tags.update(tags)
            for tag, keys in tags.items():
                for key in keys:
                    self._inverse_tags[key].add(tag)

        self._values = items or {}

    def keys(self) -> Iterable[K]:
        yield from self._values.keys()

    def items(self) -> Iterable[tuple[K, V]]:
        yield from self._values.items()

    def values(self) -> Iterable[V]:
        yield from self._values.values()

    def update(self, other: Self) -> None:
        self._values.update(dict(other.items()))

        for tag, keys in other.tags.items():
            for key in keys:
                self.set_tag(key, tag)

    def set_tag(self, key: K, tags: str | Iterable[str]) -> None:
        if isinstance(tags, str):
            tags = [tags]

        for tag in tags:
            self._tags[tag].add(key)
            self._inverse_tags[key].add(tag)

    def __getitem__(self, key: K) -> V:
        return self._values[key]

    def __setitem__(self, key: K, value: V) -> None:
        self._values[key] = value

    def __contains__(self, key: K) -> bool:
        return key in self._values

    @property
    def tags(self) -> dict[str, set[K]]:
        return self._tags

    def value_tags(self, key: K) -> set[str]:
        return self._inverse_tags[key]

    def tag(self, tag: str) -> Self:
        value_keys = self._tags[tag]
        inverse_tags = {v: self._inverse_tags[v] for v in value_keys}
        tags_dict = defaultdict(set)
        for k, value_set in inverse_tags.items():
            for v in value_set:
                tags_dict[v].add(k)

        values_dict = {k: self._values[k] for k in value_keys}

        return type(self)(values_dict, tags_dict)
