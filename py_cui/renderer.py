"""Module containing the py_cui renderer. It is used to draw all of the onscreen ui_elements and items.
"""

# Author:    Jakub Wlodek
# Created:   12-Aug-2019

import curses
import py_cui
import py_cui.colors


class Renderer:
    """Main renderer class used for drawing ui_elements to the terminal.

    Has helper functions for drawing the borders, cursor,
    and text required for the cui. All of the functions supplied by the renderer class should only be used internally.

    Attributes
    ----------
    root : py_cui.PyCUI
        The parent window
    stdscr : standard cursor
        The cursor with which renderer draws text
    color_rules : list of py_cui.colors.ColorRule
        List of currently loaded rules to apply during drawing
    """

    def __init__(self, gui):
        self._gui = gui
        self._color_rules  = []


    def _set_bold(self):
        self._gui._stdscr.attron(curses.A_BOLD)


    def _unset_bold(self):
        self._gui._stdscr.attroff(curses.A_BOLD)


    def set_color_rules(self, color_rules):
        self._color_rules = color_rules


    def set_color_mode(self, color_mode):
        self._gui._stdscr.attron(curses.color_pair(color_mode))


    def unset_color_mode(self, color_mode):
        self._gui._stdscr.attroff(curses.color_pair(color_mode))


    def reset_cursor(self, ui_element):
        self._gui.hide_cursor()
        return
        cursor_x, cursor_y = ui_element.get_widget_start_pos()
        try:
            self._gui._stdscr.move(cursor_y, cursor_x)
        except:
            self._gui._stdscr.move(0,0)


    def draw_cursor(self, cursor_y, cursor_x):
        self._gui.show_cursor()
        self._gui._stdscr.move(cursor_y, cursor_x)


    def draw_scrollbar(self, ui_element, begin, end, limit):
        _, start_y    = ui_element.get_viewport_start_pos()
        stop_x, _     = ui_element.get_widget_stop_pos()
        height        = ui_element.get_viewport_height()
        # self._gui._logger.info('scroll {} {} {}'.format(begin, end, limit))
        if begin == 1 and end >= limit:
            return
        begin_ratio = float(begin - 1) / limit
        end_ratio = float(end) / limit
        self.set_color_mode(ui_element.get_border_color())
        if ui_element.is_hovering(): self._set_bold()
        for i in range(height):
            ratio0 = float(i) / height
            ratio1 = float(i + 1) / height
            if (ratio0 <= begin_ratio <= ratio1 or
                ratio0 <= end_ratio <= ratio1 or
                begin_ratio <= ratio1 <= end_ratio):
                self._gui._stdscr.addstr(start_y + i, stop_x,
                                         self._gui._border_characters['SCROLLBAR'])
        if ui_element.is_hovering(): self._unset_bold()
        self.unset_color_mode(ui_element.get_border_color())


    def draw_border(self, ui_element):
        if ui_element.is_hovering():
            self._set_bold()

        _, border_y_start = ui_element.get_widget_start_pos()
        _, border_y_stop = ui_element.get_widget_stop_pos()

        self._draw_border_top(ui_element, border_y_start)

        for i in range(border_y_start + 1, border_y_stop):
            self._draw_blank_row(ui_element, i)

        self._draw_border_bottom(ui_element, border_y_stop)

        if ui_element.is_hovering():
            self._unset_bold()


    def _draw_border_top(self, ui_element, y):
        start_x, _ = ui_element.get_widget_start_pos()
        stop_x, _ = ui_element.get_widget_stop_pos()
        width = stop_x - start_x + 1
        title = ui_element.get_title()

        self.set_color_mode(ui_element.get_border_color())
        if not ui_element._style['show_title'] or not title or len(title) + 4 > width:
            render_text = '{}{}{}'.format(
                self._gui._border_characters['UP_LEFT'],
                self._gui._border_characters['HORIZONTAL'] * (width - 2),
                self._gui._border_characters['UP_RIGHT'])
            self._gui._stdscr.addstr(y, start_x, render_text)
        else:
            render_text = '{}{} {} {}{}'.format(
                self._gui._border_characters['UP_LEFT'],
                self._gui._border_characters['HORIZONTAL'] * 2,
                title,
                self._gui._border_characters['HORIZONTAL'] * (width - 6 - len(title)),
                self._gui._border_characters['UP_RIGHT'])
            self._gui._stdscr.addstr(y, start_x, render_text)
        self.unset_color_mode(ui_element.get_border_color())


    def _draw_border_bottom(self, ui_element, y):
        start_x, _ = ui_element.get_widget_start_pos()
        stop_x, _ = ui_element.get_widget_stop_pos()
        width = stop_x - start_x + 1
        footer = ui_element.get_footer()

        self.set_color_mode(ui_element.get_border_color())
        if not ui_element._style['show_footer'] or not footer or len(footer) + 4 > width:
            render_text = '{}{}{}'.format(
                self._gui._border_characters['DOWN_LEFT'],
                self._gui._border_characters['HORIZONTAL'] * (width - 2),
                self._gui._border_characters['DOWN_RIGHT'])
        else:
            render_text = '{}{}[{}]{}{}'.format(
                self._gui._border_characters['DOWN_LEFT'],
                self._gui._border_characters['HORIZONTAL'] * (width - 6 - len(footer)),
                footer,
                self._gui._border_characters['HORIZONTAL'] * 2,
                self._gui._border_characters['DOWN_RIGHT'])
        self._gui._stdscr.addstr(y, start_x, render_text)
        self.unset_color_mode(ui_element.get_border_color())


    def _draw_blank_row(self, ui_element, y):
        start_x, _ = ui_element.get_widget_start_pos()
        stop_x, _ = ui_element.get_widget_stop_pos()
        viewport_start_x, _ = ui_element.get_viewport_start_pos()
        width = ui_element.get_viewport_width()

        self.set_color_mode(ui_element.get_border_color())
        self._gui._stdscr.addstr(y, start_x, self._gui._border_characters['VERTICAL'])
        self._gui._stdscr.addstr(y, stop_x, self._gui._border_characters['VERTICAL'])
        self.unset_color_mode(ui_element.get_border_color())

        self._gui._stdscr.addstr(y, viewport_start_x, ' ' * width)


    def _get_render_text(self, ui_element, line, centered, selected, start_pos):
        render_text_length = ui_element.get_viewport_width() - 2

        if len(line) - start_pos < render_text_length:
            if centered:
                render_text = '{}'.format(line[start_pos:].center(render_text_length, ' '))
            else:
                render_text = '{}{}'.format(line[start_pos:],
                                            ' ' * (render_text_length - len(line[start_pos:])))
        else:
            render_text = line[start_pos:start_pos + render_text_length]

        render_text_fragments = self._generate_text_color_fragments(ui_element, line, render_text, selected)
        return render_text_fragments


    def _generate_text_color_fragments(self, ui_element, line, render_text, selected):
        fragments = [[render_text, ui_element.get_selected_color() if selected else ui_element.get_color()]]

        for color_rule in self._color_rules:
            fragments, match = color_rule.generate_fragments(ui_element, line, render_text, selected)
            if match:
                return fragments

        return fragments


    def draw_text_in_viewport(self, ui_element, multi_lines, selected=False, start_pos=0):
      start_x, start_y = ui_element.get_viewport_start_pos()
      stop_x, stop_y = ui_element.get_viewport_stop_pos()
      if ui_element._style['vertical_alignment'] == 'top':
        return self.draw_text_in(ui_element, multi_lines, start_x, stop_x, start_y, stop_y, selected, start_pos)

      count = len(multi_lines.splitlines())
      height = ui_element.get_viewport_height()
      if ui_element._style['vertical_alignment'] == 'middle':
        return self.draw_text_in(ui_element, multi_lines, start_x, stop_x,
            start_y + (height - count) // 2, stop_y, selected, start_pos)
      elif ui_element._style['vertical_alignment'] == 'bottom':
        if count > height: count = height
        return self.draw_text_in(ui_element, multi_lines, start_x, stop_x,
            stop_y - count + 1, stop_y, selected, start_pos)


    def draw_text_in(self, ui_element, multi_lines, start_x, stop_x, start_y, stop_y, selected=False, start_pos=0):
      lines = multi_lines.splitlines()
      y = start_y
      i = 0
      while y <= stop_y and i < len(lines):
        self._draw_one_line_text_in(ui_element, lines[i], start_x, stop_x, y, selected, start_pos)
        y += 1
        i += 1
      return i


    def _get_render_text_in(self, ui_element, line, space, selected, start_pos):
        render_text_length = space
        if len(line) - start_pos < render_text_length:
            render_text = ('{}'.format(line[start_pos:].center(render_text_length, ' '))
                           if ui_element._style['alignment'] == 'center'
                           else '{}{}'.format(line[start_pos:], ' ' * (render_text_length - len(line[start_pos:]))))
        else:
            render_text = line[start_pos:start_pos + render_text_length]
        render_text_fragments = self._generate_text_color_fragments(ui_element, line, render_text, selected)
        return render_text_fragments


    def _draw_one_line_text_in(self, ui_element, line, start_x, stop_x, y, selected, start_pos):
        space = stop_x - start_x + 1
        render_text = self._get_render_text_in(ui_element, line, space, selected, start_pos)
        current_start_x = start_x

        # Each text elem is a list with [text, color]
        for text_elem in render_text:
            self.set_color_mode(text_elem[1])

            # BLACK_ON_WHITE + BOLD is unreadable on windows terminals
            if selected and text_elem[1] != py_cui.BLACK_ON_WHITE:
                self._set_bold()

            self._gui._stdscr.addstr(y, current_start_x, text_elem[0])
            current_start_x += len(text_elem[0])

            if selected and text_elem[1] != py_cui.BLACK_ON_WHITE:
                self._unset_bold()

            self.unset_color_mode(text_elem[1])


    def draw_text(self, ui_element, multi_lines, y, centered=False, bordered=True, selected=False, start_pos=0):
      lines = multi_lines.splitlines()
      count = 0
      for line in lines:
        self._draw_text(ui_element, line, y + count, centered, bordered, selected, start_pos)
        count += 1
      return count


    def _draw_text(self, ui_element, line, y, centered, bordered, selected, start_pos):
        start_x, _ = ui_element.get_widget_start_pos()
        stop_x, _ = ui_element.get_widget_stop_pos()
        _, viewport_stop_y = ui_element.get_viewport_stop_pos()
        if y > viewport_stop_y:
            return

        render_text = self._get_render_text(ui_element, line, centered, selected, start_pos)
        current_start_x = start_x

        if bordered:
            if ui_element.is_hovering(): self._set_bold()
            self.set_color_mode(ui_element.get_border_color())
            self._gui._stdscr.addstr(y, start_x, self._gui._border_characters['VERTICAL'])
            current_start_x += 2
            self.unset_color_mode(ui_element.get_border_color())
            if ui_element.is_hovering(): self._unset_bold()

        # Each text elem is a list with [text, color]
        for text_elem in render_text:
            self.set_color_mode(text_elem[1])

            # BLACK_ON_WHITE + BOLD is unreadable on windows terminals
            if selected and text_elem[1] != py_cui.BLACK_ON_WHITE:
                self._set_bold()

            self._gui._stdscr.addstr(y, current_start_x, text_elem[0])
            current_start_x += len(text_elem[0])

            if selected and text_elem[1] != py_cui.BLACK_ON_WHITE:
                self._unset_bold()

            self.unset_color_mode(text_elem[1])

        if bordered:
            if ui_element.is_hovering(): self._set_bold()
            self.set_color_mode(ui_element.get_border_color())
            self._gui._stdscr.addstr(y, stop_x, self._gui._border_characters['VERTICAL'])
            self.unset_color_mode(ui_element.get_border_color())
            if ui_element.is_hovering(): self._unset_bold()
