import py_cui.keys
from .widget import Widget
from py_cui.ui import UIImplementation


class MenuImplementation(UIImplementation):
    """A scrollable menu UI element

    Allows for creating a scrollable list of items of which one is selectable.
    Analogous to a RadioButton

    Attributes
    ----------
    _top_view : int
        the uppermost menu element in view
    _bottom_view : int
        the lowermost fully-displayed menu element in view
    _selected_item : int
        the currently highlighted menu item
    _view_items : list of str
        list of menu items
    """

    def __init__(self, logger):
        """Initializer for MenuImplementation base class
        """

        super().__init__(logger)
        self._top_view         = 0
        self._bottom_view         = 0
        self._selected_item    = 0
        self._page_scroll_len  = 5
        self._view_items       = []


    def clear(self):
        """Clears all items from the Scroll Menu
        """

        self._view_items = []
        self._selected_item = 0
        self._top_view = 0
        self._bottom_view = 0

        self._logger.info('Clearing menu')



    def get_selected_item_index(self):
        """Gets the currently selected item

        Returns
        -------
        selected_item : int
            the currently highlighted menu item
        """

        return self._selected_item


    def set_selected_item_index(self, selected_item_index):
        """Sets the currently selected item

        Parameters
        ----------
        selected_item : int
            The new selected item index
        """

        self._selected_item = selected_item_index


    def _set_footer(self):
        if self.get_item_size() > 0:
            self.set_footer('{}/{}'.format(self._selected_item + 1, self.get_item_size()))
        else:
            self.set_footer('')


    def _scroll_up(self):
        """Function that scrolls the view up in the scroll menu
        """

        if self._selected_item > 0:
            if self._selected_item == self._top_view:
                self._top_view -= 1
            self._selected_item -= 1

        self._logger.info('Scrolling up to item {}'.format(self._selected_item))


    def _scroll_down(self):
        """Function that scrolls the view down in the scroll menu
        """

        if self._selected_item < len(self._view_items) - 1:
            self._selected_item += 1
            if self._selected_item > self._bottom_view:
                self._top_view += 1

        self._logger.info('Scrolling down to item {}'.format(self._selected_item))


    def _page_up(self):
        """Function for jumping up menu several spots at a time
        """

        for _ in range(self._page_scroll_len):
            self._scroll_up()


    def _page_down(self):
        """Function for jumping down the menu several spots at a time
        """

        for _ in range(self._page_scroll_len):
            self._scroll_down()


    def _jump_to_top(self):
        """Function that jumps to the top of the menu
        """

        self._top_view      = 0
        self._selected_item = 0


    def _jump_to_bottom(self, viewport_height):
        """Function that jumps to the bottom of the menu

        Parameters
        ----------
        viewport_height : int
            The number of visible viewport items
        """

        self._selected_item = len(self._view_items) - 1
        self._top_view = self._selected_item - viewport_height
        if self._top_view < 0:
            self._top_view = 0


    def add_item(self, item):
        """Adds an item to the menu.

        Parameters
        ----------
        item : Object
            Object to add to the menu. Must have implemented __str__ function
        """

        self._logger.info('Adding item {} to menu'.format(str(item)))
        self._view_items.append(item)
        self._set_footer()


    def add_item_list(self, item_list):
        """Adds a list of items to the scroll menu.

        Parameters
        ----------
        item_list : List[Object]
            list of objects to add as items to the scrollmenu
        """

        self._logger.info('Adding item list {} to menu'.format(str(item_list)))
        for item in item_list:
            self.add_item(item)


    def remove_selected_item(self):
        """Function that removes the selected item from the scroll menu.
        """

        if len(self._view_items) == 0:
            return
        self._logger.info('Removing {}'.format(str(self._view_items[self._selected_item])))
        del self._view_items[self._selected_item]
        if self._selected_item >= len(self._view_items) and self._selected_item > 0:
            self._selected_item = self._selected_item - 1
        self._set_footer()


    def remove_item(self, item):
        """Function that removes a specific item from the menu

        Parameters
        ----------
        item : Object
            Reference of item to remove
        """

        if len(self._view_items) == 0 or item not in self._view_items:
            return
        self._logger.info('Removing {}'.format(str(item)))
        i_index = self._view_items.index(item)
        del self._view_items[i_index]
        if self._selected_item >= i_index:
            self._selected_item = self._selected_item - 1
        self._set_footer()


    def clear_items(self):
        while self.get_item_size() > 0:
            self.remove_selected_item()


    def get_item_list(self):
        """Function that gets list of items in a scroll menu

        Returns
        -------
        item_list : List[Object]
            list of items in the scrollmenu
        """

        return self._view_items


    def get_item_size(self):
        return len(self._view_items)


    def get(self):
        """Function that gets the selected item from the scroll menu

        Returns
        -------
        item : Object
            selected item, or None if there are no items in the menu
        """

        if len(self._view_items) > 0:
            return self._view_items[self._selected_item]
        return None


    def set_selected_item(self, selected_item):
        """Function that replaces the currently selected item with a new item

        Parameters
        ----------
        item : Object
            A new selected item to replace the current one
        """

        if selected_item is not None and self.get() is not None:
            self._view_items[self._selected_item] = selected_item


class ScrollMenu(Widget, MenuImplementation):
    """A scroll menu widget.
    """

    def __init__(self, parent, title, row, column, row_span=1, column_span=1, padx=0, pady=0):
        """Initializer for scroll menu. calls superclass initializers and sets help text
        """

        Widget.__init__(self, parent, title, row, column, row_span, column_span, padx, pady)
        MenuImplementation.__init__(self, parent._logger)
        self._parent = parent
        self.set_help_text('Focus mode on ScrollMenu. Use Up/Down/PgUp/PgDown/Home/End to scroll, Esc to exit.')


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
        self._set_footer()


    def _handle_key_press(self, key_pressed):
        """Override base class function.

        UP_ARROW scrolls up, DOWN_ARROW scrolls down.

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """

        super()._handle_key_press(key_pressed)

        if key_pressed == py_cui.keys.KEY_UP_ARROW:
            self._scroll_up()
        elif key_pressed == py_cui.keys.KEY_DOWN_ARROW:
            self._scroll_down()
        elif key_pressed == py_cui.keys.KEY_PAGE_UP:
            self._page_up()
        elif key_pressed == py_cui.keys.KEY_PAGE_DOWN:
            self._page_down()
        elif key_pressed == py_cui.keys.KEY_HOME:
            self._jump_to_top()
        elif key_pressed == py_cui.keys.KEY_END:
            # TODO: fix
            self._jump_to_bottom(self.get_viewport_height())
        self._set_footer()


    def _draw(self):
        """Overrides base class draw function
        """

        super()._draw()
        self._parent._renderer.set_color_mode(self._color)
        self._parent._renderer.draw_border(self)

        posy = self._pady + 1
        self._bottom_view = self._top_view
        self._logger.info("menu {} {}".format(self._height, self._pady))
        for itemi in range(self._top_view, len(self._view_items)):
            posy += self._parent._renderer.draw_text(self, str(self._view_items[itemi]),
                self._start_y + posy, selected=itemi == self._selected_item)
            if posy <= self._height - self._pady - 1:
              self._bottom_view = itemi
            if posy >= self._height - self._pady - 1:
                break
        self._parent._renderer.draw_scrollbar(self, self._top_view + 1, self._bottom_view + 1, len(self._view_items))
        self._parent._renderer.unset_color_mode(self._color)
        self._parent._renderer.reset_cursor(self)


