from math import isclose

import satisfactory_tools.core.process as module
from satisfactory_tools.config.standardization import ConfigData
from tests import Materials

CONFIG = ConfigData(display_name="test", class_name="test")

def test_process_node():
    inputs = Materials(a=2, b=4)
    outputs = Materials(c=2, d=4)

    module.ProcessNode(name="Test", input_materials=inputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

def test_process_node_shift():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

    assert inputs >> first == midputs
    assert inputs >> first >> second == outputs
    assert 2*inputs >> first >> second == 2*outputs

    assert second >> outputs == midputs
    assert first >> second >> outputs == inputs
    assert first >> second >> 2*outputs == 2*inputs


def test_simple_optimization_minimize_input():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    source = module.ProcessNode(name="source", input_materials=Materials(), output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)
    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

    optimal = module.Process.minimize_input(4*outputs, [source, first, second], include_power=False)

    assert len(optimal._graph.nodes()) == 3
    assert optimal.input_materials == Materials.empty()
    assert optimal.output_materials == 4*outputs
    assert all(isclose(node.scale, 4) for node in optimal._graph.nodes())


def test_optimization_extraneous_recipes_minimize_input():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    extraneous = Materials(g=1, h=9)

    source = module.ProcessNode(name="source", input_materials=Materials(), output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)
    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)
    third = module.ProcessNode(name="third", input_materials=inputs, output_materials=extraneous, power_production=0, power_consumption=0, machine=CONFIG)
    fourth = module.ProcessNode(name="fourth", input_materials=extraneous, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)

    optimal = module.Process.minimize_input(4*outputs, [source, first, second, third, fourth], include_power=False)

    assert len(optimal._graph.nodes()) == 3
    assert optimal.input_materials == Materials.empty()
    assert optimal.output_materials == 4*outputs
    assert all(isclose(node.scale, 4) for node in optimal._graph.nodes())


def test_optimization_loop_available_minimize_input():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    extraneous = Materials(g=1, h=9)

    source = module.ProcessNode(name="source", input_materials=Materials(), output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)
    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

    loop_1 = module.ProcessNode(name="loop_1", input_materials=outputs, output_materials=extraneous, power_production=0, power_consumption=0, machine=CONFIG)
    loop_2 = module.ProcessNode(name="loop_2", input_materials=extraneous, output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)

    optimal = module.Process.minimize_input(4*outputs, [source, first, second, loop_1, loop_2], include_power=False)

    assert len(optimal._graph.nodes()) == 3
    assert optimal.input_materials == Materials.empty()
    assert optimal.output_materials == 4*outputs
    assert all(isclose(node.scale, 4) for node in optimal._graph.nodes())


def test_optimization_simple_maximize_output():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

    optimal = module.Process.maximize_output(4*inputs, outputs, [first, second], include_power=False)

    assert len(optimal._graph.nodes()) == 2
    assert optimal.input_materials == 4*inputs
    assert optimal.output_materials == 4*outputs
    assert all(isclose(node.scale, 4) for node in optimal._graph.nodes())


def test_optimization_extraneous_recipes_maximize_output():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    extraneous = Materials(g=1, h=9)

    first = module.ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = module.ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)
    third = module.ProcessNode(name="third", input_materials=inputs, output_materials=extraneous, power_production=0, power_consumption=0, machine=CONFIG)
    fourth = module.ProcessNode(name="fourth", input_materials=extraneous, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)

    optimal = module.Process.maximize_output(4*inputs, outputs, [first, second, third, fourth], include_power=False)

    assert len(optimal._graph.nodes()) == 2
    assert optimal.input_materials == 4*inputs
    assert optimal.output_materials == 4*outputs
    assert all(isclose(node.scale, 4) for node in optimal._graph.nodes())


# def test_optimization_loop_available_maximize_output():
#     pass


# TODO: tests that include power
# TODO: tests with fork in solution
