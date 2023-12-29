import itertools
import re
from dataclasses import asdict, dataclass
from typing import Iterable

from satisfactory_tools.config.standardization import (
    CYCLES_PER_MINUTE,
    ConfigData,
    get_class_name,
    standardize,
)

BUILDABLE_KEYS = [
    # assembler, constructor, blender, oilrefinery, foundry, smelter, manufacturer
    "FGBuildableManufacturer",
    # collider
    "FGBuildableManufacturerVariablePower",
]

EXTRACTOR_KEYS = [
    "FGBuildableResourceExtractor",
    "FGBuildableWaterPump"
]

GENERATOR_KEYS = [
    "FGBuildableGeneratorFuel",
    "FGBuildableGeneratorNuclear",
    "FGBuildableGeneratorGeoThermal"
]


def _values_for_key_list(simple_config: dict[str, ...], key_list: list[str]) -> Iterable[...]:
    yield from itertools.chain.from_iterable(simple_config[key].values() for key in key_list)


@dataclass
class MachineData(ConfigData):
    power_consumption: float
    power_production: float

@dataclass
class ExtractorData(MachineData):
    resources: list[str]
    cycle_time: float
    items_per_cycle: float

@dataclass
class GeneratorData(MachineData):
    fuel_resource_class: str
    fuel_load: float

    supplemental_resource: str
    supplement_load: float

    byproduct: str
    byproduct_amount: float


@dataclass
class Machines:
    producers: list[MachineData]
    extractors: list[ExtractorData]
    generators: list[GeneratorData]


def parse_machines(simple_config: dict[str, ...]) -> Machines:
    producers = [_parse_normal_machine(config) for config in _values_for_key_list(simple_config, BUILDABLE_KEYS)]
    extractors = [_parse_extractor(config) for config in _values_for_key_list(simple_config, EXTRACTOR_KEYS)]
    generators = [_parse_generator(config) for config in _values_for_key_list(simple_config, GENERATOR_KEYS)]

    return Machines(producers=producers, extractors=extractors, generators=generators)


def _parse_normal_machine(machine_config: dict[str, ...]) -> MachineData:
    power_consumption = float(machine_config["mPowerConsumption"])
    power_production = float(machine_config.get("mPowerProduction", 0))
    name = standardize(machine_config["mDisplayName"])
    key = machine_config["ClassName"]

    return MachineData(class_name=machine_config.get("mClassName") or machine_config["ClassName"],
                            display_name=machine_config["mDisplayName"],
                            power_production=power_production,
                            power_consumption=power_consumption)


def _parse_extractor(extractor_config: dict[str, ...]) -> ExtractorData:
    particle_map_pattern = r"\(ResourceNode.*?=.*?\.(\w+).*?,ParticleSystem.*?\)"

    items_per_cycle = float(extractor_config["mItemsPerCycle"])
    duration = float(extractor_config["mExtractCycleTime"]) / CYCLES_PER_MINUTE

    if extractor_config.get("mAllowedResources"):
        resources: Iterable[str] = map(get_class_name, extractor_config["mAllowedResources"].strip("()").split(","))
    elif extractor_config.get("mParticleMap"):
        resources = re.findall(particle_map_pattern, extractor_config["mParticleMap"])
    else:
        raise KeyError("Missing resources key")

    base_config = _parse_normal_machine(extractor_config)
    return ExtractorData(
        resources=list(resources),
        cycle_time=duration,
        items_per_cycle=items_per_cycle,
        **asdict(base_config)
    )


def _parse_generator(generator_config: dict[str, ...]) -> GeneratorData:
    # TODO: this is a class of fuels, rather than a fuel itself
    fuel_class = generator_config["mFuelClass"]

    supplemental_resource = generator_config["mSupplementalResourceClass"]
    supplemental_amount = float(generator_config["mSupplementalLoadAmount"])

    by_product = generator_config["mByproduct"]
    by_product_amount = generator_config["mByproductAmount"]

    fuel_load = float(generator_config["mFuelLoadAmount"])

    base_config = _parse_normal_machine(generator_config)

    return GeneratorData(
        fuel_resource_class=fuel_class,
        fuel_load = fuel_load,
        supplemental_resource=supplemental_resource,
        supplement_load=supplemental_amount,
        byproduct= by_product,
        byproduct_amount = by_product_amount,
        **asdict(base_config)
    )
