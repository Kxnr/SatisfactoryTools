from dataclasses import dataclass, fields
from functools import singledispatchmethod
from numbers import Number
from typing import Any, Mapping
from collections import defaultdict
from pydantic import BaseModel, Field, RootModel

from typing_extensions import Self


class _SignalClass:
    """
    Used for single dispatch on Self type
    """


class HashableDict(RootModel):
    root: dict[str, float]

    def __init__(self, **kwargs):
        return super().__init__(kwargs)

    def __hash__(self) -> str:
        return hash(frozenset(self.root.items()))

    def items(self):
        yield from self.root.items()

    def keys(self):
        yield from self.root.keys()

    def values(self):
        yield from self.root.values()

    def __getitem__(self, name: str):
        return self.root[name]


class MaterialSpecFactory:
    def __init__(self, **kwargs):
        self.initial_values = kwargs

    def __call__(self, **kwargs):
        return MaterialSpec(material_values=HashableDict(**(self.initial_values | kwargs)))

    def empty(self) -> Self:
        return self()

    def keys(self):
        yield from self.initial_values.keys()



class MaterialSpec(BaseModel, _SignalClass, frozen=True):
    material_values: HashableDict = Field(default_factory=HashableDict)

    @classmethod
    def empty(cls) -> Self:
        return cls()

    def __lt__(self, other: Number) -> Self:
        """
        Return a MaterialSpec where values less than the given number are kept and remaining values set to
        their default.
        """

        return type(self)(
            **{name: value for (name, value) in self if value < other}
        )

    def __gt__(self, other: Number) -> Self:
        """
        Return a MaterialSpec where values greater than the given number are kept and remaining values set to
        their default.
        """

        return type(self)(
            **{name: value for (name, value) in self if value > other}
        )

    def __le__(self, other: Number) -> Self:
        """
        Return a MaterialSpec where values less than or equal to the given number are kept and remaining
        values set to their default.
        """

        return type(self)(
            **{name: value for (name, value) in self if value <= other}
        )

    def __ge__(self, other: Number) -> Self:
        """
        Return a MaterialSpec where values greater than or equal to the given number are kept and remaining
        values set to their default.
        """

        return type(self)(
            **{name: value for (name, value) in self if value >= other}
        )

    def __add__(self, other: Self | Any) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented

        result = {}
        for name, value in self:
            result[name] = value + other[name]
        return type(self)(**result)

    def __sub__(self, other: Self | Any) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented

        result = {}
        for name, value in self:
            result[name] = value - other[name] 
        return type(self)(**result)

    def __mul__(self, scalar: Number) -> Self:
        result = {}
        for name, value in self:
            result[name] = value * scalar
        return type(self)(**result)

    def __rmul__(self, scalar: Number) -> Self:
        return self * scalar 

    @singledispatchmethod
    def __truediv__(self, other: Any) -> Number | Self:
        return NotImplemented

    @__truediv__.register
    def _(self, other: Number) -> Self:
        result = {}
        for name, value in self:
            result[name] = value / other 

        return type(self)(**result)

    @__truediv__.register(_SignalClass)
    def _(self, other: Self) -> Number:
        if all(value == 0 for _, value in other):
            raise ZeroDivisionError("Cannot divide by empty MaterialSpec.")

        return min(self.material_values[name] / value for name, value in other if value > 0)

    @singledispatchmethod
    def __floordiv__(self, other: Any) -> int | Self:
        return NotImplemented

    @__floordiv__.register(_SignalClass)
    def _(self, other: Self) -> int:
        if all(value == 0 for _, value in other):
            raise ZeroDivisionError("Cannot divide by empty MaterialSpec.")

        return min(self.material_values[name] // value for name, value in other if value > 0)

    @__floordiv__.register
    def _(self, other: Number) -> Self:
        result = {}
        for name, value in self:
            result[name] = value // other 
        return type(self)(**result)

    def __iter__(self):
        yield from self.material_values.items()

    def values(self):
        yield from self.material_values.values()

    def __or__(self, other: Self) -> Self:
        if not isinstance(other, MaterialSpec):
            return NotImplemented

        return type(self)(
            **{name: value for (name, value), (_, matched_value) in zip(self, other) if matched_value > 0})

    def __getitem__(self, item: str) -> Number:
        return self.material_values[item]

    def __repr__(self) -> str:
        return "\n".join(f"{name}: {value}" for name, value in self if value > 0)

