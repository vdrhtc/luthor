

class CellFieldParameters:
    def __init__(self, h_size, h_step, v_size, v_step):
        self._h_size = h_size
        self._h_step = h_step
        self._v_size = v_size
        self._v_step = v_step

        self._capacity = h_size * v_size

    def get_relative_coordinates(self, index):
        if index < self._capacity:
            x = (index % self._h_size) * self._h_step
            y = (index // self._h_size) * self._v_step
            #             print(index, x, y, self._h_size, self._v_size)
            return x, y
        else:
            raise ValueError("Form capacity exceeded")

