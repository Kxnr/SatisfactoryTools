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
        with ui.expansion(self.model.process.name):
            ui.plotly(self.model.graph()).classes("w-full")


class OptimizerView(View):
    def __init__(self, model: Optimizer, output_element: Element):
        self.model = model
        self.output_element = output_element

    def render(self):
        with ui.stepper().props("vertical") as stepper:
            with ui.step("Target Output") as step:
                SetterView(self.model.output_setter).render()
                ui.button("Apply", on_click=stepper.next)
            with ui.step("Input Constraints") as stp:
                SetterView(self.model.input_setter).render()
                with ui.row():
                    ui.button("Skip", on_click=lambda: (stepper.next(), self.model.clear_input()))
                    # TODO: re-set constraints if previously skipped
                    ui.button("Apply", on_click=lambda: (stepper.next(), self.model.set_input()))
                    ui.button("Previous", on_click=stepper.previous)
            with ui.step("Available Recipes") as step:
                PickerView(self.model.process_picker).render()
                with ui.row():
                    ui.button("Apply", on_click=stepper.next)
                    ui.button("Previous", on_click=stepper.previous)
            with ui.step("Optimize") as step:
                with ui.row():
                    # TODO: more description
                    # TODO: render optimization result
                    ui.button("Maximize output", on_click=partial(self.run_and_render, self.model.optimize_output, OptimizationResultView, self.output_element))
                    ui.button("Minimize input", on_click=partial(self.run_and_render, self.model.optimize_input, OptimizationResultView, self.output_element))
                    ui.button("Previous", on_click=stepper.previous)

