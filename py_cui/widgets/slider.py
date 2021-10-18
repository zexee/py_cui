from .widget import Widget
from py_cui.ui import UIImplementation
import py_cui.keys


class SliderImplementation(UIImplementation):

    def __init__(self, min_val, max_val, init_val, step, logger):
        super().__init__(logger)

        self._min_val = min_val
        self._max_val = max_val
        self._cur_val = init_val
        self._step = step

        self._bar_char = "#"

        if self._cur_val < self._min_val or self._cur_val > self._max_val:
            raise py_cui.errors.PyCUIInvalidValue(
                'initial value must be between {} and {}'
                .format(self._min_val, self._max_val))


    def set_bar_char(self, char):
        """
        Updates the character used to represent the slider bar.

        Parameters
        ----------
        char : str
            Character to represent progressive bar.
        """

        assert len(char) == 1, "char should contain exactly one character, got {} instead.".format(len(char))
        self._bar_char = char


    def update_slider_value(self, offset: int) -> float:
        """
        Steps up or down the value in offset fashion.

        Parameters
        ----------
        offset : int
            Number of steps to increase or decrease the slider value.

        Returns
        -------
        self._cur_val: float
            Current slider value.
        """

        # direction , 1 raise value, -1 lower value
        self._cur_val += (offset * self._step)

        if self._cur_val < self._min_val:
            self._cur_val = self._min_val

        elif self._cur_val > self._max_val:
            self._cur_val = self._max_val

        return self._cur_val


    def get_slider_value(self):
        """
        Returns current slider value.

        Returns
        -------
        self._cur_val: float
            Current slider value.
        """

        return self._cur_val


    def set_slider_step(self, step):
        """
        Changes the step value.

        Parameters
        ----------
        step : int
            Step size of the slider.
        """

        self._step = step


class Slider(Widget, SliderImplementation):
    """
    Widget for a Slider

    Parameters
    ----------
    min_val : int
        Lowest value of the slider
    max_val: int
        Highest value of the slider
    step : int
        Increment from low to high value
    init_val:
        Initial value of the slider
    """

    def __init__(self, parent, title,
                 min_val=0, max_val=100, step=1, init_val=50):

        SliderImplementation.__init__(self, min_val, max_val, init_val, step, parent._logger)

        Widget.__init__(self, parent, title)

        self._parent = parent
        self._display_value = True
        self._style['draw_border'] = True
        self._style['single_line_mode'] = True
        self._style['vertical_alignment'] = 'top'
        self.set_help_text("Focus mode on Slider. Use left/right to adjust value. Esc to exit.")


    def toggle_title(self):
        """Toggles visibility of the widget's name.
        """

        self._title_enabled = not self._title_enabled


    def toggle_border(self):
        """Toggles visibility of the widget's border.
        """

        self._border_enabled = not self._border_enabled


    def toggle_value(self):
        """Toggles visibility of the widget's current value in integer.
        """

        self._display_value = not self._display_value


    def _generate_bar(self, width: int) -> str:
        """
        Internal implementation to generate progression bar.

        Parameters
        ----------
        width : int
            Width of bar in character length.

        Returns
        -------
        progress: str
            progressive bar string  with length of width.
        """
        if self._display_value:
            min_string = str(self._min_val)
            value_str = str(int(self._cur_val))

            width -= len(min_string)

            bar = self._bar_char * int((width * (self._cur_val - self._min_val)) / (self._max_val - self._min_val))
            progress = (self._bar_char * len(min_string) + bar)[: -len(value_str)] + value_str
        else:
            progress = self._bar_char * int((width * (self._cur_val - self._min_val)) / (self._max_val - self._min_val))

        return progress


    def _draw_content(self):
        width = self.get_viewport_width()
        self._parent._renderer.draw_text_in_viewport(
            self, self._generate_bar(width), selected=self.is_focused())


    def _handle_key_press(self, key_pressed):
        """
        LEFT_ARROW decreases value, RIGHT_ARROW increases.

        Parameters
        ----------
        key_pressed : int
            key code of pressed key
        """

        super()._handle_key_press(key_pressed)
        if key_pressed == py_cui.keys.KEY_LEFT_ARROW:
            self.update_slider_value(-1)
        if key_pressed == py_cui.keys.KEY_RIGHT_ARROW:
            self.update_slider_value(1)


