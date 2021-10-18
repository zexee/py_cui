import shutil
import py_cui.widgets as widgets
import py_cui.keys
from .layout import Layout


class GridLayout(Layout):
  def __init__(self, gui, num_rows, num_cols, height, width):
    super().__init__(gui, height, width)
    self._num_rows = num_rows
    self._num_cols = num_cols
    self._offset_x = 0
    self._offset_y = 0
    self._row_height = 0
    self._col_width = 0


  def _refresh_height_width(self, height, width):
    self._gui._logger.info("RESIZE {} {}".format(height, width))
    super()._refresh_height_width(height, width)

    # minimal cell size is 3x3
    if (3 * self._num_cols) >= self._width:
        raise py_cui.errors.PyCUIOutOfBoundsError
    if (3 * self._num_rows) >= self._height:
        raise py_cui.errors.PyCUIOutOfBoundsError

    self._row_height = self._height // self._num_rows
    self._col_width = self._width // self._num_cols
    self._offset_x = (self._width % self._col_width) // 2
    self._offset_y = (self._height % self._row_height) // 2

    for _, (w, (row, col, row_span, col_span)) in self._widgets.items():
      this_offset_x = self._offset_x
      this_offset_y = self._offset_y
      if col == 0 and w._style['snap_border']:
        this_offset_x = 0
      if row == 0 and w._style['snap_border']:
        this_offset_y = 0
      w._start_x = col * self._col_width + self._gui._left_padding + this_offset_x
      w._start_y = row * self._row_height + self._gui._top_padding + 1 + this_offset_y

      if col + col_span == self._num_cols and w._style['snap_border']:
        w._stop_x = self._width + self._gui._left_padding - 1
      else:
        w._stop_x = col * self._col_width + self._offset_x + self._gui._left_padding + self._col_width * col_span - 1

      if row + row_span == self._num_rows and w._style['snap_border']:
        w._stop_y = self._height + self._gui._top_padding
      else:
        w._stop_y = row * self._row_height + self._offset_y + self._gui._top_padding + self._row_height * row_span
      w.update_size()


  def _is_row_col_inside(self, id, r, c):
    w, (row, col, row_span, col_span) = self._widgets[id]
    self._gui._logger.info('{} {} <= {} < {} {} <= {} < {} {}'.format(id, row, r, row+row_span, col, c, col+ col_span,
      row <= r and r < row + row_span and col <= c and c < col + col_span
      ))
    return row <= r and r < row + row_span and col <= c and c < col + col_span


  def _get_vertical_neighbor(self, row, col, row_span, col_span, direction):
    start, end, step = (row - 1, -1, -1) if direction == py_cui.keys.KEY_UP_ARROW else (row + row_span, self._num_rows, 1)

    for r in range(start, end, step):
      for c in range(col, col + col_span):
        for id in self._widgets.keys():
          if self._is_row_col_inside(id, r, c):
            return id
    return None


  def _get_horizontal_neighbor(self, row, col, row_span, col_span, direction):
    start, end, step = (col - 1, -1, -1) if direction == py_cui.keys.KEY_LEFT_ARROW else (col + col_span, self._num_cols, 1)

    for c in range(start, end, step):
      for r in range(row, row + row_span):
        for id in self._widgets.keys():
          if self._is_row_col_inside(id, r, c):
            return id
    return None


  def _get_neighbor(self, direction):
    w, (row, col, row_span, col_span) = self._widgets[self._selected_widget]

    if direction in [py_cui.keys.KEY_DOWN_ARROW, py_cui.keys.KEY_UP_ARROW]:
      return self._get_vertical_neighbor(row, col, row_span, col_span, direction)
    elif direction in [py_cui.keys.KEY_RIGHT_ARROW, py_cui.keys.KEY_LEFT_ARROW]:
      return self._get_horizontal_neighbor(row, col, row_span, col_span, direction)


  def _handle_key_presses(self, key_pressed):
      if self._in_focused_mode:
        if key_pressed == py_cui.keys.KEY_ESCAPE:
          self._gui.status_bar.set_text(self._gui._init_status_bar_text)
          self.lose_focus()
        else:
          self._widgets[self._selected_widget][0]._handle_key_press(key_pressed)
      else:
        if key_pressed in py_cui.keys.ARROW_KEYS:
          neighbor = self._get_neighbor(key_pressed)
          if neighbor is not None:
            self.set_hover(neighbor)
        elif key_pressed == py_cui.keys.KEY_ENTER and self._widgets[self._selected_widget][0]._style['selectable']:
          self.set_focus(self._selected_widget)
        else:
          self._widgets[self._selected_widget][0]._handle_key_press(key_pressed)


  def add_widget(self, widget, row, col, row_span=1, col_span=1):
      self._widgets[widget._id] = (widget, (row, col, row_span, col_span))
      if self._selected_widget is None and widget._style['selectable']:
        self.set_hover(widget._id)
      return widget


