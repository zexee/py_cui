from .widget import Widget


class Label(Widget):
    """The most basic subclass of Widget.

    Simply displays one centered row of text. Has no unique attributes or methods

    Attributes
    ----------
    draw_border : bool
        Toggle for drawing label border
    """

    def __init__(self, id, title,  grid, row, column, row_span, column_span, padx, pady, logger):
        """Initalizer for Label widget
        """

        super().__init__(id, title, grid, row, column, row_span, column_span, padx, pady, logger, selectable=False)
        self._draw_border = False


    def toggle_border(self):
        """Function that gives option to draw border around label
        """

        self._draw_border = not self._draw_border


    def _draw(self):
        """Override base draw class.

        Center text and draw it
        """

        super()._draw()
        self._renderer.set_color_mode(self._color)
        if self._draw_border:
            self._renderer.draw_border(self, with_title=False)
        target_y = self._start_y + int(self._height / 2)
        self._renderer.draw_text(self, self._title, target_y, centered=True, bordered=self._draw_border)
        self._renderer.unset_color_mode(self._color)


