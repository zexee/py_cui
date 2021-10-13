from .widget import Widget
from py_cui.ui import UIImplementation
import py_cui.keys


class TextBlockImplementation(UIImplementation):
    """Base class for TextBlockImplementation

    Contains all logic required for a textblock ui element to function.
    Currently only implemented in widget form, though popup form is possible.

    Attributes
    ----------
    _text_lines : List[str]
        the lines of text in the texbox
    _viewport_x_start, _viewport_y_start : int
        Initial location of viewport relative to text
    _cursor_text_pos_x, _cursor_text_pos_y : int
        Cursor position relative to text
    _cursor_x, _cursor_y : int
        Absolute cursor position in characters
    _cursor_max_up, _cursor_max_down : int
        cursor limits in vertical space
    _cursor_max_left, _cursor_max_right : int
        Cursor limits in horizontal space
    _viewport_height, _viewport_width : int
        The dimensions of the viewport in characters
    """

    def __init__(self, initial_text, logger):
        """Initializer for TextBlockImplementation base class

        Zeros attributes, and parses initial text
        """

        super().__init__(logger)
        self._text_lines = initial_text.splitlines()
        if len(self._text_lines) == 0:
            self._text_lines.append('')

        self._viewport_y_start   = 0
        self._viewport_x_start   = 0
        self._cursor_text_pos_x  = 0
        self._cursor_text_pos_y  = 0
        self._cursor_y           = 0
        self._cursor_x           = 0
        self._cursor_max_up      = 0
        self._cursor_max_down    = 0
        self._cursor_max_left    = 0
        self._cursor_max_right   = 0
        self._viewport_width     = 0
        self._viewport_height    = 0


    # Getters and setters

    def get_viewport_start_pos(self):
        """Gets upper left corner position of viewport

        Returns
        -------
        viewport_x_start, viewport_y_start : int
            Initial location of viewport relative to text
        """

        return self._viewport_x_start, self._viewport_y_start


    def get_viewport_dims(self):
        """Gets viewport dimensions in characters

        Returns
        -------
        viewport_height, viewport_width : int
            The dimensions of the viewport in characters
        """

        return self._viewport_height, self._viewport_width


    def get_cursor_text_pos(self):
        """Gets cursor postion relative to text

        Returns
        -------
        cursor_text_pos_x, cursor_text_pos_y : int
            Cursor position relative to text
        """


        return self._cursor_text_pos_x, self._cursor_text_pos_y


    def get_abs_cursor_position(self):
        """Gets absolute cursor position in terminal characters

        Returns
        -------
        cursor_x, cursor_y : int
            Absolute cursor position in characters
        """

        return self._cursor_x, self._cursor_y


    def get_cursor_limits_vertical(self):
        """Gets limits for cursor in vertical direction

        Returns
        -------
        cursor_max_up, cursor_max_down : int
            cursor limits in vertical space
        """

        return self._cursor_max_up, self._cursor_max_down


    def get_cursor_limits_horizontal(self):
        """Gets limits for cursor in horizontal direction

        Returns
        -------
        cursor_max_left, cursor_max_right : int
            Cursor limits in horizontal space
        """

        return self._cursor_max_left, self._cursor_max_right


    def get(self):
        """Gets all of the text in the textblock and returns it

        Returns
        -------
        text : str
            The current text in the text block
        """

        text = ''
        for line in self._text_lines:
            text = '{}{}\n'.format(text, line)
        return text


    def write(self, text):
        """Function used for writing text to the text block

        Parameters
        ----------
        text : str
            Text to write to the text block
        """

        lines = text.splitlines()
        if len(self._text_lines) == 1 and self._text_lines[0] == '':
            self.set_text(text)
        else:
            self._text_lines.extend(lines)


    def clear(self):
        """Function that clears the text block
        """

        self._cursor_x = self._cursor_max_left
        self._cursor_y = self._cursor_max_up
        self._cursor_text_pos_x = 0
        self._cursor_text_pos_y = 0
        self._viewport_y_start   = 0
        self._viewport_x_start   = 0
        self._text_lines = []
        self._text_lines.append('')
        self._set_footer()
        self._logger.info('Cleared textblock')


    def get_current_line(self):
        """Returns the line on which the cursor currently resides

        Returns
        -------
        current_line : str
            The current line of text that the cursor is on
        """

        return self._text_lines[self._cursor_text_pos_y]


    def set_text(self, text):
        """Function that sets the text for the textblock.

        Note that this will overwrite any existing text

        Parameters
        ----------
        text : str
            text to write into text block
        """

        self.clear()
        self._text_lines = text.splitlines()
        if len(self._text_lines) == 0:
            self._text_lines.append('')


    def set_text_line(self, text):
        """Function that sets the current line's text.

        Meant only for internal use

        Parameters
        ----------
        text : str
            text line to write into text block
        """

        self._text_lines[self._cursor_text_pos_y] = text


    def _set_footer(self):
        x, y = self.get_cursor_text_pos()
        x += 1
        y += 1
        self.set_footer('{}:{}'.format(x, y))

    def _move_left(self):
        """Function that moves the cursor/text position one location to the left
        """

        if self._cursor_text_pos_x > 0:
            if self._cursor_x > self._cursor_max_left:
                self._cursor_x = self._cursor_x - 1
            elif self._viewport_x_start > 0:
                self._viewport_x_start = self._viewport_x_start - 1
            self._cursor_text_pos_x = self._cursor_text_pos_x - 1

        self._logger.info('Moved cursor left to pos {}'.format(self._cursor_text_pos_x))


    def _move_right(self):
        """Function that moves the cursor/text position one location to the right
        """

        current_line = self.get_current_line()

        if self._cursor_text_pos_x < len(current_line):
            if self._cursor_x < self._cursor_max_right:
                self._cursor_x = self._cursor_x + 1
            elif self._viewport_x_start + self._viewport_width < len(current_line):
                self._viewport_x_start = self._viewport_x_start + 1
            self._cursor_text_pos_x = self._cursor_text_pos_x + 1

        self._logger.info('Moved cursor right to pos {}'.format(self._cursor_text_pos_x))


    def _move_up(self):
        """Function that moves the cursor/text position one location up
        """


        if self._cursor_text_pos_y > 0:
            if self._cursor_y > self._cursor_max_up:
                self._cursor_y = self._cursor_y - 1
            elif self._viewport_y_start > 0:
                self._viewport_y_start = self._viewport_y_start - 1
            self._cursor_text_pos_y = self._cursor_text_pos_y - 1
            if self._cursor_text_pos_x > len(self._text_lines[self._cursor_text_pos_y]):
                temp = len(self._text_lines[self._cursor_text_pos_y])
                self._cursor_x = self._cursor_x - (self._cursor_text_pos_x - temp)
                self._cursor_text_pos_x = temp

        self._logger.info('Moved cursor up to line {}'.format(self._cursor_text_pos_y))


    def _move_down(self):
        """Function that moves the cursor/text position one location down
        """

        if self._cursor_text_pos_y < len(self._text_lines) - 1:
            if self._cursor_y < self._cursor_max_down:
                self._cursor_y = self._cursor_y + 1
            elif self._viewport_y_start + self._viewport_height < len(self._text_lines):
                self._viewport_y_start = self._viewport_y_start + 1
            self._cursor_text_pos_y = self._cursor_text_pos_y + 1
            if self._cursor_text_pos_x > len(self._text_lines[self._cursor_text_pos_y]):
                temp = len(self._text_lines[self._cursor_text_pos_y])
                self._cursor_x = self._cursor_x - (self._cursor_text_pos_x - temp)
                self._cursor_text_pos_x = temp

        self._logger.info('Moved cursor down to line {}'.format(self._cursor_text_pos_y))


    def _page_up(self):
        for _ in range(self._viewport_height):
            self._move_up()


    def _page_down(self):
        for _ in range(self._viewport_height):
            self._move_down()


    def _handle_newline(self):
        """Function that handles recieving newline characters in the text
        """

        current_line = self.get_current_line()
        self._logger.info('Inserting newline in location {}'.format(self._cursor_text_pos_x))

        new_line_1 = current_line[:self._cursor_text_pos_x]
        new_line_2 = current_line[self._cursor_text_pos_x:]
        self._text_lines[self._cursor_text_pos_y] = new_line_1
        self._text_lines.insert(self._cursor_text_pos_y + 1, new_line_2)
        self._cursor_text_pos_y = self._cursor_text_pos_y + 1
        self._cursor_text_pos_x = 0
        self._cursor_x = self._cursor_max_left
        self._viewport_x_start = 0
        if self._cursor_y < self._cursor_max_down:
            self._cursor_y = self._cursor_y + 1
        elif self._viewport_y_start + self._viewport_height < len(self._text_lines):
            self._viewport_y_start = self._viewport_y_start + 1


    def _handle_backspace(self):
        """Function that handles recieving backspace characters in the text
        """

        current_line = self.get_current_line()
        self._logger.info('Inserting backspace in location {}'.format(self._cursor_text_pos_x))

        if self._cursor_text_pos_x == 0 and self._cursor_text_pos_y != 0:
            self._cursor_text_pos_x = len(self._text_lines[self._cursor_text_pos_y - 1])
            self._text_lines[self._cursor_text_pos_y - 1] = self._text_lines[self._cursor_text_pos_y - 1] + self._text_lines[self._cursor_text_pos_y]
            self._text_lines = self._text_lines[:self._cursor_text_pos_y] + self._text_lines[self._cursor_text_pos_y + 1:]
            self._cursor_text_pos_y = self._cursor_text_pos_y - 1
            self._cursor_x = self._cursor_max_left + self._cursor_text_pos_x
            if self._cursor_y > self._cursor_max_up:
                self._cursor_y = self._cursor_y - 1
            elif self._viewport_y_start > 0:
                self._viewport_y_start = self._viewport_y_start - 1
        elif self._cursor_text_pos_x > 0:
            self.set_text_line(current_line[:self._cursor_text_pos_x - 1] + current_line[self._cursor_text_pos_x:])
            if len(current_line) <= self._viewport_width:
                self._cursor_x = self._cursor_x - 1
            self._cursor_text_pos_x = self._cursor_text_pos_x - 1


    def _handle_home(self):
        """Function that handles recieving a home keypress
        """

        self._logger.info('Inserting Home')

        self._cursor_x = self._cursor_max_left
        self._cursor_text_pos_x = 0
        self._viewport_x_start = 0


    def _handle_end(self):
        """Function that handles recieving an end keypress
        """

        current_line = self.get_current_line()
        self._logger.info('Inserting End')

        self._cursor_text_pos_x = len(current_line)
        if len(current_line) > self._viewport_width:
            self._cursor_x = self._cursor_max_right
            self._viewport_x_start = self._cursor_text_pos_x - self._viewport_width
        else:
            self._cursor_x = self._cursor_max_left + len(current_line)


    def _handle_delete(self):
        """Function that handles recieving a delete keypress
        """

        current_line = self.get_current_line()
        self._logger.info('Inserting delete to pos {}'.format(self._cursor_text_pos_x))

        if self._cursor_text_pos_x == len(current_line) and self._cursor_text_pos_y < len(self._text_lines) - 1:
            self._text_lines[self._cursor_text_pos_y] = self._text_lines[self._cursor_text_pos_y] + self._text_lines[self._cursor_text_pos_y + 1]
            self._text_lines = self._text_lines[:self._cursor_text_pos_y+1] + self._text_lines[self._cursor_text_pos_y + 2:]
        elif self._cursor_text_pos_x < len(current_line):
            self.set_text_line(current_line[:self._cursor_text_pos_x] + current_line[self._cursor_text_pos_x+1:])


    def _insert_char(self, key_pressed):
        """Function that handles recieving a character

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """

        current_line = self.get_current_line()
        self._logger.info('Inserting character {} to pos {}'.format(chr(key_pressed), self._cursor_text_pos_x))

        self.set_text_line(current_line[:self._cursor_text_pos_x] + chr(key_pressed) + current_line[self._cursor_text_pos_x:])
        if len(current_line) <= self._viewport_width:
            self._cursor_x = self._cursor_x + 1
        elif self._viewport_x_start + self._viewport_width < len(current_line):
            self._viewport_x_start = self._viewport_x_start + 1
        self._cursor_text_pos_x = self._cursor_text_pos_x + 1


