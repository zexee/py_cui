"""A python library for intuitively creating CUI/TUI interfaces with pre-built widgets.
"""

#
# Author:   Jakub Wlodek
# Created:  12-Aug-2019
# Docs:     https://jwlodek.github.io/py_cui-docs
# License:  BSD-3-Clause (New/Revised)
#

# Some python core library imports
import sys
import os
import time
import copy
import shutil       # We use shutil for getting the terminal dimensions
import threading    # Threading is used for loading icon popups
import logging      # Use logging library for debug purposes


# py_cui uses the curses library. On windows this does not exist, but
# there is a open source windows-curses module that adds curses support
# for python on windows
import curses


# py_cui imports
import py_cui
import py_cui.keys
import py_cui.statusbar
import py_cui.widgets
import py_cui.dialogs
import py_cui.layouts
import py_cui.popups
import py_cui.renderer
import py_cui.debug
import py_cui.errors
from py_cui.colors import *


# Version number
__version__ = '0.1.4'


def fit_text(width, text, center=False):
    """Fits text to screen size

    Helper function to fit text within a given width. Used to fix issue with status/title bar text
    being too long

    Parameters
    ----------
    width : int
        width of window in characters
    text : str
        input text
    center : Boolean
        flag to center text

    Returns
    -------
    fitted_text : str
        text fixed depending on width
    """

    if width < 5:
        return '.' * width
    if len(text) >= width:
        return text[:width - 4] + '...'
    else:
        total_num_spaces = width - len(text) - 1
        if center:
            left_spaces = int(total_num_spaces / 2)
            right_spaces = total_num_spaces - left_spaces
            return ' ' * left_spaces + text + ' ' * right_spaces
        else:
            return text + ' ' * total_num_spaces


