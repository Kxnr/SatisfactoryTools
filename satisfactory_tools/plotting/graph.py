import itertools
import math
from textwrap import dedent
from more_itertools import bucket

import plotly.graph_objects as go
from igraph import Graph

from satisfactory_tools.core.process import Process, ProcessNode


def make_hover_label(process: ProcessNode):
    return dedent(f"""
    {name}<br>
    Recipe: TODO<br>
    Scale: {process.scale}
    """)


def plot_process(process: Process, layout=Graph.layout_auto):
    edges_x = []
    edges_y = []

    for edge in process.graph.edges():
        x0, y0 = process.graph.nodes[edge[0]]["pos"]
        edges_x.append(x0)
        edges_y.append(y0)


        x1, y1 = process.graph.nodes[edge[1]]["pos"]
        edges_x.append(x1)
        edges_y.append(y1)


    max_scale = max(n.scale for n in process.internal_nodes)
    point_scale = 20
    point_sizes = [(math.tanh(n.scale  / max_scale) + 1) * point_scale for n in process.internal_nodes]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
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
    ),

    )

    # TODO: add one trace per category
    for name, nodes in bucket(process.internal_nodes, lambda x: x.name):
        points = [node["pos"] for node in nodes]
        x, y = zip(*points)
        fig.add_trace(go.Scatter(x=x,
                             y=y,
                             mode='markers',
                             marker=dict(symbol='circle-dot',
                                         size=point_sizes,
                                         # color=[m.process_root.color for m in ordered_vertices],
                                         ),
                             text=[make_hover_label(v) for v in ordered_vertices],
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
        },
        height=1000
    )

    return fig

