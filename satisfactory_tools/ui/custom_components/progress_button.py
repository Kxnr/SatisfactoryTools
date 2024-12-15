from typing import Callable, Optional

from nicegui.elements.mixins.value_element import ValueElement

class ProgressButton(ValueElement, component='progress_button.js'):

    VALUE_PROP: str = 'value'

    def __init__(self, label: str, *, min: float = 0, max: float = 1, value: float = 0, on_change: Callable | None = None, on_click: Callable | None = None) -> None:
        super().__init__(value=value)
        self._props["label"] = label
        self._props["min"] = min
        self._props["max"] = max
        self.on("change", on_change)
        self.on("click", on_click)

