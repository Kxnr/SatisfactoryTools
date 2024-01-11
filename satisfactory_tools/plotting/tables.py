from textwrap import dedent
from dataclasses import dataclass, field

from satisfactory_tools.core.process import Process, ProcessNode


@dataclass
class Table:
    column_headers: list[str] = field(default_factory=list)
    row_headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


def production_summary(process: ProcessNode) -> Table:

    total_production = sum((node.scaled_input for node in process.internal_nodes), process.scaled_input.empty())
    total_consumption = sum((node.scaled_output for node in process.internal_nodes), process.scaled_output.empty())
    net_production = process.scaled_output - process.scaled_input

    headers = ["Material", "Total Production", "Total Consumption", "Net Production"]
    rows = []
    for material in total_production.keys():
        if material not in total_production and material not in total_consumption:
            continue
        rows.append([
            material,
            f"{total_production[material]:.2f}",
            f"{total_consumption[material]:.2f}",
            f"{net_production[material]:.2f}",
        ])

    return Table(column_headers=headers, rows=rows)



def machines_summary(process: Process) -> Table:
    headers = ["Recipe", "Count", "Machine Type", "Power Production", "Power Consumption"]
    rows = []
    for node in process.graph.nodes:
        rows.append([node.name,
                     f"{node.scale:.2f}",
                     node.machine.display_name,
                     f"{node.power_production * node.scale:.2f}",
                     f"{node.power_consumption * node.scale:.2f}",
                    ])

    return Table(column_headers=headers, rows=rows)
