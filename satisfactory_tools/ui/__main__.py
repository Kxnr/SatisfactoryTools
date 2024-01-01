from nicegui import ui, run
from satisfactory_tools.ui.models import Optimizer
from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.plotting.graph import plot_process
import random
from functools import partial
import string

from satisfactory_tools.config import parse_config

config = parse_config("./Docs.json")

# tags = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) for _ in range(15)]
# items = {"".join(random.choices(string.ascii_letters, k=random.randint(5, 10))): i for i in range(200)}
# tag_assignments = {tag: set(random.choices(list(items.keys()), k=random.randint(4, 40))) for tag in tags}
# test_collection = CategorizedCollection(items, tag_assignments)

# optimizer = Optimizer(materials, processes)
optimizer = Optimizer(config.materials, config.recipes)

column = ui.column()

def render_something():
    with column:
        ui.label("Test Result")

async def optimize(func):
    print("optimizing")
    result = await run.cpu_bound(func)
    print("rendering")

    with column:
        with ui.expansion("Result"):
            ui.plotly(plot_process(result)).classes("w-full")

with ui.header(elevated=True):
    ui.button(on_click=lambda: left_drawer.toggle(), icon="menu")
    ui.label("Satisfactory Planner")
    with ui.left_drawer(fixed=False) as left_drawer:
        left_drawer.props("width=500")
        with ui.stepper().props("vertical") as stepper:
            with ui.step("Target Output") as step:
                optimizer.set_target_output(ui)
                ui.button("Apply", on_click=stepper.next)
            with ui.step("Input Constraints") as stp:
                optimizer.set_input_constraints(ui)
                with ui.row():
                    ui.button("Skip", on_click=lambda: (stepper.next(), optimizer.clear_input_constraints()))
                    # TODO: re-set constraints if previously skipped
                    ui.button("Apply", on_click=stepper.next)
                    ui.button("Previous", on_click=stepper.previous)
            with ui.step("Available Recipes") as step:
                optimizer.set_machines(ui)
                with ui.row():
                    ui.button("Apply", on_click=stepper.next)
                    ui.button("Previous", on_click=stepper.previous)
            with ui.step("Optimize") as step:
                with ui.row():
                    # TODO: more description
                    # TODO: render optimization result
                    ui.button("Maximize output", on_click=partial(optimize, optimizer.optimize_output))
                    ui.button("Minimize input", on_click=partial(optimize, optimizer.optimize_input))
                    ui.button("Previous", on_click=stepper.previous)


ui.run()