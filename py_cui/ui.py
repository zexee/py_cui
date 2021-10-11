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

    Attributes
    ----------
    _id : str
        Internal UI element unique ID
    _title : str
        UI element title
    _padx, pady : int, int
        padding in terminal characters
    _start_x, _start_y: int, int
        Coords in terminal characters for top-left corner of element
    _stop_x, _stop_y : int, int
        Coords in terminal characters for bottom-right corner of element
    _height, width : int, int
        absolute dimensions of ui element in terminal characters
    _color : int
        Default color for which to draw element
    _border_color: int
        Color used to draw the border of the element when not focused
    _focus_border_color: int
        Color used to draw the border of the element when focused
    _selected : bool
        toggle for marking an element as selected
    _renderer : py_cui.renderer.Renderer
        The default ui renderer
    _logger   : py_cui.debug.PyCUILogger
        The default logger inherited from the parent
    _help_text: str
        Text to diplay when selected in status bar
    """

    def __init__(self, id, title, renderer, logger):
        """Initializer for UIElement base class
        """

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
        self._focus_border_color        = self._color
        self._selected_color            = self._color
        self._mouse_press_handler       = None
        self._selected                  = False
        self._renderer                  = renderer
        self._logger                    = logger
        self._help_text                 = ''


    def get_absolute_start_pos(self):
        """Must be implemented by subclass, computes the absolute coords of upper-left corner
        """

        raise NotImplementedError


    def get_absolute_stop_pos(self):
        """Must be implemented by subclass, computes the absolute coords of bottom-right corner
        """

        raise NotImplementedError


    def get_absolute_dimensions(self):
        """Gets dimensions of element in terminal characters

        Returns
        -------
        height, width : int, int
            Dimensions of element in terminal characters
        """
        start_x,    start_y = self.get_absolute_start_pos()
        stop_x,     stop_y  = self.get_absolute_stop_pos()
        return (stop_y - start_y), (stop_x - start_x)


    def update_height_width(self):
        """Function that refreshes position and dimensons on resize.

        If necessary, make sure required widget attributes updated here as well.
        """

        self._start_x, self._start_y  = self.get_absolute_start_pos()
        self._stop_x,  self._stop_y   = self.get_absolute_stop_pos()
        self._height,  self._width    = self.get_absolute_dimensions()


    def get_viewport_height(self):
        """Gets the height of the element viewport (height minus padding and borders)

        Returns
        -------
        viewport_height : int
            Height of element viewport in terminal characters
        """

        return self._height - (2 * self._pady) - 2


    def get_id(self):
        """Gets the element ID

        Returns
        -------
        id : int
            The ui element id
        """

        return self._id


    def get_title(self):
        """Getter for ui element title

        Returns
        -------
        title : str
            UI element title
        """

        return self._title


    def get_footer(self):
        """Getter for ui element footer

        Returns
        -------
        footer : str
            UI element title
        """

        return self._footer


    def get_padding(self):
        """Gets ui element padding on in characters

        Returns
        -------
        padx, pady : int, int
            Padding on either axis in characters
        """

        return self._padx, self._pady


    def get_start_position(self):
        """Gets coords of upper left corner

        Returns
        -------
        start_x, start_y : int, int
            Coords of upper right corner
        """

        return self._start_x, self._start_y


    def get_stop_position(self):
        """Gets coords of lower right corner

        Returns
        -------
        stop_x, stop_y : int, int
            Coords of lower right corner
        """

        return self._stop_x, self._stop_y


    def get_color(self):
        """Gets current element color

        Returns
        -------
        color : int
            color code for combination
        """

        return self._color


    def get_border_color(self):
        """Gets current element border color

        Returns
        -------
        color : int
            color code for combination
        """

        if self._selected:
            return self._focus_border_color
        else:
            return self._border_color


    def get_selected_color(self):
        """Gets current selected item color

        Returns
        -------
        color : int
            color code for combination
        """

        return self._selected_color


    def is_selected(self):
        """Get selected status

        Returns
        -------
        selected : bool
            True if selected, False otherwise
        """

        return self._selected


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
        if self._selected_color == self._color:
            self._selected_color = color
        self._color = color


    def set_border_color(self, color):
        """Sets element border color

        Parameters
        ----------
        color : int
            New color pair key code
        """

        self._border_color = color


    def set_focus_border_color(self, color):
        """Sets element border color if the current element
        is focused

        Parameters
        ----------
        color : int
            New color pair key code
        """

        self._focus_border_color = color


    def set_selected_color(self, color):
        """Sets element sected color

        Parameters
        ----------
        color : int
            New color pair key code
        """

        self._selected_color = color


    def set_selected(self, selected):
        """Marks the UI element as selected or not selected

        Parameters
        ----------
        selected : bool
            The new selected state of the element
        """

        self._selected = selected


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


