from textwrap import dedent
from dataclasses import dataclass, field

import plotly.graph_objects as go
from satisfactory_tools.core.process import Process


@dataclass
class Table:
    column_headers: list[str] = field(default_factory=list)
    row_headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


def production_summary(process: Process) -> Table:
    headers = ["Machine Type", "Count", "Recipe", "Ingredients", "Products"]
    rows = []
    for node in process.graph.nodes:
        # FIXME: using contains here is weird--Material should just support getting non-zero elements
        rows.append([node.machine.display_name,
                     f"{node.scale:.2f}",
                     node.name,
                     "\n".join([f"{name}: {value:.2f}" for name, value in node.scaled_input if name in node.scaled_input]),
                     "\n".join([f"{name}: {value:.2f}" for name, value in node.scaled_output if name in node.scaled_output]),
                    ])

    return Table(column_headers=headers, rows=rows)


def net_summary(process: Process) -> Table:
    # TODO
    ...

