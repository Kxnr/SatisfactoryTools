import json
from pathlib import Path
from typing import Any, Iterable, Self

from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.core.material import MaterialSpec, MaterialSpecFactory
from satisfactory_tools.core.process import Process, ProcessNode
from satisfactory_tools.plotting import graph, tables
from satisfactory_tools.ui.widgets import Picker, Setter


class DependencyException(Exception):
    """
    Raised when pre-condition for action not set in ui.
    """


class OptimizationResult:
    def __init__(self, process: Process):
        self.process = process

    def save(self, path: Path) -> None:
        path.write_text(self.process.model_dump_json())

    @classmethod
    def load(cls, path: Path) -> Self:
        with path.open() as f:
            return cls(Process(**json.load(f)))

    def graph(self) -> dict[str, Any]:
        return graph.plot_process(self.process)

    def material_table(self) -> tables.Table:
        return tables.production_summary(self.process)

    def machines_table(self) -> tables.Table:
        return tables.machines_summary(self.process)

    def per_machine_tables(self) -> dict[str, tables.Table]:
        result: dict[str, tables.Table] = {}
        for node in self.process.internal_nodes:
            result[node.name] = tables.production_summary(node)

        return result


class Optimizer:
    def __init__(self, materials: MaterialSpecFactory, available_processes: CategorizedCollection[str, ProcessNode]):
        self.include_power = False
        self.include_input = False

        self._materials = materials

        self.output_setter: Setter = Setter(list(self._materials.keys()))
        self.input_setter: Setter = Setter(list(self._materials.keys()))
        self.process_picker: Picker = Picker(available_processes, default_state=True)

        self.name = "Result"

        self.clear_output()
        self.clear_input()
        self.clear_processes()

    def reset(self):
        self.clear_input()
        self.clear_output()
        self.clear_processes()

    def clear_output(self) -> None:
        self.output_setter.clear()

    def clear_input(self) -> None:
        self.input_setter.clear()
        self.include_input = False

    def clear_processes(self) -> None:
        self.process_picker.clear()

    @property
    def input_materials(self) -> MaterialSpec | None:
        if not self.include_input:
            return None

        return self._materials(**self.input_setter.values)

    @property
    def output_materials(self) -> MaterialSpec:
        return self._materials(**self.output_setter.values)

    @property
    def processes(self) -> Iterable[ProcessNode]:
        return self.process_picker.selected

    def optimize_input(self) -> OptimizationResult:
        return OptimizationResult(Process.minimize_input(self.output_materials, list(self.processes), self.include_power, self.name))

    def optimize_output(self) -> OptimizationResult:
        if not self.input_materials:
            raise DependencyException("Available input required.")

        return OptimizationResult(Process.maximize_output(self.input_materials, self.output_materials, list(self.processes), self.include_power, self.name))

    def optimize_power(self) -> Process:
        raise NotImplementedError()

