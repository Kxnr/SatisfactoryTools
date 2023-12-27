from dataclasses import dataclass, fields, replace, Field
from functools import singledispatchmethod
from typing import Any, Iterable

import networkx as nx
import numpy as np
from pydantic import BaseModel, ConfigDict
from scipy.optimize import linprog
from typing_extensions import Self

from satisfactory_tools.core.material import MaterialSpec


def dataclass_to_list(dc):
    return [getattr(dc, f.name) for f in fields(dc)]


class SolutionFailedException(Exception):
    ...

class _SignalClass:
    """
    Used for single dispatch on Self type
    """

class ProcessNode(BaseModel, _SignalClass):
    model_config = ConfigDict(frozen=True)
    name: str  # TODO: use an enum of node types, rather than names, to make plotting easier
    input_materials: MaterialSpec
    output_materials: MaterialSpec
    power_production: float
    power_consumption: float
    # TODO: merge with CompositeNode
    # internal_nodes: set[Self] = Field(default_factory=set)
    scale: float = 1

    @classmethod
    def from_nodes(cls, *nodes: Self) -> Self:
        empty = nodes[0].input_materials.empty()  # FIXME: why
        sum_inputs = sum((node.input_materials for node in nodes), empty)
        sum_outputs = sum((node.output_materials for node in nodes), empty)

        net_inputs = (sum_inputs - (sum_outputs | sum_inputs)) > 0
        net_outputs = (sum_outputs - (sum_inputs | sum_outputs)) > 0

        power_production = sum(node.power_production for node in nodes)
        power_consumption = sum(node.power_consumption for node in nodes)

        return cls(name="Composite", input_materials=net_inputs, output_materials=net_outputs,power_production=power_production, power_consumption=power_consumption, internal_nodes=set(nodes))

    def __repr__(self) -> str:
        ingredients = " ".join(repr(self.scaled_input).splitlines())
        products = " ".join(repr(self.scaled_output).splitlines())

        return f"{ingredients} >> {products}"

    @singledispatchmethod
    def __rshift__(self, other: Any) -> Self | MaterialSpec:
        """
        self >> other
        """
        return NotImplemented

    @__rshift__.register
    def _(self, other: MaterialSpec) -> MaterialSpec:
        scale = other // self.scaled_output
        return self.scaled_input * scale

    @__rshift__.register(_SignalClass)
    def _(self, other: Self) -> Self:
        return self.from_nodes(self, other)

    @singledispatchmethod
    def __lshift__(self, other: Any) -> Self | MaterialSpec:
        """
        Solve for outputs or join process nodes
        self << other 
        """
        return NotImplemented

    @__lshift__.register
    def _(self, other: MaterialSpec) -> MaterialSpec:
        scale = other // self.scaled_input
        return self.scaled_output * scale

    @__lshift__.register(_SignalClass)
    def _(self, other: Self) -> Self:
        return self.from_nodes(other, self)

    def __rrshift__(self, other: Self | MaterialSpec | Any) -> Self | MaterialSpec:
        """
        Solve for inputs or join process nodes
        other >> self 
        """
        return self << other 

    def __rlshift__(self, other: Self | MaterialSpec | Any) -> Self | MaterialSpec:
        """
        Solve for outputs
        other << self
        """
        return self >> other

    def __mul__(self, scalar: float) -> Self:
        """
        Scale up this recipe
        """
        return self.model_copy(update={"scale": scalar * self.scale})

    def has_input(self, material: str) -> bool:
        return getattr(self.input_materials, material) > 0

    def has_output(self, material: str) -> bool:
        return getattr(self.output_materials, material) > 0

    @property
    def scaled_input(self) -> MaterialSpec:
        return self.input_materials * self.scale

    @property
    def scaled_output(self) -> MaterialSpec:
        return self.output_materials * self.scale


