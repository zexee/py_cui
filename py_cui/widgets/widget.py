import curses
import py_cui
import py_cui.ui
import py_cui.colors
import py_cui.errors


class Widget(py_cui.ui.UIElement):
  def __init__(self, parent, title):
      super().__init__(parent.get_next_id(), title,
                       parent._renderer, parent._logger)
      self._parent = parent

      self._events = {
      }

      self._key_commands     = {}
      self._text_color_rules = []
      self._default_color = py_cui.WHITE_ON_BLACK
      self._border_color = self._default_color


  def add_key_command(self, key, command):
      self._key_commands[key] = command


  def add_text_color_rule(self, regex, color, rule_type, match_type='line', region=[0,1], include_whitespace=False, selected_color=None):
      selected = color
      if selected_color is not None:
          selected = selected_color

      new_color_rule = py_cui.colors.ColorRule(regex, color, selected, rule_type, match_type, region, include_whitespace, self._logger)
      self._text_color_rules.append(new_color_rule)


  def get_grid_cell(self):
      return self._row, self._column


  def get_grid_cell_spans(self):
      return self._row_span, self._column_span


  def _handle_key_press(self, key_pressed):
      if key_pressed in self._key_commands.keys():
          command = self._key_commands[key_pressed]
          command()
          return True
      return False


  def _draw(self):
    # TODO: this should belong to specific widget, not universal.
    self._renderer.set_color_rules(self._text_color_rules)
    super()._draw()


