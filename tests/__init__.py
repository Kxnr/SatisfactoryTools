from dataclasses import field, make_dataclass

from satisfactory_tools.core.material import MaterialSpec

MATERIAL_NAMES = [chr(i) for i in range(97, 107)]

Materials = make_dataclass("Materials",
                           [(name, float, field(default=0)) for name in MATERIAL_NAMES],
                           bases=(MaterialSpec,), frozen=True)