class PyCUI:
    """Base CUI class

    Main user interface class for py_cui. To create a user interface, you must
    first create an instance of this class, and then add cells + widgets to it.

    Attributes
    ----------
    cursor_x, cursor_y : int
        absolute position of the cursor in the CUI
    title_bar : py_cui.statusbar.StatusBar
        a status bar object that gets drawn at the top of the CUI
    status_bar : py_cui.statusbar.StatusBar
        a status bar object that gets drawn at the bottom of the CUI
    keybindings : list of py_cui.keybinding.KeyBinding
        list of keybindings to check against in the main CUI loop
    height, width : int
        height of the terminal in characters, width of terminal in characters
    exit_key : key_code
        a key code for a key that exits the CUI
    simulated_terminal : List[int]
        Dimensions for an alternative simulated terminal (used for testing)
    """

    def __init__(self, num_rows, num_cols, auto_focus_buttons=True,
                 exit_key=py_cui.keys.KEY_Q_LOWER, simulated_terminal=None):
        """Constructor for PyCUI class
        """

        self._title = 'PyCUI Window'
        # When this is not set, the escape character delay
        # is too long for exiting focus mode
        os.environ.setdefault('ESCDELAY', '25')

        # For unit testing purposes, we want to simulate terminal
        # dimensions so that we don't get errors
        self._simulated_terminal = simulated_terminal

        if self._simulated_terminal is None:
            term_size = shutil.get_terminal_size()
            height  = term_size.lines
            width   = term_size.columns
        else:
            height  = simulated_terminal[0]
            width   = simulated_terminal[1]

        # Init terminal height width. Subtract 4 from height
        # for title/status bar and padding
        self._height = height
        self._width = width
        self._top_padding = 1
        self._bottom_padding = 1
        self._left_padding = 0
        self._right_padding = 0

        # Add status and title bar
        self.title_bar = py_cui.statusbar.StatusBar(self._title, BLACK_ON_WHITE)
        exit_key_char = py_cui.keys.get_char_from_ascii(exit_key)
        self._init_status_bar_text  = 'Press - {} - to exit. Arrow Keys to move ' \
                                       'between widgets. Enter to enter focus ' \
                                       'mode.'.format(exit_key_char)
        self.status_bar = py_cui.statusbar.StatusBar(self._init_status_bar_text,
                                                     BLACK_ON_WHITE)

        # Logging object initialization for py_cui
        self._logger = py_cui.debug._initialize_logger(self,
                                                       name='py_cui')

        self._renderer = py_cui.renderer.Renderer(self)
        self._border_characters = {
            'UP_LEFT'       : '+',
            'UP_RIGHT'      : '+',
            'DOWN_LEFT'     : '+',
            'DOWN_RIGHT'    : '+',
            'HORIZONTAL'    : '-',
            'VERTICAL'      : '|',
            'SCROLLBAR'     : '=',
        }
        self._stdscr                = None
        self._root                  = self.create_new_layout(num_rows, num_cols)
        self._refresh_timeout       = -1

        # Variables for determining selected widget/focus mode
        self._popup                 = None
        self._auto_focus_buttons    = auto_focus_buttons

        # CUI blocks when loading popup is open
        self._loading               = False
        self._stopped               = False
        self._post_loading_callback = None
        self._on_draw_update_func   = None

        # Top level keybindings. Exit key is 'q' by default
        self._exit_key     = exit_key
        self._forward_cycle_key = py_cui.keys.KEY_CTRL_LEFT
        self._reverse_cycle_key = py_cui.keys.KEY_CTRL_RIGHT

        # Callback to fire when CUI is stopped.
        self._on_stop = None


    def set_refresh_timeout(self, timeout):
        """Sets the CUI auto-refresh timeout to a number of seconds.

        Parameters
        ----------
        timeout : int
            Number of seconds to wait before refreshing the CUI
        """

        # We want the refresh timeout in milliseconds as an integer
        self._refresh_timeout = int(timeout * 1000)


    def set_on_draw_update_func(self, update_function):
        """Adds a function that is fired during each draw call of the CUI

        Parameters
        ----------
        update_function : function
            A no-argument or lambda function that is fired at the start of each draw call
        """

        self._on_draw_update_func = update_function


    def set_widget_cycle_key(self, forward_cycle_key=None, reverse_cycle_key=None):
        """Assigns a key for automatically cycling through widgets in both focus and overview modes

        Parameters
        ----------
        widget_cycle_key : py_cui.keys.KEY
            Key code for key to cycle through widgets
        """

        if forward_cycle_key is not None:
            self._forward_cycle_key = forward_cycle_key
        if reverse_cycle_key is not None:
            self._reverse_cycle_key = reverse_cycle_key


    def enable_logging(self, log_file_path='py_cui_log.txt', logging_level = logging.DEBUG):
        """Function enables logging for py_cui library

        Parameters
        ----------
        log_file_path : str
            The target log filepath. Default 'py_cui_log.txt
        logging_level : int
            Default logging level = logging.DEBUG
        """

        try:
            py_cui.debug._enable_logging(self._logger, filename=log_file_path, logging_level=logging_level)
            self._logger.info('Initialized logger')
        except PermissionError as e:
            print('Failed to initialize logger: {}'.format(str(e)))


    def create_new_layout(self, num_rows, num_cols):
        return py_cui.layouts.GridLayout(
            self,
            num_rows, num_cols,
            self._height - self._top_padding - self._bottom_padding - 2,
            self._width - self._left_padding - self._right_padding)


    # ----------------------------------------------#
    # Initialization functions                      #
    # Used to initialzie CUI and its features       #
    # ----------------------------------------------#


    def start(self):
      curses.wrapper(self._draw)


    def stop(self):
        """Function that stops the CUI, and fires the callback function.

        Callback must be a no arg method
        """

        self._logger.info('Stopping CUI')
        self._stopped = True


    def run_on_exit(self, command):
        """Sets callback function on CUI exit. Must be a no-argument function or lambda function

        Parameters
        ----------
        command : function
            A no-argument or lambda function to be fired on exit
        """

        self._on_stop = command


    def set_title(self, title):
        """Sets the title bar text

        Parameters
        ----------
        title : str
            New title for CUI
        """

        self._title = title


    def set_status_bar_text(self, text):
        """Sets the status bar text when in overview mode

        Parameters
        ----------
        text : str
            Status bar text
        """

        self._init_status_bar_text = text
        self.status_bar.set_text(text)


    def _initialize_colors(self):
        """Function for initialzing curses colors. Called when CUI is first created.
        """

        # Start colors in curses.
        # For each color pair in color map, initialize color combination.
        curses.start_color()
        curses.init_color(curses.COLOR_BLUE, 0, 0, 500)
        for color_pair in py_cui.colors._COLOR_MAP.keys():
            fg_color, bg_color = py_cui.colors._COLOR_MAP[color_pair]
            curses.init_pair(color_pair, fg_color, bg_color)


    def set_ansi_borders(self):
        self.set_widget_border_characters('+', '+', '+', '+', '-', '|', '=')


    def set_unicode_borders(self):
        self.set_widget_border_characters('\u256d', '\u256e', '\u2570', '\u256f', '\u2500', '\u2502', '\u2503')


    def set_widget_border_characters(self, upper_left_corner, upper_right_corner, lower_left_corner, lower_right_corner, horizontal, vertical, scroll):
        self._border_characters = {
            'UP_LEFT': upper_left_corner,
            'UP_RIGHT': upper_right_corner,
            'DOWN_LEFT': lower_left_corner,
            'DOWN_RIGHT': lower_right_corner,
            'HORIZONTAL': horizontal,
            'VERTICAL': vertical,
            'SCROLLBAR': scroll,
        }
        self._logger.info('Set border_characters to {}'.format(self._border_characters))


    def get_element_at_position(self, x, y):
        if self._popup is not None and self._popup._contains_position(x, y):
            return self._popup
        if self._popup is None:
            return self._root.get_element_at_position(x, y)
        return None


    # CUI status functions. Used to switch between widgets, set the mode, and
    # identify neighbors for overview mode

    def move_focus(self, widget, auto_press_buttons=True):
        self._root.move_focus(widget)
        if self._auto_focus_buttons and auto_press_buttons and isinstance(widget, py_cui.widgets.Button):
            if widget.command is not None:
                widget.command()
            self._logger.info('Moved focus to button {} - ran autofocus command'.format(widget.get_title()))
        elif self._auto_focus_buttons and isinstance(widget, py_cui.widgets.Button):
            self.status_bar.set_text(self._init_status_bar_text)
        else:
            self.status_bar.set_text(widget.get_help_text())
        self._logger.info('Moved focus to widget {}'.format(widget.get_title()))


    def add_key_command(self, key, command):
        self._root.add_key_command(key, command)


    def get_root(self) -> py_cui.layouts.Layout:
        return self._root

    # Popup functions. Used to display messages, warnings, and errors to the user.

    def show_message_popup(self, title, text):
        """Shows a message popup

        Parameters
        ----------
        title : str
            Message title
        text : str
            Message text
        """

        color       = WHITE_ON_BLACK
        self._popup = py_cui.popups.MessagePopup(self, title, text, color, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_warning_popup(self, title, text):
        """Shows a warning popup

        Parameters
        ----------
        title : str
            Warning title
        text : str
            Warning text
        """

        color       = YELLOW_ON_BLACK
        self._popup = py_cui.popups.MessagePopup(self, 'WARNING - ' + title, text, color, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_error_popup(self, title, text):
        """Shows an error popup

        Parameters
        ----------
        title : str
            Error title
        text : str
            Error text
        """

        color       = RED_ON_BLACK
        self._popup = py_cui.popups.MessagePopup(self, 'ERROR - ' + title, text, color, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_yes_no_popup(self, title, command):
        """Shows a yes/no popup.

        The 'command' parameter must be a function with a single boolean parameter

        Parameters
        ----------
        title : str
            Message title
        command : function
            A function taking in a single boolean parameter. Will be fired with True if yes selected, false otherwise
        """

        color       = WHITE_ON_BLACK
        self._popup = py_cui.popups.YesNoPopup(self, title + '- (y/n)', 'Yes - (y), No - (n)', color, command, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_text_box_popup(self, title, command, password=False):
        """Shows a textbox popup.

        The 'command' parameter must be a function with a single string parameter

        Parameters
        ----------
        title : str
            Message title
        command : Function
            A function with a single string parameter, fired with contents of textbox when enter key pressed
        password=False : bool
            If true, write characters as '*'
        """

        color       = WHITE_ON_BLACK
        self._popup = py_cui.popups.TextBoxPopup(self, title, color, command, self._renderer, password, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_menu_popup(self, title, menu_items, command, run_command_if_none=False):
        """Shows a menu popup.

        The 'command' parameter must be a function with a single string parameter

        Parameters
        ----------
        title : str
            menu title
        menu_items : list of str
            A list of menu items
        command : Function
            A function taking in a single string argument. Fired with selected menu item when ENTER pressed.
        run_command_if_none=False : bool
            If True, will run command passing in None if no menu item selected.
        """

        color       = WHITE_ON_BLACK
        self._popup = py_cui.popups.MenuPopup(self, menu_items, title, color, command, self._renderer, self._logger, run_command_if_none)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_loading_icon_popup(self, title, message, callback=None):
        """Shows a loading icon popup

        Parameters
        ----------
        title : str
            Message title
        message : str
            Message text. Will show as '$message...'
        callback=None : Function
            If not none, fired after loading is completed. Must be a no-arg function
        """

        if callback is not None:
            self._post_loading_callback = callback

        color         = WHITE_ON_BLACK
        self._loading = True
        self._popup   = py_cui.popups.LoadingIconPopup(self, title, message, color, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_loading_bar_popup(self, title, num_items, callback=None):
        """Shows loading bar popup.

        Use 'increment_loading_bar' to show progress

        Parameters
        ----------
        title : str
            Message title
        num_items : int
            Number of items to iterate through for loading
        callback=None : Function
            If not none, fired after loading is completed. Must be a no-arg function
        """

        if callback is not None:
            self._post_loading_callback = callback

        color         = WHITE_ON_BLACK
        self._loading = True
        self._popup   = py_cui.popups.LoadingBarPopup(self, title, num_items, color, self._renderer, self._logger)
        self._logger.info('Opened {} popup with title {}'.format(str(type(self._popup)), self._popup.get_title()))


    def show_form_popup(self, title, fields, passwd_fields=[], required=[], callback=None):
        """Shows form popup.

        Used for inputting several fields worth of values

        Parameters
        ---------
        title : str
            Message title
        fields : List[str]
            Names of each individual field
        passwd_fields : List[str]
            Field names that should have characters hidden
        required : List[str]
            Fields that are required before submission
        callback=None : Function
            If not none, fired after loading is completed. Must be a no-arg function
        """

        self._popup = py_cui.dialogs.form.FormPopup(self, fields, passwd_fields, required, {}, title, py_cui.WHITE_ON_BLACK, self._renderer, self._logger)
        if callback is not None:
            self._popup.set_on_submit_action(callback)


    def show_filedialog_popup(self, popup_type='openfile', initial_dir='.', callback=None, ascii_icons=True, limit_extensions=[]):
        """Shows form popup.

        Used for inputting several fields worth of values

        Parameters
        ---------
        title : str
            Message title
        fields : List[str]
            Names of each individual field
        passwd_fields : List[str]
            Field names that should have characters hidden
        required : List[str]
            Fields that are required before submission
        callback=None : Function
            If not none, fired after loading is completed. Must be a no-arg function
        """

        self._popup = py_cui.dialogs.filedialog.FileDialogPopup(self, callback, initial_dir, popup_type, ascii_icons, limit_extensions, py_cui.WHITE_ON_BLACK, self._renderer, self._logger)


    def increment_loading_bar(self):
        """Increments progress bar if loading bar popup is open
        """

        if self._popup is not None:
            self._popup._increment_counter()
        else:
            self._logger.warn('No popup is currently opened.')


    def stop_loading_popup(self):
        """Leaves loading state, and closes popup.

        Must be called by user to escape loading.
        """

        self._loading = False
        self.close_popup()
        self._logger.info('Stopping open loading popup')


    def close_popup(self):
        """Closes the popup, and resets focus
        """

        self.lose_focus()
        self._popup = None


    def _refresh_height_width(self, height, width):
        self._height = height
        self._width  = width
        self._root._refresh_height_width(self._height - self._top_padding - self._bottom_padding - 2,
                                         self._width - self._left_padding - self._right_padding)
        if self._popup is not None:
            self._popup.update_height_width()


    def get_absolute_size(self):
        return self._height, self._width


    def _draw_status_bars(self, stdscr, height, width):
        if self.status_bar is not None:
            stdscr.attron(curses.color_pair(self.status_bar.get_color()))
            stdscr.addstr(height - 1, 0, fit_text(width, self.status_bar.get_text(), center=True))
            stdscr.attroff(curses.color_pair(self.status_bar.get_color()))

        if self.title_bar is not None:
            stdscr.attron(curses.color_pair(self.title_bar.get_color()))
            stdscr.addstr(0, 0, fit_text(width, self._title, center=True))
            stdscr.attroff(curses.color_pair(self.title_bar.get_color()))


    def _display_window_warning(self, stdscr, error_info):
        stdscr.clear()
        stdscr.attron(curses.color_pair(RED_ON_BLACK))
        stdscr.addstr(0, 0, 'Error displaying CUI!!!')
        stdscr.addstr(1, 0, 'Error Type: {}'.format(error_info))
        stdscr.addstr(2, 0, 'Most likely terminal dimensions are too small.')
        stdscr.attroff(curses.color_pair(RED_ON_BLACK))
        stdscr.refresh()
        self._logger.info('Encountered error -> {}'.format(error_info))


    def _handle_key_presses(self, key_pressed):
        if self._popup is not None:
          self._popup._handle_key_press(key_pressed)
        else:
          self._root._handle_key_presses(key_pressed)


    def _draw(self, stdscr):
        """Main CUI draw loop called by start()

        Parameters
        ----------
        stdscr : curses Standard screen
            The screen buffer used for drawing CUI elements
        """

        # find height width, adjust if status/title bar added. We decrement the height by 4 to account for status/title bar and padding
        if self._simulated_terminal is None:
            height, width   = stdscr.getmaxyx()
        else:
            height = self._simulated_terminal[0]
            width  = self._simulated_terminal[1]
        if self._stdscr is None:
          # first time, need to initialize
          self._refresh_height_width(height, width)
        self._stdscr = stdscr

        key_pressed = 0

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        # stdscr.nodelay(False)
        #stdscr.keypad(True)

        # Initialization functions. Generates colors and renderer
        self._initialize_colors()

        # If user specified a refresh timeout, apply it here
        if self._refresh_timeout > 0:
            self._stdscr.timeout(self._refresh_timeout)

        # Loop where key_pressed is the last character pressed. Wait for exit key while no popup or focus mode
        while key_pressed != self._exit_key or self._root._in_focused_mode or self._popup is not None:
            try:
                # If we call stop, we want to break out of the main draw loop
                if self._stopped:
                    break

                # Initialization and size adjustment
                stdscr.erase()

                # If the user defined an update function to fire on each draw call,
                # Run it here. This can of course be also handled user-side
                # through a separate thread.
                if self._on_draw_update_func is not None:
                    self._on_draw_update_func()

                # This is what allows the CUI to be responsive. Adjust grid size based on current terminal size
                # Resize the grid and the widgets if there was a resize operation
                if key_pressed == curses.KEY_RESIZE:
                    if self._simulated_terminal is None:
                        height, width   = stdscr.getmaxyx()
                    else:
                        height = self._simulated_terminal[0]
                        width  = self._simulated_terminal[1]
                    self._logger.info('Resizing CUI to new dimensions {} by {}'.format(height, width))
                    try:
                        self._refresh_height_width(height, width)
                    except py_cui.errors.PyCUIOutOfBoundsError as e:
                        self._logger.info('Resized terminal too small')
                        self._display_window_warning(stdscr, str(e))

                # Here we handle mouse click events globally, or pass them to the UI element to handle
                elif key_pressed == curses.KEY_MOUSE:
                    self._logger.info('Detected mouse click')
                    try:
                      _, x, y, _, _ = curses.getmouse()
                    except:
                      # getmouse error
                      continue
                    in_element = self.get_element_at_position(x, y)

                    # In first case, we click inside already selected widget, pass click for processing
                    if in_element is not None and in_element.is_focused():
                        in_element._handle_mouse_press(x, y)
                    # Otherwise, if not a popup, select the clicked on widget
                    elif in_element is not None and not isinstance(in_element, py_cui.popups.Popup):
                        self.move_focus(in_element)
                        in_element._handle_mouse_press(x, y)

                # If we have a post_loading_callback, fire it here
                if self._post_loading_callback is not None and not self._loading:
                    self._logger.info('Firing post-loading callback function {}'.format(self._post_loading_callback.__name__))
                    self._post_loading_callback()
                    self._post_loading_callback = None

                # Handle widget cycling
                if key_pressed == self._forward_cycle_key:
                    self._root._cycle_widgets()
                elif key_pressed == self._reverse_cycle_key:
                    self._root._cycle_widgets(reverse=True)

                # Handle keypresses
                self._handle_key_presses(key_pressed)

                try:
                    # Draw status/title bar, and all widgets. Selected widget will be bolded.
                    self._draw_status_bars(stdscr, self._height, self._width)
                    self._root._draw()
                    # draw the popup if required
                    if self._popup is not None:
                        self._popup._draw()
                except curses.error as e:
                    self._logger.error('Curses error while drawing TUI')
                    self._display_window_warning(stdscr, str(e))
                except py_cui.errors.PyCUIOutOfBoundsError as e:
                    self._logger.error('Resized terminal too small')
                    self._display_window_warning(stdscr, str(e))

                # Refresh the screen
                stdscr.refresh()

                # Wait for next input
                if self._loading or self._post_loading_callback is not None:
                    # When loading, refresh screen every quarter second
                    time.sleep(0.25)
                    # Need to reset key_pressed, because otherwise the previously pressed key will be used.
                    key_pressed = 0
                elif self._stopped:
                    key_pressed = self._exit_key
                else:
                    # self._logger.info('Waiting for next keypress')
                    key_pressed = stdscr.getch()
                    if key_pressed > 0:
                        self._logger.info('keypress {}'.format(key_pressed))

            except KeyboardInterrupt:
                self._logger.info('Detect Keyboard Interrupt, Exiting...')
                self._stopped = True


        stdscr.erase()
        stdscr.refresh()
        curses.endwin()
        if self._on_stop is not None:
            self._logger.info('Firing onstop function {}'.format(self._on_stop.__name__))
            self._on_stop()


    def show_cursor(self):
      curses.curs_set(2)


    def hide_cursor(self):
      curses.curs_set(0)

