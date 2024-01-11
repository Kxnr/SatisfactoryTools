import pytest
from tests import Materials
from satisfactory_tools.core.process import ProcessNode, Process
import satisfactory_tools.plotting.graph as graph_module
from satisfactory_tools.config.standardization import ConfigData

CONFIG = ConfigData(display_name="test", class_name="test")

@pytest.fixture
def process():
    inputs = Materials(a=2, b=4)
    midputs = Materials(e=4, f=7)
    outputs = Materials(c=2, d=4)

    extraneous = Materials(g=1, h=9)

    source = ProcessNode(name="source", input_materials=Materials(), output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)
    first = ProcessNode(name="first", input_materials=inputs, output_materials=midputs, power_production=0, power_consumption=0, machine=CONFIG)
    second = ProcessNode(name="second", input_materials=midputs, output_materials=outputs, power_production=0, power_consumption=0, machine=CONFIG)

    loop_1 = ProcessNode(name="loop_1", input_materials=outputs, output_materials=extraneous, power_production=0, power_consumption=0, machine=CONFIG)
    loop_2 = ProcessNode(name="loop_2", input_materials=extraneous, output_materials=inputs, power_production=0, power_consumption=0, machine=CONFIG)

    yield Process.from_nodes([source, first, second, loop_1, loop_2])


def test_graph(process):

    graph_module.plot_process(process)
