import json
import re
from dataclasses import dataclass, make_dataclass, field

from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.config.machines import MachineData, parse_machines, Machines
from satisfactory_tools.config.materials import parse_materials
from satisfactory_tools.config.recipes import RecipeData, parse_recipes
from satisfactory_tools.core.material import MaterialSpec
from satisfactory_tools.core.process import ProcessNode


def simplify_config(game_config: list[dict[..., ...]]) -> dict[str, ...]:
    simple_config = {}
    native_class_pattern = r".*\.(\w+)'?"

    for config in game_config:
        if not (match := re.match(native_class_pattern, config["NativeClass"])):
            continue

        key = match.group(1)

        simple_config[key] = {item["ClassName"]: item for item in config["Classes"]}

    return simple_config


@dataclass
class Config:
    recipes: CategorizedCollection[str, ProcessNode]
    materials: MaterialSpec


def parse_config(config_path: str, encoding="utf-16"):
    with open(config_path, "r", encoding=encoding) as f:
        config_data = simplify_config(json.loads(f.read()))
        materials = parse_materials(config_data)
        machines = parse_machines(config_data)
        recipes = parse_recipes(config_data)
        # TODO: saved recipes

        # TODO: pydantic class to have aliases
        materials = make_dataclass("Materials",
                                   [(material.display_name, float, field(default=0)) for material in materials],
                                   bases=(MaterialSpec,), frozen=True)

        process_nodes = _sythesize_recipes_and_machines(machines, recipes, materials)

    return Config(materials=materials, recipes=process_nodes)


def _sythesize_recipes_and_machines(machines: Machines, recipes: list[RecipeData], materials: type[MaterialSpec]) -> CategorizedCollection[str, ProcessNode]:
    result: CategorizedCollection[str, ProcessNode] = CategorizedCollection()

    machines_dict = {machine.class_name: machine for machine in machines.producers}

    for recipe in recipes:
        for machine_class in recipe.machines:
            machine = machines_dict[machine_class]
            result[recipe.class_name] = ProcessNode(name=recipe.display_name,
                                                    input_materials=materials(**recipe.inputs),
                                                    output_materials=materials(**recipe.outputs),
                                                    power_production=machine.power_production,
                                                    power_consumption=machine.power_consumption)

    for extractor in machines.extractors:
        for resource in extractor.resources:
        # TODO: cycle time
            result[extractor.class_name] = ProcessNode(name=extractor.display_name,
                                                       input_materials=materials.empty(),
                                                       output_materials=materials(**{resource: extrator.items_per_cycle}),
                                                       power_production=extractor.power_production,
                                                       power_consumption=extractor.power_consumption)

    for generator in machines.extractors:
        # TODO: need the material metadata to map from class name to resource name
        pass

    return result


def _tag_recipe_node():
    pass

