from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory.core.process return ProcessNode, Process
from typing import Iterable

class Optimizer:

    def __init__(self, materials: type[MaterialSpec], available_processes: CategorizedCollection[str, ProcessNode]):
        self.include_power = False

        self._input = None
        self._output = None
        self._materials = materials
        self._available_proesses = available_processes

    def set_target_output(self, ui) -> Setter:
        # TODO get fields on MaterialSpec
        self._output = fuzzy_sort_setter(ui, self._materials)

    def set_input_constraints(self, ui) -> Setter:
        # TODO get fields on MaterialSpec
        self._input = fuzzy_sort_setter(ui, self._materials)

    def choose_machines(self, ui) -> Picker:
        self._machines = fuzzy_sort_picker(ui, self._available_proesses)

    @property
    def input_materials(self) -> MaterialSpec:
        return self._input and self._materials(**self._input.values)

    @property
    def output_materials(self) -> MaterialSpec:
        if not self._output:
            raise ValueError("Output not set.")

        return self._materials(**self.output.values)

    @property
    def processes(self) -> Iterable[ProcessNode]:
        if not self._machines:
            raise ValueError("Processes not set")

        return self._machines

    def optimize_input(self) -> Process:
        return Process.minimize_input(self.output_materials, self.processes, self.include_power)

    def optimize_output(self) -> Process:
        return Process.maximize_output(self.input_materials, self.output_materials, self.processes, self.include_power)

    def optimize_power(self) -> Process:
        pass
