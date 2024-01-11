from dataclasses import dataclass, fields, replace
from functools import singledispatchmethod
from typing import Any, Iterable
from math import isclose
from collections import defaultdict
from more_itertools import distinct_combinations

import networkx as nx
import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from scipy.optimize import linprog
from typing_extensions import Self
from itertools import chain

from satisfactory_tools.core.material import MaterialSpec
from satisfactory_tools.config.standardization import ConfigData


class SolutionFailedException(Exception):
    ...

class _SignalClass(BaseModel):
    """
    Used for single dispatch on Self type
    """

class ProcessNode(_SignalClass):
    model_config = ConfigDict(frozen=True)
    name: str
    input_materials: MaterialSpec
    output_materials: MaterialSpec
    power_production: float
    power_consumption: float
    machine: ConfigData
    internal_nodes: frozenset["ProcessNode"] = Field(default_factory=frozenset)
    scale: float = 1


    @classmethod
    def from_nodes(cls, *nodes: Self, name: str="Composite") -> Self:
        empty = nodes[0].input_materials.empty()  # FIXME: why

        # TODO: hide input/output so that scale is unavoidable
        sum_inputs = sum((node.scaled_input for node in nodes), empty)
        sum_outputs = sum((node.scaled_output for node in nodes), empty)

        net_inputs = (sum_inputs - sum_outputs) > 0
        net_outputs = (sum_outputs - sum_inputs) > 0
        power_production = sum(node.power_production * node.scale for node in nodes)

        power_consumption = sum(node.power_consumption * node.scale for node in nodes)

        return cls(name=name, 
                   input_materials=net_inputs, 
                   output_materials=net_outputs,
                   power_production=power_production,
                   power_consumption=power_consumption,
                   machine=ConfigData(display_name=name, class_name=""),
                   internal_nodes=frozenset(nodes))

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

ProcessNode.update_forward_refs()


class Process(ProcessNode):
    """
    Store graph of nodes defining process.
    """
    _graph: nx.MultiGraph

    @classmethod
    def from_nodes(cls, nodes_or_graph: Iterable[ProcessNode] | nx.MultiDiGraph) -> Self:
        if isinstance(nodes_or_graph, nx.MultiDiGraph):
            _graph = nodes_or_graph
        else:
            _graph = cls._make_graph(nodes_or_graph)

        obj = super().from_nodes(*_graph.nodes)
        obj._graph = _graph
        return obj

    @classmethod
    def _filter_eligible_nodes(cls, output_node: ProcessNode, available_nodes: list[ProcessNode]) -> list[ProcessNode]:
        graph = cls._make_graph([output_node] + available_nodes, make_pool_nodes=False)
        return list(nx.ancestors(graph, output_node) | {output_node})

    @staticmethod
    def _make_graph(nodes: list[ProcessNode], make_pool_nodes: bool = True) -> nx.MultiGraph:
        graph = nx.MultiDiGraph()
        graph.add_nodes_from(nodes)

        def join_nodes(a: ProcessNode, b: ProcessNode, material: str):
            if material in b.output_materials and material in a.input_materials:
                graph.add_edge(b, a, material=material)

            if material in a.output_materials and material in b.input_materials:
                graph.add_edge(a, b, material=material)

        adjacency_dict = defaultdict(list)
        for node in nodes:
            material_requirements = node.input_materials | node.output_materials
            for material in material_requirements.keys():
                if material in material_requirements:
                    adjacency_dict[material].append(node)
        
        for material, nodes in adjacency_dict.items():
            if len(nodes) > 2 and make_pool_nodes:
                # make a pool node for this resource, so that we don't connect every machine that
                # has a byproduct to every other machine that uses that material
                # FIXME: material spec ergonomics
                input_count = sum((node.input_materials[material] for node in nodes))
                output_count = sum((node.output_materials[material] for node in nodes))
                input_materials = nodes[0].input_materials.empty({material: input_count})
                output_materials = nodes[0].output_materials.empty({material: output_count})
                name = f"{material} Pool"

                pool_node = ProcessNode(name=name, input_materials=input_materials, output_materials=output_materials, power_production=0, power_consumption=0, machine=ConfigDict(display_name=name, class_name=""))
                for node in nodes:
                    join_nodes(node, pool_node, material)
            else:
                for a, b in distinct_combinations(nodes, 2):
                    join_nodes(a, b, material)

        return graph

    @classmethod
    def minimize_input(cls, target_output: MaterialSpec, process_nodes: list[ProcessNode], include_power=False, name="Result") -> Self:
        """
        Find the weights on process nodes that produce the desired output with the least input and
        process cost.
        
        # TODO: availability constraints
        """
        output = ProcessNode(name="Output", input_materials=target_output, output_materials=target_output, power_production=0, power_consumption=0, machine=ConfigData(display_name="Output", class_name=""))

        connected_nodes = cls._filter_eligible_nodes(output, process_nodes)
        costs = [1 for _ in connected_nodes]  # TODO: cost per recipe
        output_lower_bound = np.array(list(target_output.values()))

        material_constraints = np.array(
            [
                list((node.output_materials - node.input_materials).values())
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
        return cls.from_nodes([node * scale for node, scale in zip(connected_nodes, solution.x) if not isclose(scale, 0) and node in process_nodes])

    @classmethod
    def maximize_output(cls, available_materials: MaterialSpec, target_output: MaterialSpec, process_nodes: list[ProcessNode], include_power=False, name="Result") -> Self:
        """
        Maximize production of output materials where input materials are constrained. If extractors
        are allowed, problem may be unbounded due to unlimited material supply. This may be addressed
        by future work that constrains extractors by total available supply or changes how extractor
        cost is modelled.
        """
        # sinks node for output, mirror to minimize input requiring source nodes for ingredients
        output = ProcessNode(name="Output", input_materials=target_output, output_materials=target_output.empty(), power_production=0, power_consumption=0, machine=ConfigData(display_name="Output", class_name=""))

        visited = cls._filter_eligible_nodes(output, process_nodes)

        # small penalty for using machines, to avoid creating redundant loops, reward for producing
        # more output
        costs = [-1 if node is output else .0001 for node in visited]  # TODO: cost per recipe

        # matrix where each machine is a column and each material is a row. production is positive,
        # consumption is negative
        material_constraints = np.array(
            [list((node.output_materials - node.input_materials).values()) for node in visited]).T

        material_consumption_upper_bound = list(available_materials.values())

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
        return cls.from_nodes([node * scale for node, scale in zip(visited, solution.x) if not isclose(scale, 0) and node in process_nodes])

    @classmethod
    def optimize_power(self, target_output: float, available_nodes: Iterable[ProcessNode]) -> Self:
        ...

    @property
    def graph(self):
        return self._graph
