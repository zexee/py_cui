"""Module containing classes for generic UI elements.

Contains base UI element class, along with UI implementation agnostic UI element classes.
"""

# Author:    Jakub Wlodek
# Created:   19-Mar-2020


import py_cui
import py_cui.errors
import py_cui.colors


class UIElement:
    """Base class for all UI elements. Extended by base widget and popup classes.

    Interfaces between UIImplementation subclasses and CUI engine. For example,
    a widget is a subclass of a UIElement. Then a TextBox widget would be a subclass
    of the base widget class, and the TextBoxImplementation. The TextBoxImplementation
    superclass contains logic for all textbox required operations, while the widget base
    class contains all links to the CUI engine.
    """

    def __init__(self, id, title, renderer, logger):
        self._id                        = id
        self._title                     = title
        self._footer                    = ''
        self._padx                      = 1
        self._pady                      = 0
        self._start_x,  self._stop_y    = 0, 0
        self._stop_x,   self._start_y   = 0, 0
        self._height,   self._width     = 0, 0
        # Default UI Element color is white on black.
        self._color                     = py_cui.WHITE_ON_BLACK
        self._border_color              = self._color
        self._hover_border_color        = self._color
        self._focus_border_color        = py_cui.BLACK_ON_WHITE
        self._selected_color            = self._color  # text color if focused
        self._mouse_press_handler       = None
        self._hovering                  = False
        self._focused                   = False
        self._renderer                  = renderer
        self._logger                    = logger
        self._help_text                 = ''
        self._single_line_mode          = False


    def set_single_line_mode(self):
        self._single_line_mode = True


    def get_absolute_start_pos(self):
        """Must be implemented by subclass, computes the absolute coords of upper-left corner
        """

        raise NotImplementedError


    def get_absolute_stop_pos(self):
        """Must be implemented by subclass, computes the absolute coords of bottom-right corner
        """

        raise NotImplementedError


    def get_absolute_dimensions(self):
        start_x,    start_y = self.get_absolute_start_pos()
        stop_x,     stop_y  = self.get_absolute_stop_pos()
        return (stop_y - start_y), (stop_x - start_x)


    def get_widget_start_pos(self):
        return (self._start_x + self._padx,
                self._start_y + int(self._height / 2) - 1
                    if self._single_line_mode
                    else self._start_y + self._pady)


    def get_widget_stop_pos(self):
        return (self._stop_x - self._padx - 1,
                self._start_y + int(self._height / 2) + 1
                    if self._single_line_mode
                    else self._stop_y - self._pady - 1)


    def get_viewport_start_pos(self):
        x, y = self.get_widget_start_pos()
        return x + 1, y + 1


    def get_viewport_stop_pos(self):
        x, y = self.get_widget_stop_pos()
        return x - 1, y - 1


    def update_height_width(self):
        self._start_x, self._start_y  = self.get_absolute_start_pos()
        self._stop_x,  self._stop_y   = self.get_absolute_stop_pos()
        self._height,  self._width    = self.get_absolute_dimensions()


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


    def get_padding(self):
        return self._padx, self._pady


    def get_start_position(self):
        return self._start_x, self._start_y


    def get_stop_position(self):
        return self._stop_x, self._stop_y


    def get_color(self):
        return self._color


    def get_selected_color(self):
        return self._selected_color


    def get_border_color(self):
        if self._focused:
            return self._focus_border_color
        if self._hovering:
            return self._hover_border_color
        else:
            return self._border_color


    def is_hovering(self):
        return self._hovering


    def is_focused(self):
        return self._focused


    def get_renderer(self):
        """Gets reference to renderer object

        Returns
        -------
        renderer : py_cui.renderer.Render
            renderer object used for drawing element
        """

        return self._renderer


    def get_help_text(self):
        """Returns current help text

        Returns
        -------
        help_text : str
            Current element status bar help message
        """

        return self._help_text


    def set_title(self, title):
        """Function that sets the widget title.

        Parameters
        ----------
        title : str
            New widget title
        """

        self._title = title


    def set_footer(self, footer):
        """Function that sets the widget footer.

        Parameters
        ----------
        footer : str
            New widget footer
        """

        self._footer = footer


    def set_color(self, color):
        """Sets element default color

        Parameters
        ----------
        color : int
            New color pair key code
        """

        if self._border_color == self._color:
            self._border_color = color
        if self._focus_border_color == self._color:
            self._focus_border_color = color
        if self._hover_border_color == self._color:
            self._hover_border_color = color
        self._color = color


    def set_border_color(self, color):
        self._border_color = color


    def set_focus_border_color(self, color):
        self._focus_border_color = color


    def set_hovering_border_color(self, color):
        self._hovering_border_color = color


    def set_selected_color(self, color):
        self._selected_color = color


    def set_hovering(self, hovering):
        self._hovering = hovering


    def set_focused(self, focused):
        self._focused = focused


    def set_help_text(self, help_text):
        """Sets status bar help text

        Parameters
        ----------
        help_text : str
            New statusbar help text
        """

        self._help_text = help_text


    def set_focus_text(self, focus_text):
        """Sets status bar focus text. Legacy function, overridden by set_focus_text

        Parameters
        ----------
        focus_text : str
            New statusbar help text
        """

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


    def _draw(self):
        """Must be implemented by subclasses. Uses renderer to draw element to terminal
        """

        raise NotImplementedError


    def _assign_renderer(self, renderer, quiet=False):
        """Function that assigns a renderer object to the element

        (Meant for internal usage only)

        Parameters
        ----------
        renderer : py_cui.renderer.Renderer
            Renderer for drawing element

        Raises
        ------
        error : PyCUIError
            If parameter is not an initialized renderer.
        """

        if renderer is None:
            self._logger.debug('Renderer to assign is a NoneType')
        elif self._renderer is not None:
            raise py_cui.errors.PyCUIError('Renderer already assigned for the element')
        elif isinstance(renderer, py_cui.renderer.Renderer):
            self._renderer = renderer
        else:
            raise py_cui.errors.PyCUIError('Invalid renderer, must be of type py_cui.renderer.Renderer')


    def _contains_position(self, x, y):
        """Checks if character position is within element.

        Parameters
        ----------
        x : int
            X coordinate to check
        y : int
            Y coordinate to check

        Returns
        -------
        contains : bool
            True if (x,y) is within the element, false otherwise
        """

        within_x = self._start_x <= x and self._start_x + self._width >= x
        within_y = self._start_y <= y and self._start_y + self._height >= y
        return within_x and within_y


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


