from typing import Protocol, Callable, Self
from abc import abstractmethod
from satisfactory_tools.ui.models import Optimizer, OptimizationResult
from satisfactory_tools.ui.widgets import Setter, Picker 
from nicegui.element import Element
from nicegui import ui, run
from contextlib import nullcontext
from functools import partial


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
        self.model.render_search_box(ui)

        with ui.column():
            self.model.render_setters(ui)


class OptimizationResultView(View):
    def __init__(self, model: OptimizationResult):
        self.model = model

    def render(self):
        with ui.expansion(self.model.process.name) as container:
            container.classes("w-full")
            # ui.plotly(self.model.graph())
            ui.echart(self.model.graph()).classes("aspect-video w-full h-full")

            # TODO: table view, add tooltips on rows to show recipe
            table = self.model.table()
            columns = [{"name": label, "label": label, "field": label, "required": True} for label in table.column_headers]
            rows = [
                {k: v.replace("\n", "<br/>") for k, v in zip(table.column_headers, row)}
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
                ui.button("Skip", on_click=self.model.clear_input)
                # TODO: re-set constraints if previously skipped
                ui.button("Apply", on_click=self.model.set_input)
        with ui.expansion("Available Recipes") as ex:
            ex.classes("w-full")
            PickerView(self.model.process_picker).render()
        ui.input("name")
        with ui.row():
            ui.button("Maximize output", on_click=partial(self.run_and_render, self.model.optimize_output, OptimizationResultView, self.output_element))
            ui.button("Minimize input", on_click=partial(self.run_and_render, self.model.optimize_input, OptimizationResultView, self.output_element))

