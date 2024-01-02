from nicegui import ui, run
from satisfactory_tools.ui.models import Optimizer, OptimizationResult
from satisfactory_tools.ui.views import OptimizerView
from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.plotting.graph import plot_process
import random
from functools import partial
import string
from pathlib import Path

from satisfactory_tools.config import ConfigParser

config = ConfigParser(Path("./Docs.json")).parse_config()

# tags = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) for _ in range(15)]
# items = {"".join(random.choices(string.ascii_letters, k=random.randint(5, 10))): i for i in range(200)}
# tag_assignments = {tag: set(random.choices(list(items.keys()), k=random.randint(4, 40))) for tag in tags}
# test_collection = CategorizedCollection(items, tag_assignments)

# optimizer = Optimizer(materials, processes)
optimizer = Optimizer(config.materials, config.recipes)

column = ui.column()
optimizer_view = OptimizerView(optimizer, column)

with ui.header(elevated=True):
    ui.button(on_click=lambda: left_drawer.toggle(), icon="menu")
    ui.label("Satisfactory Planner")
    with ui.left_drawer(fixed=False) as left_drawer:
        left_drawer.props("width=500")
        optimizer_view.render()

print("run")
ui.run(reload=False)
