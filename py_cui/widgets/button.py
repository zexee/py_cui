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

    def __init__(self, parent, title, row, column, row_span, column_span, command):
        """Initializer for Button Widget
        """

        super().__init__(parent, title, row, column, row_span, column_span)
        self._style['alignment'] = 'center'
        self._style['vertical_alignment'] = 'middle'
        self._style['snap_border'] = False
        self._style['draw_title'] = False
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


    def _draw_content(self):
      return self._parent._renderer.draw_text_in_viewport(self, self._title, selected=self.is_hovering())



