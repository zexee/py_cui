from .widget import Widget


class Label(Widget):
    """A Variation of the label widget that renders a block of text.

    Attributes
    ----------
    lines : list of str
        list of lines that make up block text
    center : bool
        Decides whether or not label should be centered
    """

    def __init__(self, parent, title, row, column, row_span=1, column_span=1):
      super().__init__(parent, title, row, column, row_span, column_span)
      self._parent = parent
      self._style['show_border']  = False
      self._style['selectable'] = False


    def set_title(self, title):
      self._title = title


    def _draw_content(self):
      return self._parent._renderer.draw_text_in_viewport(self, self._title)


