import unittest
from .TestUtils import TestUtils

class Tests(unittest.TestCase):
    def test002(self):
        res = TestUtils().test("t002")
        self.assertEqual('Identical', res)

    def test003(self):
        res = TestUtils().test("t003")
        self.assertEqual('Identical', res)

    def test004(self):
        res = TestUtils().test("t004")
        self.assertEqual('Identical', res)

    def test005(self):
        res = TestUtils().test("t005")
        self.assertEqual('Identical', res)

    def test006(self):
        res = TestUtils().test("t006")
        self.assertEqual('Identical', res)

    def test007(self):
        res = TestUtils().test("t007")
        self.assertEqual('Identical', res)

    def test008(self):
        res = TestUtils().test("t008")
        self.assertEqual('Identical', res)

    def test009(self):
        res = TestUtils().test("t009")
        self.assertEqual('Identical', res)

    def test010(self):
        res = TestUtils().test("t010")
        self.assertEqual('Identical', res)

if __name__ == 'main':
    unittest.main()
