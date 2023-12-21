from nicegui import ui
from .widgets import fuzzy_sort_picker
from satisfactory_tools.categorized_collection import CategorizedCollection
import random
import string


tags = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) for _ in range(15)]
items = {"".join(random.choices(string.ascii_letters, k=random.randint(5, 10))): i for i in range(200)}
tag_assignments = {tag: set(random.choices(list(items.keys()), k=random.randint(4, 40))) for tag in tags}
test_collection = CategorizedCollection(items, tag_assignments)

ui.dark_mode()

# TODO: use an optimizer class to sage the optimization state
with ui.stepper().props("vertical").classes("w-full") as stepper:
    with ui.step("Target Output"):
        fuzzy_sort_picker(ui, test_collection)
        ui.button("Apply", on_click=stepper.next)
    with ui.step("Input Constraints"):
        fuzzy_sort_picker(ui, test_collection)
        with ui.row():
            ui.button("Skip", on_click=stepper.next)
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=stepper.previous)
    with ui.step("Available Recipes"):
        fuzzy_sort_picker(ui, test_collection)
        with ui.row():
            ui.button("Apply", on_click=stepper.next)
            ui.button("Previous", on_click=stepper.previous)
    with ui.step("Optimize"):
        with ui.row():
            # TODO: more description
            ui.button("Maximize output")
            ui.button("Minimize input")
            ui.button("Previous", on_click=stepper.previous)

ui.run()
