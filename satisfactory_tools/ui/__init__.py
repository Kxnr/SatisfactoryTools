from nicegui import ui
from .widgets import fuzzy_sort_picker, fuzzy_sort_setter
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


with ui.stepper().props("vertical").classes("w-full flex-wrap") as stepper:
    with ui.step("Target Output") as step:
        step.classes("flex-wrap")
        closed_step_one = ui_closure(ui, step_one)
        closed_step_one()
        ui.button("Apply", on_click=lambda: (step.clear(), stepper.next()))
    with ui.step("Input Constraints") as stp:
        step.classes("flex-wrap")
        fuzzy_sort_setter(ui, test_collection)
        with ui.row():
            ui.button("Skip", on_click=stepper.next)
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=lambda: (stepper.previous(), closed_step_one()))
    with ui.step("Available Recipes") as step:
        step.classes("flex-wrap")
        fuzzy_sort_picker(ui, test_collection)
        with ui.row():
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=stepper.previous)
    with ui.step("Optimize") as step:
        step.classes("flex-wrap")
        with ui.row():
            # TODO: more description
            ui.button("Maximize output")
            ui.button("Minimize input")
            ui.button("Previous", on_click=stepper.previous)

ui.run()
