from abc import abstractmethod
from contextlib import nullcontext
from functools import partial
from typing import Callable, Protocol, Self
import re

from nicegui import run, ui
from nicegui.element import Element

from satisfactory_tools.plotting.tables import Table
from satisfactory_tools.ui.models import OptimizationResult, Optimizer
from satisfactory_tools.ui.widgets import Picker, Setter


def get_trailing_digits(value: str) -> str | None:
    m = re.search(r"\d+$", value)
    return m and m.group()


class View(Protocol):
    container = ui.element

    @abstractmethod
    def render(self):
        # TODO: auto wrap in container, use __init_subclass__ auto decorator?
        ...

    def clear(self):
        self.container.clear()

    def update(self):
        self.clear()
        self.render()

    def delete(self):
        self.container.delete()


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
            container.classes("w-full")
            # TODO: on_click with overwrite handling, name input, real placement for button
            ui.button("save")

            ui.echart(self.model.graph()).classes("aspect-video w-full h-full")

            self._render_table(Table(
                column_headers=["Total Machines", "Total Power Production", "Total Power Consumption"],
                rows=[[f"{sum((node.scale for node in self.model.process.internal_nodes)):.2f}",
                      f"{self.model.process.power_production: .2f}",
                      f"{self.model.process.power_consumption: .2f}"]]
            )).classes("w-full")
            self._render_table(self.model.material_table()).classes("w-full")
            self._render_table(self.model.machines_table()).classes("w-full")

            # TODO: layout for per-machine tables
            with ui.row().classes("w-full"):
                for name, table in self.model.per_machine_tables().items():
                    with ui.card():
                        ui.label(name)
                        self._render_table(table)


    @staticmethod
    def _render_table(table: Table):
            columns = [{"name": label, "label": label, "field": label, "required": True} for label in table.column_headers]
            rows = [
                {k: v for k, v in zip(table.column_headers, row)}
                for row in table.rows
            ]

            return ui.table(columns=columns, rows=rows)



class OptimizerView(View):
    # TODO: load
    def __init__(self, model: Optimizer, output_element: Element):
        self.model = model
        self.output_element = output_element
        self.output_view = SetterView(self.model.output_setter)
        self.input_view = SetterView(self.model.input_setter)
        self.process_view = PickerView(self.model.process_picker)

    def render(self):
        async def optimize_and_render(callback: Callable[[], OptimizationResult]) -> None:
            result = await run.cpu_bound(callback)

            # TODO: prompt on duplicate, delete existing process. We can await a button event
            # TODO: in prompt
            self.model.process_picker.add(self.model.name, result, {"custom",})
            self.process_view.update()

            trailing_digits = get_trailing_digits(self.model.name)

            if trailing_digits:
                self.model.name = f"{self.model.name[:-len(trailing_digits)]}{int(trailing_digits) + 1}"
            else:
                self.model.name += " 1"

            with self.output_element:
                OptimizationResultView(result).render()

        with ui.expansion("Target Output") as ex:
            ex.classes("w-full")
            self.output_view.render()
        with ui.expansion("Input Constraints") as ex:
            ex.classes("w-full")
            self.input_view.render()
            with ui.row():
                ui.switch("Apply").bind_value(self.model.__dict__, "include_input")
                ui.button("Clear", on_click=self.model.clear_input)
        with ui.expansion("Available Recipes") as ex:
            ex.classes("w-full")
            self.process_view.render()
        with ui.card():
            ui.input("name").bind_value(self.model.__dict__, "name")
            with ui.row():
                # TODO: disable button while optimizing--optimization is generally fast enough that
                # TODO: this isn't all that important
                ui.button("Maximize output", on_click=partial(optimize_and_render, self.model.optimize_output))
                ui.button("Minimize input", on_click=partial(optimize_and_render, self.model.optimize_input))


