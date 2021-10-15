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
    _viewable_text_x, _viewable_text_y : int
        Initial location of viewport relative to text
    _cursor_text_x, _cursor_text_y : int
        Cursor position relative to text
    _cursor_x, _cursor_y : int
        Absolute cursor position in characters
    _cursor_max_up, _cursor_max_down : int
        cursor limits in vertical space
    _cursor_max_left, _cursor_max_right : int
        Cursor limits in horizontal space
    """

    def __init__(self, logger):
        """Initializer for TextBlockImplementation base class

        Zeros attributes, and parses initial text
        """

        super().__init__(logger)
        self._text_lines = ['']
        self._viewable_text_y = 0
        self._viewable_text_x = 0
        self._cursor_text_x = 0
        self._cursor_text_y = 0

        self._cursor_y = 0
        self._cursor_x = 0
        self._cursor_max_up = 0
        self._cursor_max_down = 0
        self._cursor_max_left = 0
        self._cursor_max_right = 0


    # Getters and setters
    def get_cursor_text_pos(self):
        return self._cursor_text_x, self._cursor_text_y


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
        self._cursor_text_x = 0
        self._cursor_text_y = 0
        self._viewable_text_y   = 0
        self._viewable_text_x   = 0
        self._text_lines = ['']
        self._set_footer()
        self._logger.info('Cleared textblock')


    def get_current_line(self):
        """Returns the line on which the cursor currently resides

        Returns
        -------
        current_line : str
            The current line of text that the cursor is on
        """

        return self._text_lines[self._cursor_text_y]


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

        self._text_lines[self._cursor_text_y] = text


    def _set_footer(self):
        x, y = self.get_cursor_text_pos()
        self.set_footer('{}:{}'.format(x + 1, y + 1))

    def _move_left(self):
        if self._cursor_text_x > 0:
          self._cursor_text_x -= 1
          if self._cursor_x > self._cursor_max_left:
            self._cursor_x -= 1
          elif self._viewable_text_x > 0:
            self._viewable_text_x -= 1


    def _move_right(self):
        current_line = self.get_current_line()
        if self._cursor_text_x < len(current_line):
          if self._cursor_x < self._cursor_max_right:
            self._cursor_x += 1
          elif self._viewable_text_x + self._viewport_width < len(current_line):
            self._viewable_text_x += 1
          self._cursor_text_x += 1


    def _move_up(self):
      if self._cursor_text_y > 0:
        if self._cursor_y > self._cursor_max_up:
          self._cursor_y -= 1
        elif self._viewable_text_y > 0:
          self._viewable_text_y -= 1
        self._cursor_text_y -= 1
        if self._cursor_text_x > len(self._text_lines[self._cursor_text_y]):
          length = len(self._text_lines[self._cursor_text_y])
          self._cursor_x -= self._cursor_text_x - length
          self._cursor_text_x = length


    def _move_down(self):
      if self._cursor_text_y < len(self._text_lines) - 1:
        if self._cursor_y < self._cursor_max_down:
          self._cursor_y += 1
        elif self._viewable_text_y + self._viewport_height < len(self._text_lines):
          self._viewable_text_y += 1
        self._cursor_text_y += 1
        if self._cursor_text_x > len(self._text_lines[self._cursor_text_y]):
          length = len(self._text_lines[self._cursor_text_y])
          self._cursor_x -= self._cursor_text_x - length
          self._cursor_text_x = length


    def _page_up(self):
      for _ in range(self._viewport_height):
        self._move_up()


    def _page_down(self):
      for _ in range(self._viewport_height):
        self._move_down()


    def _handle_newline(self):
        current_line = self.get_current_line()
        self._logger.info('Inserting newline in location {}'.format(self._cursor_text_x))

        new_line_1 = current_line[:self._cursor_text_x]
        new_line_2 = current_line[self._cursor_text_x:]
        self._text_lines[self._cursor_text_y] = new_line_1
        self._text_lines.insert(self._cursor_text_y + 1, new_line_2)
        self._cursor_text_y += 1
        self._cursor_text_x = 0
        self._cursor_x = self._cursor_max_left
        self._viewable_text_x = 0
        if self._cursor_y < self._cursor_max_down:
          self._cursor_y += 1
        elif self._viewable_text_y + self._viewport_height < len(self._text_lines):
          self._viewable_text_y += 1


    def _handle_backspace(self):
        current_line = self.get_current_line()
        self._logger.info('Inserting backspace in location {}'.format(self._cursor_text_x))

        if self._cursor_text_x == 0 and self._cursor_text_y != 0:
          self._cursor_text_x = len(self._text_lines[self._cursor_text_y - 1])
          self._text_lines[self._cursor_text_y - 1] = self._text_lines[self._cursor_text_y - 1] + self._text_lines[self._cursor_text_y]
          self._text_lines = self._text_lines[:self._cursor_text_y] + self._text_lines[self._cursor_text_y + 1:]
          self._cursor_text_y -= 1
          self._cursor_x = self._cursor_max_left + self._cursor_text_x
          if self._cursor_y > self._cursor_max_up:
            self._cursor_y -= 1
          elif self._viewable_text_y > 0:
            self._viewable_text_y -= 1
        elif self._cursor_text_x > 0:
          self.set_text_line(current_line[:self._cursor_text_x - 1] + current_line[self._cursor_text_x:])
          if len(current_line) <= self._viewport_width:
            self._cursor_x -= 1
          self._cursor_text_x -= 1


    def _handle_home(self):
      self._cursor_x = self._cursor_max_left
      self._cursor_text_x = 0
      self._viewable_text_x = 0


    def _handle_end(self):
      current_line = self.get_current_line()

      self._cursor_text_x = len(current_line)
      if len(current_line) > self._viewport_width:
        self._cursor_x = self._cursor_max_right
        self._viewable_text_x = self._cursor_text_x - self._viewport_width
      else:
        self._cursor_x = self._cursor_max_left + len(current_line)


    def _handle_delete(self):
      current_line = self.get_current_line()

      if self._cursor_text_x == len(current_line) and self._cursor_text_y < len(self._text_lines) - 1:
        self._text_lines[self._cursor_text_y] = self._text_lines[self._cursor_text_y] + self._text_lines[self._cursor_text_y + 1]
        self._text_lines = self._text_lines[:self._cursor_text_y+1] + self._text_lines[self._cursor_text_y + 2:]
      elif self._cursor_text_x < len(current_line):
        self.set_text_line(current_line[:self._cursor_text_x] + current_line[self._cursor_text_x+1:])


    def _insert_char(self, key_pressed):
      current_line = self.get_current_line()

      self.set_text_line(current_line[:self._cursor_text_x] + chr(key_pressed) + current_line[self._cursor_text_x:])
      if len(current_line) <= self._viewport_width:
        self._cursor_x += 1
      elif self._viewable_text_x + self._viewport_width < len(current_line):
        self._viewable_text_x += 1
      self._cursor_text_x += 1


class ScrollTextBlock(Widget, TextBlockImplementation):
    """Widget for editing large multi-line blocks of text
    """

    def __init__(self, parent, title, row, column, row_span, column_span):
      Widget.__init__(self, parent, title, row, column, row_span, column_span)
      TextBlockImplementation.__init__(self, parent._logger)
      self._parent = parent
      self.update_height_width()
      self.set_help_text('Focus mode on TextBlock. Press Esc to exit focus mode.')


    def update_height_width(self):
      Widget.update_height_width(self)
      self._viewable_text_y = 0
      self._viewable_text_x = 0
      self._cursor_text_x  = 0
      self._cursor_text_y  = 0
      self._cursor_x, self._cursor_y = self.get_viewport_start_pos()
      self._cursor_max_left, self._cursor_max_up = self._cursor_x, self._cursor_y
      self._cursor_max_right, self._cursor_max_down = self.get_viewport_stop_pos()
      self._viewport_width = self.get_viewport_width()
      self._viewport_height = self.get_viewport_height()


    def _handle_mouse_press(self, x, y):
      super()._handle_mouse_press(x, y)
      if y >= self._cursor_max_up and y <= self._cursor_max_down:
        if x >= self._cursor_max_left and x <= self._cursor_max_right:
          line_clicked_index = y - self._cursor_max_up + self._viewable_text_y
          if len(self._text_lines) <= line_clicked_index:
            self._cursor_text_y = len(self._text_lines) - 1
            self._cursor_y = self._cursor_max_up + self._cursor_text_y - self._viewable_text_y
            line = self._text_lines[len(self._text_lines) - 1]
          else:
            self._cursor_text_y = line_clicked_index
            self._cursor_y = y
            line = self._text_lines[line_clicked_index]

          if x <= len(line) + self._cursor_max_left:
            old_text_pos = self._cursor_text_x
            old_cursor_x = self._cursor_x
            self._cursor_x = x
            self._cursor_text_x = old_text_pos + (x - old_cursor_x)
          else:
            self._cursor_x = self._cursor_max_left + len(line)
            self._cursor_text_x = len(line)
      self._set_footer()


    def _handle_key_press(self, key_pressed):
      if super()._handle_key_press(key_pressed):
          return

      if key_pressed == py_cui.keys.KEY_LEFT_ARROW: self._move_left()
      elif key_pressed == py_cui.keys.KEY_RIGHT_ARROW: self._move_right()
      elif key_pressed == py_cui.keys.KEY_UP_ARROW: self._move_up()
      elif key_pressed == py_cui.keys.KEY_DOWN_ARROW: self._move_down()
      elif key_pressed == py_cui.keys.KEY_PAGE_UP: self._page_up()
      elif key_pressed == py_cui.keys.KEY_PAGE_DOWN: self._page_down()
      elif key_pressed == py_cui.keys.KEY_BACKSPACE: self._handle_backspace()
      elif key_pressed == py_cui.keys.KEY_DELETE: self._handle_delete()
      elif key_pressed == py_cui.keys.KEY_ENTER: self._handle_newline()
      elif key_pressed == py_cui.keys.KEY_TAB:
          for _ in range(0, 4):
              self._insert_char(py_cui.keys.KEY_SPACE)
      elif key_pressed == py_cui.keys.KEY_HOME: self._handle_home()
      elif key_pressed == py_cui.keys.KEY_END: self._handle_end()
      elif key_pressed > 31 and key_pressed < 128:
          self._insert_char(key_pressed)
      self._set_footer()


    def _draw_content(self):
      startx, starty = self.get_viewport_start_pos()
      stopx, stopy = self.get_viewport_stop_pos()
      posy = starty
      self.lastline = self._viewable_text_y
      for linei in range(self._viewable_text_y, self._viewable_text_y + self._viewport_height):
        render_text = self._text_lines[linei] if linei < len(self._text_lines) else ''
        self._parent._renderer.draw_text_in(self, render_text,
            startx, stopx, posy, stopy, selected=self._focused)
        self.lastline = linei
        posy += 1


    def _draw_scrollbar(self):
      self._parent._renderer.draw_scrollbar(self, self._viewable_text_y + 1, self.lastline + 1, len(self._text_lines))


    def _draw_cursor(self):
        if self._focused:
            self._parent._renderer.draw_cursor(self._cursor_y, self._cursor_x)
        else:
            self._parent._renderer.reset_cursor(self)


