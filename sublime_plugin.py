##
# @file sublime_plugin.py
# @brief Contains mock functions for unit testing

import sublime

class TextCommand(object):
	def __init__(self):
		self.view = sublime.View()
