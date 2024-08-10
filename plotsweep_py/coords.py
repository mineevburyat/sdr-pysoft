from typing import Generic, TypeVar, List, Tuple, Protocol

R = TypeVar('R', bound='Ranged')

class Ranged(Protocol):
    ValueType = TypeVar('ValueType')
    
    def map(self, value: ValueType, limit: Tuple[int, int]) -> int:
        ...
    
    def key_points(self, hint) -> List[ValueType]:
        ...
    
    def range(self) -> range:
        ...
    
    def axis_pixel_range(self, limit: Tuple[int, int]) -> range:
        ...

class AsRangedCoord(Protocol):
    def into(self) -> R:
        ...

class DefaultFormatting:
    pass

class ReversedAxis(Generic[R]):
    def __init__(self, axis: R):
        self.axis = axis

    def map(self, value: R.ValueType, limit: Tuple[int, int]) -> int:
        return self.axis_pixel_range(limit).stop - self.axis.map(value, limit)

    def key_points(self, hint) -> List[R.ValueType]:
        return self.axis.key_points(hint)

    def range(self) -> range:
        return self.axis.range()

    def axis_pixel_range(self, limit: Tuple[int, int]) -> range:
        return self.axis.axis_pixel_range(limit)

class IntoReversedAxis(AsRangedCoord, Protocol):
    def reversed_axis(self) -> ReversedAxis[R]:
        return ReversedAxis(self.into())

def implement_into_reversed_axis(cls: R) -> None:
    cls.reversed_axis = lambda self: ReversedAxis(self.into())

