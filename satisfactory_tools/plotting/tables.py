from dataclasses import dataclass, field

from satisfactory_tools.core.process import Process, ProcessNode


@dataclass
class Table:
    column_headers: list[str] = field(default_factory=list)
    row_headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)

    def __repr__(self):
        a = ", ".join(self.column_headers)
        b = ", ".join(self.row_headers)
        c = []
        for row in self.rows:
            c.append(", ".join(row))

        return "\n".join((a, b, *c))


def production_summary(process: ProcessNode) -> Table:

    net_production = process.scaled_output - process.scaled_input

    headers = ["Material", "Total Production", "Total Consumption", "Net Production"]
    rows = []
    for material in process.scaled_input.keys():
        if material not in process.scaled_input and material not in process.scaled_output:
            continue
        rows.append([
            material,
            f"{process.scaled_output[material]:.2f}",
            f"{process.scaled_input[material]:.2f}",
            f"{net_production[material]:.2f}",
        ])

    table = Table(column_headers=headers, rows=rows)
    return table


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
