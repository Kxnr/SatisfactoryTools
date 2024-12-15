import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

from pathlib import Path
from nicegui import ui

from satisfactory_tools.config.parser import ConfigParser
from satisfactory_tools.ui.models import Optimizer
from satisfactory_tools.ui.views import OptimizerView

config = ConfigParser(Path("./Docs.json")).parse_config()

optimizer = Optimizer(config.materials, config.recipes)


with ui.header(elevated=True):
    ui.label("Satisfactory Planner")

with ui.splitter(value=25) as splitter:
    splitter.classes("w-full")
    with splitter.before:
        planning_column = ui.column()
        planning_column.classes("w-full")
    with splitter.after:
        result_column = ui.column().classes("flex-col-reverse shrink")
        result_column.classes("w-full")

with planning_column:
    optimizer_view = OptimizerView(optimizer, result_column)
    optimizer_view.render()

ui.run(reload=True)
