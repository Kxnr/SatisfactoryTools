from pathlib import Path

from nicegui import ui

from satisfactory_tools.config.parser import ConfigParser
from satisfactory_tools.ui.models import Optimizer
from satisfactory_tools.ui.views import OptimizerView

config = ConfigParser(Path("./Docs.json")).parse_config()

# tags = ["".join(random.choices(string.ascii_letters, k=random.randint(5, 10))) for _ in range(15)]
# items = {"".join(random.choices(string.ascii_letters, k=random.randint(5, 10))): i for i in range(200)}
# tag_assignments = {tag: set(random.choices(list(items.keys()), k=random.randint(4, 40))) for tag in tags}
# test_collection = CategorizedCollection(items, tag_assignments)

# optimizer = Optimizer(materials, processes)
optimizer = Optimizer(config.materials, config.recipes)


with ui.header(elevated=True):
    ui.label("Satisfactory Planner")

with ui.grid(columns=3) as row:
    # TODO: move back to collapsible left drawer
    row.classes("w-full")
    planning_column = ui.column()
    result_column = ui.column().classes("flex-col-reverse")
    planning_column.classes("col-span-1 border w-full")
    result_column.classes("col-span-2 w-full")

with planning_column:
    optimizer_view = OptimizerView(optimizer, result_column)
    optimizer_view.render()


print("run")
ui.run(reload=False)
