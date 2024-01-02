from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.core.process import ProcessNode, Process
from satisfactory_tools.core.material import MaterialSpec, MaterialSpecFactory
from satisfactory_tools.plotting import graph, sankey, tables
from satisfactory_tools.ui.widgets import Picker, Setter
from typing import Iterable, Protocol, Self
from pathlib import Path
import json
from abc import abstractmethod


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
            return Process(**json.load(f))

    def graph(self):
        return graph.plot_process(self.process)

    def sankey(self):
        return sankey.plot_process(self.process)

    def table(self):
        return tables.recipe_summary(self.process)

    def summary(self):
        return (
            f"Total Process Nodes: {len(self.process.internal_nodes)}"
            f"Total Power Production: {sum(node.power_production * node.scale for node in self.process.internal_nodes)}\n"
            f"Total Power Consumption: {sum(node.consumption * node.scale for node in self.process.internal_nodes)}\n"
        )


class Optimizer:
    def __init__(self, materials: MaterialSpecFactory, available_processes: CategorizedCollection[str, ProcessNode]):
        self.include_power = False
        self._include_input = False

        self._materials = materials

        self.output_setter: Setter = Setter(list(self._materials.keys()))
        self.input_setter: Setter = Setter(list(self._materials.keys()))
        self.process_picker: Picker = Picker(available_processes)

        self.clear_output()
        self.clear_input()
        self.clear_processes()

    def reset(self):
        self.clear_input()
        self.clear_output()
        self.clear_processes()

    def clear_output(self) -> None:
        self.output_setter.clear()

    def set_input(self) -> None:
        self.include_input = True

    def clear_input(self) -> None:
        self.input_setter.clear()
        self._include_input = False

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
        return OptimizationResult(Process.minimize_input(self.output_materials, list(self.processes), self.include_power))

    def optimize_output(self) -> OptimizationResult:
        if not self.input_materials:
            raise DependencyException("Available input required.")

        return OptimizationResult(Process.maximize_output(self.input_materials, self.output_materials, list(self.processes), self.include_power))

    def optimize_power(self) -> Process:
        raise NotImplementedError()

