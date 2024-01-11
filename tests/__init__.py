
from satisfactory_tools.core.material import MaterialSpecFactory

MATERIAL_NAMES = [chr(i) for i in range(97, 107)]

Materials = MaterialSpecFactory(**{name: 0 for name in MATERIAL_NAMES})

