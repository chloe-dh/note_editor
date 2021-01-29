# #!/usr/bin/env python
#
# import tkinter as tk
# import pytest
# from pynput.keyboard import Key, Controller
# from note_editor.main import MainWindow
#
#
# def key_press_release(*args):
#     """simulate key press and release"""
#     key_dict = {'return': Key.enter, 'control': Key.ctrl, 'escape': Key.esc}
#     keyboard = Controller()
#     for key in args:
#         keyboard.press(key_dict[key])
#     for key in reversed(args):
#         keyboard.release(key_dict[key])
#
#
# def test_main_click_buttons():
#     """click on the buttons in MainWindow"""
#     gui = MainWindow()
#     number_buttons = 0
#     # loop through widgets
#
#     for children in gui.root.winfo_children():
#         # click on buttons
#         if children.winfo_class() == 'Button':
#             number_buttons += 1
#             try:
#                 children.invoke()
#             except tk.TclError:
#                 assert False
#             else:
#                 assert True
#     # check number of buttons
#     assert number_buttons == 3
#
#
# def test_main_return_key_press():
#     gui = MainWindow()
#     gui.root.mainloop()
#     # all widgets
#     possible_focus_on = gui.root.winfo_children()
#     # focus on main window
#     possible_focus_on.append(gui.root)
#     for elt in possible_focus_on:
#         elt.focus_set()
#         try:
#             key_press_release('return')
#         except tk.TclError:
#             assert False
#         else:
#             assert True
#
#
# def test_window_esc_key_press():
#     gui = MainWindow()
#     key_press_release('escape')
#     assert gui
#
#
# # @pytest.fixture
# # def response():
# #     """Sample pytest fixture.
# #
# #     See more at: http://doc.pytest.org/en/latest/fixture.html
# #     """
# #     # import requests
# #     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
# #
# #
# # def test_content(response):
# #     """Sample pytest test function with the pytest fixture as an argument."""
# #     # from bs4 import BeautifulSoup
# #     # assert 'GitHub' in BeautifulSoup(response.content).title.string
