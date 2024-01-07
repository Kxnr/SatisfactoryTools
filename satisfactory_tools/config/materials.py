import itertools
from dataclasses import dataclass, fields
from enum import Enum

from satisfactory_tools.config.standardization import ConfigData
from satisfactory_tools.core.material import MaterialSpec

RESOURCE_KEYS = ("FGItemDescriptor",
                 "FGResourceDescriptor",
                 "FGConsumableDescriptor",
                 "FGItemDescriptorBiomass",
                 "FGAmmoTypeProjectile",
                 "FGItemDescriptorNuclearFuel",
                 "FGAmmoTypeInstantHit",
                 "FGAmmoTypeSpreadshot",
                 "FGEquipmentDescriptor"
                 )


class MaterialType(Enum):
    SOLID: str = "RF_SOLID"
    LIQUID: str = "RF_LIQUID"
    GAS: str = "RF_GAS"

    def scale(self) -> float:
        match self:
            case self.SOLID:
                return 1.0
            case _:
                return 1000.0



@dataclass(frozen=True)
class MaterialMetadata(ConfigData):
    material_type: MaterialType
    energy_value: float


def parse_materials(simple_config: dict[str, ...]) -> list[MaterialMetadata]:
    metadata: list[MaterialMetadata] = []
    for internal_name, item in itertools.chain.from_iterable((simple_config[key].items() for key in RESOURCE_KEYS)):
        name = item["mDisplayName"]
        material_type = MaterialType(item["mForm"])
        metadata.append(MaterialMetadata(class_name = internal_name,
                                    display_name = item["mDisplayName"],
                                    material_type = material_type,
                                    energy_value = float(item["mEnergyValue"])))

    return metadata 

