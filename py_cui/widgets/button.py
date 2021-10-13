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

    def __init__(self, parent, title, row, column, row_span, column_span, padx, pady, command):
        """Initializer for Button Widget
        """

        super().__init__(parent, title, row, column, row_span, column_span, padx, pady)
        self.command = command
        self._parent = parent
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
        self._parent._renderer.set_color_mode(self.get_color())
        self._parent._renderer.draw_border(self, with_title=False)
        button_text_y_pos = self._start_y + int(self._height / 2)
        self._parent._renderer.draw_text(self, self._title, button_text_y_pos, centered=True)
        self._parent._renderer.reset_cursor(self)
        self._parent._renderer.unset_color_mode(self.get_color())


