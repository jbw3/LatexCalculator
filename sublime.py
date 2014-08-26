##
# @file sublime.py
# @brief Contains mock functions for unit testing

class Region(object):
	def __init__(self, a, b):
		self.a = a
		self.b = b

	def __str__(self):
		return "(" + str(self.a) + ", " + str(self.b) + ")"

	def __eq__(self, right):
		return (self.a == right.a and self.b == right.b)

	def __ne__(self, right):
		return (self.a != right.a or self.b != right.b)

	def begin(self):
		return min(self.a, self.b)

	def end(self):
		return max(self.a, self.b)

	def empty(self):
		return (self.a == self.b)

class View(object):
	def __init__(self):
		self.str = ""

	def substr(self, region):
		try:
			return self.str[region.begin() : region.end()]
		except(AttributeError):
			return self.str[region]
