import plotly.graph_objects as go
from satisfactory_tools.core.process import Process


def plot_process(process: Process):
    # in digraph, last element of tuple is weights
    source, target, *_ = zip(*process.graph.edges)
    nodes = list(process.graph.nodes)
    source = list((nodes.index(node) for node in source))
    target = list((nodes.index(node) for node in target))

    # TODO: scale links with edge properties. WIP while edge properties not implemented
    labels, weights = zip(*[(nodes[ind].name, nodes[ind].scale) for ind in source])

    # labels, weights = zip(*[get_materials_for_link(start, end, ordered_vertices) for (start, end) in edges])

    fig = go.Figure()
    fig.add_trace(
        go.Sankey(
            node=dict(
                label = [nodes[ind].name for ind in source]
            ),
            link=dict(
                source=source,
                target=target,
                value=weights,
                label=labels
            )
        )
    )
    return fig 
