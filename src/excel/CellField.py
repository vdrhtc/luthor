import re

from src.excel.utils import index_from_letters, letters_from_index

class CellField:
    def __init__(self, origin, form_params):
        self._origin = origin

        raw_x, raw_y = re.split("(\d+)", self._origin)[:2]
        self._x0, self._y0 = index_from_letters(raw_x), int(raw_y)

        self._params = form_params

    def get_excel_coordinates(self, index):
        dx, dy = self._params.get_relative_coordinates(index)
        return letters_from_index(self._x0 + dx) + str(self._y0 + dy)

    def fill_mapping(self, string_value):
        mapping = {}
        for idx, char in enumerate(string_value):
            position = self.get_excel_coordinates(idx)
            mapping[position] = char
        return mapping