from satisfactory_tools.config.standardization import ConfigData
from satisfactory_tools.core.process import ProcessNode
from tests import MATERIAL_NAMES, Materials

_MATERIAL_FRACTION = len(MATERIAL_NAMES) // 4
_SUBSET = _MATERIAL_FRACTION // 2
RAW_MATERIALS = MATERIAL_NAMES[:_MATERIAL_FRACTION]
FIRST_ORDER_MATERIALS = MATERIAL_NAMES[_MATERIAL_FRACTION:2*_MATERIAL_FRACTION]
SECOND_ORDER_MATERIALS = MATERIAL_NAMES[2*_MATERIAL_FRACTION:3*_MATERIAL_FRACTION]
FINAL_ORDER_MATERIALS = MATERIAL_NAMES[3*_MATERIAL_FRACTION:4*_MATERIAL_FRACTION]

CONFIG = ConfigData(display_name="test", class_name="test")
# extractors for first quarter of resources
EXTRACTORS = [
    ProcessNode(name=f"extractor_{name}", input_materials=Materials(), output_materials=Materials(**{name: 10}), power_production=0, power_consumption=0, machine=CONFIG)
    for name in RAW_MATERIALS
]

# paired producer from first quarter to second quarter
FIRST_ORDER_PROCESSES = [
    ProcessNode(name=f"first_order_{in_name}_to_{out_name}", input_materials=Materials(**{in_name: 15}), output_materials=Materials(**{out_name: 7}), power_production=0, power_consumption=0, machine=CONFIG)
    for in_name, out_name in zip(RAW_MATERIALS, FIRST_ORDER_MATERIALS)
]

# paired producer from second quarter to third quarter 
SECOND_ORDER_PROCESSES = [
    ProcessNode(name=f"second_order_{in_name}_to_{out_name}", input_materials=Materials(**{in_name: 21}), output_materials=Materials(**{out_name: 9}), power_production=0, power_consumption=0, machine=CONFIG)
    for in_name, out_name in zip(FIRST_ORDER_MATERIALS, SECOND_ORDER_MATERIALS)
    ]

# producers that take first and second order products to produce fourth quarter product
FINAL_PROCESSES = [
    ProcessNode(name=f"final_order_{first_in}_{second_in}_to_{out}", input_materials=Materials(**{first_in: 14, second_in: 12}), output_materials=Materials(**{out: 2}), power_production=0, power_consumption=0, machine=CONFIG) for (first_in, second_in), out
    in zip(zip(FIRST_ORDER_MATERIALS, SECOND_ORDER_MATERIALS), FINAL_ORDER_MATERIALS)
]

# processes that take second order products and produce first order ingredients
FEEDBACK_PROCESSES = [
    ProcessNode(name=f"feedback_{in_name}_to_{out_name}", input_materials=Materials(**{in_name: 10}), output_materials=Materials(**{out_name: 5}), power_production=0, power_consumption=0, machine=CONFIG)
    for in_name, out_name in zip(SECOND_ORDER_MATERIALS, reversed(FIRST_ORDER_MATERIALS))
]

# take two second order ingredients and produce two final products
SIDE_PRODUCT_PROCESSES = [
    ProcessNode(name=f"side_product_{first_in}_{second_in}_to_{first_out}_{second_out}", input_materials=Materials(**{first_in: 6, second_in: 8}), output_materials=Materials(**{first_out: 2, second_out: 3}), power_production=0, power_consumption=0, machine=CONFIG) for (first_in, second_in), (first_out, second_out)
    in zip(zip(SECOND_ORDER_MATERIALS[:_SUBSET], SECOND_ORDER_MATERIALS[_SUBSET:]), zip(FINAL_ORDER_MATERIALS[:_SUBSET], FINAL_ORDER_MATERIALS[_SUBSET:]))
]

# TODO
# take second order ingredients and make power
# GENERATOR_PROCESSES = [
#
# ]
