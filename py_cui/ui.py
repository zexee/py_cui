import py_cui
import py_cui.errors
import py_cui.colors


class UIElement:
    def __init__(self, id, title, renderer, logger):
        self._id = id
        self._start_x, self._stop_y = 0, 0
        self._stop_x, self._start_y = 0, 0

        self._title = title
        self._footer = ''
        self._help_text = ''

        self._height, self._width = 0, 0
        # Default UI Element color is white on black.
        self._mouse_press_handler = None
        self._hovering = False
        self._focused = False
        self._renderer = renderer
        self._logger = logger

        # default attributes
        self._style = {
            'color': py_cui.WHITE_ON_BLACK,
            'border_color': py_cui.WHITE_ON_BLACK,
            'hover_border_color': py_cui.WHITE_ON_BLACK,
            'focus_border_color': py_cui.BLACK_ON_WHITE,
            'selected_color': py_cui.WHITE_ON_BLACK,
            'margin_x': 0,
            'margin_y': 0,
            'padding_x': 1,
            'padding_y': 0,
            'border_width': 1,
            'snap_border': True,
            'alignment': 'left',
            'vertical_alignment': 'top',
            'selectable': True,
            'show_border': True,
            'show_title': True,
            'show_footer': True,
            'single_line_mode': False,
        }


    def set_style(self, key, value):
      # easy setting style
      self._style[key] = value
      return self


    def get_absolute_start_pos(self):
        raise NotImplementedError


    def get_absolute_stop_pos(self):
        raise NotImplementedError


    def get_absolute_dimensions(self):
        return (self._stop_y - self._start_y + 1), (self._stop_x - self._start_x + 1)


    def get_widget_start_pos(self):
        return (self._start_x + self._style['margin_x'],
                self._start_y + int(self._height / 2) - 1
                    if self._style['single_line_mode']
                    else self._start_y + self._style['margin_y'])


    def get_widget_stop_pos(self):
        return (self._stop_x - self._style['margin_x'],
                self._start_y + int(self._height / 2) + 1
                    if self._style['single_line_mode']
                    else self._stop_y - self._style['margin_y'])


    def get_viewport_start_pos(self):
        x, y = self.get_widget_start_pos()
        return (x + (self._style['border_width'] if self._style['show_border'] else 0) + self._style['padding_x'],
                y + (self._style['border_width'] if self._style['show_border'] else 0) + self._style['padding_y'])


    def get_viewport_stop_pos(self):
        x, y = self.get_widget_stop_pos()
        return (x - (self._style['border_width'] if self._style['show_border'] else 0) - self._style['padding_x'],
                y - (self._style['border_width'] if self._style['show_border'] else 0) - self._style['padding_y'])


    def update_size(self):
        self._height = self._stop_y - self._start_y + 1
        self._width = self._stop_x - self._start_x + 1


    def get_viewport_width(self):
      startx, _ = self.get_viewport_start_pos()
      stopx, _ = self.get_viewport_stop_pos()
      return stopx - startx + 1


    def get_viewport_height(self):
      _, starty = self.get_viewport_start_pos()
      _, stopy = self.get_viewport_stop_pos()
      return stopy - starty + 1


    def get_id(self):
        return self._id


    def get_title(self):
        return self._title


    def get_footer(self):
        return self._footer


    def get_start_position(self):
        return self._start_x, self._start_y


    def get_stop_position(self):
        return self._stop_x, self._stop_y


    def get_color(self):
        return self._style['color']


    def get_selected_color(self):
        return self._style['selected_color']


    def get_border_color(self):
        if self._focused:
            return self._style['focus_border_color']
        if self._hovering:
            return self._style['hover_border_color']
        else:
            return self._style['border_color']


    def is_hovering(self):
        return self._hovering


    def is_focused(self):
        return self._focused


    def get_renderer(self):
        return self._renderer


    def get_help_text(self):
        return self._help_text


    def set_title(self, title):
        self._title = title


    def set_footer(self, footer):
        self._footer = footer


    def set_color(self, color):
        if self._style['border_color'] == self._style['color']:
            self._style['border_color'] = color
        if self._style['focus_border_color'] == self._style['color']:
            self._style['focus_border_color'] = color
        if self._style['hover_border_color'] == self._style['color']:
            self._style['hover_border_color'] = color
        self._style['color'] = color


    def set_border_color(self, color):
        self._style['border_color'] = color


    def set_focus_border_color(self, color):
        self._style['focus_border_color'] = color


    def set_hovering_border_color(self, color):
        self._style['hovering_border_color'] = color


    def set_selected_color(self, color):
        self._style['selected_color'] = color


    def set_hovering(self, hovering):
        self._hovering = hovering


    def set_focused(self, focused):
        self._focused = focused


    def set_help_text(self, help_text):
        self._help_text = help_text


    def set_focus_text(self, focus_text):
        self._help_text = focus_text


    def _handle_key_press(self, key_pressed):
        """Must be implemented by subclass. Used to handle keypresses
        """

        raise NotImplementedError


    def add_mouse_press_handler(self, mouse_press_handler_func):
        """Sets a mouse press handler function

        Parameters
        ----------
        mouse_press_handler_func : function / lambda function
            Function that takes 2 parameters: x and y of a mouse press. Executes when mouse pressed and element is selected
        """

        self._mouse_press_handler = mouse_press_handler_func


    def _handle_mouse_press(self, x, y):
        """Can be implemented by subclass. Used to handle mouse presses

        Parameters
        ----------
        x, y : int, int
            Coordinates of the mouse press event.
        """

        if self._mouse_press_handler is not None:
            self._mouse_press_handler(x, y)


    def _draw_border(self):
      self._renderer.draw_border(self)


    def _draw_scrollbar(self):
      # for multiline-overflow widget, need to override this if need cursor
      pass


    def _draw_cursor(self):
      # for editing widget, need to override this if need cursor
      self._parent._renderer.reset_cursor(self)


    def _draw_content(self):
        """Must be implemented by subclasses.
        """

        raise NotImplementedError


    def _draw(self):
        self._renderer.set_color_mode(self._style['color'])
        if self._style['show_border']:
          self._draw_border()
        self._draw_content()
        # _draw_scrollbar should be after _draw_content, since _draw_content need to count the displaying lines.
        self._draw_scrollbar()
        self._renderer.unset_color_mode(self._style['color'])
        if self.is_focused():
          self._draw_cursor()
        else:
          x, y = self.get_widget_start_pos()
          self._parent._renderer.draw_cursor(y, x)


    def _contains_position(self, x, y):
        return self._start_x <= x and self._stop_x >= x and self._start_y <= y and self._stop_y >= y


class UIImplementation:
    """Base class for ui implementations.

    Should be extended for creating logic common accross ui elements.
    For example, a textbox needs the same logic for a widget or popup.
    This base class is only used to initialize the logger

    Attributes
    ----------
    _logger : py_cui.debug.PyCUILogger
        parent logger object reference.
    """

    def __init__(self, logger):
        self._logger = logger


