##
# @file LatexCalculator.py
# @author John Wilkes

import math
import sublime, sublime_plugin

DEBUG = False

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def cot(x):
	return 1 / math.tan(x)

def sec(x):
	return 1 / math.cos(x)

def csc(x):
	return 1 / math.sin(x)

class LatexCalculatorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			## @todo make sure we're not in a comment

			# get the region before the cursor
			beforeRegion = sublime.Region(0, region.begin())
			beforeStr = self.view.substr(beforeRegion)

			count = self.countDollars(beforeRegion)

			mathRegion = self.getMathRegion(region)
			#print(mathRegion.a, mathRegion.b)

			mathStr = self.view.substr(mathRegion)
			#print(mathStr)

			evalRegion, ansRegion = self.getEvalRegion(mathRegion)

			evalStr = self.view.substr(evalRegion)

			evalStr = self.formatEvalStr(evalStr)

			ansStr = self.calcAnswer(evalStr)

			self.view.replace(edit, ansRegion, self.getEqualStr(evalRegion) + ansStr)

	##
	# @brief Count the $ symbols in the given region
	# @todo Don't count $ symbols in comments or \$
	def countDollars(self, region):
		substr = self.view.substr(region)
		count = substr.count("$")
		return count

	##
	# @todo Ignore $ symbols in comments and \$
	def findMathBegin(self, selPos):
		region = sublime.Region(0, selPos)
		return self.view.substr(region).rfind("$") + 1

	##
	# @todo Ignore $ symbols in comments and \$
	def findMathEnd(self, selPos):
		region = sublime.Region(selPos, self.view.find("\n", selPos).a)
		index = self.view.substr(region).find("$")
		if index != -1:
			return index + selPos
		return region.end()

	def getMathRegion(self, selRegion):
		return sublime.Region(self.findMathBegin(selRegion.begin()), self.findMathEnd(selRegion.begin()))

	##
	# @brief Insert the equal symbol at the end the eval region if there
	# is not one already
	def getEqualStr(self, evalRegion):
		# don't add a space in front of the equal sign if there
		# is already one
		if self.view.substr(evalRegion.end() - 1) not in " \t":
			return " = "
		return "= "

	##
	# @return the eval region and the answer region
	def getEvalRegion(self, mathRegion):
		evalRegion = sublime.Region(0, 0)
		mathStr = self.view.substr(mathRegion)

		lastEqual = mathStr.rfind("=")
		# if there are no equal signs, the eval string is the math string
		if lastEqual == -1:
			evalRegion = mathRegion
		# else if there is at least one equal sign...
		else:
			afterIsEval = False
			afterStr = mathStr[lastEqual+1:].strip()

			# if there is something after the equal sign, check it...
			if afterStr != "":
				# check what's after the equal sign to see if it's a number...
				try:
					float(afterStr)
				# if it's not a number, it must be the eval string
				except:
					afterIsEval = True

			# if the eval string is after the equal sign...
			if afterIsEval:
				evalRegion = sublime.Region(mathRegion.begin() + lastEqual + 1, mathRegion.end())
			# else the eval string must be before the equal sign
			else:
				beginIndex = mathStr.rfind("=", 0, lastEqual)
				# if beginIndex is -1, this starts at the beginning of the
				# region, otherwise it starts after the equal sign found
				evalRegion = sublime.Region(mathRegion.begin() + beginIndex + 1, mathRegion.begin() + lastEqual)

		ansRegion = sublime.Region(evalRegion.end(), mathRegion.end())

		if DEBUG:
			print("\""+self.view.substr(evalRegion)+"\", \""+self.view.substr(ansRegion)+"\"")

		return (evalRegion, ansRegion)

	##
	# @todo replace \frac{}{}, \sqrt{}, \binom, \choose, \bmod, \pmod, \\,
	# \lfloor, \rfloor, \lceil, \rceil
	#
	# @brief Convert LaTeX string into Python string
	# @param evalStr the LaTeX string to convert
	# @return the Python string
	def formatEvalStr(self, evalStr):
		newStr = ""
		length = len(evalStr)
		i = 0
		while i < length:
			ch = evalStr[i]
			if ch == "^":
				## @todo this needs to look for {} after ^
				newStr += "**"
			elif ch == "[" or ch == "{":
				newStr += "("
			elif ch == "]" or ch == "}":
				newStr += ")"
			elif ch == "\\":
				i += 1
				if i < length:
					temp = evalStr[i]
					i += 1
					if temp.upper() in ALPHABET:
						while i < length and evalStr[i].upper() in ALPHABET:
							temp += evalStr[i]
							i += 1
					newStr += self.evalSymbol(temp)
				else:
					newStr += ch
				continue
			elif ch == "\n" or ch == "\r":
				newStr += " "
			else:
				newStr += ch

			i += 1

		newStr = self.addMultiplication(newStr)

		return newStr

	##
	# @todo Add arcsin, arccos, arctan, arccot, arcsec, arccsc,
	# sinh, cosh, tanh, coth, sech, csch
	def evalSymbol(self, s):
		if s == "times" or s == "cdot":
			return "*"
		if s == "div":
			return "/"
		if s == "pi":
			return "math.pi"
		if s == "sin":
			return "math.sin"
		if s == "cos":
			return "math.cos"
		if s == "tan":
			return "math.tan"
		if s == "cot":
			return "cot"
		if s == "sec":
			return "sec"
		if s == "csc":
			return "csc"
		if s == "{":
			return "("
		if s == "}":
			return ")"
		return "\\"+s

	##
	# @todo This needs to add a multiplication sign when the first number
	# does not have parenthesis (e.g. 2(3) -> 2*(3))
	def addMultiplication(self, string):
		newStr = ""

		needsOp = False
		for ch in string:
			if ch == ")":
				needsOp = True
			elif ch == "(" and needsOp:
				newStr += "*"
				needsOp = False
			elif ch not in " \t":
				needsOp = False
			newStr += ch

		return newStr

	def calcAnswer(self, evalStr):
		ansStr = ""
		try:
			ans = eval(evalStr)
			ans = round(ans, 3) ##@todo make rounding precision configurable
		except:
			if DEBUG:
				print("Error")
		else:
			ansStr = str(ans)
			# strip trailing zeros after decimal point
			if "." in ansStr:
				ansStr = ansStr.rstrip("0").rstrip(".")

		return ansStr
