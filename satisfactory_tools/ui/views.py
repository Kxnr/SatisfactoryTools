from typing import Protocol


class View(Protocol):
    def render(self):
        ...

    def update(self):
        ...


class OptimizerView:
    pass


class OptimizationResultView:
    pass

