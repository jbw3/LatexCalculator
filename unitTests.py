##
# @file unitTests.py
# @author John Wilkes

import unittest
from LatexCalculator import *

class TestLatexCalculator(unittest.TestCase):
	def setUp(self):
		self.calc = LatexCalculatorCommand()
		self.calc.view.str = ""

	def tearDown(self):
		del self.calc

	def testGetEqualStr(self):
		self.calc.view.str = "$1 + 1$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 1))
		self.assertEqual(equalStr, " = ")

		self.calc.view.str = "$(5.69 * 45) + (7 - 90) + 4**7$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 1))
		self.assertEqual(equalStr, " = ")

		self.calc.view.str = "$1 * 4 $"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 1))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4\t$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 1))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4   $"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 1))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4=$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 2))
		self.assertEqual(equalStr, " = ")

		self.calc.view.str = "$1 * 4 =$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 2))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4 = $"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 3))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4 =\t$"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 3))
		self.assertEqual(equalStr, "= ")

		self.calc.view.str = "$1 * 4 =    $"
		equalStr = self.calc.getEqualStr(sublime.Region(1, len(self.calc.view.str) - 6))
		self.assertEqual(equalStr, "= ")

	def testGetEvalRegion(self):
		self.calc.view.str = "$1 + 2$"
		mathReg = sublime.Region(1, len(self.calc.view.str) - 1)
		evalReg = self.calc.getEvalRegion(mathReg)
		self.assertEqual(evalReg[0], sublime.Region(1, 6))
		self.assertEqual(evalReg[1], sublime.Region(6, 6))

		self.calc.view.str = "$1 + 2 = $"
		mathReg = sublime.Region(1, len(self.calc.view.str) - 1)
		evalReg = self.calc.getEvalRegion(mathReg)
		self.assertEqual(evalReg[0], sublime.Region(1, 7))
		self.assertEqual(evalReg[1], sublime.Region(7, 9))

		self.calc.view.str = "$1 + 2 = 4 - 1$"
		mathReg = sublime.Region(1, len(self.calc.view.str) - 1)
		evalReg = self.calc.getEvalRegion(mathReg)
		self.assertEqual(evalReg[0], sublime.Region(8, 14))
		self.assertEqual(evalReg[1], sublime.Region(14, 14))

		self.calc.view.str = "$1 + 2 = 4 $"
		mathReg = sublime.Region(1, len(self.calc.view.str) - 1)
		evalReg = self.calc.getEvalRegion(mathReg)
		self.assertEqual(evalReg[0], sublime.Region(1, 7))
		self.assertEqual(evalReg[1], sublime.Region(7, 11))

		self.calc.view.str = "$1 + 2 = 4 - 1 = 3$"
		mathReg = sublime.Region(1, len(self.calc.view.str) - 1)
		evalReg = self.calc.getEvalRegion(mathReg)
		self.assertEqual(evalReg[0], sublime.Region(8, 15))
		self.assertEqual(evalReg[1], sublime.Region(15, 18))

	def testAddMultiplication(self):
		s = self.calc.addMultiplication("(2.56)(34)")
		self.assertEqual(s, "(2.56)*(34)")

		s = self.calc.addMultiplication("(2.56) (34)")
		self.assertEqual(s, "(2.56) *(34)")

		s = self.calc.addMultiplication("(2.56)\t(34)")
		self.assertEqual(s, "(2.56)\t*(34)")

		s = self.calc.addMultiplication("(2.56)(34)(1 - 2)(35.2/16)")
		self.assertEqual(s, "(2.56)*(34)*(1 - 2)*(35.2/16)")

		s = self.calc.addMultiplication("(2.56)(34 - (2)(8.1))")
		self.assertEqual(s, "(2.56)*(34 - (2)*(8.1))")

		s = self.calc.addMultiplication("(2.56)*(34)")
		self.assertEqual(s, "(2.56)*(34)")

		s = self.calc.addMultiplication("(2.56)+(34)")
		self.assertEqual(s, "(2.56)+(34)")

		s = self.calc.addMultiplication("(2.56) + (34)")
		self.assertEqual(s, "(2.56) + (34)")

	def testFormatEvalStr(self):
		evalStr = self.calc.formatEvalStr("1 + 2")
		self.assertEqual(evalStr, "1 + 2")

		evalStr = self.calc.formatEvalStr("[(1 + 2) * 3]")
		self.assertEqual(evalStr, "((1 + 2) * 3)")

		evalStr = self.calc.formatEvalStr("16^{0.25}")
		self.assertEqual(evalStr, "16**(0.25)")

		evalStr = self.calc.formatEvalStr("42 \\times 8")
		self.assertEqual(evalStr, "42 * 8")

		evalStr = self.calc.formatEvalStr("42 \\cdot 8")
		self.assertEqual(evalStr, "42 * 8")

		evalStr = self.calc.formatEvalStr("\\{42 \\times 8\\}")
		self.assertEqual(evalStr, "(42 * 8)")

		evalStr = self.calc.formatEvalStr("42 \\div 8")
		self.assertEqual(evalStr, "42 / 8")

		evalStr = self.calc.formatEvalStr("2^3")
		self.assertEqual(evalStr, "2**3")

		evalStr = self.calc.formatEvalStr("2 * \\pi")
		self.assertEqual(evalStr, "2 * math.pi")

		evalStr = self.calc.formatEvalStr("\\sin(\\pi)")
		self.assertEqual(evalStr, "math.sin(math.pi)")

		evalStr = self.calc.formatEvalStr("\\cos(\\pi/2)")
		self.assertEqual(evalStr, "math.cos(math.pi/2)")

		evalStr = self.calc.formatEvalStr("\\tan(\\pi)")
		self.assertEqual(evalStr, "math.tan(math.pi)")

		evalStr = self.calc.formatEvalStr("\\cot(\\pi)")
		self.assertEqual(evalStr, "cot(math.pi)")

		evalStr = self.calc.formatEvalStr("\\sec(\\pi)")
		self.assertEqual(evalStr, "sec(math.pi)")

		evalStr = self.calc.formatEvalStr("\\csc(\\pi)")
		self.assertEqual(evalStr, "csc(math.pi)")

		evalStr = self.calc.formatEvalStr("8\n*\r3")
		self.assertEqual(evalStr, "8 * 3")

		evalStr = self.calc.formatEvalStr("(8.123456)(3.324)")
		self.assertEqual(evalStr, "(8.123456)*(3.324)")

	def testCalcAnswer(self):
		ansStr = self.calc.calcAnswer("1 + 1")
		self.assertEqual(ansStr, "2")

		ansStr = self.calc.calcAnswer("1 + 2 * 3")
		self.assertEqual(ansStr, "7")

		ansStr = self.calc.calcAnswer("(1 + 2) * 3")
		self.assertEqual(ansStr, "9")

		ansStr = self.calc.calcAnswer("2 * math.pi")
		self.assertEqual(ansStr, "6.283")

		ansStr = self.calc.calcAnswer("25 **.5")
		self.assertEqual(ansStr, "5")

		ansStr = self.calc.calcAnswer("10**3")
		self.assertEqual(ansStr, "1000")

		ansStr = self.calc.calcAnswer("(1 + 2 * 3")
		self.assertEqual(ansStr, "")

		ansStr = self.calc.calcAnswer("")
		self.assertEqual(ansStr, "")

		ansStr = self.calc.calcAnswer("cot(math.pi/3)")
		self.assertEqual(ansStr, "0.577")

		ansStr = self.calc.calcAnswer("sec(math.pi/3)")
		self.assertEqual(ansStr, "2")

		ansStr = self.calc.calcAnswer("csc(math.pi/3)")
		self.assertEqual(ansStr, "1.155")

if __name__ == "__main__":
	unittest.main()
