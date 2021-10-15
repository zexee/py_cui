from .widget import Widget
from .scroll_menu import MenuImplementation
import py_cui.keys


class CheckBoxMenuImplementation(MenuImplementation):
    """Class representing checkbox menu ui implementation

    Attributes
    ----------
    _selected_item_dict : dict of object -> bool
        stores each object and maps to its current selected status
    _checked_char : char
        Character to mark checked items
    """

    def __init__(self, logger, checked_char):
        super().__init__(logger)
        self._selected_item_dict = {}
        self._checked_char = checked_char


    def add_item(self, item):
        super().add_item(item)
        self._selected_item_dict[item] = False


    def remove_selected_item(self):
        del self._selected_item_dict[self.get()]
        super().remove_selected_item()


    def remove_item(self, item):
        del self._selected_item_dict[item]
        super().remove_item(item)


    def mark_item_as_checked(self, item):
        self._selected_item_dict[item] = not self._selected_item_dict[item]


    def is_checked(self, item):
          return self._selected_item_dict[item]


class CheckBoxMenu(Widget, CheckBoxMenuImplementation):
    """Extension of ScrollMenu that allows for multiple items to be selected at once.

    Attributes
    ----------
    selected_item_list : list of str
        List of checked items
    checked_char : char
        Character to represent a checked item
    """

    def __init__(self, parent, title, row, column, row_span, column_span, checked_char='*'):
        Widget.__init__(self, parent, title, row, column, row_span, column_span)
        CheckBoxMenuImplementation.__init__(self, parent._logger, checked_char)
        self._parent = parent
        self.set_help_text('Focus mode on CheckBoxMenu. Use up/down to scroll, Enter to toggle set, unset, Esc to exit.')

        self._events['on_change'] = lambda : 0


    def _handle_mouse_press(self, x, y):
        super()._handle_mouse_press(x, y)
        _, viewport_top = self.get_viewport_start_pos()
        if viewport_top <= y and viewport_top + len(self._view_items) - self._top_view >= y:
            elem_clicked = y - viewport_top + self._top_view
            if elem_clicked < len(self._view_items):
              self.set_selected_item_index(elem_clicked)
              self.mark_item_as_checked(self._view_items[elem_clicked])
              self._events['on_change']()


    def _handle_key_press(self, key_pressed):
      Widget._handle_key_press(self, key_pressed)
      if key_pressed == py_cui.keys.KEY_UP_ARROW:
          self._scroll_up()
      if key_pressed == py_cui.keys.KEY_DOWN_ARROW:
          self._scroll_down()
      if key_pressed == py_cui.keys.KEY_HOME:
          self._jump_to_top()
      if key_pressed == py_cui.keys.KEY_END:
          self._jump_to_bottom()
      if key_pressed == py_cui.keys.KEY_PAGE_UP:
          self._scroll_up()
      if key_pressed == py_cui.keys.KEY_PAGE_DOWN:
          self._scroll_down()
      if key_pressed == py_cui.keys.KEY_ENTER:
          self.mark_item_as_checked(self.get())
          self._events['on_change']()


    def _draw_content(self):
      startx, posy = self.get_viewport_start_pos()
      stopx, stopy = self.get_viewport_stop_pos()
      i = self._top_view
      while i < len(self._view_items) and posy <= stopy:
        item = self._view_items[i]
        line = '[{}] - {}'.format(self._checked_char if self._selected_item_dict[item] else ' ', str(item))
        posy += self._parent._renderer.draw_text_in(self, line, startx, stopx, posy, stopy, selected=i == self._selected_item)
        i += 1



