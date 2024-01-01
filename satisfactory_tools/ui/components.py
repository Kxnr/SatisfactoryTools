from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.core.process import ProcessNode, Process
from satisfactory_tools.core.material import MaterialSpec
from satisfactory_tools.ui.widgets import Picker, Setter, fuzzy_sort_picker, fuzzy_sort_setter
from typing import Iterable


class Optimizer:
    def __init__(self, materials: type[MaterialSpec], available_processes: CategorizedCollection[str, ProcessNode]):
        self.include_power = False

        self._input: Setter | None = None
        self._output: Setter | None = None
        self._materials = materials
        self._available_proesses = available_processes
        self._machines: Picker | None = None

    def set_target_output(self, ui) -> None:
        self._output = fuzzy_sort_setter(ui, list(self._materials.keys()))

    def set_input_constraints(self, ui) -> None:
        self._input = fuzzy_sort_setter(ui, list(self._materials.keys()))

    def clear_input_constraints(self) -> None:
        self._input = None

    def set_machines(self, ui) -> None:
        self._machines = fuzzy_sort_picker(ui, self._available_proesses)

    @property
    def input_materials(self) -> MaterialSpec | None:
        return self._input and self._materials(**self._input.values)

    @property
    def output_materials(self) -> MaterialSpec:
        if not self._output:
            raise ValueError("Output not set.")

        return self._materials(**self._output.values)

    @property
    def processes(self) -> Iterable[ProcessNode]:
        if not self._machines:
            raise ValueError("Processes not set")

        return self._machines.selected

    def optimize_input(self) -> Process:
        return Process.minimize_input(self.output_materials, list(self.processes), self.include_power)

    def optimize_output(self) -> Process:
        return Process.maximize_output(self.input_materials, self.output_materials, list(self.processes), self.include_power)

    def optimize_power(self) -> Process:
        raise NotImplementedError()