class ScrollTextBlock(Widget, TextBlockImplementation):
    """Widget for editing large multi-line blocks of text
    """

    def __init__(self, parent, title, row, column, row_span, column_span, padx=0, pady=0, initial_text=''):
        """Initializer for TextBlock Widget. Uses TextBlockImplementation as base
        """

        Widget.__init__(self, parent, title, row, column, row_span, column_span, padx, pady)
        TextBlockImplementation.__init__(self, initial_text, parent._logger)
        self._parent = parent
        self.update_height_width()
        self.set_help_text('Focus mode on TextBlock. Press Esc to exit focus mode.')


    def update_height_width(self):
        """Function that updates the position of the text and cursor on resize
        """

        Widget.update_height_width(self)
        self._viewport_y_start   = 0
        self._viewport_x_start   = 0
        self._cursor_text_pos_x  = 0
        self._cursor_text_pos_y  = 0
        self._cursor_y           = self._start_y + 1
        self._cursor_x           = self._start_x + self._padx + 2
        self._cursor_max_up      = self._cursor_y
        self._cursor_max_down    = self._start_y + self._height - self._pady - 2
        self._cursor_max_left    = self._cursor_x
        self._cursor_max_right   = self._start_x + self._width - self._padx - 1
        self._viewport_width     = self._cursor_max_right - self._cursor_max_left
        self._viewport_height    = self._cursor_max_down  - self._cursor_max_up


    def _handle_mouse_press(self, x, y):
        """Override of base class function, handles mouse press in menu

        Parameters
        ----------
        x, y : int
            Coordinates of mouse press
        """

        super()._handle_mouse_press(x, y)
        if y >= self._cursor_max_up and y <= self._cursor_max_down:
            if x >= self._cursor_max_left and x <= self._cursor_max_right:
                line_clicked_index = y - self._cursor_max_up + self._viewport_y_start
                if len(self._text_lines) <= line_clicked_index:
                    self._cursor_text_pos_y = len(self._text_lines) - 1
                    self._cursor_y = self._cursor_max_up + self._cursor_text_pos_y - self._viewport_y_start
                    line = self._text_lines[len(self._text_lines) - 1]
                else:
                    self._cursor_text_pos_y = line_clicked_index
                    self._cursor_y = y
                    line = self._text_lines[line_clicked_index]

                if x <= len(line) + self._cursor_max_left:
                    old_text_pos = self._cursor_text_pos_x
                    old_cursor_x = self._cursor_x
                    self._cursor_x = x
                    self._cursor_text_pos_x = old_text_pos + (x - old_cursor_x)
                else:
                    self._cursor_x = self._cursor_max_left + len(line)
                    self._cursor_text_pos_x = len(line)
        self._set_footer()


    def _handle_key_press(self, key_pressed):
        """Override of base class handle key press function

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """

        if super()._handle_key_press(key_pressed):
            return

        if key_pressed == py_cui.keys.KEY_LEFT_ARROW:
            self._move_left()
        elif key_pressed == py_cui.keys.KEY_RIGHT_ARROW:
            self._move_right()
        elif key_pressed == py_cui.keys.KEY_UP_ARROW:
            self._move_up()
        elif key_pressed == py_cui.keys.KEY_DOWN_ARROW:
            self._move_down()
        elif key_pressed == py_cui.keys.KEY_PAGE_UP:
            self._page_up()
        elif key_pressed == py_cui.keys.KEY_PAGE_DOWN:
            self._page_down()
        elif key_pressed == py_cui.keys.KEY_BACKSPACE:
            self._handle_backspace()
        elif key_pressed == py_cui.keys.KEY_DELETE:
            self._handle_delete()
        elif key_pressed == py_cui.keys.KEY_ENTER:
            self._handle_newline()
        elif key_pressed == py_cui.keys.KEY_TAB:
            for _ in range(0, 4):
                self._insert_char(py_cui.keys.KEY_SPACE)
        elif key_pressed == py_cui.keys.KEY_HOME:
            self._handle_home()
        elif key_pressed == py_cui.keys.KEY_END:
            self._handle_end()
        elif key_pressed > 31 and key_pressed < 128:
            self._insert_char(key_pressed)
        self._set_footer()


    def _draw(self):
        """Override of base class draw function
        """

        super()._draw()

        self._parent._renderer.set_color_mode(self._color)
        self._parent._renderer.draw_border(self)
        posy = self._cursor_max_up
        lastline = self._viewport_y_start
        for linei in range(self._viewport_y_start, self._viewport_y_start + self._viewport_height + 1):
            if linei >= len(self._text_lines):
                break
            render_text = self._text_lines[linei]
            self._parent._renderer.draw_text(self, render_text, posy,
                start_pos=self._viewport_x_start, selected=self._focused)
            lastline = linei
            posy += 1
        self._parent._renderer.draw_scrollbar(self, self._viewport_y_start + 1, lastline + 1, len(self._text_lines))
        if self._focused:
            self._parent._renderer.draw_cursor(self._cursor_y, self._cursor_x)
        else:
            self._parent._renderer.reset_cursor(self)
        self._parent._renderer.unset_color_mode(self._color)


