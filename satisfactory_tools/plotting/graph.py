import math
import pprint

from networkx.drawing import spring_layout

from satisfactory_tools.core.process import Process


def plot_process(process: Process, layout=spring_layout):
    def scale_coordinate(pt: float) -> float:
        return (pt + 1) * 250

    def scale_value(value: float, pre_scale: float=.1) -> float:
        scaled_value = 1 / (1 + math.exp(2 - (value*pre_scale)))
        return scaled_value * 25

    min_scale = min((node.scale for node in process.internal_nodes))

    positions = layout(process.graph)
    categories = [{"name": machine.display_name} for machine in {node.machine for node in process.graph.nodes}]
    category_indices = {cat["name"]: i for i, cat in enumerate(categories)}
    config = {
        "legend": {},
        "tooltip": {},
        "responsive": True,
        "maintainAspectRatio": False,
        "series": [
            {
                "type": 'graph',
                "layout": 'none',
                "label": {
                    "show": True,
                    "position": 'inside',
                    "formatter": '{b}',
                    "color": "#000",
                    "fontStyle": "normal",
                    "fontWeight": "normal",

                },
                "draggable": True,
                "roam": True,
                "edgeSymbol": ['circle', 'arrow'],
                "edgeSymbolSize": [0, 8],
                "edgeLabel": {
                    "fontSize": 20
                },
                "nodes": [
                    {"name": node.name,
                     "x": scale_coordinate(positions[node][0]),
                     "y": scale_coordinate(positions[node][1]),
                     "category": category_indices[node.machine.display_name],
                     "value": f"{node.scale:.2f}",
                     "symbolSize": scale_value(node.scale, pre_scale=1/min_scale)
                     }
                     for node in process.graph.nodes
                ],
                "categories": categories,
                # TODO: scale edges and show direction, base on material properties of edge (also TODO)
                "edges": [
                    {"source": edge[0].name,
                     "target": edge[1].name}
                    for edge in process.graph.edges()
                ],
                "itemStyle": {},
                "emphasis": {
                    "focus": 'adjacency',
                    "lineStyle": {
                        "width": 10
                    }
                },
                "select": {},
                "autoCurveness": True
            }
        ]
    }
    pprint.pprint(config)
    return config
