from .widget import Widget
from py_cui.ui import UIImplementation
import py_cui.keys


class TextBoxImplementation(UIImplementation):
    """UI implementation for a single-row textbox input

    Attributes
    ----------
    _text : str
        The text in the text box
    _initial_cursor : int
        Initial position of the cursor
    _cursor_x, _cursor_y : int
        The absolute positions of the cursor in the terminal window
    _cursor_text_pos : int
        the cursor position relative to the text
    _cursor_max_left, cursor_max_right : int
        The cursor bounds of the text box
    _viewport_width : int
        The width of the textbox viewport
    _password : bool
        Toggle to display password characters or text
    """

    def __init__(self, password, logger):
        """Initializer for the TextBoxImplementation base class
        """

        super().__init__(logger)
        self._text             = ''
        self._password         = password
        self._initial_cursor   = 0
        self._cursor_text_pos  = 0
        self._cursor_max_left  = 0
        self._cursor_x         = 0
        self._cursor_max_right = 0
        self._cursor_y         = 0
        self._viewport_width   = 0


    # Variable getter + setter functions

    def get_initial_cursor_pos(self):
        """Gets initial cursor position

        Returns
        -------
        initial_cursor : int
            Initial position of the cursor
        """

        return self._initial_cursor


    def get_cursor_text_pos(self):
        """Gets current position of cursor relative to text

        Returns
        -------
        cursor_text_pos : int
            the cursor position relative to the text
        """

        return self._cursor_text_pos


    def get_cursor_limits(self):
        """Gets cursor extreme points in terminal position

        Returns
        -------
        cursor_max_left, cursor_max_right : int
            The cursor bounds of the text box
        """

        return self._cursor_max_left, self._cursor_max_right


    def get_cursor_position(self):
        """Returns current cursor poition

        Returns
        -------
        cursor_x, cursor_y : int
            The absolute positions of the cursor in the terminal window
        """

        return self._cursor_x, self._cursor_y


    def get_viewport_width(self):
        """Gets the width of the textbox viewport

        Returns
        -------
        viewport_width : int
            The width of the textbox viewport
        """

        return self._viewport_width


    def set_text(self, text):
        """Sets the value of the text. Overwrites existing text

        Parameters
        ----------
        text : str
            The text to write to the textbox
        """

        self._text = text
        if self._cursor_text_pos > len(self._text):
            diff = self._cursor_text_pos - len(self._text)
            self._cursor_text_pos = len(self._text)
            self._cursor_x = self._cursor_x - diff


    def get(self):
        """Gets value of the text in the textbox

        Returns
        -------
        text : str
            The current textbox test
        """

        return self._text


    def clear(self):
        """Clears the text in the textbox
        """

        self._cursor_x         = self._cursor_max_left
        self._cursor_text_pos  = 0
        self._text             = ''


    def _move_left(self):
        """Shifts the cursor the the left. Internal use only
        """

        if  self._cursor_text_pos > 0:
            if self._cursor_x > self._cursor_max_left:
                self._cursor_x = self._cursor_x - 1
            self._cursor_text_pos = self._cursor_text_pos - 1


    def _move_right(self):
        """Shifts the cursor the the right. Internal use only
        """
        if self._cursor_text_pos < len(self._text):
            if self._cursor_x < self._cursor_max_right:
                self._cursor_x = self._cursor_x + 1
            self._cursor_text_pos = self._cursor_text_pos + 1


    def _insert_char(self, key_pressed):
        """Inserts char at cursor position. Internal use only

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """
        self._text = self._text[:self._cursor_text_pos] + chr(key_pressed) + self._text[self._cursor_text_pos:]
        if len(self._text) < self._viewport_width:
            self._cursor_x = self._cursor_x + 1
        self._cursor_text_pos = self._cursor_text_pos + 1


    def _jump_to_start(self):
        """Jumps to the start of the textbox. Internal use only
        """

        self._cursor_x = self._initial_cursor
        self._cursor_text_pos = 0


    def _jump_to_end(self):
        """Jumps to the end to the textbox. Internal use only
        """

        self._cursor_text_pos = len(self._text)
        self._cursor_x = self._initial_cursor + self._cursor_text_pos


    def _erase_char(self):
        """Erases character at textbox cursor. Internal Use only
        """

        if self._cursor_text_pos > 0:
            self._text = self._text[:self._cursor_text_pos - 1] + self._text[self._cursor_text_pos:]
            if len(self._text) < self._viewport_width:
                self._cursor_x = self._cursor_x - 1
            self._cursor_text_pos = self._cursor_text_pos - 1


    def _delete_char(self):
        """Deletes character to right of texbox cursor. Internal use only
        """

        if self._cursor_text_pos < len(self._text):
            self._text = self._text[:self._cursor_text_pos] + self._text[self._cursor_text_pos + 1:]


