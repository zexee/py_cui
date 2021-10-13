import curses
import py_cui
import py_cui.ui
import py_cui.colors
import py_cui.errors


class Widget(py_cui.ui.UIElement):
    """Top Level Widget Base Class

    Extended by all widgets. Contains base classes for handling key presses, drawing,
    and setting status bar text.

    Attributes
    ----------
    _grid : py_cui.grid.Grid
        The parent grid object of the widget
    _row, _column : int
        row and column position of the widget
    _row_span, _column_span : int
        number of rows or columns spanned by the widget
    _selectable : bool
        Flag that says if a widget can be selected
    _key_commands : dict
        Dictionary mapping key codes to functions
    _text_color_rules : List[py_cui.ColorRule]
        color rules to load into renderer when drawing widget
    """

    def __init__(self, parent, title, row, column, row_span, column_span, padx, pady, selectable = True):
        """Initializer for base widget class

        Calss UIElement superclass initialzier, and then assigns widget to grid, along with row/column info
        and color rules and key commands
        """

        super().__init__(parent.get_next_id(), title, None, parent._logger)
        self._grid = parent._grid
        self._parent = parent
        grid_rows, grid_cols = self._grid.get_dimensions()
        if (grid_cols < column + column_span) or (grid_rows < row + row_span):
            raise py_cui.errors.PyCUIOutOfBoundsError("Target grid too small for widget {}".format(title))

        self._row          = row
        self._column       = column
        self._row_span     = row_span
        self._column_span  = column_span
        self._padx         = padx
        self._pady         = pady
        self._selectable       = selectable
        self._key_commands     = {}
        self._text_color_rules = []
        self._default_color = py_cui.WHITE_ON_BLACK
        self._border_color = self._default_color
        self.update_height_width()


    def add_key_command(self, key, command):
        """Maps a keycode to a function that will be executed when in focus mode

        Parameters
        ----------
        key : py_cui.keys.KEY
            ascii keycode used to map the key
        command : function without args
            a non-argument function or lambda function to execute if in focus mode and key is pressed
        """

        self._key_commands[key] = command


    def update_key_command(self, key, command):
        """Maps a keycode to a function that will be executed when in focus mode, if key is already mapped

        Parameters
        ----------
        key : py_cui.keys.KEY
            ascii keycode used to map the key
        command : function without args
            a non-argument function or lambda function to execute if in focus mode and key is pressed
        """

        if key in self._key_commands.keys():
            self.add_key_command(key, command)


    def add_text_color_rule(self, regex, color, rule_type, match_type='line', region=[0,1], include_whitespace=False, selected_color=None):
        """Forces renderer to draw text using given color if text_condition_function returns True

        Parameters
        ----------
        regex : str
            A string to check against the line for a given rule type
        color : int
            a supported py_cui color value
        rule_type : string
            A supported color rule type
        match_type='line' : str
            sets match type. Can be 'line', 'regex', or 'region'
        region=[0,1] : [int, int]
            A specified region to color if using match_type='region'
        include_whitespace : bool
            if false, strip string before checking for match
        """

        selected = color
        if selected_color is not None:
            selected = selected_color

        new_color_rule = py_cui.colors.ColorRule(regex, color, selected, rule_type, match_type, region, include_whitespace, self._logger)
        self._text_color_rules.append(new_color_rule)


    def get_absolute_start_pos(self):
        """Gets the absolute position of the widget in characters. Override of base class function

        Returns
        -------
        x_pos, y_pos : int
            position of widget in terminal
        """

        offset_x, offset_y      = self._grid.get_offsets()
        row_height, col_width   = self._grid.get_cell_dimensions()

        x_pos = self._column * col_width + offset_x
        # Always add two to the y_pos, because we have a title bar + a pad row
        y_pos = self._row * row_height + offset_y + self._parent._gui._top_padding + 1
        return x_pos, y_pos


    def get_absolute_stop_pos(self):
        """Gets the absolute dimensions of the widget in characters. Override of base class function
        """

        start_x, start_y = self.get_absolute_start_pos()
        row_height, col_width   = self._grid.get_cell_dimensions()
        return start_x + col_width * self._column_span - 1, start_y + row_height * self._row_span - 1


    def get_grid_cell(self):
        """Gets widget row, column in grid

        Returns
        -------
        row, column : int
            Initial row and column placement for widget in grid
        """

        return self._row, self._column


    def get_grid_cell_spans(self):
        """Gets widget row span, column span in grid

        Returns
        -------
        row_span, column_span : int
            Initial row span and column span placement for widget in grid
        """

        return self._row_span, self._column_span


    def set_selectable(self, selectable):
        """Setter for widget selectablility

        Paramters
        ---------
        selectable : bool
            Widget selectable if true, otherwise not
        """

        self._selectable = selectable


    def is_selectable(self):
        """Checks if the widget is selectable

        Returns
        -------
        selectable : bool
            True if selectable, false otherwise
        """

        return self._selectable


    def _is_row_col_inside(self, row, col):
        """Checks if a particular row + column is inside the widget area

        Parameters
        ----------
        row, col : int
            row and column position to check

        Returns
        -------
        is_inside : bool
            True if row, col is within widget bounds, false otherwise
        """

        is_within_rows  = self._row    <= row and row <= (self._row           + self._row_span   - 1)
        is_within_cols  = self._column <= col and col <= (self._column_span   + self._column     - 1)

        if is_within_rows and is_within_cols:
            return True
        else:
            return False


    # BELOW FUNCTIONS SHOULD BE OVERWRITTEN BY SUB-CLASSES


    def _handle_key_press(self, key_pressed):
        """Base class function that handles all assigned key presses.

        When overwriting this function, make sure to add a super()._handle_key_press(key_pressed) call,
        as this is required for user defined key command support

        Parameters
        ----------
        key_pressed : int
            key code of key pressed

        Returns
        -------
        is_inside : bool
            Whether the key is handled
        """

        if key_pressed in self._key_commands.keys():
            command = self._key_commands[key_pressed]
            command()
            return True
        return False


    def _draw(self):
        """Base class draw class that checks if renderer is valid.

        Should be called with super()._draw() in overrides.
        Also intializes color rules, so if not called color rules will not be applied
        """

        if self._renderer is None:
            return
        else:
            self._renderer.set_color_rules(self._text_color_rules)


