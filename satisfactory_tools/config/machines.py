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


@dataclass(frozen=True)
class MachineData(ConfigData):
    power_consumption: float
    power_production: float

@dataclass(frozen=True)
class ExtractorData(MachineData):
    resources: list[str]
    cycle_time: float
    items_per_cycle: float

@dataclass(frozen=True)
class FuelManifest:
    fuel: str
    byproduct: str | None = None
    supplemental: str | None = None

    fuel_load: float = 0
    byproduct_load: float = 0
    supplemental_load: float = 0

@dataclass(frozen=True)
class GeneratorData(MachineData):
    fuels: tuple[FuelManifest, ...]

@dataclass(frozen=True)
class Machines:
    producers: list[MachineData]
    extractors: list[ExtractorData]
    generators: list[GeneratorData]


def parse_machines(simple_config: dict[str, ...]) -> Machines:
    producers = [_parse_normal_machine(config) for config in _values_for_key_list(simple_config, BUILDABLE_KEYS)]
    extractors = [_parse_extractor(config) for config in _values_for_key_list(simple_config, EXTRACTOR_KEYS)]
    generators = [_parse_generator(config) for config in _values_for_key_list(simple_config, GENERATOR_KEYS)]
    generators = [g for g in generators if g is not None]

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
        resources: Iterable[str] = [get_class_name(r) for r in extractor_config["mAllowedResources"].strip("()").split(",")]
    elif extractor_config.get("mParticleMap"):
        resources = re.findall(particle_map_pattern, extractor_config["mParticleMap"])
    else:
        raise KeyError("Missing resources key")

    base_config = _parse_normal_machine(extractor_config)
    return ExtractorData(
        resources=tuple(resources),
        cycle_time=duration,
        items_per_cycle=items_per_cycle,
        **asdict(base_config)
    )


def _parse_generator(generator_config: dict[str, ...]) -> GeneratorData | None:
    # TODO: this is a class of fuels, rather than a fuel itself
    if "mFuel" not in generator_config:
        return None

    fuels = tuple(
        FuelManifest(
            fuel=fuel_config["mFuelClass"],
            byproduct=fuel_config["mByproduct"],
            supplemental=fuel_config["mSupplementalResourceClass"],

            fuel_load=float(generator_config["mFuelLoadAmount"] or 0),
            byproduct_load=float(fuel_config["mByproductAmount"] or 0),
            supplemental_load=float(generator_config["mSupplementalLoadAmount"] or 0)
        )
        for fuel_config in generator_config["mFuel"]
    )

    base_config = _parse_normal_machine(generator_config)

    return GeneratorData(
        fuels=fuels,
        **asdict(base_config)
    )
