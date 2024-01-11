from abc import abstractmethod
from contextlib import nullcontext
from functools import partial
from typing import Callable, Protocol, Self

from nicegui import run, ui
from nicegui.element import Element

from satisfactory_tools.plotting.tables import Table
from satisfactory_tools.ui.models import OptimizationResult, Optimizer
from satisfactory_tools.ui.widgets import Picker, Setter


class View(Protocol):
    @abstractmethod
    def render(self):
        ...

    # TODO: update and reset methods?

    async def run_and_render(self, callback: Callable[[], ...], result_view: Self, render_context: Element | None = None):
        # FIXME: better way to run sub processes and deal with result
        result = await run.cpu_bound(callback)

        with (render_context or nullcontext()):
            result_view(result).render()


class PickerView(View):
    def __init__(self, model: Picker):
        self.model = model

    def render(self):
        self.model.render_search_box(ui)

        with ui.row(wrap=True) as row:
            row.classes("max-h-80 max-w-96 overflow-scroll")
            self.model.render_category_selectors(ui)

        with ui.row(wrap=True) as row:
            row.classes("max-h-80 max-w-96 overflow-scroll")
            self.model.render_selectors(ui)


class SetterView(View):
    def __init__(self, model: Setter):
        self.model = model

    def render(self):
        with ui.column():
            self.model.render_setters(ui)

        self.model.render_search_box(ui)

class OptimizationResultView(View):
    def __init__(self, model: OptimizationResult):
        self.model = model

    def render(self):
        with ui.expansion(self.model.process.name) as container:
            # ui.plotly(self.model.graph())
            container.classes("w-full")
            with ui.card():
                ui.label(f"Total Machines: {sum((node.scale for node in self.model.process.internal_nodes)):.2f}")
                ui.label(f"Total Power Production: {self.model.process.power_production: .2f}")
                ui.label(f"Total Power Consumption: {self.model.process.power_consumption: .2f}")
            ui.echart(self.model.graph()).classes("aspect-video w-full h-full")

            self._render_table(self.model.material_table())
            self._render_table(self.model.machines_table())
            for name, table in self.model.per_machine_tables().items():
                with ui.card():
                    ui.label(name)
                    self._render_table(table)


    @staticmethod
    def _render_table(table: Table) -> None:
            columns = [{"name": label, "label": label, "field": label, "required": True} for label in table.column_headers]
            rows = [
                {k: v for k, v in zip(table.column_headers, row)}
                for row in table.rows
            ]

            ui.table(columns=columns, rows=rows)



class OptimizerView(View):
    def __init__(self, model: Optimizer, output_element: Element):
        self.model = model
        self.output_element = output_element

    def render(self):
        # TODO: set name
        with ui.expansion("Target Output") as ex:
            ex.classes("w-full")
            SetterView(self.model.output_setter).render()
        with ui.expansion("Input Constraints") as ex:
            ex.classes("w-full")
            SetterView(self.model.input_setter).render()
            with ui.row():
                ui.switch("Apply").bind_value(self.model.__dict__, "include_input")
                ui.button("Clear", on_click=self.model.clear_input)
        with ui.expansion("Available Recipes") as ex:
            ex.classes("w-full")
            PickerView(self.model.process_picker).render()
        with ui.card():
            ui.input("name").bind_value(self.model.__dict__, "name")
            with ui.row():
                ui.button("Maximize output", on_click=partial(self.run_and_render, self.model.optimize_output, OptimizationResultView, self.output_element))
                ui.button("Minimize input", on_click=partial(self.run_and_render, self.model.optimize_input, OptimizationResultView, self.output_element))

