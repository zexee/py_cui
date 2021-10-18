import shutil
import py_cui.widgets as widgets
import py_cui.keys


class Layout:
  def __init__(self, gui, height, width):
    self._gui = gui
    self._logger = gui._logger  # for widget to call
    self._renderer = gui._renderer  # for widget to call
    self._widgets = {}
    self._keybindings = {}
    self._height = height
    self._width = width
    self._selected_widget = None
    self._in_focused_mode = False  # if in_focused_mode the widget handles key press


  def set_selected_widget(self, widget_id):
    self._selected_widget = widget_id


  def _refresh_height_width(self, height, width):
    self._height = height
    self._width = width


  def _cycle_widgets(self, reverse=False):
    ids = list(self._widgets.keys())
    pos = ids.index(self._selected_widget)
    pos += 1 if not reverse else -1
    if pos >= len(ids): pos = 0
    self.set_selected_widget(ids[pos])


  def _draw(self):
    for id, w in self._widgets.items():
      if id != self._selected_widget:
        w[0]._draw()
    # We draw the selected widget last to support cursor location.
    if self._selected_widget is not None:
        self._widgets[self._selected_widget][0]._draw()


  def lose_focus(self):
      self._in_focused_mode = False
      self._widgets[self._selected_widget][0].set_focused(False)
      self._widgets[self._selected_widget][0].set_hovering(True)


  def set_focus(self, id):
      self.lose_focus()
      self._selected_widget = id
      self._widgets[self._selected_widget][0].set_focused(True)
      self._in_focused_mode = True


  def add_key_command(self, key, command):
      self._keybindings[key] = command


  def get_next_id(self):
      return len(self._widgets.keys())


