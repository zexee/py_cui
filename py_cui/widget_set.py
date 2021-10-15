"""File containing class that abstracts a collection of widgets.

It can be used to swap between collections of widgets (screens) in a py_cui
"""

# Author:    Jakub Wlodek
# Created:   12-Aug-2019

# TODO: Should create an initial widget set in PyCUI class that widgets are added to by default.

import shutil
import py_cui.widgets as widgets
import py_cui.grid as grid
import py_cui.keys


class WidgetSet:
    """Class that represents a collection of widgets.

    Use PyCUI.apply_widget_set() to set a given widget set for display

    Attributes
    ----------
    grid : py_cui.grid.Grid
        The main layout manager for the CUI
    widgets : dict of str - py_cui.widgets.Widget
        dict of widget in the grid
    keybindings : list of py_cui.keybinding.KeyBinding
        list of keybindings to check against in the main CUI loop
    height, width : int
        height of the terminal in characters, width of terminal in characters
    """

    def __init__(self, gui, num_rows, num_cols, height, width):
        """Constructor for WidgetSet
        """

        self._gui = gui
        self._logger = gui._logger  # for widget to call
        self._renderer = gui._renderer  # for widget to call
        self._widgets      = {}
        self._keybindings  = {}
        self._height = height
        self._width = width

        self._grid = grid.Grid(gui, num_rows, num_cols, self._height, self._width)

        self._selected_widget = None
        self._in_focused_mode = False  # if in_focused_mode the widget handles key press


    def set_selected_widget(self, widget_id):
        """Function that sets the selected cell for the CUI

        Parameters
        ----------
        cell_title : str
            the title of the cell
        """

        if widget_id in self._widgets.keys():
            self._selected_widget = widget_id


    def _refresh_height_width(self, height, width):
        self._grid.update_grid_height_width(height, width)
        for _, w in self._widgets.items():
            w.update_height_width()


    def _draw_widgets(self):
        """Function that draws all of the widgets to the screen
        """

        for id, w in self._widgets.items():
            if id != self._selected_widget:
                w._draw()

        # We draw the selected widget last to support cursor location.
        if self._selected_widget is not None:
            self._widgets[self._selected_widget]._draw()

        # self._gui._logger.info('Drew widgets')


    def get_widgets(self):
        """Function that gets current set of widgets

        Returns
        -------
        widgets : dict of str -> widget
            dictionary mapping widget IDs to object instances
        """

        return self._widgets


    def _get_horizontal_neighbors(self, widget, direction):
        _, num_cols = self._grid.get_dimensions()
        row_start, col_start = widget.get_grid_cell()
        row_span, col_span = widget.get_grid_cell_spans()
        id_list = []

        if direction == py_cui.keys.KEY_LEFT_ARROW:
            col_range_start = 0
            col_range_stop = col_start
        else:
            col_range_start = col_start + col_span
            col_range_stop = num_cols

        for col in range(col_range_start, col_range_stop):
            for row in range(row_start, row_start + row_span):
                for id, w in self._widgets.items():
                    if w._is_row_col_inside(row, col) and id not in id_list:
                        id_list.append(id)

        if direction == py_cui.keys.KEY_LEFT_ARROW:
            id_list.reverse()

        self._gui._logger.info('Neighbors with ids {} for cell {},{} span {},{}'.format(id_list,
                                                                                   row_start,
                                                                                   col_start,
                                                                                   row_span,
                                                                                   col_span))
        return id_list


    def _get_vertical_neighbors(self, widget, direction):
        num_rows,   _           = self._grid.get_dimensions()
        row_start,  col_start   = widget.get_grid_cell()
        row_span,   col_span    = widget.get_grid_cell_spans()
        id_list                 = []

        if direction == py_cui.keys.KEY_UP_ARROW:
            row_range_start = 0
            row_range_stop = row_start
        else:
            row_range_start = row_start + row_span
            row_range_stop = num_rows

        for row in range(row_range_start, row_range_stop):
            for col in range(col_start, col_start + col_span):
                for id, w in self._widgets.items():
                    if w._is_row_col_inside(row, col) and id not in id_list:
                        id_list.append(id)

        if direction == py_cui.keys.KEY_UP_ARROW:
            id_list.reverse()

        self._gui._logger.info('Neighbors with ids {} for cell {},{} span {},{}'.format(id_list,
                                                                                   row_start,
                                                                                   col_start,
                                                                                   row_span,
                                                                                   col_span))
        return id_list


    def get_element_at_position(self, x, y):
        for _, w in self._widgets.items():
            if w._contains_position(x, y):
                return w
        return None


    def get_selected_widget(self):
      if self._selected_widget is not None:
            return self._widgets[self._selected_widget]
      else:
            self._gui._logger.warn('Selected widget ID is None or invalid')
            return None


    def set_selected_widget(self, id):
        if id in self._widgets.keys():
            if self._selected_widget:
                self._widgets[self._selected_widget].set_hovering(False)
            self._gui._logger.info('Setting selected widget to ID {}'.format(id))
            self._selected_widget = id
            self._widgets[self._selected_widget].set_hovering(True)
        else:
            self._gui._logger.warn('Widget w/ ID {} does not exist among current widgets.'.format(id))


    def lose_focus(self):
        self._in_focused_mode = False
        self._widgets[self._selected_widget].set_focused(False)
        self._widgets[self._selected_widget].set_hovering(True)


    def move_focus(self, widget):
        self.lose_focus()
        self.set_selected_widget(widget._id)
        self._widgets[self._selected_widget].set_focused(True)
        self._in_focused_mode = True
        self._gui._logger.info('Moved focus to widget {}'.format(widget.get_title()))


    def add_key_command(self, key, command):
        self._keybindings[key] = command


    def get_next_id(self):
        return len(self._widgets.keys())


    def add_widget(self, widget):
        self._widgets[widget._id] = widget
        if self._selected_widget is None and widget._style['selectable']:
            self.set_selected_widget(widget._id)
        self._gui._logger.info('Adding widget {} w/ ID {} of type {}'.format(widget._title, widget._id, str(type(widget))))
        return widget


    def add_scroll_menu(self, title, row, column, row_span=1, column_span=1, padx=1, pady=0) -> widgets.ScrollMenu:
        return self.add_widget(
            widgets.ScrollMenu(self, title,
                               row, column, row_span, column_span, padx, pady))


    def add_checkbox_menu(self, title, row, column, row_span=1, column_span=1, padx=1, pady=0, checked_char='X') -> widgets.CheckBoxMenu:
        return self.add_widget(
            widgets.CheckBoxMenu(self, title,
                                 row, column, row_span, column_span, padx, pady,
                                 checked_char))


    def add_text_box(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, initial_text = '', password = False) -> widgets.TextBox:
        return self.add_widget(
            widgets.TextBox(self, title,
                            row, column, row_span, column_span, padx, pady,
                            initial_text, password))


    def add_text_block(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, initial_text = '') -> widgets.ScrollTextBlock:
        return self.add_widget(
            widgets.ScrollTextBlock(self, title,
                                    row, column, row_span, column_span, padx, pady,
                                    initial_text))


    def add_label(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0) -> widgets.Label:
        return self.add_widget(
            widgets.Label(self, title,
                          row, column, row_span, column_span, padx, pady))


    def add_block_label(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, center=True) -> widgets.BlockLabel:
        return self.add_widget(
            widgets.BlockLabel(self, title,
                               row, column, row_span, column_span, padx, pady,
                               center))


    def add_button(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, command=None) -> widgets.Button:
        return self.add_widget(
            widgets.Button(self, title,
                           row, column, row_span, column_span, padx, pady,
                           command))


    def add_slider(self, title, row, column, row_span=1,
                   column_span=1, padx=1, pady=0,
                   min_val=0, max_val=100, step=1, init_val=0) -> widgets.slider.Slider:
        return self.add_widget(
            widgets.slider.Slider(parent, title,
                                  row, column, row_span, column_span, padx, pady,
                                  min_val, max_val, step, init_val))

