import plotly.graph_objects as go
from satisfactory_tools.core.process import Process


def plot_process(process: Process):
    source, target = zip(*process.graph.edges)
    source = list(source)
    target = list(target)

    # TODO: scale links with edge properties. WIP while edge properties not implemented
    labels, weights = [(node.name, node.scale) for node in source ]

    # labels, weights = zip(*[get_materials_for_link(start, end, ordered_vertices) for (start, end) in edges])

    fig = go.Figure()
    fig.add_trace(
        go.Sankey(
            node=dict(
                label = [node.name for node in source]
            ),
            link=dict(
                source=source,
                target=target,
                value=weights,
                label=labels
            )
        )
    )
    fig.show()
