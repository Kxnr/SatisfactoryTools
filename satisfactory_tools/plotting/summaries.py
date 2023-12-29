from material import MaterialSpec
from process import Process


def total_power(process: Process):
    return sum(node.scale * node.power_consumption
               for node in process.graph.nodes())


def summarize_materials(materials: MaterialSpec):
    pass


def machine_counts(process: Process):
    pass