class Process(ProcessNode):
    """
    Store graph as adjacency matrix, no real value in adjacency list here because optimization runs on the full graph
    rather than traversal. This also saves us from the issue of binding a ProcessNodes to Optimization instances
    1:1, since it may be useful to re-use the same CompositeProcessNode, representing a factory, in multiple
    different contexts or optimizations. Representing the graph this way saves us from needing an additional
    intermediate class or modifying nodes.

    # TODO: save solution to Process
    """
    _graph: nx.MultiGraph

    @classmethod
    def from_nodes(cls, nodes_or_graph: Iterable[ProcessNode] | nx.MultiGraph) -> Self:
        if isinstance(nodes_or_graph, nx.MultiGraph):
            _graph =nodes_or_graph
        else:
            _graph = cls._make_graph(nodes_or_graph)

        self = super().from_nodes(*_graph.nodes)
        self._graph = _graph
        return self

    @classmethod
    def _filter_eligible_nodes(cls, output_node: ProcessNode, available_nodes: list[ProcessNode]) -> list[ProcessNode]:
        graph = cls._make_graph([output_node] + available_nodes)
        return nx.ancestors(graph, output_node) | {output_node}

    @staticmethod
    def _make_graph(nodes: list[ProcessNode]) -> nx.MultiGraph:
        graph = nx.MultiGraph()
        graph.add_nodes_from(nodes)

        for i, node_1 in enumerate(nodes):
            for node_2 in nodes[i:]:
                # TODO: add all materials as attributes to node
                # TODO: add scale attribute to node
                # TODO: add cost attribute to node
                if any(v for _, v in node_1.input_materials | node_2.output_materials):
                    graph.add_edge(node_1, node_2)
                if any(v for _, v in node_2.input_materials | node_1.output_materials):
                    graph.add_edge(node_2, node_1)

        return graph

    @classmethod
    def minimize_input(cls, target_output: MaterialSpec, process_nodes: list[ProcessNode],include_power=False) -> Self:
        """
        Find the weights on process nodes that produce the desired output with the least input and
        process cost.
        
        # TODO: availability constraints
        """
        output = ProcessNode(name="Output", input_materials=target_output, output_materials=target_output, power_production=0, power_consumption=0)

        connected_nodes = cls._filter_eligible_nodes(output, process_nodes)
        costs = [1 for _ in connected_nodes]  # TODO: cost per recipe
        output_lower_bound = np.array(dataclass_to_list(target_output))

        # matrix where each machine is a column and each material is a row
        material_constraints = np.array(
            [dataclass_to_list(node.output_materials - node.input_materials) 
                + ([node.power_consumption - node.power_production] if include_power else []) 
                for node in connected_nodes]).T

        # use -1 factor to convert problem of materials * coeefficients >= outputs to minimization
        # production >= target
        bounds = (0, None)
        solution = linprog(c=costs,
                           bounds=bounds,
                           A_ub=material_constraints * -1, b_ub=output_lower_bound * -1)

        if not solution.success:
            raise SolutionFailedException(solution)

        # TODO: remove output node from solution
        # TODO: remove source node from solution
        return cls.from_nodes([node * scale for node, scale in zip(connected_nodes, solution.x) if scale >= 0])

    @classmethod
    def maximize_output(cls, available_materials: MaterialSpec, target_output: MaterialSpec, process_nodes: list[ProcessNode], include_power=False) -> Self:
        """
        Maximize production of output materials where input materials are constrained. If extractors
        are allowed, problem may be unbounded due to unlimited material supply. This may be addressed
        by future work that constrains extractors by total available supply or changes how extractor
        cost is modelled.
        """
        # sinks node for output, mirror to minimize input requiring source nodes for ingredients
        output = ProcessNode(name="Output", input_materials=target_output, output_materials=target_output.empty(), power_production=0, power_consumption=0)

        visited = cls._filter_eligible_nodes(output, process_nodes)

        # small penalty for using machines, to avoid creating redundant loops, reward for producing
        # more output
        costs = [-1 if node is output else .0001 for node in visited]  # TODO: cost per recipe

        # matrix where each machine is a column and each material is a row. production is positive,
        # consumption is negative
        material_constraints = np.array(
            [dataclass_to_list(node.output_materials - node.input_materials) for node in visited]).T

        material_consumption_upper_bound = dataclass_to_list(available_materials)

        # -1*consumption <= available
        # byproducts >= 0
        bounds = (0, None)

        solution = linprog(c=costs,
                           bounds=bounds,
                           A_ub=material_constraints*-1,
                           b_ub=material_consumption_upper_bound)

        if not solution.success:
            raise SolutionFailedException(solution)

        # TODO: remove sink node from solution
        # TODO: remove source node from solution
        return cls.from_nodes([node * scale for node, scale in zip(visited, solution.x) if scale >= 0])

    @classmethod
    def optimize_power(self, target_output: float, available_nodes: Iterable[ProcessNode]) -> Self:
        ...
