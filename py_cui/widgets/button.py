from .widget import Widget
from py_cui.colors import *


class Button(Widget):
    """Basic button widget.

    Allows for running a command function on Enter

    Attributes
    ----------
    command : function
        A no-args function to run when the button is pressed.
    """

    def __init__(self, id, title, grid, row, column, row_span, column_span, padx, pady, logger, command):
        """Initializer for Button Widget
        """

        super().__init__(id, title, grid, row, column, row_span, column_span, padx, pady, logger)
        self.command = command
        self.set_color(py_cui.MAGENTA_ON_BLACK)
        self.set_help_text('Focus mode on Button. Press Enter to press button, Esc to exit focus mode.')


    def _handle_key_press(self, key_pressed):
        """Override of base class, adds ENTER listener that runs the button's command

        Parameters
        ----------
        key_pressed : int
            Key code of pressed key
        """

        super()._handle_key_press(key_pressed)
        if key_pressed == py_cui.keys.KEY_ENTER:
            if self.command is not None:
                return self.command()


    def _draw(self):
        """Override of base class draw function
        """

        super()._draw()
        self._renderer.set_color_mode(self.get_color())
        self._renderer.draw_border(self, with_title=False)
        button_text_y_pos = self._start_y + int(self._height / 2)
        self._renderer.draw_text(self, self._title, button_text_y_pos, centered=True, selected=self._selected)
        self._renderer.reset_cursor(self)
        self._renderer.unset_color_mode(self.get_color())


