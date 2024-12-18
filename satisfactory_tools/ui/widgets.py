from functools import partial
from typing import Iterable

from nicegui import ui
from thefuzz import process

from satisfactory_tools.categorized_collection import CategorizedCollection
from satisfactory_tools.ui.custom_components.progress_button import ProgressButton


class Picker:
    default_visibility = True

    def __init__(self, elements: CategorizedCollection[str, ...], default_state: bool = False):
        self.elements = elements
        self.default_state = default_state
        self._selected = {key: self.default_state for key in self.elements.keys()}
        self._selector_visibility = {key: self.default_visibility for key in self.elements.keys()}

        self._category_visibility = {key: self.default_visibility for key in self.elements.keys()}
        self._category_counters = {key: 0 for key in self.elements.keys()}

    def clear(self):
        # TODO
        pass

    def render_category_selectors(self, ui: ui) -> None:
        for tag in self.elements.tags.keys():
            with ProgressButton(tag, min=0, max=len(self.elements.tag(tag)), on_click=partial(self._category_select, tag)) as button:
                button.bind_visibility_from(self._category_visibility, tag)
                button.bind_value_from(self._category_counters, tag)

    def render_search_box(self, ui: ui) -> None:
        searchbox = ui.input(placeholder="Search...", on_change=lambda e: self._filter(e.value))
        searchbox.props("clearable")

    def render_selectors(self, ui: ui) -> None:
        for key in self.elements.keys():
            # FIXME: there might be an update order thing here, with a race between updating selected
            # FIXME: and updating the category selectors. The on_change might have the value in an event,
            # FIXME: which would obviate this issue entirely.
            # FIXME: there's also a parallel issue, in that selecting by category will trigger the
            # FIXME: on_change for every element in the category
            switch = ui.switch(key, on_change=partial(self._update_category_selectors, item=key))
            switch.bind_value(self._selected, key)
            switch.bind_visibility_from(self._selector_visibility, key)

    def _category_select(self, category: str) -> None:
        # TODO: can category select be moved into js/quasar? this would cut the number of bindings
        # TODO: to 3-4 per instances, rather than 100+
        visible_keys = set(self.elements.tag(category).keys()) & {
            k for k, v in self._selector_visibility.items() if v
        }
        all_selected = all(self._selected[key] for key in visible_keys)
        for value in visible_keys:
            self._selected[value] = not all_selected

        self._update_category_selectors()

    def _update_category_selectors(self, item: str | None = None):
        if item:
            update_tags = self.elements.value_tags(item)
        else:
            update_tags = set(self.elements.tags.keys())

        for tag in update_tags:
            self._category_counters[tag] = sum(
                self._selected[k] for k in self.elements.tag(tag).keys()
            )

    def _filter(self, search: str):
        if not search:
            for key in self._selector_visibility.keys():
                self._selector_visibility[key] = self.default_visibility

            for key in self._category_visibility.keys():
                self._category_visibility[key] = self.default_visibility

            return

        threshold = 75

        item_scores = process.extract(search, self.elements.keys(), limit=None)
        tag_scores = process.extract(search, self.elements.tags.keys(), limit=None)
        visible_categories = {k for k, score in tag_scores if score > threshold}
        for k, score in item_scores:
            self._selector_visibility[k] = (score > threshold) or any(
                visible_categories & self.elements.value_tags(k)
            )

        for k, score in tag_scores:
            self._category_visibility[k] = score > threshold

    @property
    def selected(self) -> set[...]:
        yield from (self.elements[key] for key, value in self._selected.items() if value)

    def add(self, key: str, value: ..., tags: set[str], selected: bool | None = None):
        self.elements[key] = value
        self.elements.set_tag(key, tags)
        self._selected[key] = selected if selected is not None else self.default_state
        self._selector_visibility[key] = self.default_visibility

        for tag in tags:
            self._category_visibility.setdefault(tag, self.default_visibility)
            self._category_counters.setdefault(tag, 0)

        self._update_category_selectors(key)


class Setter:
    default_visibility = False

    def __init__(self, elements: Iterable[str], default_state: bool = False):
        self.elements = elements
        self.default_state = default_state
        self._selected = {key: self.default_state for key in self.elements}
        self._values = {key: 0 for key in self.elements}

    def clear(self):
        # TODO
        pass

    def render_search_box(self, ui: ui) -> None:
        def _set_keys(keys: list[str]):
            for key in self._selected.keys():
                self._selected[key] = key in keys

        ui.select(
            self.elements, with_input=True, multiple=True, on_change=lambda e: _set_keys(e.value)
        ).props("use-chips")

    def render_setters(self, ui):
        for key in self.elements:
            with ui.row() as row:
                row.classes("content-center")
                row.props("content-center")

                row.bind_visibility_from(self._selected, key)

                ui.number(key).bind_value(self._values, key)

    @property
    def values(self) -> dict[str, int]:
        return {key: value for key, value in self._values.items() if value}
