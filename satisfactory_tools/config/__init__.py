import json
import re
from dataclasses import dataclass, make_dataclass, field
from pathlib import Path
from more_itertools import only

from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.auto_mapping import AutoMapping
from satisfactory_tools.config.machines import MachineData, parse_machines, Machines, GeneratorData, ExtractorData
from satisfactory_tools.config.materials import parse_materials, MaterialMetadata, MaterialType
from satisfactory_tools.config.recipes import RecipeData, parse_recipes
from satisfactory_tools.config.standardization import standardize
from satisfactory_tools.core.material import MaterialSpec, MaterialSpecFactory
from satisfactory_tools.core.process import ProcessNode


@dataclass
class Config:
    recipes: CategorizedCollection[str, ProcessNode]
    materials: MaterialSpecFactory


class ConfigParser:
    def __init__(self, config_path: Path, user_dir: Path | None = None, encoding="utf-16"):
        self.config_path = config_path
        self.user_dir = user_dir

        with config_path.open(encoding=encoding) as f:
            config_data = self._simplify_config(json.load(f))
            self.material_data = AutoMapping(parse_materials(config_data))
            self.recipe_data = parse_recipes(config_data)
            self.machine_data = parse_machines(config_data)

    @staticmethod
    def _simplify_config(game_config: list[dict[..., ...]]) -> dict[str, ...]:
        simple_config = {}
        native_class_pattern = r".*\.(\w+)'?"

        for config in game_config:
            if not (match := re.match(native_class_pattern, config["NativeClass"])):
                continue

            key = match.group(1)

            simple_config[key] = {item["ClassName"]: item for item in config["Classes"]}

        return simple_config

    def parse_config(self) -> Config:
        materials = MaterialSpecFactory(**{material.display_name: 0 for material in self.material_data.values})
        process_nodes = self._synthesize_recipes_and_machines(materials)
        return Config(materials=materials, recipes=process_nodes)

    def _synthesize_recipes_and_machines(self, material_class: MaterialSpecFactory) -> CategorizedCollection[str, ProcessNode]:
        result: CategorizedCollection[str, ProcessNode] = CategorizedCollection()

        producers_lookup: AutoMapping[MachineData] = AutoMapping(self.machine_data.producers)

        for recipe in self.recipe_data:
            for machine_class in recipe.machines:
                # ignores recipes that can't be created by parsed machines
                for machine in producers_lookup.class_name[machine_class].values:
                    result[recipe.class_name] = ProcessNode(name=recipe.display_name,
                                                            input_materials=self._dict_to_material_spec(recipe.inputs, material_class),
                                                            output_materials=self._dict_to_material_spec(recipe.outputs, material_class),
                                                            power_production=machine.power_production,
                                                            power_consumption=machine.power_consumption)

        for extractor in self.machine_data.extractors:
            for resource in extractor.resources:
                # TODO: cycle time
                result[extractor.class_name] = ProcessNode(name=extractor.display_name,
                                                   input_materials=material_class.empty(),
                                                   output_materials=self._dict_to_material_spec({resource: extractor.items_per_cycle}, material_class),
                                                   power_production=extractor.power_production,
                                                   power_consumption=extractor.power_consumption)

        for generator in self.machine_data.generators:
            # TODO: need the material metadata to map from class name to resource name
            pass

        return result

    def _tag_process_node(self, node: ProcessNode):
        pass

    def _dict_to_material_spec(self, materials_dict: dict[str, float], materials_factory: MaterialSpecFactory) -> MaterialSpec:
        # names may be display or class names
        def lookup_material(name: str) -> MaterialMetadata:
            maybe = only(self.material_data.class_name[name].values, None)

            if maybe is None:
                maybe = only(self.material_data.display_name[name].values, None)

            if maybe is None:
                # FIXME: custom exception
                raise KeyError("Missing material")

            return maybe

        def get_scale(material_type: MaterialType) -> float:
            match material_type:
                case MaterialType.SOLID:
                    return 1.0
                case _:
                    return 1000.0

        try:
            return materials_factory(**{material.display_name: value / get_scale(material.material_type) for material, value in zip(map(lookup_material, materials_dict.keys()), materials_dict.values())})
        except KeyError:
            # FIXME: custom exception
            raise Exception("Recipe requires excluded material or produces excluded product.")

    def parse_user_dir(self):
        # load saved user ProcessNodes
        pass

def _tag_recipe_node():
    pass

