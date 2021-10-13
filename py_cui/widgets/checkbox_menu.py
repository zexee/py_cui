from .widget import Widget
from .scroll_menu import MenuImplementation


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
        """Initializer for the checkbox menu implementation
        """

        super().__init__(logger)
        self._selected_item_dict = {}
        self._checked_char       = checked_char


    def add_item(self, item):
        """Extends base class function, item is added and marked as unchecked to start

        Parameters
        ----------
        item : object
            The item being added
        """

        super().add_item(item)
        self._selected_item_dict[item] = False


    def remove_selected_item(self):
        """Removes selected item from item list and selected item dictionary
        """

        del self._selected_item_dict[self.get()]
        super().remove_selected_item()


    def remove_item(self, item):
        """Removes item from item list and selected item dict

        Parameters
        ----------
        item : object
            Item to remove from menu
        """

        del self._selected_item_dict[item]
        super().remove_item(item)


    def mark_item_as_checked(self, item):
        """Function that marks an item as selected

        Parameters
        ----------
        item : object
            Mark item as checked
        """

        self._selected_item_dict[item] = not self._selected_item_dict[item]


class CheckBoxMenu(Widget, CheckBoxMenuImplementation):
    """Extension of ScrollMenu that allows for multiple items to be selected at once.

    Attributes
    ----------
    selected_item_list : list of str
        List of checked items
    checked_char : char
        Character to represent a checked item
    """

    def __init__(self, parent, title, row, column, row_span, column_span, padx, pady, checked_char):
        """Initializer for CheckBoxMenu Widget
        """

        Widget.__init__(self, parent, title, row, column, row_span, column_span, padx, pady)
        py_cui.ui.CheckBoxMenuImplementation.__init__(self, parent._logger, checked_char)
        self.set_help_text('Focus mode on CheckBoxMenu. Use up/down to scroll, Enter to toggle set, unset, Esc to exit.')


    def _handle_mouse_press(self, x, y):
        """Override of base class function, handles mouse press in menu

        Parameters
        ----------
        x, y : int
            Coordinates of mouse press
        """

        super()._handle_mouse_press(x, y)
        viewport_top = self._start_y + self._pady + 1
        if viewport_top <= y and viewport_top + len(self._view_items) - self._top_view >= y:
            elem_clicked = y - viewport_top + self._top_view
            self.set_selected_item_index(elem_clicked)
            self.mark_item_as_checked(self._view_items[elem_clicked])


    def _handle_key_press(self, key_pressed):
        """Override of key presses.

        First, run the superclass function, scrolling should still work.
        Adds Enter command to toggle selection

        Parameters
        ----------
        key_pressed : int
            key code of pressed key
        """

        Widget._handle_key_press(self, key_pressed)
        viewport_height = self.get_viewport_height()
        if key_pressed == py_cui.keys.KEY_UP_ARROW:
            self._scroll_up()
        if key_pressed == py_cui.keys.KEY_DOWN_ARROW:
            self._scroll_down(viewport_height)
        if key_pressed == py_cui.keys.KEY_HOME:
            self._jump_to_top()
        if key_pressed == py_cui.keys.KEY_END:
            self._jump_to_bottom(viewport_height)
        if key_pressed == py_cui.keys.KEY_PAGE_UP:
            self._jump_up()
        if key_pressed == py_cui.keys.KEY_PAGE_DOWN:
            self._jump_down(viewport_height)
        if key_pressed == py_cui.keys.KEY_ENTER:
            self.mark_item_as_checked(self.get())


    def _draw(self):
        """Overrides base class draw function
        """

        Widget._draw(self)
        self._renderer.set_color_mode(self._color)
        self._renderer.draw_border(self)
        counter = self._pady + 1
        line_counter = 0
        for item in self._view_items:
            if self._selected_item_dict[item]:
                line = '[{}] - {}'.format(self._checked_char, str(item))
            else:
                line = '[ ] - {}'.format(str(item))
            if line_counter < self._top_view:
                line_counter = line_counter + 1
            else:
                if counter >= self._height - self._pady - 1:
                    break
                if line_counter == self._selected_item:
                    self._renderer.draw_text(self, line, self._start_y + counter, selected=True)
                else:
                    self._renderer.draw_text(self, line, self._start_y + counter)
                counter = counter + 1
                line_counter = line_counter + 1
        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)


