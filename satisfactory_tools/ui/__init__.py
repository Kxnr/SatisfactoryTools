from nicegui import ui
from satisfactory_tools.ui.components import Optimizer
from satisfactory_tools.categorized_collection import CategorizedCollection
import random
from functools import partial
import string


tags = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) for _ in range(15)]
items = {"".join(random.choices(string.ascii_letters, k=random.randint(5, 10))): i for i in range(200)}
tag_assignments = {tag: set(random.choices(list(items.keys()), k=random.randint(4, 40))) for tag in tags}
test_collection = CategorizedCollection(items, tag_assignments)

def ui_closure(ui, render):
    return partial(render, ui)

def step_one(ui):
    fuzzy_sort_setter(ui, test_collection)

from dataclasses import make_dataclass, field
from satisfactory_tools.core.material import MaterialSpec
Materials = make_dataclass("Materials",
                           [(name, float, field(default=0)) for name in items],
                           bases=(MaterialSpec,), frozen=True)

# optimizer = Optimizer(materials, processes)
optimizer = Optimizer(Materials, test_collection)

with ui.stepper().props("vertical").classes("w-full flex-wrap") as stepper:
    with ui.step("Target Output") as step:
        step.classes("flex-wrap")
        optimizer.set_target_output(ui)
        ui.button("Apply", on_click=stepper.next)
    with ui.step("Input Constraints") as stp:
        step.classes("flex-wrap")
        optimizer.set_input_constraints(ui)
        with ui.row():
            ui.button("Skip", on_click=lambda: (stepper.next(), optimizer.clear_input_constraints()))
            # TODO: re-set constraints if previously skipped
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=stepper.previous)
    with ui.step("Available Recipes") as step:
        step.classes("flex-wrap")
        optimizer.set_machines(ui)
        with ui.row():
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=stepper.previous)
    with ui.step("Optimize") as step:
        step.classes("flex-wrap")
        with ui.row():
            # TODO: more description
            # TODO: render optimization result
            ui.button("Maximize output", on_click=optimizer.optimize_output)
            ui.button("Minimize input", on_click=optimizer.optimize_input)
            ui.button("Previous", on_click=stepper.previous)

ui.run()
