import itertools
import math
from textwrap import dedent
from more_itertools import bucket

import plotly.graph_objects as go
from networkx.drawing import spring_layout

from satisfactory_tools.core.process import Process, ProcessNode


def make_hover_label(process: ProcessNode):
    return dedent(f"""
    {process.name}<br>
    Recipe: TODO<br>
    Scale: {process.scale}
    """)


def plot_process(process: Process, layout=spring_layout):
    edges_x = []
    edges_y = []

    positions = layout(process.graph)

    for edge in process.graph.edges():
        x0, y0 = positions[edge[0]]
        edges_x.append(x0)
        edges_y.append(y0)


        x1, y1 = positions[edge[1]]
        edges_x.append(x1)
        edges_y.append(y1)

        edges_x.append(None)
        edges_y.append(None)


    max_scale = max(n.scale for n in process.internal_nodes)
    point_scale = 20
    point_sizes = [(math.tanh(n.scale  / max_scale) + 1) * point_scale for n in process.internal_nodes]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edges_x,
            y=edges_y,
            mode='lines+markers',
            hoverinfo='none',
            line_shape='spline',
            marker=dict(
                symbol="arrow-wide",
                size=10,
                color="black",
                angleref="previous",
                standoff=point_scale//2
            ),
            showlegend=False
        )
    )

    buckets = bucket(process.internal_nodes, lambda x: x.name)
    for name in buckets:
        nodes = buckets[name]
        x, y = zip(*positions.values())
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=dict(symbol='circle-dot',
                            size=point_sizes,
                            # color=[m.process_root.color for m in ordered_vertices],
                            ),
                text=[make_hover_label(v) for v in process.graph.nodes],
                hovertemplate="%{text}<extra></extra>",
                # TODO: show machine types in legend
                showlegend=False,
            )
        )

    # TODO: better sizing, theming
    fig.update_layout(
        autosize=True,
        xaxis={
            'showgrid': False,  # thin lines in the background
            'zeroline': False,  # thick line at x=0
            'visible': False,  # numbers below
        },
        yaxis={
            'showgrid': False,  # thin lines in the background
            'zeroline': False,  # thick line at x=0
            'visible': False,  # numbers below
        }
    )

    return fig

