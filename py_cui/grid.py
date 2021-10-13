"""File containing the Grid Class.

The grid is currently the only supported layout manager for py_cui
"""

# Author:    Jakub Wlodek
# Created:   12-Aug-2019


import py_cui


class Grid:
    """Class representing the CUI grid
    """


    def __init__(self, gui, num_rows, num_columns, height, width):
        self._gui           = gui
        self._num_rows      = num_rows
        self._num_columns   = num_columns
        self._height        = int(height)
        self._width         = int(width)
        self._update_size()


    def get_dimensions(self):
        return self._num_rows, self._num_columns


    def get_dimensions_absolute(self):
        return self._height, self._width


    def get_offsets(self):
        return self._offset_x, self._offset_y


    def get_cell_dimensions(self):
        return self._row_height, self._column_width


    def _update_size(self):
        # minimal cell size is 3x3
        if (3 * self._num_columns) >= self._width:
            raise py_cui.errors.PyCUIOutOfBoundsError
        if (3 * self._num_rows) >= self._height:
            raise py_cui.errors.PyCUIOutOfBoundsError

        self._row_height    = int(self._height / self._num_rows)
        self._column_width  = int(self._width / self._num_columns)
        self._offset_x      = int((self._width % self._column_width) / 2)
        self._offset_y      = int((self._height % self._row_height) / 2)
        self._gui._logger.info('Updated grid. Cell dims: {}x{}, Offsets {},{}'.format(self._row_height, self._column_width, self._offset_x, self._offset_y))


    def set_num_rows(self, num_rows):
        self._num_rows = num_rows
        self._update_size()


    def set_num_cols(self, num_columns):
        self._num_columns   = num_columns
        self._update_size()


    def update_grid_height_width(self, height, width):
        self._gui._logger.info('Updating grid height and width')
        self._height = int(height)
        self._width = int(width)
        self._update_size()

