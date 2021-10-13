from .widget import Widget


class BlockLabel(Widget):
    """A Variation of the label widget that renders a block of text.

    Attributes
    ----------
    lines : list of str
        list of lines that make up block text
    center : bool
        Decides whether or not label should be centered
    """

    def __init__(self, parent, title, row, column, row_span=1, column_span=1, padx=0, pady=0, center=True):
        """Initializer for blocklabel widget
        """

        super().__init__(parent, title, row, column, row_span, column_span, padx, pady, selectable=False)
        self._parent = parent
        self._lines        = title.splitlines()
        self._center       = center
        self._draw_border  = False


    def set_title(self, title):
        """Override of base class, splits title into lines for rendering line by line.

        Parameters
        ----------
        title : str
            The new title for the block label object.
        """

        self._title = title
        self._lines = title.splitlines()


    def toggle_border(self):
        """Function that gives option to draw border around label
        """

        self._draw_border = not self._draw_border


    def _draw(self):
        """Override base draw class.

        Center text and draw it
        """

        super()._draw()
        self._parent._renderer.set_color_mode(self._color)
        if self._draw_border:
            self._parent._renderer.draw_border(self, with_title=False)
        counter = self._start_y
        for line in self._lines:
            if counter == self._start_y + self._height - self._pady:
                break
            self._parent._renderer.draw_text(self, line, counter, centered = self._center, bordered=self._draw_border)
            counter = counter + 1
        self._parent._renderer.unset_color_mode(self._color)


