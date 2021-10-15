#!/usr/bin/python3.9

import py_cui
import logging

if __name__ == '__main__':
  gui = py_cui.PyCUI(10, 10)
  gui.enable_logging(log_file_path='./all-in-one.log', logging_level=logging.DEBUG)
  gui.set_refresh_timeout(1)

  gui.set_title("All-in-one Demo")

  root = gui.get_root()
  root.add_widget(py_cui.widgets.BlockLabel(root, '   col\nrow   ', 0, 0, 1, 1))

  root.add_widget(py_cui.widgets.Label(root, 'row1', 1, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row2', 2, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row3', 3, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row4', 4, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row5', 5, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row6', 6, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row7', 7, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row8', 8, 0))
  root.add_widget(py_cui.widgets.Label(root, 'row9', 9, 0))

  root.add_widget(py_cui.widgets.Label(root, 'col1', 0, 1))
  root.add_widget(py_cui.widgets.Label(root, 'col2', 0, 2))
  root.add_widget(py_cui.widgets.Label(root, 'col3', 0, 3))
  root.add_widget(py_cui.widgets.Label(root, 'col4', 0, 4))
  root.add_widget(py_cui.widgets.Label(root, 'col5', 0, 5))
  root.add_widget(py_cui.widgets.Label(root, 'col6', 0, 6))
  root.add_widget(py_cui.widgets.Label(root, 'col7', 0, 7))
  root.add_widget(py_cui.widgets.Label(root, 'col8', 0, 8))
  root.add_widget(py_cui.widgets.Label(root, 'col9', 0, 9))

  menu = root.add_widget(py_cui.widgets.ScrollMenu(root, 'Menu Demo', 1, 1, 6, 3))

  menu.add_item_list(['item {}'.format(i) for i in range(26)])
  root.add_widget(py_cui.widgets.Button(root, "Add Item", 7, 1, 1, 3,
      command=lambda : menu.add_item('item {}'.format(menu.get_item_size()))))
  root.add_widget(py_cui.widgets.Button(root, "Remove Item", 8, 1, 1, 3,
      command=lambda : menu.remove_selected_item()))
  root.add_widget(py_cui.widgets.Button(root, "Clear Items", 9, 1, 1, 3,
      command=lambda : menu.clear_items()))

  text1 = root.add_widget(py_cui.widgets.TextBox(root, "TextBox Demo", 1, 4, 1, 3))
  text2 = root.add_widget(py_cui.widgets.ScrollTextBlock(root, "ScrollTextBlock Demo", 2, 4, 6, 3))
  def ShowDetail():
    text1.set_text('ONE ' + menu.get())
    text2.set_text('\n'.join([menu.get() * i for i in range(10)]))
  menu.add_key_command(py_cui.keys.KEY_ENTER, ShowDetail);

  check = root.add_widget(py_cui.widgets.CheckBoxMenu(root, "CheckBoxMenu Demo", 8, 4, 2, 3))
  check.add_item('UTF8 Rendering')
  check._events['on_change'] = lambda: gui.set_unicode_borders() if check.is_checked('UTF8 Rendering') else gui.set_ansi_borders()

  slider = root.add_widget(py_cui.widgets.Slider(root, "Slider Demo", 1, 7, 1, 3))

  gui.start()
