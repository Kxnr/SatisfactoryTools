from textwrap import dedent

import plotly.graph_objects as go
from process import Process


def make_row(values: list[str]):
    return "<tr>" + "".join([f"<td>{v}</td>" for v in values]) + "</tr>"

def make_table(headers: list[str], values: list[list[str]]):
    header = make_row(headers)
    rows = "\n".join([make_row(row) for row in values])

    return dedent(f"""
    <table>
    <thead>
    {header}
    </thead>
    <tbody>
    {rows}
    </tbody>
    </table>""")

def recipe_summary(process: Process):
    headers = ["Machine Type", "Count", "Recipe", "Ingredients", "Products"]
    rows = []
    for node in process.graph.nodes:
        rows.append([node.name,
                     node.scale,
                     node.name,
                     "<br>".join([f"{name}: {value * node.scale:.2f}" for name, value in node.input_materials]),
                     "<br>".join([f"{name}: {value * node.scale:.2f}" for name, value in node.output_materials]),
                         ])

    # transpose row to column major order
    go.Table(header=dict(values=headers), cells=dict(values=list(map(list, zip(*rows)))))

    return make_table(headers, rows)


