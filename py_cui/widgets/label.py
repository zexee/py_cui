from .widget import Widget


class Label(Widget):
    """The most basic subclass of Widget.

    Simply displays one centered row of text. Has no unique attributes or methods

    Attributes
    ----------
    draw_border : bool
        Toggle for drawing label border
    """

    def __init__(self, parent, title, row, column, row_span=1, column_span=1):
        """Initalizer for Label widget
        """

        super().__init__(parent, title, row, column, row_span, column_span)
        self._style['selectable'] = False
        self._style['alignment'] = 'center'
        self._style['vertical_alignment'] = 'middle'
        self._style['draw_border'] = False
        self._style['single_line_mode'] = True
        self._parent = parent


    def _draw_content(self):
      self._parent._renderer.draw_text_in_viewport(self, self._title)