class TextBox(Widget, TextBoxImplementation):
    """Widget for entering small single lines of text
    """

    def __init__(self, parent, title, password=False):
        """Initializer for TextBox widget. Uses TextBoxImplementation as base
        """

        Widget.__init__(self, parent, title)
        TextBoxImplementation.__init__(self, password, parent._logger)
        self._style['single_line_mode'] = True
        self._parent = parent
        self.set_help_text('Focus mode on TextBox. Press Esc to exit focus mode.')


    def update_size(self):
        super().update_size()
        self._cursor_x, self._cursor_y = self.get_viewport_start_pos()
        _, self._cursor_max_right = self.get_viewport_stop_pos()
        self._cursor_max_left = self._cursor_x
        self._initial_cursor = self._cursor_x
        self._cursor_text_pos = 0
        self._viewport_width = self.get_viewport_width()


    def _handle_mouse_press(self, x, y):
        """Override of base class function, handles mouse press in menu

        Parameters
        ----------
        x, y : int
            Coordinates of mouse press
        """

        super()._handle_mouse_press(x, y)
        if y == self._cursor_y and x >= self._cursor_max_left and x <= self._cursor_max_right:
            if x <= len(self._text) + self._cursor_max_left:
                old_text_pos = self._cursor_text_pos
                old_cursor_x = self._cursor_x
                self._cursor_x = x
                self._cursor_text_pos = old_text_pos + (x - old_cursor_x)
            else:
                self._cursor_x = self._cursor_max_left + len(self._text)
                self._cursor_text_pos = len(self._text)


    def _handle_key_press(self, key_pressed):
        super()._handle_key_press(key_pressed)
        if key_pressed == py_cui.keys.KEY_LEFT_ARROW:
            self._move_left()
        elif key_pressed == py_cui.keys.KEY_RIGHT_ARROW:
            self._move_right()
        elif key_pressed == py_cui.keys.KEY_BACKSPACE:
            self._erase_char()
        elif key_pressed == py_cui.keys.KEY_DELETE:
            self._delete_char()
        elif key_pressed == py_cui.keys.KEY_HOME:
            self._jump_to_start()
        elif key_pressed == py_cui.keys.KEY_END:
            self._jump_to_end()
        elif key_pressed > 31 and key_pressed < 128 or \
                key_pressed > 1000 and key_pressed < 1128:
            self._insert_char(key_pressed)


    def _draw_content(self):
      render_text = self._text
      if len(self._text) > self._viewport_width:
        end = len(self._text) - self._viewport_width
        if self._cursor_text_pos < end:
          render_text = self._text[self._cursor_text_pos:self._cursor_text_pos + self._viewport_width]
        else:
          render_text = self._text[end:]
      if self._password:
        temp = '*' * len(render_text)
        render_text = temp
      self._parent._renderer.draw_text_in_viewport(self, render_text, selected=self._focused)


    def _draw_cursor(self):
        if self._focused:
            self._parent._renderer.draw_cursor(self._cursor_y, self._cursor_x)
        else:
            self._parent._renderer.reset_cursor(self)


